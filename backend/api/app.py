"""
api/app.py
----------
FastAPI application factory.
Wires up CORS, routers and the APScheduler lifespan.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.health import router as health_router
from api.routes.leads  import router as leads_router
from api.routes.jobs   import router as jobs_router
from api.deps          import get_scheduler


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background scheduler (non-blocking)
    scheduler = get_scheduler()
    scheduler.start_non_blocking()
    yield
    # Graceful shutdown
    scheduler.stop()


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="LeadBot AI API",
        description=(
            "REST API for the AI-powered lead generation system.\n\n"
            "**Services**: Website Development · WhatsApp Bot · SEO\n\n"
            "Start a run via `POST /jobs/run`, then poll `GET /jobs/{id}/status`."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://localhost:3000"
    ).split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(leads_router,  prefix="/api/v1")
    app.include_router(jobs_router,   prefix="/api/v1")

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "service": "LeadBot AI API",
            "docs":    "/docs",
            "health":  "/health",
        }

    return app


app = create_app()
