"""
Shared state schema for the LangGraph agent pipeline.
All agents read from and write to this TypedDict.
"""
from typing import Optional, Any
from typing_extensions import TypedDict


class RepoState(TypedDict):
    # Input
    repo_url: str
    owner: str
    repo_name: str

    # Raw data from GitHub
    metadata: dict          # repo metadata from GitHub API
    file_tree: list[dict]   # full git tree
    readme: str             # README content
    file_contents: dict     # {path: content}
    folder_structure: str   # text tree diagram

    # Agent outputs
    summary: str            # Planner → project summary
    tech_stack: list[str]   # detected technologies
    complexity_score: int   # 1–10 complexity rating
    folder_explanations: dict  # {folder: explanation}
    architecture_diagram: str  # ASCII / text diagram
    setup_instructions: str    # step-by-step setup
    interview_questions: list[str]  # generated Q&A

    # Chat / RAG
    chat_history: list[dict]  # [{role, content}]
    last_answer: str

    # Error tracking
    error: Optional[str]
