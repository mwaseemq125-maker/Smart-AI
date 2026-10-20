from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from nodes import extract_tasks, prioritize_tasks, format_results


class TaskState(TypedDict):
    input_text: str
    tasks: list[dict[str, Any]]
    summary: str
    result_text: str


def build_graph():
    workflow = StateGraph(TaskState)

    workflow.add_node("extract_tasks", extract_tasks)
    workflow.add_node("prioritize_tasks", prioritize_tasks)
    workflow.add_node("format_results", format_results)

    workflow.add_edge(START, "extract_tasks")
    workflow.add_edge("extract_tasks", "prioritize_tasks")
    workflow.add_edge("prioritize_tasks", "format_results")
    workflow.add_edge("format_results", END)

    return workflow.compile()


task_graph = build_graph()
