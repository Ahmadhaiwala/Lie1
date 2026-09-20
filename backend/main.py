"""
main.py — uvicorn entry point

Run:
    cd backend
    uvicorn main:app --host 0.0.0.0 --port 8000

Or with the helper script:
    python main.py
"""
import os
import sys

# Ensure the backend/ directory is on the path so all local imports resolve
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from api.app import app  # noqa: F401 (imported so uvicorn can reference it)

if __name__ == "__main__":
    # Playwright starts its Node driver as a subprocess.  Uvicorn's reload
    # supervisor selects WindowsSelectorEventLoopPolicy, which does not
    # implement asyncio subprocesses and makes Playwright fail with
    # NotImplementedError.  Keep reload opt-in so the default works on Windows.
    reload_enabled = os.getenv("RELOAD", "false").lower() == "true"
    if sys.platform == "win32" and reload_enabled:
        raise RuntimeError(
            "RELOAD=true is incompatible with Playwright on Windows. "
            "Start without reload (the default) so asyncio can use the "
            "Windows Proactor event loop."
        )

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=reload_enabled,
        log_level="info",
    )
