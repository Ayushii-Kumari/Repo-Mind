"""
Code Analyzer Agent — explains each folder and generates
the architecture diagram + setup instructions.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
from agents.state import RepoState

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_top_level_dirs(file_tree: list[dict]) -> list[str]:
    dirs = set()
    for item in file_tree:
        parts = item["path"].split("/")
        if len(parts) > 1:
            dirs.add(parts[0])
    return sorted(dirs)


def explainer_agent(state: RepoState) -> RepoState:
    """
    Step 3: Explain each folder and top-level files.
    Populates: folder_explanations
    """
    print("\n🔍 [Code Analyzer Agent] Analyzing structure...")

    if state.get("error"):
        return state

    try:
        dirs = _get_top_level_dirs(state["file_tree"])
        file_sample = "\n".join(
            f"- {path}: {content[:300]}..."
            for path, content in list(state.get("file_contents", {}).items())[:8]
        )

        prompt = f"""You are a senior developer explaining a GitHub repository structure.

Project: {state['owner']}/{state['repo_name']}
Summary: {state.get('summary', '')}
Tech Stack: {', '.join(state.get('tech_stack', []))}

Top-level folders: {dirs}
Folder structure:
{state.get('folder_structure', '')}

Sample file contents:
{file_sample}

Explain each folder (and root files like README, Dockerfile) in 1-2 sentences.
Respond ONLY with valid JSON:
{{
  "folder_name_or_file": "explanation",
  "backend": "Contains FastAPI routes and business logic",
  "frontend": "React SPA with Vite build toolchain"
}}
Include every folder from the list. Use clear, developer-friendly language.
"""
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        state["folder_explanations"] = data
        print(f"   ✅ Explained {len(data)} folders/files.")

    except Exception as e:
        state["error"] = f"Explainer agent failed: {e}"
        print(f"   ❌ Error: {e}")

    return state
