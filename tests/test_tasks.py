"""Unit and integration tests for Task CRUD endpoints."""

from fastapi.testclient import TestClient


def test_create_task_success(client: TestClient) -> None:
    """Test creating a task with custom fields."""
    payload = {
        "title": "Implement authentication",
        "description": "Add JWT authentication to the API",
        "status": "todo",
        "priority": "high",
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


def test_filter_tasks_by_priority(client: TestClient) -> None:
    """Test filtering tasks by priority."""
    client.post("/api/v1/tasks", json={"title": "Task Low", "priority": "low"})
    client.post("/api/v1/tasks", json={"title": "Task High", "priority": "high"})

    res = client.get("/api/v1/tasks?priority=high")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Task High"


def test_search_tasks(client: TestClient) -> None:
    """Test searching tasks by title or description keyword."""
    client.post(
        "/api/v1/tasks",
        json={"title": "Fix login bug", "description": "Users cannot log in"},
    )
    client.post(
        "/api/v1/tasks",
        json={"title": "Refactor database", "description": "Optimize queries"},
    )

    # Search in title
    res_title = client.get("/api/v1/tasks?search=login")
    assert res_title.status_code == 200
    assert res_title.json()["total"] == 1
    assert res_title.json()["items"][0]["title"] == "Fix login bug"

    # Search in description
    res_desc = client.get("/api/v1/tasks?search=optimize")
    assert res_desc.status_code == 200
    assert res_desc.json()["total"] == 1
    assert res_desc.json()["items"][0]["title"] == "Refactor database"


def test_pagination(client: TestClient) -> None:
    """Test task list pagination limit and offset."""
    for i in range(5):
        client.post("/api/v1/tasks", json={"title": f"Task {i + 1}"})

    res = client.get("/api/v1/tasks?limit=2&offset=1")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 1


def test_get_task_by_id(client: TestClient) -> None:
    """Test retrieving a single task by ID."""
    created = client.post("/api/v1/tasks", json={"title": "Specific Task"}).json()
    task_id = created["id"]

    res = client.get(f"/api/v1/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["id"] == task_id
    assert res.json()["title"] == "Specific Task"


def test_get_task_not_found(client: TestClient) -> None:
    """Test 404 when task ID does not exist."""
    res = client.get("/api/v1/tasks/99999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_update_task_partial(client: TestClient) -> None:
    """Test partially updating a task."""
    created = client.post(
        "/api/v1/tasks",
        json={"title": "Initial Title", "status": "todo", "priority": "low"},
    ).json()
    task_id = created["id"]

    # Update status and title only
    patch_res = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "status": "done"},
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["id"] == task_id
    assert updated["title"] == "Updated Title"
    assert updated["status"] == "done"
    assert updated["priority"] == "low"  # Unchanged
    assert updated["updated_at"] >= created["updated_at"]


def test_update_task_not_found(client: TestClient) -> None:
    """Test 404 when updating non-existent task."""
    res = client.patch("/api/v1/tasks/99999", json={"title": "Ghost"})
    assert res.status_code == 404


def test_delete_task_success(client: TestClient) -> None:
    """Test deleting a task returns 204 and is subsequent 404."""
    created = client.post("/api/v1/tasks", json={"title": "To Delete"}).json()
    task_id = created["id"]

    del_res = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/tasks/{task_id}")
    assert get_res.status_code == 404


def test_delete_task_not_found(client: TestClient) -> None:
    """Test 404 when deleting a non-existent task."""
    del_res = client.delete("/api/v1/tasks/99999")
    assert del_res.status_code == 404
