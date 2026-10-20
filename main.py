import os
import uuid
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langgraph.checkpoint.memory import InMemorySaver

from graph import task_graph

load_dotenv()


# ---------------- REQUEST SCHEMAS ----------------

class TaskRequest(BaseModel):
    input_text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Natural-language description of tasks",
    )


class TaskResponse(BaseModel):
    thread_id: str
    summary: str
    tasks: list[dict[str, Any]]
    result_text: str


# ---------------- APPLICATION LIFESPAN ----------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY is missing from .env")

    app.state.checkpointer = InMemorySaver()
    print("AI Task Organizer API started successfully.")

    yield

    print("AI Task Organizer API shutting down.")


# ---------------- FASTAPI APPLICATION ----------------

app = FastAPI(
    title="AI Task Organizer API",
    description=(
        "An intelligent task organizer powered by Google Gemini "
        "and LangGraph. Extracts tasks, assigns priorities, "
        "and formats an organized to-do list."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ---------------- HEALTH CHECK ----------------

@app.get("/", tags=["General"])
async def root():
    return {
        "message": "AI Task Organizer API is running!",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "application": "AI Task Organizer",
        "workflow": "Gemini + LangGraph",
    }


# ---------------- ORGANIZE TASKS ----------------

@app.post(
    "/organize",
    response_model=TaskResponse,
    tags=["Tasks"],
)
async def organize_tasks(request: TaskRequest):
    input_text = request.input_text.strip()

    if not input_text:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid task description.",
        )

    try:
        thread_id = str(uuid.uuid4())

        initial_state = {
            "input_text": input_text,
            "tasks": [],
            "summary": "",
            "result_text": "",
        }

        result = await task_graph.ainvoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )

        return TaskResponse(
            thread_id=thread_id,
            summary=result.get("summary", ""),
            tasks=result.get("tasks", []),
            result_text=result.get("result_text", ""),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to organize tasks. Check the Gemini API key, "
                "model availability, and server logs."
            ),
        ) from exc


# ---------------- RUN DIRECTLY ----------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )