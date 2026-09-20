"""
filters/
--------
Business filter layer — sits between lead qualification and outreach composition.

Pipeline position:
    discover → qualify → [FILTER] → compose → save

Exports:
    BusinessFilter   – main class: evaluates online presence + business model
    FilterResult     – result dataclass with priority + justification
    FilterPriority   – enum: HIGH | MEDIUM | DISCARD
"""

from filters.business_filter import BusinessFilter, FilterResult, FilterPriority

__all__ = ["BusinessFilter", "FilterResult", "FilterPriority"]
