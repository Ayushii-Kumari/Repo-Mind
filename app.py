"""
RepoMind v2 — Launcher
======================
Runs the FastAPI backend. The React frontend is served separately via npm.

Usage:
    # Terminal 1 — Backend
    uv run app.py

    # Terminal 2 — Frontend (first time: cd frontend && npm install)
    cd frontend && npm run dev

Then open: http://localhost:5173
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    port = os.getenv("BACKEND_PORT", "8000")
    print("🚀 Starting RepoMind backend...")
    print(f"   API → http://localhost:{port}")
    print(f"   Docs → http://localhost:{port}/docs")
    print()
    print("   Frontend: open a new terminal and run:")
    print("   cd frontend && npm install && npm run dev")
    print()
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--reload",
        f"--port={port}",
        "--host=0.0.0.0",
    ])
