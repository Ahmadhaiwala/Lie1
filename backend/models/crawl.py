"""
Crawl Job Models
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CrawlStatus(str, Enum):
    """Crawl job status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


class CrawlPriority(str, Enum):
    """Crawl priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CrawlResult(BaseModel):
    """Result from a crawl operation"""
    url: str
    status_code: Optional[int] = None
    success: bool
    
    # Content
    html: Optional[str] = None
    markdown: Optional[str] = None
    cleaned_html: Optional[str] = None
    
    # Extracted data
    title: Optional[str] = None
    meta_description: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    
    # Metadata
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0


class CrawlJob(BaseModel):
    """Crawl job for a business website"""
    id: Optional[str] = None
    business_id: str
    
    # URLs to crawl
    seed_url: HttpUrl
    discovered_urls: List[str] = Field(default_factory=list)
    crawled_urls: List[str] = Field(default_factory=list)
    failed_urls: List[str] = Field(default_factory=list)
    
    # Configuration
    max_pages: int = 10
    max_depth: int = 2
    respect_robots_txt: bool = True
    priority: CrawlPriority = CrawlPriority.NORMAL
    
    # Status
    status: CrawlStatus = CrawlStatus.PENDING
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Results
    results: List[CrawlResult] = Field(default_factory=list)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Policies
    crawl_policies: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "biz_123",
                "seed_url": "https://example.com",
                "max_pages": 10,
                "max_depth": 2,
                "status": "pending"
            }
        }
