"""
Automation Package for Lead Generation

This package automates finding, qualifying, and reaching out to
potential customers who need:
- Website development
- WhatsApp bots
- SEO services
"""

from automation.scheduler import LeadScheduler
from automation.workflows import LeadWorkflow, LeadQualifier
from automation.jobs import (
    WebsiteLeadJob,
    WhatsAppBotLeadJob,
    SEOLeadJob,
    JobRunner,
)

__all__ = [
    "LeadScheduler",
    "LeadWorkflow",
    "LeadQualifier",
    "WebsiteLeadJob",
    "WhatsAppBotLeadJob",
    "SEOLeadJob",
    "JobRunner",
]
