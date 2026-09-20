"""
main.py — uvicorn entry point

Run:
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

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
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level="info",
    )
