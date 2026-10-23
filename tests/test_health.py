"""Tests for health and root endpoints."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test the /health endpoint returns healthy status and DB check."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"
    assert "version" in data
    assert "environment" in data


def test_root_endpoint(client: TestClient) -> None:
    """Test the / root discovery endpoint."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["app"] == "task-tracker-api"
    assert data["docs_url"] == "/docs"
    assert data["health_url"] == "/health"
    assert data["tasks_url"] == "/api/v1/tasks"
