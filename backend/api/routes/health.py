"""GET /health — liveness probe"""
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "LeadBot AI API",
        "version": "1.0.0",
    }
