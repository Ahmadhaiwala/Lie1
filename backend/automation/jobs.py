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
    discovered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    outreach_sent: bool = False
    notes: str = ""

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
    ):
        self.crawler_config = crawler_config or CrawlerConfig(
            headless=True,
            page_timeout=20000,
        )
        self.llm_config = llm_config or LLMConfig.from_env()
        self.llm = LLMProvider(self.llm_config)
        self.search_provider = SearchProvider()

    # ------------------------------------------------------------------
    # Subclass contracts
    # ------------------------------------------------------------------

    @property
    def search_queries(self) -> List[str]:
        raise NotImplementedError

    @property
    def qualification_system_prompt(self) -> str:
        raise NotImplementedError

    def qualification_user_prompt(self, content: str) -> str:
        raise NotImplementedError

    def contact_extraction_prompt(self, content: str) -> str:
        return f"""Extract ALL contact information from the following text.
Return a JSON object with keys:
  - emails: list of email addresses
  - phones: list of phone numbers
  - business_name: string (best guess at the business name)
  - website: string or null

Content:
{content[:8000]}

Return ONLY valid JSON, no extra text."""

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def _scrape_search_results(
        self, crawler: WebCrawler, query: str
    ) -> List[Dict[str, Any]]:
        """Scrape Google search results for a query and return page snippets + links."""
        import urllib.parse
        encoded = urllib.parse.quote_plus(query)
        url = self.GOOGLE_SEARCH_URL.format(query=encoded, num=self.RESULTS_PER_QUERY)

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
            and "google.com" not in lnk.get("href", "")
            and "youtube.com" not in lnk.get("href", "")
        ]

        snippets = []
        for href in external[: self.RESULTS_PER_QUERY]:
            snippets.append({"url": href, "snippet": result.get("markdown", "")[:2000]})

        return snippets

    async def _qualify_lead(self, content: str, url: str) -> Optional[Lead]:
        """Use LLM to decide if the page represents a qualified lead."""
        try:
            qualification_raw = await self.llm.complete(
                prompt=self.qualification_user_prompt(content),
                system_prompt=self.qualification_system_prompt,
                json_mode=True,
                max_tokens=512,
            )
            qual = json.loads(qualification_raw)
        except Exception as exc:
            logger.error("Qualification LLM error for %s: %s", url, exc)
            return None

        score = float(qual.get("score", 0))
        if score < 0.5:
            return None  # not a good lead

        # Extract contacts
        try:
            contact_raw = await self.llm.complete(
                prompt=self.contact_extraction_prompt(content),
                json_mode=True,
                max_tokens=512,
            )
            contacts = json.loads(contact_raw)
        except Exception:
            contacts = {"emails": [], "phones": [], "business_name": "Unknown", "website": None}

        import uuid
        lead = Lead(
            id=str(uuid.uuid4()),
            source_url=url,
            business_name=contacts.get("business_name", "Unknown"),
            service_needed=self.SERVICE_LABEL,
            contact_email=contacts.get("emails", []),
            contact_phone=contacts.get("phones", []),
            website=contacts.get("website"),
            pain_points=qual.get("pain_points", []),
            qualification_score=score,
            raw_snippet=content[:500],
        )
        return lead

    async def _run_with_search_api(self, started_at: str) -> JobResult:
        """Discover and qualify leads from API results without starting Playwright."""
        leads: List[Lead] = []
        errors: List[str] = []
        logger.info("[%s] Using %s for discovery; Playwright is not started.", self.JOB_NAME, self.search_provider.name)

        for query in self.search_queries:
            try:
                results = await self.search_provider.search(query, self.RESULTS_PER_QUERY)
                logger.info("[%s] Query '%s' returned %d API results", self.JOB_NAME, query, len(results))
                for item in results:
                    # Extract contact info directly from API result
                    url = item.get("website") or item.get("url", "")
                    business_name = item.get("name", "Unknown")
                    phone = item.get("phone", "")
                    email = item.get("email", "")
                    address = item.get("address", "")
                    rating = item.get("rating", "N/A")
                    
                    # Skip only if business name is Unknown (means API returned nothing useful)
                    if business_name == "Unknown":
                        logger.debug("[%s] Skipping - no business name", self.JOB_NAME)
                        continue
                    
                    try:
                        # Qualify based on content
                        lead = await self._qualify_lead(item.get("content", "")[:6000], url or business_name)
                        if lead:
                            # Override with actual contact info from API
                            lead.business_name = business_name
                            lead.contact_phone = [phone] if phone else []
                            lead.contact_email = [email] if email else []
                            lead.website = url
                            lead.source_url = url or business_name
                            
                            leads.append(lead)
                            logger.info(
                                "[%s] Lead found: %s | Phone: %s | Email: %s | Website: %s (score=%.2f)", 
                                self.JOB_NAME, 
                                business_name, 
                                phone or "N/A",
                                email or "N/A",
                                url or "N/A",
                                lead.qualification_score
                            )
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

        logger.info("[%s] Starting job with %d queries", self.JOB_NAME, len(self.search_queries))

        if self.search_provider.configured:
            return await self._run_with_search_api(started_at)

        logger.warning(
            "[%s] SERPAPI_API_KEY and GOOGLE_MAPS_API_KEY are not configured; falling back to browser crawling.",
            self.JOB_NAME,
        )

        async with WebCrawler(self.crawler_config) as crawler:
            for query in self.search_queries:
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
    Finds businesses in Ahmedabad that:
    - Have no website at all (social-media-only presence)
    - Have an outdated/broken website (last decade design, no mobile support)
    - Are actively asking for help getting a website

    Targets small businesses, local shops, freelancers, restaurants, etc. in Ahmedabad
    """

    JOB_NAME = "website_lead_job"
    SERVICE_LABEL = "website"

    @property
    def search_queries(self) -> List[str]:
        return [
            "businesses in Ahmedabad without website",
            "small shops in Ahmedabad need web design",
            "restaurants in Ahmedabad no online presence",
            "retail stores Ahmedabad social media only",
            "Ahmedabad local businesses poor website design",
            "service providers Ahmedabad need website",
            "Ahmedabad shops looking for web development",
            "Ahmedabad businesses outdated website redesign",
        ]

    @property
    def qualification_system_prompt(self) -> str:
        return """You are analyzing a business website or business listing from Ahmedabad, India.
Decide if this business needs a website or website redesign.

Score HIGH if:
- Business has no website (only Google My Business, Facebook page)
- Website is very outdated (old design, broken links)
- No mobile responsive design
- Website has missing contact info or broken forms
- Business is in service/retail/F&B sector

Return JSON with:
{
  "score": <float 0.0-1.0>,
  "pain_points": [<specific issues>],
  "reasoning": "<one sentence>"
}"""

    def qualification_user_prompt(self, content: str) -> str:
        return f"""Analyze this Ahmedabad business and score as website development lead.

Content:
{content[:5000]}

Return ONLY valid JSON."""


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
        return [
            "business using whatsapp for customer support manual replies",
            "small business whatsapp orders management problem",
            "restaurant order via whatsapp overwhelmed",
            "need whatsapp automation for my business",
            "whatsapp business bot setup help",
            "automate whatsapp replies for online store",
            "clinic hospital appointment booking whatsapp manual",
            "customer service whatsapp chatbot affordable",
        ]

    @property
    def qualification_system_prompt(self) -> str:
        return """You are a lead qualification expert for a WhatsApp bot development agency.
Analyse page content to identify businesses that need WhatsApp automation.

Signals of a GOOD lead (score high):
- Mentions WhatsApp as primary customer channel
- Complaints about being overwhelmed with messages
- Manual order/booking/support via WhatsApp
- Asking for automation or bot solutions
- High-volume customer interaction business (restaurant, clinic, online store)

Return JSON with:
{
  "score": <float 0.0-1.0>,
  "pain_points": [<list of specific issues>],
  "reasoning": "<one sentence>"
}"""

    def qualification_user_prompt(self, content: str) -> str:
        return f"""Analyse this page and score it as a WhatsApp bot lead.

Page content:
{content[:5000]}

Return ONLY valid JSON."""


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
        return [
            "business website not showing on google need SEO help",
            "small business low website traffic need marketing",
            "local business page 5 google looking for SEO service",
            "ecommerce store no organic traffic need SEO",
            "startup needs digital marketing SEO affordable",
            "dentist lawyer accountant website no google ranking",
            "my website gets no visitors need help with SEO",
            "improve google ranking for small business affordable",
        ]

    @property
    def qualification_system_prompt(self) -> str:
        return """You are a lead qualification expert for an SEO agency.
Analyse page content to identify businesses that need SEO services.

Signals of a GOOD lead (score high):
- Has a website but mentions poor visibility or low traffic
- Operating in a competitive local niche (dental, legal, restaurant, retail)
- No structured content, poor meta descriptions, thin pages
- Explicitly asking about improving Google ranking
- Running PPC ads as a substitute for organic traffic (opportunity)
- Blog not updated in 1+ year

Return JSON with:
{
  "score": <float 0.0-1.0>,
  "pain_points": [<list of specific SEO issues>],
  "reasoning": "<one sentence>"
}"""

    def qualification_user_prompt(self, content: str) -> str:
        return f"""Analyse this page and score it as an SEO lead.

Page content:
{content[:5000]}

Return ONLY valid JSON."""


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

    def _build_jobs(self) -> List[BaseLeadJob]:
        return [
            WebsiteLeadJob(self.crawler_config, self.llm_config),
            WhatsAppBotLeadJob(self.crawler_config, self.llm_config),
            SEOLeadJob(self.crawler_config, self.llm_config),
        ]

    async def run_all(self, parallel: bool = False) -> List[JobResult]:
        """Run all jobs. Set parallel=True to run concurrently."""
        jobs = self._build_jobs()
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

    async def run_single(self, service: str) -> JobResult:
        """Run a single job by service name: 'website' | 'whatsapp_bot' | 'seo'"""
        mapping = {
            "website": WebsiteLeadJob,
            "whatsapp_bot": WhatsAppBotLeadJob,
            "seo": SEOLeadJob,
        }
        cls = mapping.get(service)
        if not cls:
            raise ValueError(f"Unknown service: {service}. Choose from {list(mapping)}")
        job = cls(self.crawler_config, self.llm_config)
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
