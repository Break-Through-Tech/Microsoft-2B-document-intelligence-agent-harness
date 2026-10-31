from typing import TypedDict

from langgraph.graph import StateGraph, END

from inspection import inspect
from answer_generation import answer


class WorkflowState(TypedDict, total=False):
    question: str
    evidence: dict
    is_sufficient: bool
    result: dict


def retrieve_node(state: WorkflowState):
    """Retrieve and inspect relevant document chunks."""
    evidence = inspect(state["question"])

    return {"evidence": evidence}


def assess_node(state: WorkflowState):
    """Determine whether enough evidence was retrieved."""
    evidence = state["evidence"]

    is_sufficient = (
        evidence.get("is_sufficient", False)
        and bool(evidence.get("chunks"))
    )

    return {"is_sufficient": is_sufficient}


def route_after_assessment(state: WorkflowState):
    """Choose whether to answer or refuse."""
    if state["is_sufficient"]:
        return "answer"

    return "refuse"


def answer_node(state: WorkflowState):
    """Generate an answer using the retrieved evidence."""
    result = answer(
        question=state["question"],
        inspector=lambda _: state["evidence"],
    )

    return {"result": result}


def refuse_node(state: WorkflowState):
    """Return a refusal when evidence is insufficient."""
    result = answer(
        question=state["question"],
        inspector=lambda _: {"is_sufficient": False, "chunks": []},
    )

    return {"result": result}


def build_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("assess", assess_node)
    graph.add_node("answer", answer_node)
    graph.add_node("refuse", refuse_node)

    graph.set_entry_point("retrieve")

    graph.add_edge("retrieve", "assess")

    graph.add_conditional_edges(
        "assess",
        route_after_assessment,
        {
            "answer": "answer",
            "refuse": "refuse",
        },
    )

    graph.add_edge("answer", END)
    graph.add_edge("refuse", END)

    return graph.compile()


if __name__ == "__main__":
    workflow = build_workflow()

    question = "What does the documentation say about the system?"

    output = workflow.invoke({"question": question})

    print(output["result"]["answer"])