"""
Leads endpoints
  GET  /leads              list all leads (filter + sort)
  GET  /leads/{id}         get single lead
  PATCH /leads/{id}        update fields (e.g. mark outreach sent)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.deps import load_all_leads, update_lead_field

router = APIRouter(prefix="/leads", tags=["leads"])


class LeadPatch(BaseModel):
    outreach_sent: Optional[bool] = None
    notes: Optional[str] = None


@router.get("", response_model=List[dict])
async def get_leads(
    service: Optional[str] = Query(None, description="Filter by service: website | whatsapp_bot | seo"),
    tier:    Optional[str] = Query(None, description="Filter by tier: hot | warm | cold"),
    q:       Optional[str] = Query(None, description="Search by business name or email"),
    limit:   int            = Query(100, ge=1, le=500),
    offset:  int            = Query(0,   ge=0),
):
    """
    Return leads from persisted leads_output/*.json files.
    Falls back to an empty list when no runs have been executed yet.
    """
    leads = load_all_leads()

    # ── Filters ──────────────────────────────────────────────────────────────
    if service:
        leads = [l for l in leads if l.get("service_needed") == service]

    if tier:
        def _tier(score: float) -> str:
            if score >= 0.8:  return "hot"
            if score >= 0.65: return "warm"
            return "cold"
        leads = [l for l in leads if _tier(l.get("qualification_score", 0)) == tier]

    if q:
        ql = q.lower()
        leads = [
            l for l in leads
            if ql in l.get("business_name", "").lower()
            or any(ql in e.lower() for e in l.get("contact_email", []))
        ]

    total = len(leads)
    return leads[offset : offset + limit]


@router.get("/stats")
async def get_stats():
    """Return aggregate stats across all leads."""
    leads = load_all_leads()
    total    = len(leads)
    hot      = sum(1 for l in leads if l.get("qualification_score", 0) >= 0.8)
    warm     = sum(1 for l in leads if 0.65 <= l.get("qualification_score", 0) < 0.8)
    cold     = total - hot - warm
    sent     = sum(1 for l in leads if l.get("outreach_sent"))
    by_svc   = {}
    for l in leads:
        s = l.get("service_needed", "unknown")
        by_svc[s] = by_svc.get(s, 0) + 1
    return {
        "total": total,
        "hot": hot,
        "warm": warm,
        "cold": cold,
        "outreach_sent": sent,
        "by_service": by_svc,
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
