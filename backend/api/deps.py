"""
api/deps.py
-----------
Shared application state:
  - In-memory job registry  (job_id → JobRecord)
  - Scheduler singleton     (LeadScheduler, started non-blocking on app startup)
  - Helper to read persisted leads from leads_output/
"""

from __future__ import annotations

import glob
import json
import os
import uuid
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional

from automation.scheduler import LeadScheduler


# ── Job record ───────────────────────────────────────────────────────────────

class JobStatus(str, Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    DONE     = "done"
    FAILED   = "failed"


class JobRecord:
    """Live state for a single automation run."""

    def __init__(self, job_id: str, service: Optional[str], min_score: float):
        self.job_id      = job_id
        self.service     = service          # None → all three
        self.min_score   = min_score
        self.status      = JobStatus.PENDING
        self.started_at  = datetime.utcnow().isoformat()
        self.finished_at: Optional[str] = None
        self.progress    = 0                # 0-100
        self.log_lines: List[str] = []
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id":      self.job_id,
            "service":     self.service,
            "min_score":   self.min_score,
            "status":      self.status,
            "started_at":  self.started_at,
            "finished_at": self.finished_at,
            "progress":    self.progress,
            "log_lines":   self.log_lines[-50:],   # last 50 lines
            "result":      self.result,
            "error":       self.error,
        }


# ── Registry (process-global singleton) ─────────────────────────────────────

_registry: Dict[str, JobRecord] = {}
_registry_lock = Lock()


def create_job(service: Optional[str], min_score: float) -> JobRecord:
    job = JobRecord(str(uuid.uuid4()), service, min_score)
    with _registry_lock:
        _registry[job.job_id] = job
    return job


def get_job(job_id: str) -> Optional[JobRecord]:
    return _registry.get(job_id)


def list_jobs() -> List[Dict[str, Any]]:
    with _registry_lock:
        return [j.to_dict() for j in _registry.values()]


# ── Scheduler singleton ──────────────────────────────────────────────────────

_scheduler: Optional[LeadScheduler] = None


def get_scheduler() -> LeadScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = LeadScheduler(min_score=0.5, output_dir="leads_output")
    return _scheduler


# ── Lead persistence helpers ─────────────────────────────────────────────────

LEADS_DIR = os.getenv("LEADS_OUTPUT_DIR", "leads_output")


def _all_lead_files() -> List[str]:
    """Return leads_*.json files sorted newest-first."""
    pattern = os.path.join(LEADS_DIR, "leads_*.json")
    return sorted(glob.glob(pattern), reverse=True)


def load_all_leads() -> List[Dict[str, Any]]:
    """
    Read every leads_*.json from LEADS_DIR and return a deduplicated
    flat list, sorted by qualification_score desc.
    """
    seen_ids: set = set()
    leads: List[Dict[str, Any]] = []

    for path in _all_lead_files():
        try:
            with open(path, encoding="utf-8") as f:
                batch = json.load(f)
            if isinstance(batch, list):
                for lead in batch:
                    lid = lead.get("id")
                    if lid and lid not in seen_ids:
                        seen_ids.add(lid)
                        leads.append(lead)
        except Exception:
            pass  # skip corrupt files

    leads.sort(key=lambda l: l.get("qualification_score", 0), reverse=True)
    return leads


def update_lead_field(lead_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Patch fields (e.g. outreach_sent=True) in whichever leads_*.json
    file contains the given lead_id.  Returns the updated lead or None.
    """
    for path in _all_lead_files():
        try:
            with open(path, encoding="utf-8") as f:
                batch: List[Dict] = json.load(f)
        except Exception:
            continue

        for lead in batch:
            if lead.get("id") == lead_id:
                lead.update(fields)
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(batch, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass
                return lead

    return None
