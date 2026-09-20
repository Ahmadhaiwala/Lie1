"""
Search Intent Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    """Type of search to perform"""
    BUSINESS_NAME = "business_name"
    INDUSTRY = "industry"
    LOCATION = "location"
    KEYWORD = "keyword"
    COMBINED = "combined"


class SearchQuery(BaseModel):
    """Individual search query"""
    query: str
    search_type: SearchType
    location: Optional[str] = None
    radius_miles: Optional[int] = None
    max_results: int = 20


class SearchIntent(BaseModel):
    """Parsed search intent with multiple query strategies"""
    id: Optional[str] = None
    
    # Original input
    raw_input: str
    
    # Parsed components
    industry: Optional[str] = None
    location: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    business_size: Optional[str] = None  # "small", "medium", "large"
    
    # Generated queries
    queries: List[SearchQuery] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Filters
    filters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_input": "coffee shops in San Francisco",
                "industry": "Food & Beverage",
                "location": "San Francisco, CA",
                "keywords": ["coffee", "cafe"],
                "queries": [
                    {
                        "query": "coffee shops San Francisco",
                        "search_type": "combined",
                        "location": "San Francisco, CA",
                        "max_results": 20
                    }
                ]
            }
        }
