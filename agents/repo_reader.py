"""
Repo Reader Agent — fetches important files and loads them
into FAISS vector store for RAG-based chat.
"""
import os
from dotenv import load_dotenv
from agents.state import RepoState
from utils.github_utils import get_important_files, fetch_file_content
from vector_db.embeddings import CodeVectorStore

load_dotenv()


def repo_reader_agent(state: RepoState) -> RepoState:
    """
    Step 2: Fetch key files and index them in FAISS.
    Populates: file_contents (dict of {path: content})
    """
    print("\n📖 [Repo Reader Agent] Fetching important files...")

    if state.get("error"):
        return state

    try:
        owner = state["owner"]
        repo_name = state["repo_name"]
        tree = state["file_tree"]

        important = get_important_files(tree, max_files=20)
        print(f"   Found {len(important)} key files to analyze.")

        file_contents = {}
        for path in important:
            print(f"   Reading: {path}")
            content = fetch_file_content(owner, repo_name, path)
            if content:
                file_contents[path] = content[:8000]  # cap at 8k chars per file

        state["file_contents"] = file_contents
        print(f"   ✅ Loaded {len(file_contents)} files.")

        # Index into FAISS
        print("   Indexing into FAISS vector store...")
        store = CodeVectorStore()
        store.add_files(file_contents)
        store.save()
        print(f"   ✅ Indexed {store.index.ntotal if store.index else 0} chunks.")

    except Exception as e:
        state["error"] = f"Repo Reader agent failed: {e}"
        print(f"   ❌ Error: {e}")

    return state
