"""Pydantic request and response models for the Task Tracker API."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


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


class SeverityLevel(StrEnum):
    """Enumeration of task severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


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
    severity: SeverityLevel = Field(
        default=SeverityLevel.MEDIUM,
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

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated title of the task",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Updated description of the task",
    )
    status: TaskStatus | None = Field(
        default=None,
        description="Updated status of the task",
    )
    priority: TaskPriority | None = Field(
        default=None,
        description="Updated priority level of the task",
    )
    severity: SeverityLevel | None = Field(
        default=None,
        description="Updated severity level of the task",
    )
    due_date: str | None = Field(
        default=None,
        description="Updated due date in ISO format",
    )


class TaskResponse(TaskBase):
    """Response model representing a stored task."""

    id: int = Field(..., description="Unique task identifier")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Paginated list response for tasks."""
