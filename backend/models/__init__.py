"""
Data Models
"""
from .business import Business, BusinessLocation, BusinessContact
from .search_intent import SearchIntent, SearchQuery
from .research_job import ResearchJob, ResearchTask
from .crawl import CrawlJob, CrawlResult, CrawlStatus
from .evidence import Evidence, EvidenceType, EvidenceScore
from .opportunity import Opportunity, OpportunityType, OpportunityScore

__all__ = [
    'Business',
    'BusinessLocation',
    'BusinessContact',
    'SearchIntent',
    'SearchQuery',
    'ResearchJob',
    'ResearchTask',
    'CrawlJob',
    'CrawlResult',
    'CrawlStatus',
    'Evidence',
    'EvidenceType',
    'EvidenceScore',
    'Opportunity',
    'OpportunityType',
    'OpportunityScore',
]
