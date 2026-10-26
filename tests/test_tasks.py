"""Unit and integration tests for Task CRUD endpoints."""

from fastapi.testclient import TestClient


def test_create_task_success(client: TestClient) -> None:
    """Test creating a task with custom fields."""
    payload = {
        "title": "Implement authentication",
        "description": "Add JWT authentication to the API",
        "status": "todo",
        "priority": "high",
        "severity": "high",
        "due_date": "2026-11-15",
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert data["severity"] == "high"
    assert data["due_date"] == "2026-11-15"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_default_values(client: TestClient) -> None:
    """Test creating a task with minimal payload uses correct defaults."""
    payload = {"title": "Quick task"}
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Quick task"
    assert data["description"] == ""
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["severity"] == "medium"
    assert data["due_date"] is None


def test_create_task_validation_error(client: TestClient) -> None:
    """Test validation errors on empty title and invalid enum values."""
    # Empty title
    res_empty_title = client.post("/api/v1/tasks", json={"title": ""})
    assert res_empty_title.status_code == 422

    # Invalid status
    res_bad_status = client.post(
        "/api/v1/tasks", json={"title": "Test", "status": "invalid_status"}
    )
    assert res_bad_status.status_code == 422

    # Invalid priority
    res_bad_priority = client.post(
        "/api/v1/tasks", json={"title": "Test", "priority": "extreme"}
    )
    assert res_bad_priority.status_code == 422

    # Invalid severity
    res_bad_severity = client.post(
        "/api/v1/tasks", json={"title": "Test", "severity": "critical"}
    )
    assert res_bad_severity.status_code == 422


def test_list_tasks_empty(client: TestClient) -> None:
    """Test listing tasks when none exist."""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200

    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 50
    assert data["offset"] == 0


def test_list_tasks_populated(client: TestClient) -> None:
    """Test listing tasks returns created items."""
    client.post("/api/v1/tasks", json={"title": "Task 1"})
    client.post("/api/v1/tasks", json={"title": "Task 2"})

    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_filter_tasks_by_status(client: TestClient) -> None:
    """Test filtering tasks by status."""
    client.post("/api/v1/tasks", json={"title": "Task A", "status": "todo"})
    client.post("/api/v1/tasks", json={"title": "Task B", "status": "in_progress"})
    client.post("/api/v1/tasks", json={"title": "Task C", "status": "done"})

    res = client.get("/api/v1/tasks?status=in_progress")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Task B"
