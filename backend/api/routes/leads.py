"""
Leads endpoints
  GET  /leads              list all leads (filter + sort + priority)
  GET  /leads/stats        aggregate stats including priority breakdown
  GET  /leads/{id}         get single lead
  PATCH /leads/{id}        update fields (e.g. mark outreach sent)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.deps import load_all_leads, update_lead_field

router = APIRouter(prefix="/leads", tags=["leads"])

VALID_PRIORITIES = {"high", "medium", "discard", "unfiltered"}
VALID_TIERS      = {"hot", "warm", "cold"}
VALID_SERVICES   = {"website", "whatsapp_bot", "seo"}


class LeadPatch(BaseModel):
    outreach_sent:      Optional[bool] = None
    notes:              Optional[str]  = None
    filter_priority:    Optional[str]  = None   # allow manual override


# ── helpers ───────────────────────────────────────────────────────────────────

def _tier(score: float) -> str:
    if score >= 0.8:  return "hot"
    if score >= 0.65: return "warm"
    return "cold"


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[dict])
async def get_leads(
    service:  Optional[str] = Query(None, description="website | whatsapp_bot | seo"),
    tier:     Optional[str] = Query(None, description="hot | warm | cold  (qualification score tier)"),
    priority: Optional[str] = Query(None, description="high | medium | discard | unfiltered"),
    q:        Optional[str] = Query(None, description="Search business name or email"),
    limit:    int            = Query(100, ge=1, le=500),
    offset:   int            = Query(0,   ge=0),
):
    """
    Return leads from persisted leads_output/*.json files.

    New filter: **priority** — based on BusinessFilter evaluation:
      - high     → clear online-presence gap + strong digital service need
      - medium   → some potential, worth reaching out
      - discard  → wrong business type (food stalls, offline-only, etc.)
      - unfiltered → not yet evaluated by BusinessFilter
    """
    leads = load_all_leads()

    if service and service in VALID_SERVICES:
        leads = [l for l in leads if l.get("service_needed") == service]

    if tier and tier in VALID_TIERS:
        leads = [l for l in leads if _tier(l.get("qualification_score", 0)) == tier]

    if priority and priority in VALID_PRIORITIES:
        leads = [l for l in leads if l.get("filter_priority", "unfiltered") == priority]

    if q:
        ql = q.lower()
        leads = [
            l for l in leads
            if ql in l.get("business_name", "").lower()
            or any(ql in e.lower() for e in l.get("contact_email", []))
        ]

    return leads[offset : offset + limit]


@router.get("/stats")
async def get_stats():
    """
    Return aggregate stats including the new priority breakdown.
    """
    leads = load_all_leads()
    total = len(leads)

    # Qualification score tiers
    hot   = sum(1 for l in leads if l.get("qualification_score", 0) >= 0.8)
    warm  = sum(1 for l in leads if 0.65 <= l.get("qualification_score", 0) < 0.8)
    cold  = total - hot - warm
    sent  = sum(1 for l in leads if l.get("outreach_sent"))

    # BusinessFilter priority breakdown
    by_priority = {"high": 0, "medium": 0, "discard": 0, "unfiltered": 0}
    for l in leads:
        p = l.get("filter_priority", "unfiltered")
        by_priority[p] = by_priority.get(p, 0) + 1

    # Service breakdown
    by_service: dict = {}
    for l in leads:
        s = l.get("service_needed", "unknown")
        by_service[s] = by_service.get(s, 0) + 1

    # Average filter scores (only for evaluated leads)
    evaluated = [l for l in leads if l.get("filter_online_score", -1) >= 0]
    avg_online      = round(sum(l["filter_online_score"]      for l in evaluated) / len(evaluated), 1) if evaluated else None
    avg_suitability = round(sum(l["filter_suitability_score"] for l in evaluated) / len(evaluated), 1) if evaluated else None

    return {
        "total":               total,
        "hot":                 hot,
        "warm":                warm,
        "cold":                cold,
        "outreach_sent":       sent,
        "by_service":          by_service,
        "by_priority":         by_priority,
        "avg_online_score":    avg_online,
        "avg_suitability":     avg_suitability,
        "evaluated_count":     len(evaluated),
    }


@router.get("/{lead_id}")
async def get_lead(lead_id: str):
    leads = load_all_leads()
    for l in leads:
        if l.get("id") == lead_id:
            return l
    raise HTTPException(status_code=404, detail="Lead not found")


@router.patch("/{lead_id}")
async def patch_lead(lead_id: str, body: LeadPatch):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    updated = update_lead_field(lead_id, fields)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated
