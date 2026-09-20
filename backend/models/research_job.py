"""
Research Job Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Research job status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Type of research task"""
    DISCOVER_BUSINESSES = "discover_businesses"
    RESOLVE_WEBSITE = "resolve_website"
    CRAWL_WEBSITE = "crawl_website"
    EXTRACT_EVIDENCE = "extract_evidence"
    QUALIFY_LEAD = "qualify_lead"
    GENERATE_OUTREACH = "generate_outreach"


class ResearchTask(BaseModel):
    """Individual research task"""
    id: Optional[str] = None
    job_id: str
    task_type: TaskType
    
    # Input/Output
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    status: JobStatus = JobStatus.PENDING
    error_message: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3


class ResearchJob(BaseModel):
    """Main research job orchestrating multiple tasks"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    
    # Search parameters
    search_intent: Dict[str, Any]  # SearchIntent as dict
    
    # Tasks
    tasks: List[ResearchTask] = Field(default_factory=list)
    
    # Status
    status: JobStatus = JobStatus.PENDING
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Results
    businesses_discovered: int = 0
    businesses_qualified: int = 0
    opportunities_found: int = 0
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # User/Owner
    user_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "SF Coffee Shops Research",
                "description": "Discover coffee shops in San Francisco",
                "search_intent": {
                    "raw_input": "coffee shops in San Francisco",
                    "industry": "Food & Beverage",
                    "location": "San Francisco, CA"
                },
                "status": "pending"
            }
        }
