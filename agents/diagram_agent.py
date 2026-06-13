"""
Diagram / Chat Agent — handles RAG-based Q&A about the repo.
Uses FAISS to retrieve relevant code chunks, then answers with Groq.
"""
import os
from groq import Groq
from dotenv import load_dotenv
from agents.state import RepoState
from vector_db.embeddings import CodeVectorStore

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def chat_agent(state: RepoState, question: str) -> str:
    """
    RAG-based chat: retrieve relevant code chunks, then answer the question.
    This is called on-demand (not part of the main pipeline).
    """
    store = CodeVectorStore()
    loaded = store.load()

    context_str = ""
    if loaded:
        results = store.search(question, top_k=5)
        context_str = store.format_context(results)
    else:
        # Fall back to file contents summary
        file_contents = state.get("file_contents", {})
        snippets = []
        for path, content in list(file_contents.items())[:5]:
            snippets.append(f"### {path}\n```\n{content[:500]}\n```")
        context_str = "\n\n".join(snippets) if snippets else "No code context available."

    # Build message history
    history = state.get("chat_history", [])

    system_prompt = f"""You are an expert code assistant helping a developer understand the GitHub repository '{state.get('owner', '')}/{state.get('repo_name', '')}'.

Project summary: {state.get('summary', '')}
Tech stack: {', '.join(state.get('tech_stack', []))}

Use the retrieved code context below to answer the user's question accurately and concisely.

Retrieved code context:
{context_str}
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])  # last 3 turns
    messages.append({"role": "user", "content": question})

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=800,
    )
    answer = resp.choices[0].message.content.strip()

    # Update chat history in state
    state["chat_history"] = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
    state["last_answer"] = answer
    return answer


def chat_agent_stream(state: RepoState, question: str):
    """
    RAG-based chat that yields JSON-formatted events to support streaming.
    """
    import json

    # 1. Searching status
    yield json.dumps({"type": "status", "content": "Searching vector database..."}) + "\n"

    try:
        store = CodeVectorStore()
        loaded = store.load()

        context_str = ""
        if loaded:
            results = store.search(question, top_k=5)
            context_str = store.format_context(results)
        else:
            # Fall back to file contents summary
            file_contents = state.get("file_contents", {})
            snippets = []
            for path, content in list(file_contents.items())[:5]:
                snippets.append(f"### {path}\n```\n{content[:500]}\n```")
            context_str = "\n\n".join(snippets) if snippets else "No code context available."

        # 2. Generating status
        yield json.dumps({"type": "status", "content": "Writing response..."}) + "\n"

        # Build message history
        history = state.get("chat_history", [])

        system_prompt = f"""You are an expert code assistant helping a developer understand the GitHub repository '{state.get('owner', '')}/{state.get('repo_name', '')}'.

Project summary: {state.get('summary', '')}
Tech stack: {', '.join(state.get('tech_stack', []))}

Use the retrieved code context below to answer the user's question accurately and concisely.

Retrieved code context:
{context_str}
"""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-6:])  # last 3 turns
        messages.append({"role": "user", "content": question})

        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=800,
            stream=True,
        )

        full_answer = []
        for chunk in resp:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_answer.append(delta)
                    yield json.dumps({"type": "content", "content": delta}) + "\n"

        answer = "".join(full_answer)

        # Update chat history in state
        state["chat_history"] = history + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
        state["last_answer"] = answer
        yield json.dumps({"type": "done"}) + "\n"
    except Exception as e:
        yield json.dumps({"type": "error", "content": str(e)}) + "\n"


def diagram_finalize_agent(state: RepoState) -> RepoState:
    """
    Step 5 (final in pipeline): Initialize chat history and confirm all outputs are ready.
    """
    print("\n🗺️  [Diagram Agent] Finalizing outputs...")

    if state.get("error"):
        return state

    state.setdefault("chat_history", [])
    state.setdefault("last_answer", "")

    print("   ✅ Pipeline complete! All outputs ready.")
    return state
