# 🧠 RepoMind — GitHub Repository Explainer

React + FastAPI + Groq + LangGraph + FAISS. No Streamlit.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18 + Vite |
| Backend | FastAPI + uvicorn |
| LLM | Groq → llama-3.3-70b-versatile |
| Agents | LangGraph (5-agent pipeline) |
| RAG | FAISS + sentence-transformers |
| Package | uv |

## Quick Start

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and enter project
```bash
cd repo-mind
```

### 3. Add your API key
Edit `.env`:
```
GROQ_API_KEY=gsk_your_key_here
GITHUB_TOKEN=ghp_your_token_here   # optional
```

### 4. Create venv and install Python deps
```bash
uv venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
uv sync
```

### 5. Install frontend deps
```bash
cd frontend
npm install
cd ..
```

### 6. Run backend (Terminal 1)
```bash
uv run app.py
```

### 7. Run frontend (Terminal 2)
```bash
cd frontend && npm run dev
```

Open → **http://localhost:5173**

---

## Project Structure

```
repo-explainer/
├── agents/
│   ├── state.py          ← LangGraph state schema
│   ├── planner.py        ← Agent 1: summary + tech stack
│   ├── repo_reader.py    ← Agent 2: fetch files + FAISS index
│   ├── explainer.py      ← Agent 3: folder explanations
│   ├── docs_agent.py     ← Agent 4: architecture + setup + Qs
│   ├── diagram_agent.py  ← Agent 5: finalize + RAG chat
│   └── pipeline.py       ← LangGraph StateGraph
├── backend/
│   └── main.py           ← FastAPI: /analyze /chat /explain-file
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx        ← Dark/light toggle
│   │   │   ├── Hero.jsx          ← Landing page
│   │   │   ├── AnalysisPanel.jsx ← 6-tab results view
│   │   │   ├── AgentPipeline.jsx ← Agent status bar
│   │   │   └── Chat.jsx          ← RAG chat UI
│   │   └── index.css             ← CSS variables (dark + light)
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── utils/github_utils.py
├── vector_db/embeddings.py
├── app.py                ← Backend launcher
├── pyproject.toml
└── .env
```

## Deploy

**Frontend → Vercel:**
```bash
cd frontend
npm run build
# Push to GitHub → import in vercel.com
# Set env var: VITE_API_URL=https://your-backend.onrender.com
```

**Backend → Render:**
- Connect GitHub repo
- Build command: `pip install uv && uv sync`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Add env vars: `GROQ_API_KEY`, `GITHUB_TOKEN`
