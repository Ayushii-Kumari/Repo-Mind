"""
GitHub utility functions for fetching repo data.
"""
import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
BASE_URL = "https://api.github.com"


def get_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def parse_repo_url(url: str) -> tuple[str, str]:
    """Parse 'https://github.com/owner/repo' → ('owner', 'repo')"""
    url = url.rstrip("/").replace("https://github.com/", "").replace("http://github.com/", "")
    parts = url.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return parts[0], parts[1]


def fetch_repo_metadata(owner: str, repo: str) -> dict:
    """Fetch repo metadata from GitHub API."""
    resp = requests.get(f"{BASE_URL}/repos/{owner}/{repo}", headers=get_headers())
    resp.raise_for_status()
    return resp.json()


def fetch_repo_tree(owner: str, repo: str, branch: str = "main") -> list[dict]:
    """Fetch the full file tree of a repo."""
    # Try main first, then master
    for br in [branch, "master", "HEAD"]:
        resp = requests.get(
            f"{BASE_URL}/repos/{owner}/{repo}/git/trees/{br}",
            params={"recursive": "1"},
            headers=get_headers(),
        )
        if resp.status_code == 200:
            return resp.json().get("tree", [])
    resp.raise_for_status()
    return []


def fetch_file_content(owner: str, repo: str, file_path: str) -> Optional[str]:
    """Fetch the raw content of a file."""
    import base64
    resp = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/contents/{file_path}",
        headers=get_headers(),
    )
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None
    return data.get("content")


def fetch_readme(owner: str, repo: str) -> Optional[str]:
    """Fetch the README content."""
    resp = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/readme",
        headers=get_headers(),
    )
    if resp.status_code != 200:
        return None
    import base64
    data = resp.json()
    if data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None
    return data.get("content")


def get_important_files(tree: list[dict], max_files: int = 20) -> list[str]:
    """Return the most important files to analyze."""
    priority = [
        "README.md", "readme.md", "README.rst",
        "requirements.txt", "pyproject.toml", "package.json",
        "Dockerfile", "docker-compose.yml",
        "app.py", "main.py", "index.py", "server.py",
        ".github/workflows",
        "setup.py", "setup.cfg",
    ]
    all_paths = [item["path"] for item in tree if item["type"] == "blob"]

    selected = []
    # First add priority files
    for p in priority:
        for path in all_paths:
            if path.endswith(p) or path == p:
                if path not in selected:
                    selected.append(path)

    # Then add Python/JS/TS files from root and key folders
    code_exts = (".py", ".js", ".ts", ".go", ".rs", ".java", ".tsx", ".jsx")
    for path in all_paths:
        if len(selected) >= max_files:
            break
        if path.endswith(code_exts) and path not in selected:
            selected.append(path)

    return selected[:max_files]


def build_folder_tree(tree: list[dict]) -> str:
    """Build a text representation of the folder structure."""
    dirs = set()
    files_by_dir: dict[str, list[str]] = {}

    for item in tree:
        path = item["path"]
        parts = path.split("/")
        if len(parts) == 1:
            files_by_dir.setdefault(".", []).append(parts[0])
        else:
            d = parts[0]
            dirs.add(d)
            files_by_dir.setdefault(d, []).append("/".join(parts[1:]))

    lines = []
    root_files = files_by_dir.get(".", [])
    for f in root_files:
        lines.append(f"├── {f}")
    for d in sorted(dirs):
        lines.append(f"├── {d}/")
        for f in files_by_dir.get(d, [])[:5]:
            lines.append(f"│   ├── {f}")
        extras = len(files_by_dir.get(d, [])) - 5
        if extras > 0:
            lines.append(f"│   └── ... ({extras} more files)")

    return "\n".join(lines)
