"""
Evidence & Verification Models

Implements the CLOREL evidence tracking system:
- Separate facts from assumptions
- Track source, timestamp, and confidence
- Maintain audit trail for all decisions
- Enable transparent reasoning for lead qualification
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EvidenceType(str, Enum):
    """Types of evidence collected"""
    IDENTITY = "identity"  # Name/location/category match
    DIGITAL_PRESENCE = "digital_presence"  # Website, booking, social
    SEARCH_INTENT = "search_intent"  # Local/booking/informational intent
    BUSINESS_CONTEXT = "business_context"  # Hours, reviews, rating
    SERVICE_FIT = "service_fit"  # Service-specific opportunity
    DEMAND_SIGNAL = "demand_signal"  # Search volume/trends
    CAPABILITY = "capability"  # Website/platform capability check


class FactOrAssumption(str, Enum):
    """Distinguish facts from assumptions"""
    FACT = "fact"  # Observed, verified, sourced
    ASSUMPTION = "assumption"  # Inferred, not directly verified
    UNCERTAIN = "uncertain"  # Data unavailable, crawl failed, etc.


class Evidence(BaseModel):
    """Single piece of evidence backing a lead qualification"""
    id: Optional[str] = None
    
    # Core fields
    claim: str  # What is being claimed (e.g., "Website is active with booking capability")
    fact_vs_assumption: FactOrAssumption  # Is this a fact or assumption?
    evidence_type: EvidenceType  # Category of evidence
    
    # Source tracking
    source: str  # Where did this come from? (e.g., "google_maps", "crawl", "serp")
    source_url: Optional[str] = None  # Provider/API that provided this evidence
    provider_record_id: Optional[str] = None  # ID from the source provider
    
    # Timing
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # When evidence becomes stale
    
    # Quality
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)  # 0.0-1.0 confidence score
    reason_for_uncertainty: Optional[str] = None  # Why uncertain? (timeout, crawl failed, etc.)
    
    # Relationships
    business_id: Optional[str] = None
    lead_id: Optional[str] = None
    campaign_id: Optional[str] = None
    
    # Additional context
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Extra data (e.g., crawl_time_ms)
    
    class Config:
        json_schema_extra = {
            "example": {
                "claim": "Website is accessible with booking capability",
                "fact_vs_assumption": "fact",
                "evidence_type": "digital_presence",
                "source": "playwright_crawl",
                "source_url": "https://businesswebsite.com",
                "observed_at": "2026-09-20T15:30:00Z",
                "confidence": 0.95,
                "metadata": {"crawl_time_ms": 2345, "has_booking_link": True}
            }
        }


class VerificationGate(str, Enum):
    """Verification gates that leads must pass"""
    IDENTITY = "identity"  # name/location/category match
    DIGITAL = "digital"  # website + alternatives checked or explicitly unknown
    SERVICE_FIT = "service_fit"  # credible service-relevant evidence
    CONFIDENCE = "confidence"  # strong/recent/consistent evidence


class GateResult(BaseModel):
    """Result of a verification gate check"""
    gate: VerificationGate
    passed: bool
    score: float = Field(ge=0.0, le=1.0)  # 0.0-1.0
    reason: str  # Why passed/failed?
    supporting_evidence: List[str] = Field(default_factory=list)  # Evidence IDs supporting this
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class WebsiteStatus(str, Enum):
    """Website status classification"""
    ACTIVE = "active"  # Accessible with relevant content
    URL_MISSING = "url_missing"  # No URL found in listing
    CRAWL_FAILED = "crawl_failed"  # Timeout, CAPTCHA, 403/429, DNS error, etc.
    UNVERIFIED = "unverified"  # Dead domain after repeated checks
    NOT_FOUND = "not_found"  # Not found across defined sources


class DigitalPresenceCheck(BaseModel):
    """Result of checking digital presence"""
    website_status: WebsiteStatus
    website_url: Optional[str] = None
    has_booking: bool = False  # Third-party booking/order found
    has_social: bool = False  # Social media profiles found
    has_marketplace: bool = False  # Listed on marketplace (Uber, DoorDash, etc.)
    
    # Crawl details
    crawl_attempted: bool = True
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow)
    crawl_confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    crawl_error: Optional[str] = None  # e.g., "timeout", "403_forbidden", "dns_error"
    
    # Alternative channels
    alternative_channels: Dict[str, str] = Field(default_factory=dict)  # e.g., {"booking": "https://...", "social": "https://..."}
    
    # Metadata
    check_reason: Optional[str] = None  # Why was this checked?
    notes: Optional[str] = None


class Route(str, Enum):
    """Where a lead is routed after verification"""
    SALES_REVIEW = "sales_review"  # Evidence threshold met, ready for sales review
    FUTURE_OPPORTUNITY = "future_opportunity"  # Some fit signals but insufficient evidence
    HOLD_UNCERTAIN = "hold_uncertain"  # Missing/conflicting/stale data, needs follow-up
    SUPPRESS_DEPRIORITIZE = "suppress_deprioritize"  # Hard mismatch, duplicate, exclusion


class VerificationResult(BaseModel):
    """Complete verification result for a lead"""
    id: Optional[str] = None
    lead_id: Optional[str] = None
    campaign_id: Optional[str] = None
    
    # Verification results
    route: Route
    routing_reason: str  # Why this route?
    gate_results: List[GateResult] = Field(default_factory=list)
    
    # Evidence summary
    all_evidence: List[Evidence] = Field(default_factory=list)
    evidence_count: int = 0
    weak_evidence_count: int = 0  # confidence < 0.7
    stale_evidence_count: int = 0  # observed > 7 days ago
    conflicting_evidence: bool = False
    
    # Scoring
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    service_fit_confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    digital_gap_confidence: float = Field(ge=0.0, le=1.0, default=0.5)  # How confident about digital gap?
    
    # Verification metadata
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    heuristic_version: str = "1.0"  # For audit trail
    last_human_review: Optional[datetime] = None
    review_notes: Optional[str] = None
    
    # Audit trail
    reviewed_by: Optional[str] = None  # Human reviewer ID
    review_decision: Optional[str] = None  # approve, reject, future, hold
    review_timestamp: Optional[datetime] = None
    reviewer_edits: Dict[str, Any] = Field(default_factory=dict)  # Fields corrected by reviewer


class CampaignFilter(BaseModel):
    """Campaign-level filters for lead qualification"""
    # Required filters
    city: str
    service_area: Optional[str] = None
    category: str  # Business category
    upstkey_service: str  # Which Upstkey service (website, booking, seo, etc.)
    
    # Optional hard filters
    minimum_rating: Optional[float] = None  # e.g., 4.0+
    minimum_review_count: Optional[int] = None  # e.g., 10+ reviews
    
    # Goals, not quotas
    target_qualified_leads: int = 50  # Target, not minimum
    
    # Optional soft filters
    search_intent: Optional[str] = None  # local, booking, informational
    search_volume_window: Optional[str] = None  # e.g., "last_30_days"
    confidence_threshold: Optional[float] = None  # Minimum confidence to pass
    
    # Context
    campaign_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(BaseModel):
    """Audit trail for all verification decisions"""
    id: Optional[str] = None
    lead_id: str
    campaign_id: str
    
    # Action
    action: str  # "verified", "routed", "reviewed", "corrected"
    actor: str  # "system", "reviewer_name", "algorithm_v1"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Details
    details: Dict[str, Any]  # e.g., {"previous_route": "hold", "new_route": "sales_review", "reason": "..."}
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "lead_123",
                "campaign_id": "campaign_456",
                "action": "reviewed",
                "actor": "reviewer_jane",
                "timestamp": "2026-09-20T15:30:00Z",
                "details": {
                    "previous_route": "hold_uncertain",
                    "new_route": "sales_review",
                    "reason": "Verified website booking capability via phone"
                }
            }
        }
