"""
Lead Workflows

Handles the end-to-end lifecycle of a lead after discovery:

  1. LeadQualifier    – re-scores and filters leads using the LLM
  2. BusinessFilter   – evaluates online presence + business model suitability
                        classifies as High Priority / Medium Priority / Discard
  3. OutreachComposer – generates personalised outreach messages
  4. LeadWorkflow     – orchestrates discovery → qualify → filter → compose → save

Supported outreach channels:
  - Email draft (ready to paste into Gmail/SMTP)
  - WhatsApp message draft
  - Cold DM (LinkedIn / Instagram style)
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from llm.llm_client import LLMClient
from llm.llm_config import LLMConfig
from crawler.config import CrawlerConfig
from automation.jobs import (
    Lead,
    JobResult,
    JobRunner,
    WebsiteLeadJob,
    WhatsAppBotLeadJob,
    SEOLeadJob,
)
from filters.business_filter import BusinessFilter, FilterPriority
from discovery.business_discovery import BusinessDiscovery, SearchIntent, SearchQuery

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Agency / Sender Identity (read from env or use defaults)
# ---------------------------------------------------------------------------

AGENCY_NAME = os.getenv("AGENCY_NAME", "YourAgency")
AGENCY_WEBSITE = os.getenv("AGENCY_WEBSITE", "https://youragency.com")
SENDER_NAME = os.getenv("SENDER_NAME", "Ahmad")
SENDER_WHATSAPP = os.getenv("SENDER_WHATSAPP", "+1234567890")


# ---------------------------------------------------------------------------
# Lead Qualifier
# ---------------------------------------------------------------------------

class LeadQualifier:
    """
    Re-evaluates a list of leads and enriches them with:
    - A refined qualification score
    - Best outreach channel recommendation
    - Priority tier (hot / warm / cold)
    """

    SCORE_HOT = 0.75
    SCORE_WARM = 0.50

    SYSTEM_PROMPT = f"""You are a senior sales consultant at {AGENCY_NAME}.
Your job is to evaluate a potential lead and decide:
1. How likely they are to convert (score 0-1)
2. The best outreach channel (email | whatsapp | linkedin | instagram)
3. The key selling angle for this specific business

Be practical and honest. Not every lead is worth chasing."""

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient()

    def tier(self, score: float) -> str:
        if score >= self.SCORE_HOT:
            return "hot"
        if score >= self.SCORE_WARM:
            return "warm"
        return "cold"

    async def enrich(self, lead: Lead) -> Lead:
        """Re-score and add outreach recommendation to a lead."""
        prompt = f"""Evaluate this lead for our {lead.service_needed.replace('_', ' ')} service:

Business: {lead.business_name}
Source URL: {lead.source_url}
Pain points identified: {', '.join(lead.pain_points) or 'none'}
Contact emails: {lead.contact_email}
Current score: {lead.qualification_score}

Return JSON:
{{
  "refined_score": <float 0.0-1.0>,
  "best_channel": "email|whatsapp|linkedin|instagram",
  "selling_angle": "<one sentence tailored pitch hook>",
  "priority": "hot|warm|cold"
}}"""

        try:
            raw = await self.llm.complete(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                json_mode=True,
                max_tokens=256,
            )
            data = json.loads(raw)
            lead.qualification_score = float(data.get("refined_score", lead.qualification_score))
            lead.notes = (
                f"Best channel: {data.get('best_channel', 'email')} | "
                f"Angle: {data.get('selling_angle', '')} | "
                f"Priority: {data.get('priority', self.tier(lead.qualification_score))}"
            )
        except Exception as exc:
            logger.warning("Enrichment failed for %s: %s", lead.business_name, exc)

        return lead

    async def filter_and_enrich(
        self, leads: List[Lead], min_score: float = 0.5
    ) -> List[Lead]:
        """Filter leads below min_score, then enrich survivors."""
        candidates = [l for l in leads if l.qualification_score >= min_score]
        enriched = await asyncio.gather(*[self.enrich(l) for l in candidates])
        # Sort: hot first, then warm, then cold; within tier sort by score desc
        return sorted(enriched, key=lambda l: l.qualification_score, reverse=True)


# ---------------------------------------------------------------------------
# Outreach Composer
# ---------------------------------------------------------------------------

class OutreachComposer:
    """
    Generates personalised outreach drafts for each lead.

    Produces three variants:
      - email_subject + email_body
      - whatsapp_message
      - cold_dm (LinkedIn / Instagram)
    """

    SERVICE_VALUE_PROPS = {
        "website": (
            "a modern, mobile-friendly website that brings you more customers "
            "and builds trust online"
        ),
        "whatsapp_bot": (
            "a WhatsApp bot that handles customer inquiries 24/7 automatically, "
            "so you never miss a sale while you sleep"
        ),
        "seo": (
            "SEO that gets your business to page 1 of Google so customers find "
            "you before they find your competitors"
        ),
    }

    SYSTEM_PROMPT = (
        f"You are a persuasive, friendly copywriter at {AGENCY_NAME}. "
        "Write short, human-sounding outreach messages. No jargon. No spam. "
        "Focus on the prospect's specific pain. Always include a clear call to action."
    )

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient()

    async def compose(self, lead: Lead) -> Dict[str, str]:
        """Generate all outreach variants for a lead."""
        value_prop = self.SERVICE_VALUE_PROPS.get(lead.service_needed, "our services")
        pain = ", ".join(lead.pain_points[:3]) if lead.pain_points else "challenges with your online presence"

        prompt = f"""Write outreach messages to {lead.business_name} who needs {lead.service_needed.replace('_', ' ')}.

Their pain points: {pain}
Our offer: {value_prop}
Our agency: {AGENCY_NAME} ({AGENCY_WEBSITE})
Sender: {SENDER_NAME}
WhatsApp: {SENDER_WHATSAPP}

Return JSON with exactly these keys:
{{
  "email_subject": "<compelling subject line, under 60 chars>",
  "email_body": "<3-4 short paragraphs, plain text, ends with CTA>",
  "whatsapp_message": "<casual, under 300 chars, includes a question to start conversation>",
  "cold_dm": "<friendly LinkedIn/Instagram DM, 2-3 sentences, soft ask>"
}}"""

        try:
            raw = await self.llm.complete(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                json_mode=True,
                max_tokens=1024,
                temperature=0.8,
            )
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Outreach compose failed for %s: %s", lead.business_name, exc)
            return {
                "email_subject": f"Quick question about {lead.business_name}'s online presence",
                "email_body": (
                    f"Hi,\n\nI noticed {lead.business_name} could benefit from {value_prop}.\n\n"
                    f"We are {AGENCY_NAME} and we help businesses like yours grow online.\n\n"
                    f"Would you have 10 minutes for a quick chat?\n\nBest,\n{SENDER_NAME}"
                ),
                "whatsapp_message": (
                    f"Hi! I came across {lead.business_name} and think we could help with "
                    f"{lead.service_needed.replace('_', ' ')}. Quick question – are you currently "
                    f"happy with your online presence? 🙂"
                ),
                "cold_dm": (
                    f"Hey! I noticed {lead.business_name} and had an idea that could help you "
                    f"with {lead.service_needed.replace('_', ' ')}. Worth a quick chat?"
                ),
            }

    async def compose_batch(self, leads: List[Lead]) -> Dict[str, Dict[str, str]]:
        """Compose outreach for multiple leads in parallel."""
        messages = await asyncio.gather(*[self.compose(l) for l in leads])
        return {lead.id: msg for lead, msg in zip(leads, messages)}


# ---------------------------------------------------------------------------
# Full Lead Workflow
# ---------------------------------------------------------------------------

class LeadWorkflow:
    """
    Orchestrates the complete lead generation pipeline:

    Step 1: Run discovery jobs (Website / WhatsApp / SEO)
    Step 2: Qualify and enrich leads
    Step 3: Compose personalised outreach for each lead
    Step 4: Save everything to JSON output files

    Quick start:
        workflow = LeadWorkflow()
        report = await workflow.run()
        print(report["summary"])
    """

    def __init__(
        self,
        crawler_config: Optional[CrawlerConfig] = None,
        llm_config: Optional[LLMConfig] = None,
        min_score: float = 0.5,
        output_dir: str = "leads_output",
    ):
        self.llm_config = llm_config or LLMConfig.from_env()
        self.crawler_config = crawler_config or CrawlerConfig(headless=True, page_timeout=20000)
        self.min_score = min_score
        self.output_dir = output_dir

        llm = LLMClient(self.llm_config)
        self.qualifier = LeadQualifier(llm)
        self.composer  = OutreachComposer(llm)
        self.runner    = JobRunner(self.crawler_config, self.llm_config)
        self.biz_filter = BusinessFilter(llm)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_output_dir(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def _save_json(self, data: Any, filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Saved → %s", path)
        return path

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------

    async def step_discover(self, service: Optional[str] = None) -> List[Lead]:
        """Step 1: Discover raw leads via SerpAPI (REAL Google search)."""
        logger.info(f"Starting discovery with SerpAPI... (service={service})")
        
        from crawler.web_crawler import WebCrawler
        from models.business import BusinessStatus
        
        discovery = BusinessDiscovery()
        
        # Parse service-specific queries
        logger.info(f"[DEBUG] service type: {type(service)}, value: '{service}'")
        if service == "website":
            queries = [
                ("website design agencies", "India"),
                ("web development companies", "India"),
                ("professional website builders", "India"),
            ]
        elif service == "whatsapp_bot":
            queries = [
                ("whatsapp business automation", "India"),
                ("chatbot development services", "India"),
                ("whatsapp api development", "India"),
            ]
        elif service == "seo":
            queries = [
                ("seo services", "India"),
                ("search engine optimization agencies", "India"),
                ("google ranking optimization", "India"),
            ]
        else:
            queries = [("general search", "India")]
        
        all_leads = []
        
        # Search using SerpAPI for REAL data
        async with WebCrawler() as crawler:
            for query, location in queries:
                try:
                    logger.info(f"Searching: {query} in {location}")
                    
                    # Get REAL Google search results
                    real_results = await crawler.search_google(
                        query=query,
                        location=location,
                        num_results=10
                    )
                    
                    logger.info(f"Found {len(real_results)} results for '{query}'")
                    
                    # Convert to Lead objects
                    for result in real_results:
                        lead = Lead(
                            name=result.get('name', 'Unknown'),
                            email=result.get('email'),
                            phone=result.get('phone'),
                            website=result.get('website'),
                            location=result.get('address') or location,
                            services=result.get('description', query),
                            score=result.get('score', 0.8),
                            status="discovered",
                            source=result.get('source', 'google_search'),
                        )
                        if lead.name and lead.name != 'Unknown':
                            all_leads.append(lead)
                            logger.info(f"✓ Found lead: {lead.name}")
                
                except Exception as e:
                    logger.error(f"Search error for '{query}': {str(e)}")
                    # Fall back to mock data if search fails
                    mock_discovery = BusinessDiscovery()
                    intent = SearchIntent(
                        raw_input=query,
                        industry=service or "General",
                        location=location,
                        keywords=[query],
                        queries=[SearchQuery(query=query, search_type="combined", location=location)]
                    )
                    
                    businesses = await mock_discovery.discover(intent)
                    for biz in businesses:
                        lead = Lead(
                            name=biz.name,
                            email=biz.contact.email if biz.contact else None,
                            phone=biz.contact.phone if biz.contact else None,
                            website=biz.contact.website if biz.contact else None,
                            location=f"{biz.locations[0].city}, {biz.locations[0].state}" if biz.locations else location,
                            services=biz.description,
                            score=0.7,
                            status="discovered",
                            source="mock_fallback",
                        )
                        all_leads.append(lead)
        
        logger.info(f"Discovery complete. Raw leads: {len(all_leads)}")
        return all_leads

    async def step_qualify(self, leads: List[Lead]) -> List[Lead]:
        """Step 2: Filter and enrich leads."""
        qualified = await self.qualifier.filter_and_enrich(leads, self.min_score)
        logger.info("After qualification: %d leads", len(qualified))
        return qualified

    async def step_filter(self, leads: List[Lead]) -> List[Lead]:
        """
        Step 3: Business filter — online presence + business model evaluation.

        Each lead is scored on:
          - Online presence quality  (0-10)
          - Suitability for digital services (0-10)

        Then classified as:
          HIGH     → pursue immediately
          MEDIUM   → worth reaching out
          DISCARD  → wrong business type (food stalls, cash-only, etc.) — removed

        Returns only HIGH and MEDIUM leads, sorted HIGH-first.
        """
        logger.info("[FILTER] Running business filter on %d leads…", len(leads))
        filter_results = await self.biz_filter.evaluate_batch(leads, concurrency=4)
        filtered = self.biz_filter.apply_to_leads(leads, filter_results)

        high   = sum(1 for l in filtered if getattr(l, "filter_priority", "") == FilterPriority.HIGH)
        medium = sum(1 for l in filtered if getattr(l, "filter_priority", "") == FilterPriority.MEDIUM)
        removed = len(leads) - len(filtered)
        logger.info(
            "[FILTER] Done: %d high, %d medium, %d discarded",
            high, medium, removed,
        )
        return filtered

    async def step_compose_outreach(
        self, leads: List[Lead]
    ) -> Dict[str, Dict[str, str]]:
        """Step 3: Generate outreach messages."""
        messages = await self.composer.compose_batch(leads)
        logger.info("Outreach composed for %d leads", len(messages))
        return messages

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def run(self, service: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the full pipeline.

        Args:
            service: Optional – run only for 'website', 'whatsapp_bot', or 'seo'.
                     If None, runs all three.

        Returns:
            report dict with keys: leads, outreach, summary, saved_files
        """
        self._ensure_output_dir()
        ts = self._timestamp()

        # 1. Discover
        raw_leads = await self.step_discover(service)

        # 2. Qualify (score-based filter)
        qualified_leads = await self.step_qualify(raw_leads)

        # 3. Business filter (online presence + model suitability → HIGH/MEDIUM/DISCARD)
        filtered_leads = await self.step_filter(qualified_leads)

        # 4. Compose outreach (only for HIGH + MEDIUM leads)
        outreach = await self.step_compose_outreach(filtered_leads)

        # 5. Save
        leads_file = self._save_json(
            [l.to_dict() for l in filtered_leads],
            f"leads_{ts}.json",
        )
        outreach_file = self._save_json(outreach, f"outreach_{ts}.json")

        # 6. Build report
        high_leads   = sum(1 for l in filtered_leads if getattr(l, "filter_priority", "") == FilterPriority.HIGH)
        medium_leads = sum(1 for l in filtered_leads if getattr(l, "filter_priority", "") == FilterPriority.MEDIUM)
        discarded    = len(qualified_leads) - len(filtered_leads)

        summary = {
            "run_at":            ts,
            "service_filter":    service or "all",
            "raw_leads":         len(raw_leads),
            "qualified_leads":   len(qualified_leads),
            "filtered_leads":    len(filtered_leads),
            "high_priority":     high_leads,
            "medium_priority":   medium_leads,
            "discarded":         discarded,
            "hot_leads":         sum(1 for l in filtered_leads if l.qualification_score >= LeadQualifier.SCORE_HOT),
            "warm_leads":        sum(1 for l in filtered_leads if LeadQualifier.SCORE_WARM <= l.qualification_score < LeadQualifier.SCORE_HOT),
            "outreach_drafted":  len(outreach),
        }

        report = {
            "summary":      summary,
            "leads":        [l.to_dict() for l in filtered_leads],
            "outreach":     outreach,
            "saved_files":  [leads_file, outreach_file],
        }

        # Print summary to console
        print(f"\n{'='*60}")
        print("  WORKFLOW COMPLETE")
        print(f"{'='*60}")
        for k, v in summary.items():
            print(f"  {k:<25} {v}")
        print(f"{'='*60}\n")

        return report

    # ------------------------------------------------------------------
    # Convenience: run just outreach for existing leads
    # ------------------------------------------------------------------

    async def compose_for_leads(self, leads: List[Lead]) -> Dict[str, Dict[str, str]]:
        """Compose outreach messages for an already-discovered list of leads."""
        return await self.step_compose_outreach(leads)
