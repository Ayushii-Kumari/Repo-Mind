"""
Planner Agent — reads repo metadata + README, produces:
- Project summary
- Tech stack list
- Complexity score (1–10)
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
from agents.state import RepoState
from utils.github_utils import (
    parse_repo_url,
    fetch_repo_metadata,
    fetch_repo_tree,
    fetch_readme,
    build_folder_tree,
    get_important_files,
    fetch_file_content,
)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def planner_agent(state: RepoState) -> RepoState:
    """
    Step 1: Fetch repo data and plan the analysis.
    Populates: owner, repo_name, metadata, file_tree, readme, folder_structure, tech_stack, summary, complexity_score
    """
    print("\n🧠 [Planner Agent] Starting...")

    try:
        owner, repo_name = parse_repo_url(state["repo_url"])
        state["owner"] = owner
        state["repo_name"] = repo_name

        print(f"   Fetching metadata for {owner}/{repo_name}...")
        metadata = fetch_repo_metadata(owner, repo_name)
        state["metadata"] = metadata

        print("   Fetching file tree...")
        tree = fetch_repo_tree(owner, repo_name, metadata.get("default_branch", "main"))
        state["file_tree"] = tree

        print("   Fetching README...")
        readme = fetch_readme(owner, repo_name) or "No README found."
        state["readme"] = readme

        folder_structure = build_folder_tree(tree)
        state["folder_structure"] = folder_structure

        # Ask Groq to plan
        prompt = f"""You are a senior software architect analyzing a GitHub repository.

Repository: {owner}/{repo_name}
Description: {metadata.get('description', 'N/A')}
Stars: {metadata.get('stargazers_count', 0)}
Language: {metadata.get('language', 'Unknown')}

Folder structure:
{folder_structure}

README (first 2000 chars):
{readme[:2000]}

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "summary": "2-3 sentence project summary",
  "tech_stack": ["list", "of", "technologies"],
  "complexity_score": 7,
  "complexity_reason": "one sentence explaining the score"
}}
"""
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)

        state["summary"] = data.get("summary", "Could not generate summary.")
        state["tech_stack"] = data.get("tech_stack", [])
        state["complexity_score"] = int(data.get("complexity_score", 5))

        print(f"   ✅ Summary generated. Complexity: {state['complexity_score']}/10")

    except Exception as e:
        state["error"] = f"Planner agent failed: {e}"
        print(f"   ❌ Error: {e}")

    return state
