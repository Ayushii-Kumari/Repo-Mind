"""
FastAPI backend for the GitHub Repository Explainer.
Exposes endpoints consumed by the Streamlit frontend.
"""
import os
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RepoMind API",
    description="Agentic GitHub Repository Explainer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (for demo; use Redis in production)
_sessions: dict[str, dict] = {}


class AnalyzeRequest(BaseModel):
    repo_url: str


class ChatRequest(BaseModel):
    repo_url: str
    question: str


class ExplainFileRequest(BaseModel):
    repo_url: str
    file_path: str


@app.get("/")
def root():
    return {"status": "ok", "message": "RepoMind API is running 🚀"}


@app.post("/analyze")
def analyze_repo(req: AnalyzeRequest):
    """
    Run the full 5-agent pipeline on a GitHub repo.
    Returns all analysis outputs.
    """
    from agents.pipeline import run_pipeline

    if not req.repo_url or "github.com" not in req.repo_url:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL.")

    state = run_pipeline(req.repo_url)

    if state.get("error"):
        raise HTTPException(status_code=500, detail=state["error"])

    # Cache session (keyed by repo URL)
    _sessions[req.repo_url] = state

    return {
        "owner": state["owner"],
        "repo_name": state["repo_name"],
        "summary": state["summary"],
        "tech_stack": state["tech_stack"],
        "complexity_score": state["complexity_score"],
        "folder_explanations": state["folder_explanations"],
        "folder_structure": state["folder_structure"],
        "architecture_diagram": state["architecture_diagram"],
        "setup_instructions": state["setup_instructions"],
        "interview_questions": state["interview_questions"],
        "stars": state["metadata"].get("stargazers_count", 0),
        "language": state["metadata"].get("language", "Unknown"),
        "description": state["metadata"].get("description", ""),
    }


@app.post("/chat")
def chat_with_repo(req: ChatRequest):
    """
    RAG-based Q&A about the repo. Requires /analyze to have been called first.
    """
    from agents.diagram_agent import chat_agent_stream

    state = _sessions.get(req.repo_url)
    if not state:
        raise HTTPException(
            status_code=404,
            detail="Repo not analyzed yet. Call /analyze first.",
        )

    try:
        generator = chat_agent_stream(state, req.question)
        return StreamingResponse(generator, media_type="application/x-ndjson")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain-file")
def explain_file(req: ExplainFileRequest):
    """
    Explain a specific file in the repo.
    """
    from groq import Groq
    from utils.github_utils import parse_repo_url, fetch_file_content

    state = _sessions.get(req.repo_url)
    if not state:
        raise HTTPException(status_code=404, detail="Repo not analyzed yet.")

    # Check if we already have the file
    content = state.get("file_contents", {}).get(req.file_path)
    if not content:
        owner, repo = parse_repo_url(req.repo_url)
        content = fetch_file_content(owner, repo, req.file_path)

    if not content:
        raise HTTPException(status_code=404, detail=f"File not found: {req.file_path}")

    groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = groq.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {
                "role": "user",
                "content": f"""Explain this file from the {state['owner']}/{state['repo_name']} repository.
File: {req.file_path}

```
{content[:6000]}
```

Provide:
1. What this file does (2-3 sentences)
2. Key functions/classes/components
3. How it connects to the rest of the project
""",
            }
        ],
        temperature=0.3,
        max_tokens=600,
    )
    return {"explanation": resp.choices[0].message.content.strip()}


@app.get("/health")
def health():
    return {"status": "healthy", "sessions": len(_sessions)}
