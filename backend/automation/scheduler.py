"""
Lead Generation Scheduler

Runs the lead generation workflow on a configurable schedule using APScheduler.
Supports:
  - Cron-based scheduling (daily, weekly, custom)
  - One-shot immediate runs
  - Rotating log files per run
  - Email/webhook notifications on completion (optional)

Quick start (run immediately then on a daily cron):
    python -m automation.scheduler --run-now --daily 09:00

Or import and use programmatically:
    scheduler = LeadScheduler()
    scheduler.add_daily_job(hour=9, minute=0)
    scheduler.start()
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Optional

# APScheduler is a soft dependency – instructions below if not installed
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

from automation.workflows import LeadWorkflow
from crawler.config import CrawlerConfig
from llm.llm_config import LLMConfig

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(LOG_DIR, f"scheduler_{datetime.utcnow().strftime('%Y%m%d')}.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scheduled Task
# ---------------------------------------------------------------------------

async def _run_workflow(
    service: Optional[str] = None,
    min_score: float = 0.5,
    output_dir: str = "leads_output",
) -> None:
    """The async task that APScheduler calls on each trigger."""
    logger.info("=== Scheduled lead run starting (service=%s) ===", service or "all")
    try:
        workflow = LeadWorkflow(
            crawler_config=CrawlerConfig(headless=True, page_timeout=25000),
            llm_config=LLMConfig.from_env(),
            min_score=min_score,
            output_dir=output_dir,
        )
        report = await workflow.run(service=service)
        summary = report["summary"]
        logger.info(
            "=== Run complete: %d qualified leads (%d hot, %d warm) ===",
            summary["qualified_leads"],
            summary["hot_leads"],
            summary["warm_leads"],
        )
        # Optional: notify via webhook
        _notify(summary)
    except Exception as exc:
        logger.exception("Scheduled lead run failed: %s", exc)


def _notify(summary: dict) -> None:
    """
    Send a notification when a run completes.
    Configure NOTIFY_WEBHOOK_URL in .env to enable.
    Set NOTIFY_EMAIL=you@example.com for email (requires smtplib setup).
    """
    webhook_url = os.getenv("NOTIFY_WEBHOOK_URL")
    if webhook_url:
        try:
            import urllib.request, json as _json
            payload = _json.dumps(summary).encode()
            req = urllib.request.Request(
                webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)
            logger.info("Notification sent to webhook.")
        except Exception as exc:
            logger.warning("Webhook notify failed: %s", exc)


# ---------------------------------------------------------------------------
# Scheduler Class
# ---------------------------------------------------------------------------

class LeadScheduler:
    """
    Wraps APScheduler to manage lead generation jobs.

    Example usage:
        scheduler = LeadScheduler()
        scheduler.add_daily_job(hour=9, minute=0)          # every day at 09:00
        scheduler.add_weekly_job(day_of_week="mon", hour=8) # every Monday 08:00
        scheduler.add_interval_job(hours=6)                 # every 6 hours
        scheduler.start()                                   # blocks event loop
    """

    def __init__(
        self,
        service: Optional[str] = None,
        min_score: float = 0.5,
        output_dir: str = "leads_output",
        timezone: str = "UTC",
    ):
        if not APSCHEDULER_AVAILABLE:
            raise RuntimeError(
                "APScheduler is not installed. Run: pip install apscheduler>=3.10.0"
            )
        self.service = service
        self.min_score = min_score
        self.output_dir = output_dir
        self._scheduler = AsyncIOScheduler(timezone=timezone)

    # ------------------------------------------------------------------
    # Job registration helpers
    # ------------------------------------------------------------------

    def _task(self):
        """Return a coroutine for the current config."""
        return _run_workflow(
            service=self.service,
            min_score=self.min_score,
            output_dir=self.output_dir,
        )

    def add_daily_job(self, hour: int = 9, minute: int = 0) -> None:
        """Add a daily cron trigger."""
        self._scheduler.add_job(
            self._task,
            CronTrigger(hour=hour, minute=minute),
            id="daily_lead_run",
            name=f"Daily lead run @ {hour:02d}:{minute:02d}",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info("Scheduled daily lead run at %02d:%02d", hour, minute)

    def add_weekly_job(self, day_of_week: str = "mon", hour: int = 8, minute: int = 0) -> None:
        """Add a weekly cron trigger."""
        self._scheduler.add_job(
            self._task,
            CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
            id="weekly_lead_run",
            name=f"Weekly lead run on {day_of_week} @ {hour:02d}:{minute:02d}",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info("Scheduled weekly lead run on %s at %02d:%02d", day_of_week, hour, minute)

    def add_interval_job(self, hours: int = 12) -> None:
        """Add an interval trigger (every N hours)."""
        self._scheduler.add_job(
            self._task,
            IntervalTrigger(hours=hours),
            id="interval_lead_run",
            name=f"Lead run every {hours}h",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info("Scheduled interval lead run every %d hours", hours)

    def add_custom_cron(self, cron_expression: str) -> None:
        """
        Add a job using a raw cron expression string.
        E.g.: "0 9,17 * * *"  →  9am and 5pm every day
        """
        parts = cron_expression.strip().split()
        if len(parts) != 5:
            raise ValueError("cron_expression must have 5 fields: min hour dom month dow")
        minute, hour, dom, month, dow = parts
        self._scheduler.add_job(
            self._task,
            CronTrigger(minute=minute, hour=hour, day=dom, month=month, day_of_week=dow),
            id="custom_cron_lead_run",
            name=f"Custom cron lead run ({cron_expression})",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info("Scheduled custom cron lead run: %s", cron_expression)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the scheduler and block on the event loop."""
        self._scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler…")
            self._scheduler.shutdown()

    def start_non_blocking(self) -> None:
        """Start the scheduler without blocking (for embedding in larger apps)."""
        self._scheduler.start()
        logger.info("Scheduler started (non-blocking).")

    def stop(self) -> None:
        """Gracefully shut down the scheduler."""
        self._scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")

    async def run_now(self) -> None:
        """Execute the workflow immediately (outside of scheduled triggers)."""
        logger.info("Running lead workflow immediately…")
        await _run_workflow(
            service=self.service,
            min_score=self.min_score,
            output_dir=self.output_dir,
        )


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Lead Generation Scheduler",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--run-now", action="store_true",
        help="Run the workflow immediately without waiting for next schedule",
    )
    parser.add_argument(
        "--service", choices=["website", "whatsapp_bot", "seo"], default=None,
        help="Run only for a specific service (default: all three)",
    )
    parser.add_argument(
        "--daily", metavar="HH:MM", default=None,
        help='Schedule a daily run at given time (e.g. "09:00")',
    )
    parser.add_argument(
        "--weekly", metavar="DAY@HH:MM", default=None,
        help='Schedule a weekly run (e.g. "mon@08:00")',
    )
    parser.add_argument(
        "--every", metavar="HOURS", type=int, default=None,
        help="Schedule a run every N hours",
    )
    parser.add_argument(
        "--cron", metavar="EXPR", default=None,
        help='Raw cron expression (5 fields, e.g. "0 9,17 * * *")',
    )
    parser.add_argument(
        "--min-score", type=float, default=0.5,
        help="Minimum qualification score for leads (default: 0.5)",
    )
    parser.add_argument(
        "--output-dir", default="leads_output",
        help="Directory to save output JSON files (default: leads_output)",
    )
    return parser.parse_args()


async def _main_async(args):
    scheduler = LeadScheduler(
        service=args.service,
        min_score=args.min_score,
        output_dir=args.output_dir,
    )

    # Register schedules
    scheduled = False
    if args.daily:
        h, m = map(int, args.daily.split(":"))
        scheduler.add_daily_job(hour=h, minute=m)
        scheduled = True
    if args.weekly:
        day, time = args.weekly.split("@")
        h, m = map(int, time.split(":"))
        scheduler.add_weekly_job(day_of_week=day, hour=h, minute=m)
        scheduled = True
    if args.every:
        scheduler.add_interval_job(hours=args.every)
        scheduled = True
    if args.cron:
        scheduler.add_custom_cron(args.cron)
        scheduled = True

    # Run immediately if requested
    if args.run_now:
        await scheduler.run_now()

    # Start scheduler if any triggers registered
    if scheduled:
        scheduler.start()
    elif not args.run_now:
        print("No action specified. Use --run-now or a schedule flag.")
        print("Run: python -m automation.scheduler --help")


def main():
    args = _parse_args()
    asyncio.run(_main_async(args))


if __name__ == "__main__":
    main()
