"""Pytest configuration and fixtures for testing Task Tracker API."""

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database import get_db, init_db
from app.main import app


@pytest.fixture
def test_db_path(tmp_path: Path) -> str:
    """Provide an isolated SQLite database path for each test."""
    db_file = tmp_path / "test_tasks.db"
    db_path = str(db_file)
    init_db(db_path)
    return db_path


@pytest.fixture
def client(test_db_path: str) -> Generator[TestClient, None, None]:
    """Provide a TestClient with an isolated database dependency override."""

    def override_get_db() -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(
            test_db_path,
            check_same_thread=False,
            autocommit=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
