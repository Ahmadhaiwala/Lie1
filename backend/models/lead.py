"""
Lead Data Models with CLOREL Verification Fields
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    """Lead lifecycle status"""
    DISCOVERED = "discovered"
    VERIFIED = "verified"
    IN_REVIEW = "in_review"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    REJECTED = "rejected"


class Lead(BaseModel):
    """Lead entity - qualified business opportunity with CLOREL verification"""
    id: Optional[str] = None
    
    # Core lead info
    business_name: str
    service_needed: str  # "website" | "whatsapp_bot" | "seo"
    
    # Contact info
    contact_email: List[str] = Field(default_factory=list)
    contact_phone: List[str] = Field(default_factory=list)
    website: Optional[str] = None
    
    # Business context
    location: Optional[str] = None
    industry: Optional[str] = None
    
    # Lead qualification
    qualification_score: float = Field(ge=0.0, le=1.0, default=0.5)  # 0.0-1.0
    pain_points: List[str] = Field(default_factory=list)
    raw_snippet: Optional[str] = None
    
    # Filtering & priority
    filter_priority: str = "unfiltered"  # "high" | "medium" | "discard" | "unfiltered"
    filter_justification: Optional[str] = None
    filter_reasoning: Optional[str] = None
    filter_online_score: float = -1.0  # 0-10, -1 = not evaluated
    filter_suitability_score: float = -1.0  # 0-10, -1 = not evaluated
    filter_recommended: List[str] = Field(default_factory=list)
    
    # CLOREL Verification Fields
    route: Optional[str] = None  # "sales_review" | "future_opportunity" | "hold_uncertain" | "suppress"
    route_reason: Optional[str] = None
    verification_score: float = Field(ge=0.0, le=1.0, default=0.0)  # Overall confidence
    evidence_count: int = 0
    last_verified: Optional[datetime] = None
    
    # Digital presence verification
    website_status: Optional[str] = None  # "active" | "url_missing" | "crawl_failed" | "unverified"
    has_booking: bool = False
    has_social: bool = False
    alternative_channels: Dict[str, str] = Field(default_factory=dict)
    
    # Outreach tracking
    outreach_sent: bool = False
    outreach_message: Optional[str] = None
    outreach_timestamp: Optional[datetime] = None
    
    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    source_id: Optional[str] = None
    campaign_id: Optional[str] = None
    
    # Custom notes
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "lead_123",
                "business_name": "Ahmed's Restaurant",
                "service_needed": "website",
                "contact_phone": ["+92-300-1234567"],
                "website": None,
                "location": "Ahmedabad",
                "industry": "Food & Beverage",
                "qualification_score": 0.85,
                "route": "sales_review",
                "route_reason": "Website missing, local search intent high, booking opportunity clear",
                "verification_score": 0.82,
                "filter_priority": "high",
                "website_status": "url_missing",
                "has_booking": False
            }
        }
