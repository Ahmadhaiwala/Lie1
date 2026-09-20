"""
Business Data Models
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BusinessStatus(str, Enum):
    """Business discovery status"""
    DISCOVERED = "discovered"
    VALIDATED = "validated"
    ENRICHED = "enriched"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"


class BusinessLocation(BaseModel):
    """Business location information"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None  # Distance from search center
    is_primary: bool = True


class BusinessContact(BaseModel):
    """Business contact information"""
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None
    social_media: Dict[str, str] = Field(default_factory=dict)
    contact_form_url: Optional[str] = None


class Business(BaseModel):
    """Core business entity"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    
    # Contact & Location
    contact: BusinessContact
    locations: List[BusinessLocation] = Field(default_factory=list)
    
    # Metadata
    status: BusinessStatus = BusinessStatus.DISCOVERED
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Discovery source
    source: Optional[str] = None  # e.g., "google_maps", "yelp", "manual"
    source_id: Optional[str] = None
    
    # Enrichment data
    employee_count: Optional[int] = None
    revenue_range: Optional[str] = None
    founded_year: Optional[int] = None
    technologies: List[str] = Field(default_factory=list)
    
    # Flags
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    
    # Custom fields
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Coffee Shop",
                "description": "Local coffee shop serving specialty drinks",
                "industry": "Food & Beverage",
                "contact": {
                    "email": "info@acmecoffee.com",
                    "phone": "+1-555-0123",
                    "website": "https://acmecoffee.com"
                },
                "locations": [{
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "USA"
                }]
            }
        }
