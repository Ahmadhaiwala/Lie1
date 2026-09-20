"""
Contact endpoints
  POST /contact  receive contact form submissions (store to JSON or DB)
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contact", tags=["contact"])

# ── Schema ────────────────────────────────────────────────────────────────────

class ContactMessage(BaseModel):
    name:    str
    email:   EmailStr
    service: str        # "Website Development" | "WhatsApp Bot" | "SEO Services" | "All Three"
    message: str = ""


# ── Storage ───────────────────────────────────────────────────────────────────

CONTACT_DIR = Path("contact_submissions")
CONTACT_DIR.mkdir(exist_ok=True)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("", status_code=200)
async def submit_contact(body: ContactMessage):
    """
    Receive a contact form submission.
    Stores it as JSON in contact_submissions/{timestamp}_{email}.json
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{body.email.replace('@', '_at_')}.json"
        filepath = CONTACT_DIR / filename

        data = {
            "timestamp": timestamp,
            "name":      body.name,
            "email":     body.email,
            "service":   body.service,
            "message":   body.message,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Contact submission saved: {filename}")

        return {
            "status":  "received",
            "message": f"Thank you {body.name}! We'll reach out to {body.email} within 24 hours.",
        }

    except Exception as exc:
        logger.exception("Failed to save contact submission")
        raise HTTPException(status_code=500, detail=str(exc))
