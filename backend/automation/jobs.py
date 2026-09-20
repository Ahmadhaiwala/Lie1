"""
Lead Generation Jobs

Each job class targets one specific service category:
  - WebsiteLeadJob    → finds businesses with no/bad websites
  - WhatsAppBotLeadJob → finds businesses that rely on manual WhatsApp support
  - SEOLeadJob         → finds businesses with poor search visibility

Jobs use the existing WebCrawler + LLMClient to discover leads, extract
contact info, and produce a qualified lead record.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any

from crawler.web_crawler import WebCrawler
from crawler.config import CrawlerConfig
from llm.llm_provider import LLMProvider
from llm.llm_config import LLMConfig
from automation.search_provider import SearchProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class Lead:
    """A single qualified lead"""
    id: str
    source_url: str
    business_name: str
    service_needed: str          # "website" | "whatsapp_bot" | "seo"
    contact_email: List[str]
    contact_phone: List[str]
    website: Optional[str]
    pain_points: List[str]
    qualification_score: float   # 0.0 – 1.0
    raw_snippet: str
    location: str = ""
    industry: str = ""
    discovered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    outreach_sent: bool = False
    notes: str = ""
    
    # Geographic data
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None  # Distance from search center

    # ── Filter layer fields (populated by BusinessFilter) ──────────────
    # Priority assigned after online-presence + business-model evaluation
    filter_priority: str = "unfiltered"        # "high" | "medium" | "discard" | "unfiltered"
    filter_justification: str = ""             # 1-sentence reason shown in UI card
    filter_reasoning: str = ""                 # full paragraph shown on expand
    filter_online_score: float = -1.0          # 0-10, -1 = not evaluated
    filter_suitability_score: float = -1.0     # 0-10, -1 = not evaluated
    filter_recommended: List[str] = field(default_factory=list)  # recommended services

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class JobResult:
    """Result returned by every job"""
    job_name: str
    started_at: str
    finished_at: str
    leads_found: int
    leads: List[Lead]
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_name": self.job_name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "leads_found": self.leads_found,
            "leads": [l.to_dict() for l in self.leads],
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# Base Job
# ---------------------------------------------------------------------------

class BaseLeadJob:
    """
    Base class for all lead generation jobs.

    Subclasses must implement:
      - search_queries  → list[str]  search terms to use on Google/Bing
      - service_label   → str        human-readable service name
      - qualification_system_prompt → str
      - qualification_user_prompt(content) → str
    """

    JOB_NAME = "base_lead_job"
    SERVICE_LABEL = "unknown"

    # Search result pages to scrape per query
    RESULTS_PER_QUERY = 5

    # Google search URL template – returns a simple results page
    GOOGLE_SEARCH_URL = "https://www.google.com/search?q={query}&num={num}"

    def __init__(
        self,
        crawler_config: Optional[CrawlerConfig] = None,
        llm_config: Optional[LLMConfig] = None,
        custom_queries: Optional[List[str]] = None,
    ):
        self.crawler_config = crawler_config or CrawlerConfig(
            headless=True,
            page_timeout=20000,
        )
        self.llm_config = llm_config or LLMConfig.from_env()
        self.llm = LLMProvider(self.llm_config)
        self.search_provider = SearchProvider()
        self.custom_queries = [query.strip() for query in (custom_queries or []) if query.strip()]

    # ------------------------------------------------------------------
    # Subclass contracts
    # ------------------------------------------------------------------

    @property
    def search_queries(self) -> List[str]:
        raise NotImplementedError

    @property
    def active_search_queries(self) -> List[str]:
        """Use caller-supplied terms when present, otherwise the service defaults."""
        return self.custom_queries or self.search_queries

    @property
    def qualification_system_prompt(self) -> str:
        raise NotImplementedError

    def qualification_user_prompt(self, content: str) -> str:
        raise NotImplementedError

    def contact_extraction_prompt(self, content: str) -> str:
        return f"""Extract only contact details explicitly present in this business evidence.
Never invent a business name, website, email, or phone number.
Return JSON with emails, phones, business_name, website, location, and industry.

Evidence:
{content[:8000]}

Return ONLY valid JSON."""

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def _scrape_search_results(
        self, crawler: WebCrawler, query: str
    ) -> List[Dict[str, Any]]:
        """
        Scrape Google search results for a query and return page snippets + links.
        
        Filters out obvious content sources (YouTube, Reddit, Quora, etc.)
        to focus on actual business websites.
        """
        import urllib.parse
        encoded = urllib.parse.quote_plus(query)
        url = self.GOOGLE_SEARCH_URL.format(query=encoded, num=self.RESULTS_PER_QUERY * 2)  # Get more to filter

        result = await crawler.crawl(url, bypass_cache=True)
        if not result["success"]:
            logger.warning("Search crawl failed for query '%s': %s", query, result.get("error_message"))
            return []

        # Extract outbound links that look like real business sites
        links = result.get("links", {})
        external = [
            lnk.get("href", "")
            for lnk in links.get("external", [])
            if lnk.get("href", "").startswith("http")
        ]
        
        # Filter out non-business sources
        filtered_links = []
        for href in external:
            # Skip if it's a content source
            if self._is_content_source(href):
                logger.debug("Skipping content source: %s", href)
                continue
            
            # Skip known aggregators and search engines
            skip_domains = [
                "google.com", "bing.com", "yahoo.com", "duckduckgo.com",
                "wikipedia.org", "wikihow.com",
                "yelp.com", "tripadvisor.com", "zomato.com",  # We want specific businesses, not directories
                "amazon.com", "ebay.com", "etsy.com",  # Marketplaces, not direct businesses
            ]
            
            if any(domain in href.lower() for domain in skip_domains):
                logger.debug("Skipping aggregator/marketplace: %s", href)
                continue
            
            filtered_links.append(href)
            
            if len(filtered_links) >= self.RESULTS_PER_QUERY:
                break

        snippets = []
        for href in filtered_links:
            snippets.append({"url": href, "snippet": result.get("markdown", "")[:2000]})

        logger.info("Filtered %d business links from %d total results for query '%s'", 
                    len(snippets), len(external), query)
        return snippets

    @staticmethod
    def _is_valid_business_name(name: Any) -> bool:
        """
        Validate that a business name represents a SPECIFIC, IDENTIFIABLE business.
        
        REJECT:
        - Generic categories
        - Content platforms
        - Article/video titles
        - Questions or "how to" phrases
        """
        if not isinstance(name, str) or len(name.strip()) < 2:
            return False
        
        name_lower = name.strip().lower()
        
        # Reject generic categories
        generic_names = {
            "small business", "small businesses", "restaurant", "restaurants",
            "local business", "local businesses", "business owners", "unknown",
            "youtube", "reddit", "quora", "clinic", "clinics", "dental clinic",
            "restaurants", "gyms", "fitness centers", "salons", "spas",
            "contractors", "plumbers", "electricians", "agencies", "shops",
            "stores", "companies", "firms", "practices", "null", "none",
        }
        
        # Reject content-first platforms and sources
        content_platforms = {
            "youtube", "reddit", "quora", "facebook", "instagram", "twitter",
            "linkedin article", "medium", "blog post", "tutorial", "video",
            "channel", "article", "guide", "forum", "discussion",
        }
        
        # Reject if name contains obvious content indicators
        content_indicators = [
            "how to", "best way", "tips for", "guide to", "tutorial",
            "what is", "why is", "can i", "should i", "do i need",
            "watch:", "video:", "article:", "post:", "thread:",
            "question:", "answer:", "discussion:", "review:",
            "?", " vs ", " or ",  # Questions and comparisons
            "best ", "top ", "practices", "strategies", "techniques",  # Generic advice/listicle phrases
        ]
        
        if name_lower in generic_names:
            return False
        
        if name_lower in content_platforms:
            return False
        
        for indicator in content_indicators:
            if indicator in name_lower:
                return False
        
        return True
    
    @staticmethod
    def _is_content_source(url: str) -> bool:
        """
        Check if URL is from a content platform (not an actual business).
        
        Returns True if the URL should be REJECTED as non-business content.
        """
        url_lower = url.lower()
        
        content_domains = [
            "youtube.com", "youtu.be",
            "reddit.com", "redd.it",
            "quora.com",
            "medium.com",
            "facebook.com/watch", "fb.watch",
            "instagram.com/tv", "instagram.com/reel",
            "tiktok.com",
            "twitter.com", "x.com",
            "linkedin.com/pulse", "linkedin.com/posts",
            "stackoverflow.com",
            "github.com",
            "dev.to",
            "hashnode.com",
            "substack.com",
            "/blog/", "/article/", "/post/", "/tutorial/",
            "/how-to", "/guide", "/tips",
        ]
        
        for domain in content_domains:
            if domain in url_lower:
                return True
        
        return False
    
    @staticmethod
    def _is_saas_or_agency(url: str, business_name: str, content: str) -> bool:
        """
        Check if the source is a SaaS company or agency OFFERING the same service.
        
        These are competitors, not leads.
        """
        combined = f"{url} {business_name} {content}".lower()
        
        saas_indicators = [
            "saas", "software as a service", "platform for",
            "app for", "tool for", "solution for",
            "pricing", "free trial", "get started", "sign up",
            "plans & pricing", "subscribe", "subscription",
            "features & benefits", "demo", "book a demo",
            "api documentation", "api docs",
        ]
        
        # Agency indicators
        agency_indicators = [
            "we build", "we create", "we design", "we develop",
            "our services", "our clients", "portfolio",
            "web development agency", "digital agency", "marketing agency",
            "web design services", "seo services", "development services",
            "hire us", "contact us for", "get a quote",
        ]
        
        indicator_count = 0
        for indicator in saas_indicators + agency_indicators:
            if indicator in combined:
                indicator_count += 1
        
        # If 3+ indicators found, likely a service provider not a customer
        return indicator_count >= 3

    async def _qualify_lead(
        self, content: str, url: str, candidate: Optional[Dict[str, str]] = None
    ) -> Optional[Lead]:
        """
        Create a lead ONLY when ALL of these conditions are met:
        1. Source is NOT content (YouTube, Reddit, Quora, blog, article)
        2. Source is NOT a SaaS/agency offering the same service
        3. A specific, identifiable business name exists
        4. Direct evidence exists that THIS business needs the service
        5. A contact path exists (website, email, or phone)
        """
        candidate = candidate or {}
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STAGE 1: Source Type Validation
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # REJECT: Content platforms (YouTube, Reddit, Quora, etc.)
        if self._is_content_source(url):
            logger.debug("❌ REJECTED: Content source - %s", url)
            return None
        
        # REJECT: SaaS companies or agencies offering the same service
        if self._is_saas_or_agency(url, candidate.get("business_name", ""), content[:3000]):
            logger.debug("❌ REJECTED: SaaS/Agency competitor - %s", url)
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STAGE 2: Business Identity & Need Validation (LLM)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        enhanced_system_prompt = f"""{self.qualification_system_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL B2B LEAD QUALIFICATION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A valid lead MUST have ALL of these:

1. SPECIFIC BUSINESS IDENTITY
   ✓ Real company/business name (ABC Dental, Royal Spice Restaurant)
   ✗ Generic categories (small businesses, restaurants, clinics)
   ✗ Article/video titles
   ✗ Question phrases ("How to...", "Why is...")
   ✗ Platform names (YouTube, Reddit, Quora)

2. VERIFIABLE BUSINESS EXISTENCE
   ✓ Business website URL found in content
   ✓ Business address/location mentioned
   ✓ Business phone/email in content
   ✗ Only social media mentions without business details
   
3. DIRECT SERVICE-NEED EVIDENCE (not assumptions!)
   ✓ "Restaurant accepts orders by phone only - no online ordering"
   ✓ "Website last updated in 2015 with broken links"
   ✓ "Clinic asks patients to call reception for appointments"
   ✗ "Restaurants probably need WhatsApp bots" (generic assumption)
   ✗ "Small businesses could benefit from SEO" (no specific business)

4. SOURCE TYPE CHECK
   ✗ REJECT if source is:
     - YouTube video/tutorial
     - Reddit post/question
     - Quora question/answer
     - Blog article
     - "How to" guide
     - SaaS product page
     - Agency/competitor site
     - Generic discussion
     - News article
     - Marketing content

REMEMBER: Source URL ≠ Business
- https://youtube.com/watch?v=123 → This is NOT a business
- Content ABOUT a problem → NOT a lead unless it identifies a specific business

SCORING GUIDANCE:
- 0.0-0.2: Not a business / Pure content
- 0.2-0.4: Might be a business but no clear service need
- 0.4-0.6: Identifiable business, weak/indirect need signals
- 0.6-0.8: Clear business + meaningful evidence of service need
- 0.8-1.0: Specific business + strong direct evidence + verified contact

Return JSON:
{{
  "is_real_business": <boolean>,
  "source_type": "actual_business" | "content" | "saas_provider" | "generic_discussion",
  "business_name": "<ACTUAL business name or null>",
  "website": "<business website URL or null>",
  "location": "<city, state or empty>",
  "industry": "<specific industry>",
  "has_contact_path": <boolean>,
  "score": <0.0-1.0>,
  "pain_points": ["<specific observed issues ONLY>"],
  "evidence": "<direct evidence about THIS business>",
  "rejection_reason": "<why this is NOT a lead, if applicable>"
}}"""
        
        try:
            qualification_raw = await self.llm.complete(
                prompt=self.qualification_user_prompt(content),
                system_prompt=enhanced_system_prompt,
                json_mode=True,
                max_tokens=600,
            )
            qual = json.loads(qualification_raw)
        except Exception as exc:
            logger.error("Qualification LLM error for %s: %s", url, exc)
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STAGE 3: Validation Checks
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        source_type = qual.get("source_type", "")
        if source_type in ["content", "saas_provider", "generic_discussion"]:
            logger.debug("❌ REJECTED: LLM classified as %s - %s", source_type, url)
            return None
        
        if not qual.get("is_real_business", False):
            logger.debug("❌ REJECTED: Not a real business - %s", url)
            return None
        
        try:
            score = float(qual.get("score", 0))
        except (TypeError, ValueError):
            logger.debug("❌ REJECTED: Invalid score - %s", url)
            return None
        
        # Minimum score threshold
        if score < 0.5:
            logger.debug("❌ REJECTED: Score too low (%.2f) - %s", score, url)
            return None
        
        # Business name validation
        business_name = candidate.get("business_name") or qual.get("business_name", "")
        if not business_name or business_name == "null" or not self._is_valid_business_name(business_name):
            logger.debug("❌ REJECTED: Invalid business name '%s' - %s", business_name, url)
            return None
        
        # Pain points must be specific, not generic
        pain_points = qual.get("pain_points", [])
        if isinstance(pain_points, list):
            # Filter out generic/assumed pain points
            generic_phrases = [
                "probably", "likely", "could benefit", "may need",
                "should consider", "might want", "would help",
                "common problem", "typical issue", "general need",
                "poor seo", "poor visibility", "low ranking",  # Too vague
                "thin content", "poor meta", "bad structure",  # Need specifics
            ]
            
            original_count = len(pain_points)
            pain_points = [
                p for p in pain_points
                if isinstance(p, str) and not any(phrase in p.lower() for phrase in generic_phrases)
            ]
            
            if original_count > 0 and len(pain_points) < original_count:
                logger.debug("Filtered %d generic pain points, %d remain", 
                           original_count - len(pain_points), len(pain_points))
        
        # Must have at least ONE specific pain point for score >= 0.6
        if score >= 0.6 and not pain_points:
            logger.debug("❌ REJECTED: High score (%.2f) but no specific pain points - %s", score, url)
            # Lower the score or reject
            score = 0.4  # Demote to low-confidence lead
        
        if not pain_points:
            logger.debug("⚠️  WARNING: No specific pain points - %s", url)
            # Still proceed but with lowered confidence
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STAGE 4: Contact Information Extraction & Website Detection
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Extract website from source_url if it's the business website
        website = qual.get("website")
        if not website and url:
            # Check if source_url is likely the business website
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.netloc and not self._is_content_source(url):
                # Extract domain as website
                website = f"{parsed.scheme}://{parsed.netloc}"
        
        phones = [candidate["phone"]] if candidate.get("phone") else []
        
        try:
            contact_raw = await self.llm.complete(
                prompt=self.contact_extraction_prompt(content),
                json_mode=True,
                max_tokens=512,
            )
            contacts = json.loads(contact_raw)
        except Exception:
            contacts = {"emails": [], "phones": []}
        
        emails = contacts.get("emails", []) if isinstance(contacts.get("emails"), list) else []
        extracted_phones = contacts.get("phones", []) if isinstance(contacts.get("phones"), list) else []
        phones.extend(phone for phone in extracted_phones if phone not in phones)
        
        # Update website from contacts if not already set
        if not website:
            website = contacts.get("website")
        
        # Must have at least ONE contact method
        has_contact_path = bool(website or emails or phones)
        if not has_contact_path:
            logger.debug("❌ REJECTED: No contact path - %s", url)
            return None
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STAGE 5: Create Lead
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        import uuid
        lead = Lead(
            id=str(uuid.uuid4()),
            source_url=url,
            business_name=business_name.strip(),
            service_needed=self.SERVICE_LABEL,
            contact_email=emails,
            contact_phone=phones,
            website=website,
            pain_points=pain_points,
            qualification_score=score,
            raw_snippet=content[:500],
            location=candidate.get("location") or qual.get("location", ""),
            industry=candidate.get("industry") or qual.get("industry", ""),
            latitude=candidate.get("latitude"),
            longitude=candidate.get("longitude"),
            distance_km=candidate.get("distance_km"),
        )
        
        logger.info("✅ VALID LEAD: %s (score=%.2f) - %s", business_name, score, url)
        return lead

    async def _run_with_search_api(self, started_at: str) -> JobResult:
        """
        Discover and qualify leads from API results without starting Playwright.
        
        Filters out content sources before qualification.
        """
        leads: List[Lead] = []
        errors: List[str] = []
        logger.info("[%s] Using %s for discovery; Playwright is not started.", self.JOB_NAME, self.search_provider.name)

        for query in self.active_search_queries:
            try:
                results = await self.search_provider.search(query, self.RESULTS_PER_QUERY * 2)  # Get more to filter
                logger.info("[%s] Query '%s' returned %d API results", self.JOB_NAME, query, len(results))
                
                # Filter results before processing
                filtered_results = []
                for item in results:
<<<<<<< HEAD
                    url = item["url"]
                    
                    # Skip content sources
                    if self._is_content_source(url):
                        logger.debug("[%s] Skipping content source: %s", self.JOB_NAME, url)
                        continue
                    
                    filtered_results.append(item)
                    
                    if len(filtered_results) >= self.RESULTS_PER_QUERY:
                        break
                
                logger.info("[%s] %d results after filtering content sources", self.JOB_NAME, len(filtered_results))
                
                # Qualify filtered results
                for item in filtered_results:
                    url = item["url"]
                    try:
                        # Pass the full item as candidate so coordinates are included
                        lead = await self._qualify_lead(
                            content=item.get("content", "")[:6000],
                            url=url,
                            candidate=item  # Pass full item with lat/lng/distance
                        )
=======
                    # Extract contact info directly from API result
                    url = item.get("website") or item.get("url", "")
                    business_name = item.get("name", "Unknown")
                    phone = item.get("phone", "")
                    email = item.get("email", "")
                    address = item.get("address", "")
                    rating = item.get("rating", "N/A")
                    
                    # Skip if no contact info
                    if not (phone or email):
                        logger.debug("[%s] Skipping %s - no phone or email", self.JOB_NAME, business_name)
                        continue
                    
                    try:
                        # Qualify based on content
                        lead = await self._qualify_lead(item.get("content", "")[:6000], url or business_name)
>>>>>>> bee865b1c38482700b7eadb39e940580c6cd2cdc
                        if lead:
                            # Override with actual contact info from API
                            lead.business_name = business_name
                            lead.contact_phone = [phone] if phone else []
                            lead.contact_email = [email] if email else []
                            lead.website = url
                            lead.source_url = url or business_name
                            
                            leads.append(lead)
<<<<<<< HEAD
                            logger.info("[%s] Lead found: %s (score=%.2f, distance=%.1fkm)", 
                                      self.JOB_NAME, lead.business_name, lead.qualification_score, 
                                      lead.distance_km if lead.distance_km else 0)
=======
                            logger.info(
                                "[%s] Lead found: %s | Phone: %s | Email: %s (score=%.2f)", 
                                self.JOB_NAME, 
                                business_name, 
                                phone or "N/A",
                                email or "N/A",
                                lead.qualification_score
                            )
>>>>>>> bee865b1c38482700b7eadb39e940580c6cd2cdc
                    except Exception as exc:
                        err = f"API result qualification error [{business_name}]: {exc}"
                        logger.error(err)
                        errors.append(err)
            except Exception as exc:
                err = f"API search error [{query}]: {exc}"
                logger.error(err)
                errors.append(err)

        result = JobResult(
            job_name=self.JOB_NAME,
            started_at=started_at,
            finished_at=datetime.utcnow().isoformat(),
            leads_found=len(leads),
            leads=leads,
            errors=errors,
        )
        logger.info("[%s] Done - %d leads found, %d errors", self.JOB_NAME, len(leads), len(errors))
        return result

    async def run(self) -> JobResult:
        """Execute the job end-to-end and return a JobResult."""
        started_at = datetime.utcnow().isoformat()
        leads: List[Lead] = []
        errors: List[str] = []

        logger.info("[%s] Starting job with %d queries", self.JOB_NAME, len(self.active_search_queries))

        if self.search_provider.configured:
            return await self._run_with_search_api(started_at)

        logger.warning(
            "[%s] SERPAPI_API_KEY and GOOGLE_MAPS_API_KEY are not configured; falling back to browser crawling.",
            self.JOB_NAME,
        )

        async with WebCrawler(self.crawler_config) as crawler:
            for query in self.active_search_queries:
                try:
                    snippets = await self._scrape_search_results(crawler, query)
                    logger.info("[%s] Query '%s' → %d results", self.JOB_NAME, query, len(snippets))

                    for item in snippets:
                        url = item["url"]
                        try:
                            page = await crawler.crawl(url)
                            if not page["success"]:
                                continue
                            content = page.get("markdown") or page.get("cleaned_html") or ""
                            lead = await self._qualify_lead(content[:6000], url)
                            if lead:
                                leads.append(lead)
                                logger.info("[%s] ✓ Lead found: %s (score=%.2f)", self.JOB_NAME, lead.business_name, lead.qualification_score)
                        except Exception as exc:
                            err = f"Page crawl error [{url}]: {exc}"
                            logger.error(err)
                            errors.append(err)

                except Exception as exc:
                    err = f"Query error [{query}]: {exc}"
                    logger.error(err)
                    errors.append(err)

        finished_at = datetime.utcnow().isoformat()
        result = JobResult(
            job_name=self.JOB_NAME,
            started_at=started_at,
            finished_at=finished_at,
            leads_found=len(leads),
            leads=leads,
            errors=errors,
        )
        logger.info("[%s] Done – %d leads found, %d errors", self.JOB_NAME, len(leads), len(errors))
        return result


# ---------------------------------------------------------------------------
# Website Development Leads
# ---------------------------------------------------------------------------

class WebsiteLeadJob(BaseLeadJob):
    """
    Finds businesses that:
    - Have no website at all (social-media-only presence)
    - Have an outdated/broken website (last decade design, no mobile support)
    - Are actively asking for help getting a website

    Targets small businesses, local shops, freelancers, restaurants, etc.
    """

    JOB_NAME = "website_lead_job"
    SERVICE_LABEL = "website"

    @property
    def search_queries(self) -> List[str]:
        """
        Business-discovery queries - find actual businesses, NOT articles/discussions.
        
        Strategy: Target business directories, local listings, and business profiles
        rather than "how to" content or problem discussions.
        """
        return [
            # Local business directories
            "local small businesses directory contact information",
            "local restaurants business listings phone website",
            "small business directory local shops contact",
            "independent retail stores local business list",
            
            # Facebook-only businesses (no website)
            "business facebook page only no website contact",
            "restaurant facebook only menu contact phone",
            "local shop facebook page business contact",
            
            # Social media business profiles
            "local businesses instagram only no website",
            "small business social media contact information",
            
            # Outdated websites (more specific)
            'site:.com "copyright 2015" OR "copyright 2016" contact',
            'site:.com "last updated 2015" OR "last updated 2016"',
        ]

    @property
    def qualification_system_prompt(self) -> str:
        return """You are a lead qualification expert for a web development agency.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: EVIDENCE-BASED QUALIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Only report OBSERVED website issues, not assumptions.

✅ VALID EVIDENCE:
- "Business has Facebook page but website link returns 404"
- "Website shows 'Under Construction' message"
- "Homepage copyright says 2010, uses Flash player"
- "Site has broken images on all pages"
- "Business explicitly states 'contact us on Facebook, website coming soon'"
- "No website URL found in any business listing"

❌ INVALID (ASSUMPTIONS):
- "Small business probably needs a website" (no evidence)
- "Old-looking website" (subjective without specifics)
- "Could benefit from redesign" (assumption)

WEBSITE STATUS:
- "none": No website found at all OR website explicitly doesn't exist
- "basic": Website exists but has observable major issues (broken, outdated)
- "functional": Website works but may have minor issues
- "strong": Professional, modern website
- "unknown": Cannot determine

SCORING (0.0-1.0):
- 40% Business identity (real, identifiable business?)
- 30% Evidence strength (observed website problem?)
- 20% Service fit (does website/lack thereof match our service?)
- 10% Contactability

NO WEBSITE + IDENTIFIABLE BUSINESS = HIGH SCORE (0.7-0.9)
HAS WEBSITE + NO CLEAR ISSUES = LOW SCORE (0.2-0.3)

Return JSON:
{
  "is_real_business": boolean,
  "source_type": "actual_business"|"content"|...,
  "business_name": "Actual business NOT person",
  "website": "URL or null",
  "website_status": "none"|"basic"|"functional"|"strong"|"unknown",
  "location": "city, state",
  "industry": "industry",
  "has_contact_path": boolean,
  "score": 0.0-1.0,
  "pain_points": ["OBSERVED issues only"],
  "evidence": "What I actually saw",
  "rejection_reason": "if rejected"
}"""

    def qualification_user_prompt(self, content: str) -> str:
        return f"""Analyse this content for a web development lead.

EVIDENCE-BASED REQUIREMENTS:
- Business name = actual business entity (not person)
- Website status = based on what you observe
- Pain points = ONLY observed issues (broken site, no site, explicitly mentioned needs)

Content:
{content[:5000]}

ASK YOURSELF:
- Is there NO website at all? → High score, note "no website found"
- Is website broken/unusable? → High score, describe what's broken
- Is website just old-looking? → Not enough, need specific issues
- Does business say they need a website? → High score, quote them

Return ONLY valid JSON with all required fields."""


# ---------------------------------------------------------------------------
# WhatsApp Bot Leads
# ---------------------------------------------------------------------------

class WhatsAppBotLeadJob(BaseLeadJob):
    """
    Finds businesses that:
    - Use WhatsApp for manual customer support
    - Have high inquiry volume they struggle to handle
    - Are looking for chatbot or automation solutions
    """

    JOB_NAME = "whatsapp_bot_lead_job"
    SERVICE_LABEL = "whatsapp_bot"

    @property
    def search_queries(self) -> List[str]:
        """
        Business-discovery queries - find actual businesses using WhatsApp,
        NOT tutorials or SaaS products.
        """
        return [
            # Businesses that list WhatsApp as contact method
            '"contact us on whatsapp" restaurant menu order',
            '"whatsapp" clinic appointment booking phone number',
            '"order via whatsapp" local business phone',
            '"message us on whatsapp" shop store contact',
            
            # Business directories with WhatsApp
            "businesses whatsapp contact directory local",
            "restaurants whatsapp number menu local",
            "clinics whatsapp appointment local area",
            
            # Google My Business profiles
            "business whatsapp contact google maps",
            "local restaurant whatsapp phone hours",
        ]

    @property
    def qualification_system_prompt(self) -> str:
        return """You are a lead qualification expert for a WhatsApp bot development agency.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: EVIDENCE-BASED QUALIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Only report OBSERVED WhatsApp usage and pain points.

✅ VALID EVIDENCE:
- "Business lists WhatsApp number as primary contact"
- "Website says 'message us on WhatsApp for orders'"
- "Reviews mention 'had to wait hours for WhatsApp response'"
- "Business explicitly posts 'WhatsApp only between 9am-5pm'"
- "Menu says 'order via WhatsApp: +123456789'"

❌ INVALID (ASSUMPTIONS):
- "Restaurant probably uses WhatsApp" (no evidence)
- "Could benefit from automation" (no observed manual process)
- "High volume business" (unless stated or demonstrated)

WHATSAPP EVIDENCE REQUIRED:
You can only score high (0.6+) if you observe:
1. Business actually uses WhatsApp (number visible or mentioned)
2. Evidence of manual process or pain (reviews, business statement, hours limitation)

SCORING (0.0-1.0):
- 40% Business identity
- 30% WhatsApp usage evidence (do they use it?)
- 20% Pain point evidence (is manual process causing problems?)
- 10% Contactability

USES WHATSAPP + MANUAL PAIN = HIGH (0.7-0.9)
USES WHATSAPP + NO PAIN = MEDIUM (0.4-0.6)
NO WHATSAPP EVIDENCE = LOW (0.1-0.3)

Return JSON:
{
  "is_real_business": boolean,
  "source_type": "actual_business"|...,
  "business_name": "Actual business NOT person",
  "website": "URL or null",
  "website_status": "none"|"basic"|"functional"|"strong"|"unknown",
  "location": "city, state",
  "industry": "industry",
  "has_contact_path": boolean,
  "score": 0.0-1.0,
  "pain_points": ["OBSERVED WhatsApp/automation issues"],
  "evidence": "What I saw about WhatsApp usage",
  "rejection_reason": "if rejected"
}"""

    def qualification_user_prompt(self, content: str) -> str:
        return f"""Analyse this content for a WhatsApp bot lead.

EVIDENCE REQUIREMENTS:
1. Business name = actual business (not person)
2. WhatsApp evidence = number visible OR explicitly mentioned
3. Pain points = OBSERVED issues (manual replies, limited hours, review complaints)

Content:
{content[:5000]}

EVIDENCE CHECK:
- Do I see a WhatsApp number? → Note it
- Does content mention WhatsApp orders/bookings? → Quote it
- Do reviews mention WhatsApp issues? → Describe them
- Does business state WhatsApp hours? → Note limitation
- NO EVIDENCE? → Low score, reject or note insufficient evidence

Return ONLY valid JSON with all required fields."""


# ---------------------------------------------------------------------------
# SEO Service Leads
# ---------------------------------------------------------------------------

class SEOLeadJob(BaseLeadJob):
    """
    Finds businesses that:
    - Have a website but rank poorly in search results
    - Are running businesses in competitive niches without SEO
    - Explicitly mention needing more traffic or online visibility
    """

    JOB_NAME = "seo_lead_job"
    SERVICE_LABEL = "seo"

    @property
    def search_queries(self) -> List[str]:
        """
        Business-discovery queries - find actual businesses with websites,
        NOT articles about SEO problems.
        """
        return [
            # Local business websites (can analyze for SEO issues)
            "local businesses website contact information",
            "restaurants website menu phone local area",
            "dentists website location phone hours",
            "law firms website contact local",
            "real estate agents website listings local",
            
            # Businesses in directories
            "small business directory website contact local",
            "local business listings website phone",
            "independent businesses website contact area",
            
            # Chamber of Commerce / Business associations
            "chamber of commerce member businesses directory",
            "local business association member directory website",
        ]

    @property
    def qualification_system_prompt(self) -> str:
        return """You are a lead qualification expert for an SEO agency.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: EVIDENCE-BASED QUALIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST NEVER create pain points based on industry assumptions.
Every pain point REQUIRES direct observable evidence.

❌ NEVER ASSUME (even if common for industry):
- "Poor SEO" (too generic)
- "Poor meta descriptions" (unless you saw missing/duplicate meta tags)
- "Thin content" (unless you saw actual pages with little content)
- "Low Google ranking" (unless explicitly mentioned or observed)
- "Poor structured data" (unless you inspected and found it missing)

✅ ONLY REPORT OBSERVED EVIDENCE:
- "Homepage has no meta description tag"
- "Title tag is missing on contact page"
- "Multiple pages have duplicate title 'Home'"
- "Service page contains only 50 words of content"
- "No LocalBusiness schema detected in HTML"
- "Business not indexed for 'business name + city' search"

WEBSITE EXISTENCE CHECK:
- If source_url points to a business website → website must be set, NOT empty
- Example: source_url = "https://businessname.com/about" → website = "https://businessname.com"
- Never say "No web presence" when the source IS the business website

BUSINESS NAME vs PERSON NAME:
- "Dr. John Smith" is a PERSON, not a business
- If you can identify the actual practice: business_name = "Smith Dental Clinic"
- If only person mentioned: business_name = null, reject the lead

QUALIFICATION SCORING (0.0-1.0):
- 40% Business identity confidence (is this a real, identifiable business?)
- 30% Evidence of actual need (did I observe specific problems?)
- 20% Service fit (does the problem match SEO service?)
- 10% Contactability (can we reach them?)

REAL BUSINESS + NO DEMONSTRATED SEO NEED = LOW SCORE (0.3-0.4)
REAL BUSINESS + OBSERVED SEO ISSUES = HIGH SCORE (0.7-0.9)

Return JSON with:
{
  "is_real_business": <boolean>,
  "source_type": "actual_business"|"content"|"saas_provider"|"generic_discussion",
  "business_name": "<ACTUAL business name NOT person name, or null>",
  "website": "<business website URL from source_url or null>",
  "website_status": "none"|"basic"|"functional"|"strong"|"unknown",
  "location": "<city, state>",
  "industry": "<specific industry>",
  "has_contact_path": <boolean>,
  "score": <0.0-1.0 based on formula above>,
  "pain_points": ["<ONLY observed, specific issues with evidence>"],
  "evidence": "<what you ACTUALLY saw, not assumed>",
  "rejection_reason": "<if rejected, why>"
}"""

    def qualification_user_prompt(self, content: str) -> str:
        return f"""Analyse this content and determine if it represents a real business that needs SEO.

CRITICAL RULES:
1. Business name MUST be actual business entity, NOT a person name
2. Pain points MUST be OBSERVED issues, NOT industry assumptions
3. If source_url is a business website, extract the website domain
4. Score reflects: identity (40%) + evidence (30%) + service fit (20%) + contact (10%)

Content:
{content[:5000]}

EVIDENCE CHECK - Ask yourself:
- Did I see missing meta tags? (YES → report specific page | NO → don't mention)
- Did I see thin content? (YES → report which page | NO → don't mention)
- Did I see duplicate titles? (YES → report details | NO → don't mention)
- Is there explicit SEO problem mentioned? (YES → report it | NO → low score)

Return ONLY valid JSON with all required fields."""


# ---------------------------------------------------------------------------
# Job Runner – runs multiple jobs and aggregates results
# ---------------------------------------------------------------------------

class JobRunner:
    """
    Runs one or many lead generation jobs, optionally in parallel,
    and returns aggregated results.

    Usage:
        runner = JobRunner()
        results = await runner.run_all()
        runner.save_results(results, "leads_output.json")
    """

    def __init__(
        self,
        crawler_config: Optional[CrawlerConfig] = None,
        llm_config: Optional[LLMConfig] = None,
    ):
        self.crawler_config = crawler_config
        self.llm_config = llm_config

    def _build_jobs(self, custom_queries: Optional[List[str]] = None) -> List[BaseLeadJob]:
        return [
            WebsiteLeadJob(self.crawler_config, self.llm_config, custom_queries),
            WhatsAppBotLeadJob(self.crawler_config, self.llm_config, custom_queries),
            SEOLeadJob(self.crawler_config, self.llm_config, custom_queries),
        ]

    async def run_all(
        self, parallel: bool = False, custom_queries: Optional[List[str]] = None
    ) -> List[JobResult]:
        """Run all jobs. Set parallel=True to run concurrently."""
        jobs = self._build_jobs(custom_queries)
        if parallel:
            results = await asyncio.gather(*[j.run() for j in jobs], return_exceptions=True)
            # Replace exceptions with empty results
            clean = []
            for i, r in enumerate(results):
                if isinstance(r, Exception):
                    logger.error("Job %s crashed: %s", jobs[i].JOB_NAME, r)
                    clean.append(JobResult(
                        job_name=jobs[i].JOB_NAME,
                        started_at="",
                        finished_at="",
                        leads_found=0,
                        leads=[],
                        errors=[str(r)],
                    ))
                else:
                    clean.append(r)
            return clean
        else:
            results = []
            for job in jobs:
                result = await job.run()
                results.append(result)
            return results

    async def run_single(
        self, service: str, custom_queries: Optional[List[str]] = None
    ) -> JobResult:
        """Run a single job by service name: 'website' | 'whatsapp_bot' | 'seo'"""
        mapping = {
            "website": WebsiteLeadJob,
            "whatsapp_bot": WhatsAppBotLeadJob,
            "seo": SEOLeadJob,
        }
        cls = mapping.get(service)
        if not cls:
            raise ValueError(f"Unknown service: {service}. Choose from {list(mapping)}")
        job = cls(self.crawler_config, self.llm_config, custom_queries)
        return await job.run()

    @staticmethod
    def save_results(results: List[JobResult], output_path: str = "leads_output.json") -> None:
        """Save all job results to a JSON file."""
        data = [r.to_dict() for r in results]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Results saved to %s", output_path)

    @staticmethod
    def print_summary(results: List[JobResult]) -> None:
        """Print a human-readable summary to stdout."""
        total = sum(r.leads_found for r in results)
        print(f"\n{'='*60}")
        print(f"  LEAD GENERATION SUMMARY")
        print(f"{'='*60}")
        for r in results:
            print(f"\n  [{r.job_name}]")
            print(f"    Leads found : {r.leads_found}")
            print(f"    Errors      : {len(r.errors)}")
            for lead in r.leads:
                print(f"    • {lead.business_name} ({lead.source_url[:50]}...)")
                print(f"      Score: {lead.qualification_score:.2f} | Emails: {lead.contact_email}")
        print(f"\n{'='*60}")
        print(f"  TOTAL LEADS: {total}")
        print(f"{'='*60}\n")
