"""
research_planner.py
-------------------
Converts a ParsedIntent into a concrete ResearchPlan that tells the
crawler WHAT pages to look at and WHAT signals to look for.

Input  : ParsedIntent
Output : ResearchPlan dataclass
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .intent_parser import ParsedIntent, ServiceIntent


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class CrawlConfig:
    max_pages: int = 25
    max_depth: int = 2
    timeout_seconds: int = 30


@dataclass
class ResearchPlan:
    """Tells the crawler exactly what to do for a given intent."""
    business_type: str = ""
    target_service: str = ""
    pages_to_prioritize: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    negative_signals: List[str] = field(default_factory=list)
    crawl: CrawlConfig = field(default_factory=CrawlConfig)

    def to_dict(self) -> dict:
        return {
            "business_type": self.business_type,
            "target_service": self.target_service,
            "pages_to_prioritize": self.pages_to_prioritize,
            "signals": self.signals,
            "negative_signals": self.negative_signals,
            "crawl": {
                "max_pages": self.crawl.max_pages,
                "max_depth": self.crawl.max_depth,
                "timeout_seconds": self.crawl.timeout_seconds,
            },
        }


# ---------------------------------------------------------------------------
# Service → signal mapping  (expand as new service profiles are added)
# ---------------------------------------------------------------------------

_SERVICE_PROFILES: dict[str, dict] = {
    "online_booking_system": {
        "pages": ["booking", "appointment", "schedule", "contact", "about", "pricing"],
        "signals": ["book now", "appointment", "reserve", "schedule", "availability", "calendar", "whatsapp", "phone"],
        "negative_signals": ["book online", "online booking", "book appointment", "calendly", "setmore"],
    },
    "online_ordering_system": {
        "pages": ["menu", "order", "delivery", "contact", "pricing"],
        "signals": ["call to order", "whatsapp", "phone order", "no online order", "visit us"],
        "negative_signals": ["order online", "add to cart", "place order", "ubereats", "deliveroo"],
    },
    "lead_followup_automation": {
        "pages": ["contact", "inquiry", "membership", "pricing", "about"],
        "signals": ["contact form", "inquiry form", "call us", "email us", "whatsapp"],
        "negative_signals": ["crm", "hubspot", "salesforce", "zoho", "automated follow"],
    },
    "ai_appointment_assistant": {
        "pages": ["contact", "booking", "about", "services", "faq"],
        "signals": ["contact us", "call to book", "manual scheduling", "receptionist"],
        "negative_signals": ["ai assistant", "chatbot", "virtual assistant", "live chat bot"],
    },
    "general_service": {
        "pages": ["home", "about", "services", "contact", "pricing"],
        "signals": ["contact", "phone", "email", "whatsapp"],
        "negative_signals": [],
    },
}

_BUSINESS_PAGE_HINTS: dict[str, List[str]] = {
    "gym": ["membership", "classes", "pricing", "personal-training"],
    "restaurant": ["menu", "reservations", "delivery", "catering"],
    "dental": ["appointments", "services", "patients", "insurance"],
    "salon": ["services", "booking", "gallery", "prices"],
    "hotel": ["rooms", "reservations", "amenities", "contact"],
    "general_business": [],
}


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

class ResearchPlanner:
    """
    Takes a ParsedIntent and produces a ResearchPlan.

    Usage
    -----
    >>> planner = ResearchPlanner()
    >>> plan = planner.plan(parsed_intent)
    """

    def plan(self, intent: ParsedIntent) -> ResearchPlan:
        """
        Build a ResearchPlan from the given ParsedIntent.

        Parameters
        ----------
        intent : ParsedIntent
            Structured intent produced by IntentParser.

        Returns
        -------
        ResearchPlan
        """
        service_name = intent.target_service.name
        profile = _SERVICE_PROFILES.get(service_name, _SERVICE_PROFILES["general_service"])

        business_type = intent.business_types[0] if intent.business_types else "general_business"
        extra_pages = _BUSINESS_PAGE_HINTS.get(business_type, [])

        # Merge and deduplicate pages list
        pages = list(dict.fromkeys(profile["pages"] + extra_pages))

        return ResearchPlan(
            business_type=business_type,
            target_service=service_name,
            pages_to_prioritize=pages,
            signals=profile["signals"],
            negative_signals=profile["negative_signals"],
            crawl=self._crawl_config(business_type),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _crawl_config(self, business_type: str) -> CrawlConfig:
        """Return a sensible crawl config for the business type."""
        # Larger businesses may have more complex sites
        if business_type in ("hotel", "restaurant"):
            return CrawlConfig(max_pages=40, max_depth=3)
        return CrawlConfig(max_pages=25, max_depth=2)
