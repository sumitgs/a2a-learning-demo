"""Pydantic request and response models for the Task Tracker API."""

from enum import StrEnum
from datetime import datetime

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    """Enumeration of possible task statuses."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(StrEnum):
    """Enumeration of task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskSeverity(StrEnum):
    """Enumeration of task severity levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskBase(BaseModel):
    """Shared task attributes."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the task",
        examples=["Fix navigation bar layout"],
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Detailed description of the task",
        examples=["The navigation bar overflows on mobile screens."],
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Current status of the task",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Priority level of the task",
    )
    severity: TaskSeverity = Field(
        default=TaskSeverity.MEDIUM,
        description="Severity level of the task",
    )
    due_date: str | None = Field(
        default=None,
        description="Due date in ISO format (e.g. YYYY-MM-DD or ISO 8601 timestamp)",
        examples=["2026-11-01"],
    )


class TaskCreate(TaskBase):
    """Request model for creating a new task."""

    pass


class TaskUpdate(BaseModel):
    """Request model for updating an existing task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    severity: TaskSeverity | None = None
    due_date: str | None = None


class TaskResponse(TaskBase):
    """Response model for a single task."""

    id: int = Field(..., description="Unique identifier of the task")
    created_at: datetime = Field(..., description="Timestamp when the task was created")
    updated_at: datetime = Field(..., description="Timestamp when the task was last updated")

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response model for a list of tasks."""

    items: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks matching the query")
    limit: int = Field(..., description="Maximum number of items returned")
    offset: int = Field(default=0, description="Number of items skipped")
