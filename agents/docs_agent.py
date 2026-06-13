"""
Docs Agent — generates:
- Architecture diagram (ASCII)
- Setup instructions (uv-based)
- Interview questions
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
from agents.state import RepoState

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def docs_agent(state: RepoState) -> RepoState:
    """
    Step 4: Generate docs, architecture diagram, setup steps, and interview questions.
    """
    print("\n📝 [Docs Agent] Generating documentation...")

    if state.get("error"):
        return state

    try:
        context = f"""
Project: {state['owner']}/{state['repo_name']}
Summary: {state.get('summary', '')}
Tech Stack: {', '.join(state.get('tech_stack', []))}
Complexity: {state.get('complexity_score', 5)}/10
Folder Explanations: {json.dumps(state.get('folder_explanations', {}), indent=2)}
README excerpt: {state.get('readme', '')[:1500]}
"""

        # --- Architecture Diagram ---
        arch_prompt = f"""{context}

Generate a clean ASCII architecture diagram showing how the main components connect.
Use arrows (→ or ↓) to show data flow. Keep it simple, max 20 lines.
Only output the diagram, no explanation.

Example format:
User Browser
     ↓
  Frontend (React)
     ↓
  Backend API (FastAPI)
     ↓
  AI Engine (Groq LLM)
     ↓
  Vector DB (FAISS)
"""
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": arch_prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        state["architecture_diagram"] = resp.choices[0].message.content.strip()
        print("   ✅ Architecture diagram generated.")

        # --- Setup Instructions ---
        setup_prompt = f"""{context}

Generate step-by-step setup instructions to run this project locally.
Use uv for Python package management (uv sync, uv run).
Format as numbered steps with code blocks. Keep it concise (max 15 steps).
Include: clone, env setup, install deps, run.
"""
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": setup_prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        state["setup_instructions"] = resp.choices[0].message.content.strip()
        print("   ✅ Setup instructions generated.")

        # --- Interview Questions ---
        questions_prompt = f"""{context}

Generate 8 technical interview questions about this project and its tech stack.
Include questions about architecture decisions, trade-offs, and the technologies used.
Format as a numbered list. Mix difficulty levels (easy, medium, hard).
"""
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": questions_prompt}],
            temperature=0.5,
            max_tokens=600,
        )
        raw_q = resp.choices[0].message.content.strip()
        # Parse numbered list into a Python list
        questions = []
        for line in raw_q.splitlines():
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("Q")):
                # Remove "1. " or "Q1. " prefix
                parts = line.split(".", 1)
                if len(parts) > 1:
                    questions.append(parts[1].strip())
                else:
                    questions.append(line)
        state["interview_questions"] = questions if questions else [raw_q]
        print(f"   ✅ Generated {len(state['interview_questions'])} interview questions.")

    except Exception as e:
        state["error"] = f"Docs agent failed: {e}"
        print(f"   ❌ Error: {e}")

    return state
