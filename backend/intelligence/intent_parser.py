"""
intent_parser.py
----------------
Converts a natural-language sales request into a structured intent object.

Input  : "Find gyms near me that need booking software"
Output : ParsedIntent dataclass (business_types, location, target_service, …)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class LocationIntent:
    """Represents where the user wants to search."""
    source: str = "user_location"      # "user_location" | "city" | "coordinates"
    radius_km: float = 10.0
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class ServiceIntent:
    """Represents the service/product the user wants to sell."""
    name: str = ""
    capabilities: List[str] = field(default_factory=list)


@dataclass
class ParsedIntent:
    """Full structured representation of the user's sales intent."""
    raw_request: str = ""
    intent: str = "find_potential_customers"
    business_types: List[str] = field(default_factory=list)
    location: LocationIntent = field(default_factory=LocationIntent)
    target_service: ServiceIntent = field(default_factory=ServiceIntent)
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "raw_request": self.raw_request,
            "intent": self.intent,
            "business_types": self.business_types,
            "location": {
                "source": self.location.source,
                "radius_km": self.location.radius_km,
                "city": self.location.city,
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
            },
            "target_service": {
                "name": self.target_service.name,
                "capabilities": self.target_service.capabilities,
            },
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

# Simple keyword maps — replace with LLM call in production
_BUSINESS_KEYWORDS: dict[str, List[str]] = {
    "gym": ["gym", "fitness", "crossfit", "yoga", "pilates"],
    "restaurant": ["restaurant", "cafe", "diner", "bistro", "eatery", "food"],
    "dental": ["dental", "dentist", "orthodontist", "clinic"],
    "salon": ["salon", "barber", "beauty", "hair"],
    "hotel": ["hotel", "motel", "inn", "hostel", "resort"],
}

_SERVICE_KEYWORDS: dict[str, List[str]] = {
    "online_booking_system": ["booking", "appointment", "schedule", "reservation"],
    "online_ordering_system": ["ordering", "delivery", "takeaway", "ecommerce"],
    "lead_followup_automation": ["leads", "lead", "crm", "follow-up", "followup"],
    "ai_appointment_assistant": ["ai assistant", "chatbot", "virtual assistant"],
}


class IntentParser:
    """
    Parses a natural-language request into a ParsedIntent.

    Usage
    -----
    >>> parser = IntentParser()
    >>> intent = parser.parse("Find gyms near me that need booking software")
    >>> print(intent.business_types)
    ['gym']
    """

    def parse(self, user_request: str) -> ParsedIntent:
        """
        Parse *user_request* into a structured ParsedIntent.

        Parameters
        ----------
        user_request : str
            Raw natural-language text from the user.

        Returns
        -------
        ParsedIntent
        """
        text = user_request.lower()

        business_types = self._extract_business_types(text)
        location = self._extract_location(text)
        target_service = self._extract_service(text)
        confidence = self._estimate_confidence(business_types, target_service)

        return ParsedIntent(
            raw_request=user_request,
            intent="find_potential_customers",
            business_types=business_types,
            location=location,
            target_service=target_service,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_business_types(self, text: str) -> List[str]:
        found = []
        for category, keywords in _BUSINESS_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                found.append(category)
        return found or ["general_business"]

    def _extract_location(self, text: str) -> LocationIntent:
        loc = LocationIntent()

        # Radius extraction  (e.g. "10 km", "5 miles")
        radius_match = re.search(r"(\d+(?:\.\d+)?)\s*(km|kilometers?|miles?)", text)
        if radius_match:
            value = float(radius_match.group(1))
            unit = radius_match.group(2)
            loc.radius_km = value * 1.609 if "mile" in unit else value

        # City extraction heuristic
        city_match = re.search(r"\bnear\s+([a-z\s]+?)(?:\s+that|\s+who|\s+with|$)", text)
        if city_match:
            candidate = city_match.group(1).strip()
            if candidate not in ("me", "my location", "us"):
                loc.source = "city"
                loc.city = candidate.title()
            else:
                loc.source = "user_location"

        return loc

    def _extract_service(self, text: str) -> ServiceIntent:
        for service_name, keywords in _SERVICE_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return ServiceIntent(
                    name=service_name,
                    capabilities=keywords[:3],
                )
        return ServiceIntent(name="general_service", capabilities=[])

    def _estimate_confidence(
        self, business_types: List[str], service: ServiceIntent
    ) -> float:
        score = 0.5
        if business_types and business_types[0] != "general_business":
            score += 0.25
        if service.name != "general_service":
            score += 0.25
        return round(min(score, 1.0), 2)
