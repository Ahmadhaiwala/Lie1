"""
Jobs endpoints
  POST /jobs/run              trigger a lead generation run (background task)
  GET  /jobs                  list all job records
  GET  /jobs/{id}/status      real-time status of a single job
  POST /jobs/schedule         configure recurring APScheduler trigger
"""
import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from api.deps import (
    JobStatus,
    create_job,
    get_job,
    get_scheduler,
    list_jobs,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


# ── Request / response schemas ────────────────────────────────────────────────

class RunRequest(BaseModel):
    service:   Optional[str] = Field(None, description="website | whatsapp_bot | seo | null = all")
    min_score: float          = Field(0.5,  ge=0.0, le=1.0)
    services:  Optional[List[str]] = Field(None, description="run multiple services")
    keywords:  List[str] = Field(default_factory=list, max_length=10, description="Optional custom business-search terms")


class ScheduleRequest(BaseModel):
    mode:         str          = Field(..., description="daily | weekly | interval | cron")
    hour:         Optional[int] = None
    minute:       Optional[int] = None
    day_of_week:  Optional[str] = None   # for weekly: mon, tue …
    hours:        Optional[int] = None   # for interval
    cron_expr:    Optional[str] = None   # raw cron e.g. "0 9 * * *"
    service:      Optional[str] = None
    min_score:    float         = 0.5


# ── Background task ───────────────────────────────────────────────────────────

async def _run_job_background(
    job_id: str, service: Optional[str], min_score: float, keywords: List[str]
):
    """Runs in background; updates the JobRecord throughout."""
    from automation.workflows import LeadWorkflow
    from crawler.config import CrawlerConfig
    from llm.llm_config import LLMConfig

    job = get_job(job_id)
    if not job:
        return

    job.status   = JobStatus.RUNNING
    job.progress = 5
    job.log_lines.append("[INFO] Starting LeadWorkflow…")

    try:
        # Intercept log lines by patching the workflow logger
        import logging as _log

        class _LineCapture(_log.Handler):
            def emit(self, record):
                job.log_lines.append(self.format(record))
                # Update progress heuristically
                msg = record.getMessage()
                if "Discovery complete" in msg:
                    job.progress = 40
                elif "After qualification" in msg:
                    job.progress = 65
                elif "Outreach composed" in msg:
                    job.progress = 85
                elif "WORKFLOW COMPLETE" in msg or "Saved" in msg:
                    job.progress = 95

        handler = _LineCapture()
        handler.setFormatter(_log.Formatter("%(asctime)s [%(levelname)s] %(name)s – %(message)s"))
        _log.getLogger("automation").addHandler(handler)
        _log.getLogger("automation").setLevel(_log.INFO)

        workflow = LeadWorkflow(
            crawler_config=CrawlerConfig(headless=True, page_timeout=25000),
            llm_config=LLMConfig.from_env(),
            min_score=min_score,
            output_dir="leads_output",
            search_queries=keywords,
        )

        report = await workflow.run(service=service)

        _log.getLogger("automation").removeHandler(handler)

        job.result      = report["summary"]
        job.status      = JobStatus.DONE
        job.progress    = 100
        job.log_lines.append(
            f"[SUCCESS] Run complete — "
            f"{report['summary']['qualified_leads']} qualified leads, "
            f"{report['summary']['hot_leads']} hot"
        )

    except Exception as exc:
        logger.exception("Background job %s failed", job_id)
        job.status   = JobStatus.FAILED
        job.error    = str(exc)
        job.log_lines.append(f"[ERROR] {exc}")
    finally:
        from datetime import datetime
        job.finished_at = datetime.utcnow().isoformat()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/run", status_code=202)
async def run_jobs(body: RunRequest, background_tasks: BackgroundTasks):
    """
    Trigger a lead generation run.
    Returns immediately with a job_id; poll /jobs/{job_id}/status for progress.
    """
    # Resolve service: explicit single > list > None (all)
    service = body.service
    if not service and body.services and len(body.services) == 1:
        service = body.services[0]
    elif not service and body.services and len(body.services) > 1:
        service = None   # run all; individual service filtering not supported in one call

    keywords = list(dict.fromkeys(
        keyword.strip() for keyword in body.keywords if keyword.strip()
    ))
    if any(len(keyword) > 160 for keyword in keywords):
        raise HTTPException(422, "Each keyword must be 160 characters or fewer")

    job = create_job(service, body.min_score)
    background_tasks.add_task(
        _run_job_background, job.job_id, service, body.min_score, keywords
    )
    return {
        "job_id":  job.job_id,
        "status":  job.status,
        "message": "Job queued — poll /jobs/{job_id}/status for live updates",
    }


@router.get("")
async def list_all_jobs():
    """Return all job records (newest first by started_at)."""
    jobs = list_jobs()
    jobs.sort(key=lambda j: j.get("started_at", ""), reverse=True)
    return jobs


@router.get("/{job_id}/status")
async def job_status(job_id: str):
    """Return the current state of a job (status, progress, log_lines, result)."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found. Job status is kept in memory and is cleared when the backend restarts.",
        )
    return job.to_dict()


@router.post("/schedule", status_code=200)
async def schedule_jobs(body: ScheduleRequest):
    """Configure a recurring APScheduler trigger."""
    sched = get_scheduler()
    sched.service   = body.service
    sched.min_score = body.min_score

    if body.mode == "daily":
        h = body.hour   if body.hour   is not None else 9
        m = body.minute if body.minute is not None else 0
        sched.add_daily_job(hour=h, minute=m)
        return {"message": f"Daily job scheduled at {h:02d}:{m:02d}"}

    if body.mode == "weekly":
        dow = body.day_of_week or "mon"
        h   = body.hour   if body.hour   is not None else 8
        m   = body.minute if body.minute is not None else 0
        sched.add_weekly_job(day_of_week=dow, hour=h, minute=m)
        return {"message": f"Weekly job scheduled on {dow} at {h:02d}:{m:02d}"}

    if body.mode == "interval":
        hrs = body.hours or 6
        sched.add_interval_job(hours=hrs)
        return {"message": f"Interval job scheduled every {hrs} hours"}

    if body.mode == "cron":
        if not body.cron_expr:
            raise HTTPException(400, "cron_expr required for mode=cron")
        sched.add_custom_cron(body.cron_expr)
        return {"message": f"Custom cron job scheduled: {body.cron_expr}"}

    raise HTTPException(400, f"Unknown mode '{body.mode}'. Use daily|weekly|interval|cron")
