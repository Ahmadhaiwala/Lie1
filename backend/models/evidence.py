"""
Evidence Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EvidenceType(str, Enum):
    """Type of evidence found"""
    TECHNOLOGY_STACK = "technology_stack"
    ECOMMERCE_PLATFORM = "ecommerce_platform"
    BOOKING_SYSTEM = "booking_system"
    CRM_SYSTEM = "crm_system"
    PAYMENT_PROCESSOR = "payment_processor"
    ANALYTICS_TOOL = "analytics_tool"
    MARKETING_TOOL = "marketing_tool"
    CONTACT_FORM = "contact_form"
    PHONE_NUMBER = "phone_number"
    EMAIL_ADDRESS = "email_address"
    SOCIAL_MEDIA = "social_media"
    JOB_POSTING = "job_posting"
    PAIN_POINT = "pain_point"
    OPPORTUNITY = "opportunity"
    OTHER = "other"


class EvidenceScore(BaseModel):
    """Confidence scoring for evidence"""
    confidence: float = Field(ge=0.0, le=1.0)
    relevance: float = Field(ge=0.0, le=1.0)
    quality: float = Field(ge=0.0, le=1.0)
    
    @property
    def overall_score(self) -> float:
        """Calculate overall score"""
        return (self.confidence + self.relevance + self.quality) / 3.0


class Evidence(BaseModel):
    """Piece of evidence found during research"""
    id: Optional[str] = None
    business_id: str
    crawl_job_id: Optional[str] = None
    
    # Evidence details
    evidence_type: EvidenceType
    title: str
    description: Optional[str] = None
    
    # Source
    source_url: Optional[str] = None
    source_page_title: Optional[str] = None
    context: Optional[str] = None  # Surrounding text/context
    
    # Scoring
    score: EvidenceScore
    
    # Extracted data
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False
    verified_at: Optional[datetime] = None
    
    # Flags
    is_relevant: bool = True
    is_actionable: bool = False
    
    # Tags
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "biz_123",
                "evidence_type": "ecommerce_platform",
                "title": "Using Shopify",
                "description": "Business uses Shopify for e-commerce",
                "source_url": "https://example.com/shop",
                "score": {
                    "confidence": 0.95,
                    "relevance": 0.9,
                    "quality": 0.85
                },
                "extracted_data": {
                    "platform": "Shopify",
                    "version": "2.0"
                }
            }
        }
