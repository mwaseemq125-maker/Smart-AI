from typing import Literal
from pydantic import BaseModel, Field


class Task(BaseModel):
    title: str = Field(description="Short task title")
    description: str = Field(description="Task details")
    deadline: str = Field(
        description="Deadline mentioned by user, or Not specified"
    )
    priority: Literal["High", "Medium", "Low"] = "Medium"


class TaskExtraction(BaseModel):
    tasks: list[Task]


class TaskPrioritization(BaseModel):
    tasks: list[Task]
