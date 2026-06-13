"""
LangGraph pipeline connecting all 5 agents in sequence.

Flow:
  planner_agent
      ↓
  repo_reader_agent
      ↓
  explainer_agent
      ↓
  docs_agent
      ↓
  diagram_finalize_agent
"""
from langgraph.graph import StateGraph, END
from agents.state import RepoState
from agents.planner import planner_agent
from agents.repo_reader import repo_reader_agent
from agents.explainer import explainer_agent
from agents.docs_agent import docs_agent
from agents.diagram_agent import diagram_finalize_agent


def should_continue(state: RepoState) -> str:
    """Stop the pipeline early if an error has occurred."""
    if state.get("error"):
        return END
    return "continue"


def build_pipeline() -> StateGraph:
    """Build and compile the LangGraph state machine."""
    workflow = StateGraph(RepoState)

    # Add nodes
    workflow.add_node("planner", planner_agent)
    workflow.add_node("repo_reader", repo_reader_agent)
    workflow.add_node("explainer", explainer_agent)
    workflow.add_node("docs", docs_agent)
    workflow.add_node("finalize", diagram_finalize_agent)

    # Entry point
    workflow.set_entry_point("planner")

    # Linear edges with error check between each step
    workflow.add_conditional_edges(
        "planner",
        should_continue,
        {"continue": "repo_reader", END: END},
    )
    workflow.add_conditional_edges(
        "repo_reader",
        should_continue,
        {"continue": "explainer", END: END},
    )
    workflow.add_conditional_edges(
        "explainer",
        should_continue,
        {"continue": "docs", END: END},
    )
    workflow.add_conditional_edges(
        "docs",
        should_continue,
        {"continue": "finalize", END: END},
    )
    workflow.add_edge("finalize", END)

    return workflow.compile()


def run_pipeline(repo_url: str) -> RepoState:
    """
    Run the full analysis pipeline for a GitHub repo URL.
    Returns the final state with all outputs populated.
    """
    initial_state: RepoState = {
        "repo_url": repo_url,
        "owner": "",
        "repo_name": "",
        "metadata": {},
        "file_tree": [],
        "readme": "",
        "file_contents": {},
        "folder_structure": "",
        "summary": "",
        "tech_stack": [],
        "complexity_score": 0,
        "folder_explanations": {},
        "architecture_diagram": "",
        "setup_instructions": "",
        "interview_questions": [],
        "chat_history": [],
        "last_answer": "",
        "error": None,
    }

    pipeline = build_pipeline()
    final_state = pipeline.invoke(initial_state)
    return final_state
