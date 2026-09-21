"""
clorel_qualifier.py
-------------------
Evidence-Based B2B Lead Discovery, Verification, and Qualification Agent

Implements the CLOREL framework:
  - Location-aware geographic validation
  - Business identity verification
  - Hard & soft filter separation
  - Digital presence verification (multi-channel)
  - Search intent analysis
  - Demand & business signal analysis
  - Service-fit assessment
  - Evidence confidence scoring
  - Routing: sales_review | hold | retry | reject

Core Principle: "Website Not Found ≠ Rejected Lead"
  Missing website triggers verification, not automatic rejection.
  
Goal: 10 evidence-supported prospects > 100 speculative leads
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from .competitor_filter import CompetitorFilter, CompetitorAnalysis

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class WebsiteStatus(str, Enum):
    """Website availability status."""
    ACTIVE = "active"
    MISSING = "missing"
    CRAWL_FAILED = "crawl_failed"
    UNVERIFIED = "unverified"


class SearchIntent(str, Enum):
    """Customer search intent types."""
    LOCAL_DISCOVERY = "local_discovery"
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    BOOKING = "booking"
    ORDERING = "ordering"
    RESERVATION = "reservation"
    QUOTE_REQUEST = "quote_request"
    CATALOG = "catalog"
    CONTACT = "contact"
    EVENT = "event"
    OTHER = "other"


class LeadRouting(str, Enum):
    """Lead qualification routing decision."""
    SALES_REVIEW = "sales_review"  # High confidence, ready for sales
    HOLD = "hold"                  # Valid but insufficient evidence
    RETRY = "retry"                # Technical failure, needs retry
    REJECT = "reject"              # Failed hard filters or not a business


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class DigitalPresence:
    """Multi-channel digital presence assessment."""
    website: bool = False
    instagram: bool = False
    facebook: bool = False
    google_business: bool = False
    booking_system: bool = False
    ordering_system: bool = False
    third_party_platforms: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "website": self.website,
            "instagram": self.instagram,
            "facebook": self.facebook,
            "google_business": self.google_business,
            "booking_system": self.booking_system,
            "ordering_system": self.ordering_system,
            "third_party_platforms": self.third_party_platforms,
        }


@dataclass
class SearchIntentProfile:
    """Customer search intent profile."""
    primary: SearchIntent = SearchIntent.OTHER
    secondary: List[SearchIntent] = field(default_factory=list)
    strength: float = 0.0  # 0.0 - 1.0
    
    def to_dict(self) -> dict:
        return {
            "primary": self.primary.value,
            "secondary": [s.value for s in self.secondary],
            "strength": self.strength,
        }


@dataclass
class DemandSignals:
    """Business operational and activity signals."""
    rating: Optional[float] = None
    review_count: Optional[int] = None
    recent_activity: Optional[str] = None
    opening_hours_verified: bool = False
    
    def to_dict(self) -> dict:
        return {
            "rating": self.rating,
            "review_count": self.review_count,
            "recent_activity": self.recent_activity,
            "opening_hours_verified": self.opening_hours_verified,
        }


@dataclass
class LocationData:
    """Geographic location information."""
    address: str = ""
    city: str = ""
    state: str = ""
    country: str = ""
    distance_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_confidence: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "distance_km": self.distance_km,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_confidence": self.location_confidence,
        }


@dataclass
class ClorelLead:
    """Evidence-based qualified lead following CLOREL framework."""
    # Identity
    id: str
    business_name: str
    contact_person: Optional[str] = None
    
    # Service
    service_needed: str = ""
    
    # Source
    source_url: str = ""
    discovery_source: str = "google_maps"
    
    # Contact
    website: Optional[str] = None
    contact_email: List[str] = field(default_factory=list)
    contact_phone: List[str] = field(default_factory=list)
    
    # Location
    location: LocationData = field(default_factory=LocationData)
    
    # Classification
    industry: str = ""
    website_status: WebsiteStatus = WebsiteStatus.UNVERIFIED
    
    # Digital Assessment
    digital_presence: DigitalPresence = field(default_factory=DigitalPresence)
    search_intent: SearchIntentProfile = field(default_factory=SearchIntentProfile)
    demand_signals: DemandSignals = field(default_factory=DemandSignals)
    
    # Evidence
    pain_points: List[str] = field(default_factory=list)  # Evidence-backed only
    evidence: List[str] = field(default_factory=list)      # Observed facts
    assumptions: List[str] = field(default_factory=list)   # Separated from evidence
    
    # Scoring
    qualification_score: float = 0.0          # Overall confidence
    online_presence_score: float = 0.0        # 0-10 digital presence
    service_fit_score: float = 0.0            # 0-10 service relevance
    confidence: float = 0.0                   # 0-1 evidence reliability
    
    # Routing
    routing: LeadRouting = LeadRouting.HOLD
    filter_priority: str = "unfiltered"       # high | medium | low | reject
    filter_justification: str = ""
    filter_reasoning: str = ""
    filter_recommended: List[str] = field(default_factory=list)
    review_reasons: List[str] = field(default_factory=list)
    
    # Metadata
    discovered_at: str = ""
    outreach_sent: bool = False
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "business_name": self.business_name,
            "contact_person": self.contact_person,
            "service_needed": self.service_needed,
            "source_url": self.source_url,
            "discovery_source": self.discovery_source,
            "website": self.website,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "location": self.location.to_dict(),
            "industry": self.industry,
            "website_status": self.website_status.value,
            "digital_presence": self.digital_presence.to_dict(),
            "search_intent": self.search_intent.to_dict(),
            "demand_signals": self.demand_signals.to_dict(),
            "pain_points": self.pain_points,
            "evidence": self.evidence,
            "assumptions": self.assumptions,
            "qualification_score": self.qualification_score,
            "filter_priority": self.filter_priority,
            "filter_justification": self.filter_justification,
            "filter_reasoning": self.filter_reasoning,
            "online_presence_score": self.online_presence_score,
            "service_fit_score": self.service_fit_score,
            "confidence": self.confidence,
            "filter_recommended": self.filter_recommended,
            "routing": self.routing.value,
            "review_reasons": self.review_reasons,
            "outreach_sent": self.outreach_sent,
        }


# ---------------------------------------------------------------------------
# CLOREL Qualification Pipeline
# ---------------------------------------------------------------------------

class ClorelQualifier:
    """
    Evidence-based B2B lead qualification following the CLOREL framework.
    
    Pipeline:
      1. Geographic Validation (hard constraint)
      2. Business Identity Check (real business verification)
      3. Hard Filter Validation (eligibility gates)
      4. Digital Presence Verification (multi-channel)
      5. Search Intent Analysis
      6. Demand & Business Signal Analysis
      7. Service-Fit Assessment
      8. Evidence Confidence Assessment
      9. Verification Gate → Routing
    
    Usage:
        qualifier = ClorelQualifier(llm_client)
        lead = await qualifier.qualify(raw_lead, campaign)
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize CLOREL qualifier.
        
        Args:
            llm_client: LLM client for analysis (optional)
        """
        self.llm = llm_client
        self.competitor_filter = CompetitorFilter(llm_client)
    
    # ------------------------------------------------------------------
    # Pipeline Steps
    # ------------------------------------------------------------------
    
    def validate_geography(
        self,
        lead_data: dict,
        campaign: dict,
    ) -> tuple[bool, Optional[str]]:
        """
        Step 1: Geographic Validation (HARD CONSTRAINT)
        
        Returns:
            (is_valid, rejection_reason)
        """
        campaign_location = campaign.get("location", "")
        campaign_radius = campaign.get("radius_km")
        
        if not campaign_location and not campaign_radius:
            # No geographic constraint
            return True, None
        
        lead_distance = lead_data.get("distance_km")
        lead_city = lead_data.get("city", "").lower()
        campaign_city = campaign_location.lower()
        
        # City match check
        if campaign_city and lead_city:
            if campaign_city not in lead_city and lead_city not in campaign_city:
                return False, f"Business location '{lead_city}' outside campaign area '{campaign_city}'"
        
        # Radius check
        if campaign_radius and lead_distance is not None:
            if lead_distance > campaign_radius:
                return False, f"Business is {lead_distance:.1f}km away, outside {campaign_radius}km radius"
        
        return True, None
    
    def validate_business_identity(self, lead_data: dict) -> tuple[bool, Optional[str]]:
        """
        Step 2: Business Identity Validation
        
        Confirms this is a REAL business, not:
          - Article/tutorial
          - YouTube video
          - Reddit discussion
          - Generic category
          - Service description
        
        Returns:
            (is_valid, rejection_reason)
        """
        business_name = lead_data.get("business_name", "").strip()
        source_url = lead_data.get("source_url", "")
        
        # Check for valid business name
        if not business_name or len(business_name) < 2:
            return False, "No identifiable business name"
        
        # Reject generic categories
        generic_names = {
            "small business", "restaurant", "restaurants", "clinic", "clinics",
            "gym", "gyms", "salon", "salons", "hotel", "hotels",
            "unknown", "null", "none", "youtube", "reddit", "quora",
        }
        
        if business_name.lower() in generic_names:
            return False, f"'{business_name}' is a generic category, not a specific business"
        
        # Check for content indicators
        content_indicators = [
            "how to", "best way", "tips for", "guide to", "tutorial",
            "watch:", "video:", "article:", "question:", "?",
        ]
        
        for indicator in content_indicators:
            if indicator in business_name.lower():
                return False, f"Business name contains content indicator: '{indicator}'"
        
        # Check source URL for content platforms
        content_domains = [
            "youtube.com", "youtu.be", "reddit.com", "quora.com",
            "medium.com", "facebook.com/watch", "tiktok.com",
        ]
        
        for domain in content_domains:
            if domain in source_url.lower():
                return False, f"Source is content platform: {domain}"
        
        return True, None
    
    def validate_not_competitor(
        self,
        lead_data: dict,
        campaign: dict,
    ) -> tuple[bool, Optional[str], Optional[CompetitorAnalysis]]:
        """
        Step 2b: Competitor Validation (CRITICAL)
        
        REJECT if business SELLS/PROVIDES the same service.
        
        Examples:
          - Target: website → Web agency = REJECT
          - Target: seo → SEO company = REJECT
          - Target: whatsapp_bot → Chatbot developer = REJECT
        
        Returns:
            (is_valid_customer, rejection_reason, analysis)
        """
        target_service = campaign.get("service", "")
        
        if not target_service:
            # No service specified, skip competitor check
            return True, None, None
        
        # Run competitor analysis
        analysis = self.competitor_filter.analyze(lead_data, target_service)
        
        if analysis.is_competitor:
            reason = (
                f"Competitor detected: Business appears to provide '{target_service}' services. "
                f"{analysis.rejection_reason}"
            )
            logger.info(
                "Competitor rejected: %s (confidence: %.0f%%)",
                lead_data.get("business_name", "unknown"),
                analysis.confidence * 100,
            )
            return False, reason, analysis
        
        return True, None, analysis
    
    def validate_hard_filters(
        self,
        lead_data: dict,
        campaign: dict,
    ) -> tuple[bool, Optional[str]]:
        """
        Step 3: Hard Filter Validation
        
        Hard filters determine eligibility:
          - Geographic boundary
          - Target business category
          - Minimum rating
          - Campaign-specific rules
        
        Returns:
            (is_valid, rejection_reason)
        """
        # Rating filter
        min_rating = campaign.get("minimum_rating")
        lead_rating = lead_data.get("rating")
        
        if min_rating and lead_rating is not None:
            if lead_rating < min_rating:
                return False, f"Rating {lead_rating} below minimum {min_rating}"
        
        # Category filter
        target_categories = campaign.get("target_categories", [])
        lead_industry = lead_data.get("industry", "").lower()
        
        if target_categories:
            category_match = any(
                cat.lower() in lead_industry or lead_industry in cat.lower()
                for cat in target_categories
            )
            if not category_match:
                return False, f"Industry '{lead_industry}' not in target categories"
        
        # Country filter
        campaign_country = campaign.get("country", "").lower()
        lead_country = lead_data.get("country", "").lower()
        
        if campaign_country and lead_country:
            if campaign_country != lead_country:
                return False, f"Business country '{lead_country}' != campaign country '{campaign_country}'"
        
        return True, None
    
    def assess_digital_presence(self, lead_data: dict) -> DigitalPresence:
        """
        Step 4: Digital Presence Verification
        
        Check ALL digital channels, not just website:
          - Website
          - Instagram
          - Facebook  
          - Google Business
          - Booking systems
          - Ordering systems
          - Third-party platforms
        """
        presence = DigitalPresence()
        
        # Website
        website = lead_data.get("website")
        website_status = lead_data.get("website_status", "unverified")
        
        presence.website = bool(website) and website_status == "active"
        
        # Social media (extract from source_url, pain_points, or raw data)
        source_url = lead_data.get("source_url", "").lower()
        raw_snippet = lead_data.get("raw_snippet", "").lower()
        pain_points = " ".join(lead_data.get("pain_points", [])).lower()
        
        combined_text = f"{source_url} {raw_snippet} {pain_points}"
        
        presence.instagram = "instagram" in combined_text
        presence.facebook = "facebook" in combined_text or "fb.com" in combined_text
        presence.google_business = "google" in combined_text or "maps" in combined_text
        
        # Booking/ordering systems
        presence.booking_system = any(
            term in combined_text
            for term in ["booking", "appointment", "reserve", "schedule"]
        )
        presence.ordering_system = any(
            term in combined_text
            for term in ["order online", "delivery", "takeaway", "menu"]
        )
        
        # Third-party platforms
        platforms = []
        platform_keywords = {
            "Uber Eats": "uber eats",
            "DoorDash": "doordash",
            "Zomato": "zomato",
            "Swiggy": "swiggy",
            "Booking.com": "booking.com",
            "OpenTable": "opentable",
        }
        
        for platform, keyword in platform_keywords.items():
            if keyword in combined_text:
                platforms.append(platform)
        
        presence.third_party_platforms = platforms
        
        return presence
    
    def analyze_search_intent(self, lead_data: dict, campaign: dict) -> SearchIntentProfile:
        """
        Step 5: Search Intent Analysis
        
        Determine what customers are likely trying to accomplish:
          - LOCAL_DISCOVERY: "restaurant near me"
          - ORDERING: "order food from X"
          - BOOKING: "book appointment at Y"
          - etc.
        
        Use EVIDENCE, not assumptions.
        """
        profile = SearchIntentProfile()
        
        industry = lead_data.get("industry", "").lower()
        service = campaign.get("service", "").lower()
        
        # Industry-based intent inference (with evidence)
        if any(term in industry for term in ["restaurant", "cafe", "food"]):
            profile.primary = SearchIntent.ORDERING
            profile.secondary = [SearchIntent.LOCAL_DISCOVERY, SearchIntent.RESERVATION]
            profile.strength = 0.7
        
        elif any(term in industry for term in ["dental", "clinic", "doctor", "medical"]):
            profile.primary = SearchIntent.BOOKING
            profile.secondary = [SearchIntent.CONTACT, SearchIntent.LOCAL_DISCOVERY]
            profile.strength = 0.8
        
        elif any(term in industry for term in ["hotel", "resort", "accommodation"]):
            profile.primary = SearchIntent.RESERVATION
            profile.secondary = [SearchIntent.BOOKING, SearchIntent.INFORMATIONAL]
            profile.strength = 0.8
        
        elif any(term in industry for term in ["salon", "spa", "barber", "beauty"]):
            profile.primary = SearchIntent.BOOKING
            profile.secondary = [SearchIntent.CONTACT, SearchIntent.LOCAL_DISCOVERY]
            profile.strength = 0.7
        
        elif any(term in industry for term in ["gym", "fitness", "yoga"]):
            profile.primary = SearchIntent.BOOKING
            profile.secondary = [SearchIntent.LOCAL_DISCOVERY, SearchIntent.INFORMATIONAL]
            profile.strength = 0.6
        
        else:
            # Default to discovery + contact
            profile.primary = SearchIntent.LOCAL_DISCOVERY
            profile.secondary = [SearchIntent.CONTACT, SearchIntent.INFORMATIONAL]
            profile.strength = 0.4
        
        return profile
    
    def analyze_demand_signals(self, lead_data: dict) -> DemandSignals:
        """
        Step 6: Demand & Business Signal Analysis
        
        Evaluate operational activity:
          - Review count/recent reviews
          - Opening hours
          - Recent updates
          - Social activity
        
        Do NOT interpret missing data as negative.
        """
        signals = DemandSignals()
        
        signals.rating = lead_data.get("rating")
        signals.review_count = lead_data.get("review_count")
        
        # Opening hours (presence indicates verified operational status)
        raw_snippet = lead_data.get("raw_snippet", "")
        if any(term in raw_snippet.lower() for term in ["open", "hours", "am", "pm"]):
            signals.opening_hours_verified = True
        
        # Recent activity assessment
        if signals.review_count and signals.review_count > 50:
            signals.recent_activity = "high"
        elif signals.review_count and signals.review_count > 10:
            signals.recent_activity = "moderate"
        elif signals.review_count and signals.review_count > 0:
            signals.recent_activity = "low"
        else:
            signals.recent_activity = None  # Unknown, not "inactive"
        
        return signals
    
    def assess_service_fit(
        self,
        lead_data: dict,
        digital_presence: DigitalPresence,
        search_intent: SearchIntentProfile,
        demand_signals: DemandSignals,
        campaign: dict,
    ) -> tuple[float, List[str], List[str]]:
        """
        Step 7: Service-Fit Assessment
        
        Determine if business has a REAL, EVIDENCE-BACKED opportunity
        for the requested service.
        
        Returns:
            (service_fit_score, pain_points, evidence_list)
        """
        service = campaign.get("service", "").lower()
        score = 5.0  # Baseline neutral
        pain_points = []
        evidence = []
        
        # ─────────────────────────────────────────────────────────────
        # WEBSITE SERVICE FIT
        # ─────────────────────────────────────────────────────────────
        if "website" in service:
            # Evidence: Website status
            website_status = lead_data.get("website_status", "unverified")
            
            if website_status == "missing":
                evidence.append("No website found in Google Business Profile")
                
                # Check if business needs digital interactions
                if search_intent.primary in [
                    SearchIntent.ORDERING,
                    SearchIntent.BOOKING,
                    SearchIntent.RESERVATION,
                ]:
                    score += 3.0
                    pain_points.append("Customers seek online interaction but no website exists")
                    evidence.append(f"Primary customer intent: {search_intent.primary.value}")
                
                # Check third-party platform dependence
                if digital_presence.third_party_platforms:
                    score += 1.0
                    pain_points.append(
                        f"Relies on third-party platforms: {', '.join(digital_presence.third_party_platforms)}"
                    )
                    evidence.append("Opportunity to reduce platform dependence with direct channel")
                else:
                    score += 2.0
                    pain_points.append("No direct digital ordering/booking channel found")
                
                # Activity signals increase opportunity
                if demand_signals.review_count and demand_signals.review_count > 100:
                    score += 1.0
                    evidence.append(f"High customer activity: {demand_signals.review_count} reviews")
            
            elif website_status == "crawl_failed":
                # Technical failure - cannot assess fit
                score = 5.0  # Neutral
                evidence.append("Website crawl failed - verification needed")
            
            elif website_status == "active":
                # Website exists - check quality
                score -= 2.0
                evidence.append("Website already exists - check quality/gaps")
        
        # ─────────────────────────────────────────────────────────────
        # SEO SERVICE FIT
        # ─────────────────────────────────────────────────────────────
        elif "seo" in service:
            if digital_presence.website:
                score += 2.0
                evidence.append("Website exists - SEO applicable")
                pain_points.append("Website could benefit from SEO optimization")
            else:
                score -= 3.0
                evidence.append("No website found - SEO not applicable yet")
        
        # ─────────────────────────────────────────────────────────────
        # WHATSAPP BOT SERVICE FIT
        # ─────────────────────────────────────────────────────────────
        elif "whatsapp" in service or "bot" in service:
            # Check if business uses manual communication
            raw_snippet = lead_data.get("raw_snippet", "").lower()
            pain_text = " ".join(lead_data.get("pain_points", [])).lower()
            
            if "whatsapp" in raw_snippet or "whatsapp" in pain_text:
                score += 3.0
                evidence.append("WhatsApp contact method found")
                pain_points.append("Manual WhatsApp communication - automation opportunity")
            
            if search_intent.primary == SearchIntent.CONTACT:
                score += 1.0
                evidence.append("Customers primarily seek contact - bot can handle")
        
        # Clamp score to 0-10
        score = max(0.0, min(10.0, score))
        
        return score, pain_points, evidence
    
    def calculate_online_presence_score(
        self,
        digital_presence: DigitalPresence,
    ) -> float:
        """
        Calculate online presence score (0-10)
        
        IMPORTANT: Missing website ≠ score 0
        Business may have strong multi-channel presence.
        """
        score = 0.0
        
        # Website (but not the only factor)
        if digital_presence.website:
            score += 3.0
        
        # Social media
        if digital_presence.instagram:
            score += 1.5
        if digital_presence.facebook:
            score += 1.5
        
        # Google presence
        if digital_presence.google_business:
            score += 2.0
        
        # Booking/ordering systems
        if digital_presence.booking_system:
            score += 1.0
        if digital_presence.ordering_system:
            score += 1.0
        
        # Third-party platforms
        score += min(len(digital_presence.third_party_platforms) * 0.5, 2.0)
        
        return min(score, 10.0)
    
    def calculate_confidence(
        self,
        lead_data: dict,
        evidence_count: int,
        has_contact_info: bool,
    ) -> float:
        """
        Calculate evidence confidence score (0-1)
        
        Confidence = how reliable our evidence is, NOT how likely conversion is.
        
        Factors:
          - Business identity verified
          - Contact information available
          - Location confirmed
          - Multiple evidence sources
          - Operational signals present
        """
        confidence = 0.0
        
        # Business identity (0.25)
        business_name = lead_data.get("business_name", "").strip()
        if business_name and len(business_name) > 2:
            confidence += 0.15
        
        address = lead_data.get("address", "").strip()
        if address:
            confidence += 0.10
        
        # Contact information (0.25)
        if has_contact_info:
            confidence += 0.25
        
        # Location verification (0.20)
        if lead_data.get("latitude") and lead_data.get("longitude"):
            confidence += 0.15
        
        if lead_data.get("distance_km") is not None:
            confidence += 0.05
        
        # Evidence depth (0.30)
        if evidence_count >= 5:
            confidence += 0.30
        elif evidence_count >= 3:
            confidence += 0.20
        elif evidence_count >= 1:
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def route_lead(
        self,
        hard_filters_passed: bool,
        business_identity_valid: bool,
        confidence: float,
        service_fit_score: float,
        evidence_count: int,
        has_contact_info: bool,
        website_status: str,
    ) -> tuple[LeadRouting, List[str]]:
        """
        Step 9: Verification Gate → Routing
        
        Routes:
          - SALES_REVIEW: Ready for sales team
          - HOLD: Valid but needs more evidence
          - RETRY: Technical failure
          - REJECT: Failed validation
        """
        reasons = []
        
        # REJECT cases
        if not hard_filters_passed:
            return LeadRouting.REJECT, ["Failed hard filter constraints"]
        
        if not business_identity_valid:
            return LeadRouting.REJECT, ["Not a valid business identity"]
        
        if not has_contact_info:
            return LeadRouting.REJECT, ["No contact information available"]
        
        # RETRY cases
        if website_status == "crawl_failed":
            return LeadRouting.RETRY, ["Website crawl failed - needs retry"]
        
        # SALES_REVIEW cases
        if confidence >= 0.75 and service_fit_score >= 7.0 and evidence_count >= 3:
            reasons.append("High confidence with strong service fit")
            reasons.append(f"Confidence: {confidence:.2f}, Service fit: {service_fit_score:.1f}/10")
            return LeadRouting.SALES_REVIEW, reasons
        
        # HOLD cases  
        if confidence >= 0.5 and service_fit_score >= 5.0:
            reasons.append("Moderate confidence - needs additional verification")
            reasons.append(f"Confidence: {confidence:.2f}, Service fit: {service_fit_score:.1f}/10")
            return LeadRouting.HOLD, reasons
        
        # Default HOLD
        reasons.append("Insufficient evidence for sales review")
        reasons.append(f"Confidence: {confidence:.2f}, Service fit: {service_fit_score:.1f}/10")
        return LeadRouting.HOLD, reasons
    
    # ------------------------------------------------------------------
    # Main Qualification Method
    # ------------------------------------------------------------------
    
    async def qualify(
        self,
        lead_data: dict,
        campaign: dict,
    ) -> ClorelLead:
        """
        Execute full CLOREL qualification pipeline.
        
        Args:
            lead_data: Raw lead data from discovery
            campaign: Campaign configuration with constraints
        
        Returns:
            ClorelLead with routing decision and evidence
        """
        # Initialize lead
        lead = ClorelLead(
            id=lead_data.get("id", ""),
            business_name=lead_data.get("business_name", ""),
            service_needed=campaign.get("service", ""),
            source_url=lead_data.get("source_url", ""),
            website=lead_data.get("website"),
            contact_email=lead_data.get("contact_email", []),
            contact_phone=lead_data.get("contact_phone", []),
            industry=lead_data.get("industry", ""),
            discovered_at=lead_data.get("discovered_at", ""),
        )
        
        # Location data
        lead.location = LocationData(
            address=lead_data.get("address", ""),
            city=lead_data.get("city", lead_data.get("location", "")),
            state=lead_data.get("state", ""),
            country=lead_data.get("country", ""),
            distance_km=lead_data.get("distance_km"),
            latitude=lead_data.get("latitude"),
            longitude=lead_data.get("longitude"),
            location_confidence=0.8 if lead_data.get("latitude") else 0.3,
        )
        
        # Pipeline execution
        evidence_list = []
        assumptions_list = []
        
        # Step 1: Geographic validation
        geo_valid, geo_reason = self.validate_geography(lead_data, campaign)
        if not geo_valid:
            lead.routing = LeadRouting.REJECT
            lead.filter_justification = geo_reason
            lead.filter_priority = "reject"
            return lead
        
        evidence_list.append("Geographic constraint satisfied")
        
        # Step 2: Business identity
        identity_valid, identity_reason = self.validate_business_identity(lead_data)
        if not identity_valid:
            lead.routing = LeadRouting.REJECT
            lead.filter_justification = identity_reason
            lead.filter_priority = "reject"
            return lead
        
        evidence_list.append(f"Business identity verified: {lead.business_name}")
        
        # Step 2b: Competitor check (CRITICAL)
        not_competitor, competitor_reason, competitor_analysis = self.validate_not_competitor(
            lead_data, campaign
        )
        if not not_competitor:
            lead.routing = LeadRouting.REJECT
            lead.filter_justification = competitor_reason
            lead.filter_priority = "reject"
            if competitor_analysis:
                evidence_list.extend(competitor_analysis.evidence)
            return lead
        
        evidence_list.append("Not a competitor - potential customer verified")
        
        # Step 3: Hard filters
        filters_valid, filter_reason = self.validate_hard_filters(lead_data, campaign)
        if not filters_valid:
            lead.routing = LeadRouting.REJECT
            lead.filter_justification = filter_reason
            lead.filter_priority = "reject"
            return lead
        
        evidence_list.append("Hard filters passed")
        
        # Step 4: Digital presence
        lead.digital_presence = self.assess_digital_presence(lead_data)
        lead.online_presence_score = self.calculate_online_presence_score(lead.digital_presence)
        
        # Determine website status
        if lead.website:
            if lead_data.get("website_status") == "crawl_failed":
                lead.website_status = WebsiteStatus.CRAWL_FAILED
            else:
                lead.website_status = WebsiteStatus.ACTIVE
        else:
            lead.website_status = WebsiteStatus.MISSING
        
        evidence_list.append(f"Website status: {lead.website_status.value}")
        evidence_list.append(f"Online presence score: {lead.online_presence_score:.1f}/10")
        
        # Step 5: Search intent
        lead.search_intent = self.analyze_search_intent(lead_data, campaign)
        evidence_list.append(f"Primary search intent: {lead.search_intent.primary.value}")
        
        # Step 6: Demand signals
        lead.demand_signals = self.analyze_demand_signals(lead_data)
        if lead.demand_signals.rating:
            evidence_list.append(f"Rating: {lead.demand_signals.rating}/5")
        if lead.demand_signals.review_count:
            evidence_list.append(f"Reviews: {lead.demand_signals.review_count}")
        
        # Step 7: Service fit
        service_fit, pain_points, fit_evidence = self.assess_service_fit(
            lead_data,
            lead.digital_presence,
            lead.search_intent,
            lead.demand_signals,
            campaign,
        )
        
        lead.service_fit_score = service_fit
        lead.pain_points = pain_points
        evidence_list.extend(fit_evidence)
        
        # Step 8: Confidence
        has_contact = bool(lead.contact_email or lead.contact_phone or lead.website)
        lead.confidence = self.calculate_confidence(
            lead_data,
            len(evidence_list),
            has_contact,
        )
        
        lead.evidence = evidence_list
        lead.assumptions = assumptions_list
        
        # Step 9: Routing
        lead.routing, lead.review_reasons = self.route_lead(
            hard_filters_passed=True,
            business_identity_valid=True,
            confidence=lead.confidence,
            service_fit_score=lead.service_fit_score,
            evidence_count=len(evidence_list),
            has_contact_info=has_contact,
            website_status=lead.website_status.value,
        )
        
        # Set filter priority based on routing
        if lead.routing == LeadRouting.SALES_REVIEW:
            lead.filter_priority = "high"
            lead.filter_justification = "High-confidence lead with strong evidence"
        elif lead.routing == LeadRouting.HOLD:
            lead.filter_priority = "medium"
            lead.filter_justification = "Valid lead requiring additional verification"
        elif lead.routing == LeadRouting.RETRY:
            lead.filter_priority = "medium"
            lead.filter_justification = "Technical issue - retry needed"
        else:
            lead.filter_priority = "reject"
        
        # Filter reasoning
        lead.filter_reasoning = self._build_filter_reasoning(lead)
        
        # Qualification score - Dynamic calculation based on actual lead characteristics
        # No rounding, no static weights - purely based on real data
        
        # Start with confidence as the base (most important factor)
        score = lead.confidence
        
        # Adjust based on service fit (direct impact, not averaged)
        # Higher service fit = higher score boost
        if lead.service_fit_score >= 8.0:
            score *= 1.15  # 15% boost for strong fit
        elif lead.service_fit_score >= 6.0:
            score *= 1.08  # 8% boost for good fit
        elif lead.service_fit_score >= 4.0:
            score *= 1.0   # Neutral for moderate fit
        else:
            score *= 0.92  # 8% penalty for weak fit
        
        # Adjust based on online presence (inverse - lower presence = better opportunity)
        if lead.online_presence_score <= 3.0:
            score *= 1.12  # 12% boost for very low presence (big opportunity!)
        elif lead.online_presence_score <= 5.0:
            score *= 1.05  # 5% boost for low presence
        elif lead.online_presence_score <= 7.0:
            score *= 1.0   # Neutral for moderate presence
        else:
            score *= 0.95  # 5% penalty for high presence (less opportunity)
        
        # Adjust based on evidence depth (more evidence = more confidence)
        evidence_count = len(lead.evidence)
        if evidence_count >= 10:
            score *= 1.10  # 10% boost for lots of evidence
        elif evidence_count >= 7:
            score *= 1.05  # 5% boost for good evidence
        elif evidence_count >= 5:
            score *= 1.02  # 2% boost for decent evidence
        elif evidence_count < 3:
            score *= 0.95  # 5% penalty for weak evidence
        
        # Adjust based on pain points (specific problems = better lead)
        pain_count = len(lead.pain_points)
        if pain_count >= 3:
            score *= 1.08  # 8% boost for multiple pain points
        elif pain_count >= 2:
            score *= 1.04  # 4% boost for some pain points
        elif pain_count == 0:
            score *= 0.90  # 10% penalty for no identified pain points
        
        # Clamp to valid range without rounding
        lead.qualification_score = max(0.0, min(score, 1.0))
        
        logger.debug(
            "Qualification score for %s: %.4f (confidence=%.2f, service_fit=%.1f, presence=%.1f, evidence=%d, pains=%d)",
            lead.business_name,
            lead.qualification_score,
            lead.confidence,
            lead.service_fit_score,
            lead.online_presence_score,
            len(lead.evidence),
            len(lead.pain_points),
        )
        
        # Service recommendations
        lead.filter_recommended = self._recommend_services(lead, campaign)
        
        return lead
    
    def _build_filter_reasoning(self, lead: ClorelLead) -> str:
        """Build detailed filter reasoning paragraph."""
        parts = []
        
        # Business identity
        parts.append(f"{lead.business_name} is a {lead.industry} business")
        
        # Location
        if lead.location.distance_km:
            parts.append(f"located {lead.location.distance_km:.1f}km from search center")
        
        # Digital presence
        if lead.website_status == WebsiteStatus.MISSING:
            parts.append("with no website found")
        elif lead.website_status == WebsiteStatus.ACTIVE:
            parts.append("with an active website")
        
        # Activity
        if lead.demand_signals.review_count:
            if lead.demand_signals.review_count > 100:
                parts.append(f"and high customer activity ({lead.demand_signals.review_count} reviews)")
            else:
                parts.append(f"with {lead.demand_signals.review_count} reviews")
        
        # Service fit
        if lead.service_fit_score >= 7.0:
            parts.append(f"Strong service fit ({lead.service_fit_score:.1f}/10)")
        elif lead.service_fit_score >= 5.0:
            parts.append(f"Moderate service fit ({lead.service_fit_score:.1f}/10)")
        else:
            parts.append(f"Limited service fit ({lead.service_fit_score:.1f}/10)")
        
        # Evidence
        if lead.confidence >= 0.75:
            parts.append(f"with high-confidence evidence ({lead.confidence:.0%})")
        elif lead.confidence >= 0.5:
            parts.append(f"with moderate evidence reliability ({lead.confidence:.0%})")
        else:
            parts.append(f"but limited evidence ({lead.confidence:.0%})")
        
        return ". ".join(parts) + "."
    
    def _recommend_services(self, lead: ClorelLead, campaign: dict) -> List[str]:
        """Recommend applicable services based on evidence."""
        recommendations = []
        
        # Website
        if lead.website_status == WebsiteStatus.MISSING:
            if lead.search_intent.primary in [
                SearchIntent.ORDERING,
                SearchIntent.BOOKING,
                SearchIntent.RESERVATION,
            ]:
                recommendations.append("website")
        
        # SEO
        if lead.digital_presence.website:
            recommendations.append("seo")
        
        # WhatsApp bot
        if any("whatsapp" in text.lower() for text in lead.evidence):
            recommendations.append("whatsapp_bot")
        
        return recommendations
    
    async def qualify_batch(
        self,
        leads_data: List[dict],
        campaign: dict,
    ) -> List[ClorelLead]:
        """
        Qualify multiple leads in batch.
        
        Returns leads sorted by routing priority and confidence.
        """
        qualified_leads = []
        
        for lead_data in leads_data:
            try:
                qualified = await self.qualify(lead_data, campaign)
                qualified_leads.append(qualified)
            except Exception as exc:
                logger.error(
                    "Failed to qualify lead %s: %s",
                    lead_data.get("business_name", "unknown"),
                    exc,
                )
        
        # Sort: sales_review first, then hold, then retry, reject last
        # Within each routing tier, sort by confidence desc
        routing_priority = {
            LeadRouting.SALES_REVIEW: 0,
            LeadRouting.HOLD: 1,
            LeadRouting.RETRY: 2,
            LeadRouting.REJECT: 3,
        }
        
        qualified_leads.sort(
            key=lambda l: (routing_priority[l.routing], -l.confidence)
        )
        
        return qualified_leads
