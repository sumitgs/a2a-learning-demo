"""Task CRUD endpoints."""

import sqlite3
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.database import get_db
from app.models import (
    TaskCreate,
    TaskListResponse,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def row_to_task(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a sqlite3.Row to a dictionary matching TaskResponse."""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "priority": row["priority"],
        "due_date": row["due_date"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    task_in: TaskCreate,
    db: sqlite3.Connection = Depends(get_db),
) -> TaskResponse:
    """Create a new task and persist it to SQLite."""
    now = datetime.now(UTC).isoformat()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (
            title, description, status, priority, due_date, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_in.title,
            task_in.description,
            task_in.status.value,
            task_in.priority.value,
            task_in.due_date,
            now,
            now,
        ),
    )
    task_id = cursor.lastrowid

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    return TaskResponse.model_validate(row_to_task(row))


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List tasks with optional filtering and pagination",
)
def list_tasks(
    status: TaskStatus | None = Query(
        default=None, description="Filter by status (todo, in_progress, done)"
    ),
    priority: TaskPriority | None = Query(
        default=None, description="Filter by priority (low, medium, high)"
    ),
    search: str | None = Query(
        default=None, description="Search term matching title or description"
    ),
    limit: int = Query(
        default=50, ge=1, le=100, description="Max number of items to return"
    ),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: sqlite3.Connection = Depends(get_db),
) -> TaskListResponse:
    """List tasks with filtering by status, priority, keyword, and pagination."""
    cursor = db.cursor()

    conditions: list[str] = []
    params: list[Any] = []

    if status is not None:
        conditions.append("status = ?")
        params.append(status.value)

    if priority is not None:
        conditions.append("priority = ?")
        params.append(priority.value)

    if search:
        search_pattern = f"%{search.strip()}%"
        conditions.append("(title LIKE ? OR description LIKE ?)")
        params.extend([search_pattern, search_pattern])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Total count matching filters
    count_query = f"SELECT COUNT(*) FROM tasks {where_clause}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Paginated select
    query = f"""
        SELECT * FROM tasks
        {where_clause}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, [*params, limit, offset])
    rows = cursor.fetchall()

    tasks = [TaskResponse.model_validate(row_to_task(r)) for r in rows]
    return TaskListResponse(items=tasks, total=total, limit=limit, offset=offset)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
)
def get_task(
    task_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> TaskResponse:
    """Retrieve a single task by its integer identifier."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return TaskResponse.model_validate(row_to_task(row))


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update an existing task",
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: sqlite3.Connection = Depends(get_db),
) -> TaskResponse:
    """Partially update an existing task."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    updates = task_in.model_dump(exclude_unset=True)
    if updates:
        set_clauses: list[str] = []
        params: list[Any] = []
        for field, val in updates.items():
            set_clauses.append(f"{field} = ?")
            # Enum conversion if present
            params.append(val.value if hasattr(val, "value") else val)

        now = datetime.now(UTC).isoformat()
        set_clauses.append("updated_at = ?")
        params.append(now)

        params.append(task_id)
        update_query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(update_query, params)

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    return TaskResponse.model_validate(row_to_task(row))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_task(
    task_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Response:
    """Delete a task by its identifier."""
    cursor = db.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
