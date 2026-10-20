import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas import TaskExtraction, TaskPrioritization

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is missing. Add your API key to the .env file."
        )

    return genai.Client(api_key=api_key)


def call_gemini(prompt: str, response_schema: Any) -> dict:
    client = get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.2,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return json.loads(response.text)


def extract_tasks(state: dict) -> dict:
    """Node 1: Extract individual tasks and their deadlines."""

    prompt = f"""
You are an accurate task extraction assistant.

Extract every distinct task from the user's message.
Do not invent tasks or deadlines.
Preserve the user's intended meaning.
Keep task titles short and descriptions useful.
If a deadline is missing, use 'Not specified'.
Use 'Medium' as the initial priority for every task.

Return the result using the required JSON schema.

User message:
{state['input_text']}
"""

    result = call_gemini(prompt, TaskExtraction)
    tasks = result.get("tasks", [])

    if not tasks:
        raise ValueError(
            "No tasks were found. Please describe at least one task."
        )

    return {"tasks": tasks}


def prioritize_tasks(state: dict) -> dict:
    """Node 2: Assign priorities based on urgency and importance."""

    prompt = f"""
You are an expert task prioritization assistant.

Review these extracted tasks:
{json.dumps(state['tasks'], ensure_ascii=False)}

Assign each task one priority:
- High: urgent, important, or time-critical tasks.
- Medium: important routine tasks with moderate urgency.
- Low: less urgent tasks that can reasonably wait.

Consider explicit deadlines, urgency, and importance together.
A task due today is not automatically High if it is unimportant.
Do not change task titles, descriptions, or deadlines.
Do not add or remove tasks.
Return all tasks in the same order using the required JSON schema.
"""

    result = call_gemini(prompt, TaskPrioritization)
    tasks = result.get("tasks", [])

    if len(tasks) != len(state["tasks"]):
        raise ValueError(
            "The AI changed the number of tasks. Please try again."
        )

    return {"tasks": tasks}


def format_results(state: dict) -> dict:
    """Node 3: Format the final task list and summary."""

    tasks = state["tasks"]

    high = sum(t["priority"] == "High" for t in tasks)
    medium = sum(t["priority"] == "Medium" for t in tasks)
    low = sum(t["priority"] == "Low" for t in tasks)

    summary = (
        f"{len(tasks)} tasks organized: "
        f"{high} High, {medium} Medium, {low} Low priority."
    )

    lines = ["YOUR ORGANIZED TO-DO LIST", ""]

    for index, task in enumerate(tasks, start=1):
        lines.extend([
            f"{index}. {task['title']}",
            f"   Priority: {task['priority']}",
            f"   Deadline: {task['deadline']}",
            f"   Details: {task['description']}",
            "",
        ])

    return {
        "summary": summary,
        "result_text": "\n".join(lines),
    }