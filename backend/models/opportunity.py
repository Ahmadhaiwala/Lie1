"""
Opportunity Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class OpportunityType(str, Enum):
    """Type of sales opportunity"""
    ECOMMERCE_UPGRADE = "ecommerce_upgrade"
    BOOKING_SYSTEM = "booking_system"
    CRM_IMPLEMENTATION = "crm_implementation"
    MARKETING_AUTOMATION = "marketing_automation"
    WEBSITE_REBUILD = "website_rebuild"
    SEO_OPTIMIZATION = "seo_optimization"
    PAYMENT_INTEGRATION = "payment_integration"
    ANALYTICS_SETUP = "analytics_setup"
    CUSTOM_DEVELOPMENT = "custom_development"
    OTHER = "other"


class OpportunityStage(str, Enum):
    """Sales stage"""
    IDENTIFIED = "identified"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    IN_DISCUSSION = "in_discussion"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"


class OpportunityScore(BaseModel):
    """Opportunity scoring"""
    fit_score: float = Field(ge=0.0, le=100.0)  # How well they fit ICP
    urgency_score: float = Field(ge=0.0, le=100.0)  # How urgent the need is
    value_score: float = Field(ge=0.0, le=100.0)  # Potential deal value
    
    @property
    def overall_score(self) -> float:
        """Calculate overall opportunity score"""
        return (self.fit_score + self.urgency_score + self.value_score) / 3.0


class Opportunity(BaseModel):
    """Sales opportunity"""
    id: Optional[str] = None
    business_id: str
    
    # Opportunity details
    opportunity_type: OpportunityType
    title: str
    description: str
    
    # Scoring
    score: OpportunityScore
    
    # Supporting evidence
    evidence_ids: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    value_proposition: Optional[str] = None
    
    # Sales info
    stage: OpportunityStage = OpportunityStage.IDENTIFIED
    estimated_value: Optional[float] = None
    probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Timing
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    qualified_at: Optional[datetime] = None
    expected_close_date: Optional[datetime] = None
    
    # Outreach
    outreach_message: Optional[str] = None
    outreach_subject: Optional[str] = None
    outreach_sent_at: Optional[datetime] = None
    
    # Response tracking
    response_received: bool = False
    response_date: Optional[datetime] = None
    
    # Assignment
    assigned_to: Optional[str] = None
    
    # Notes
    notes: List[str] = Field(default_factory=list)
    
    # Custom data
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "biz_123",
                "opportunity_type": "ecommerce_upgrade",
                "title": "Shopify to Custom Solution Migration",
                "description": "Business using basic Shopify plan, could benefit from custom solution",
                "score": {
                    "fit_score": 85.0,
                    "urgency_score": 60.0,
                    "value_score": 75.0
                },
                "pain_points": [
                    "Limited customization options",
                    "High monthly fees",
                    "Scalability concerns"
                ],
                "estimated_value": 25000.0
            }
        }
