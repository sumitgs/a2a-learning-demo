# Task Tracker API

[![CI](https://github.com/example/task-tracker-api/actions/workflows/ci.yml/badge.svg)](https://github.com/example/task-tracker-api/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A lightweight, clean REST API for managing tasks, built specifically as a **sandbox repository** for experimenting with **multi-agent software development** using **LangGraph** and the **A2A (Agent-to-Agent) protocol**.

---

## 1. Project Purpose & Multi-Agent Workflow

This repository serves as the target workspace for an external AI-driven software engineering workflow. The orchestrator (powered by LangGraph and A2A) lives in a separate repository and interacts with this codebase across distinct agent roles:

```
                      ┌────────────────────────────┐
                      │    Incoming GitHub Issue   │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │   Issue Analysis Agent     │
                      │  (Investigates Root Cause) │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │   Implementation Agent     │◄──────────────┐
                      │  (Modifies code, tests, PR)│               │
                      └─────────────┬──────────────┘               │
                                    │                              │
                                    ▼                              │ Addresses
                      ┌────────────────────────────┐               │ Feedback
                      │    Code Review Agent       │───────────────┘
                      │  (Analyzes diff, feedback) │
                      └─────────────┬──────────────┘
                                    │
                                    ▼ (Approved)
                      ┌────────────────────────────┐
                      │    Human Review & Merge    │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │     Deployment Agent       │
                      │  (Deploys to local/sandbox)│
                      └────────────────────────────┘
```

> **Note:** Neither LangGraph nor A2A protocol implementations reside in this repository. This repository is kept intentionally lean, straightforward, and focused solely on the Task Tracker domain so AI agents can parse, test, modify, and review it efficiently.

---

## 2. Technology Stack

- **Language:** Python 3.12+
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (REST API)
- **Data Modeling & Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **Persistence:** [SQLite](https://www.sqlite.org/) (via Python's built-in `sqlite3` module with dictionary row factory)
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
- **Automated Testing:** [Pytest](https://docs.pytest.org/) & HTTPX TestClient
- **Linting & Formatting:** [Ruff](https://docs.astral.sh/ruff/)
- **Continuous Integration:** GitHub Actions (`.github/workflows/ci.yml`)

---

## 3. Project Structure

```
task-tracker-api/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI (Ruff linter/formatter + Pytest)
├── app/
│   ├── __init__.py            # Application package & version
│   ├── config.py              # Configuration & environment variables
│   ├── database.py            # SQLite connection, migrations, and dependency
│   ├── main.py                # FastAPI app factory, lifespan, and CORS
│   ├── models.py              # Pydantic schemas (TaskCreate, TaskUpdate, etc.)
│   └── routes/
│       ├── __init__.py
│       ├── health.py          # GET /health probe
│       └── tasks.py           # Task CRUD endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Isolated SQLite test fixture & TestClient
│   ├── test_health.py         # Tests for health & discovery endpoints
│   └── test_tasks.py          # Comprehensive CRUD, filter, and validation tests
├── .env.example               # Template environment configuration
├── .gitignore                 # Standard Python & SQLite ignore rules
├── pyproject.toml             # Ruff, Pytest, and project metadata configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development & test dependencies
└── README.md                  # Project documentation
```

---

## 4. Getting Started

### Prerequisites

- Python 3.12 or higher

### Installation

1. Navigate to the project directory:
   ```bash
   cd task-tracker-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Configure environment variables (optional):
   ```bash
   cp .env.example .env
   ```

---

## 5. Running the Application

Start the development server with hot reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **API Root:** [http://localhost:8000/](http://localhost:8000/)

---

## 6. REST API Reference

All task endpoints are available under `/api/v1/tasks` (and directly under `/tasks`).

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/tasks` | Create a new task (201 Created) |
| `GET` | `/api/v1/tasks` | List tasks with filters & pagination |
| `GET` | `/api/v1/tasks/{task_id}` | Retrieve a single task by ID (404 if not found) |
| `PATCH` | `/api/v1/tasks/{task_id}` | Partially update an existing task |
| `DELETE` | `/api/v1/tasks/{task_id}` | Delete a task (204 No Content) |
| `GET` | `/health` | Health check & SQLite database connectivity |
| `GET` | `/` | API discovery and links |

### Example cURL Commands

#### 1. Create a Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Build Issue Analysis Agent",
       "description": "Agent should parse GitHub issues and locate relevant code lines.",
       "status": "in_progress",
       "priority": "high",
       "due_date": "2026-11-01"
     }'
```

#### 2. List & Filter Tasks
```bash
# Filter by status and search keyword
curl "http://localhost:8000/api/v1/tasks?status=in_progress&search=Agent&limit=10"
```

#### 3. Update a Task
```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "done"
     }'
```

#### 4. Delete a Task
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

---

## 7. Testing, Linting & Formatting

Run all automated tests:
```bash
pytest
```

Run Ruff linter:
```bash
ruff check .
```

Run Ruff formatter check:
```bash
ruff format --check .
```

Auto-format code:
```bash
ruff format .
ruff check --fix .
```

---

## 8. Sample Scenarios for AI Agent Workflows

Here are sample exercises to test your multi-agent development workflow against this repository:

1. **Bug Fix Scenario:**
   - *Issue:* "Due date accepts arbitrary invalid string formats instead of standard ISO date validation."
   - *Issue Analysis Agent:* Traces `TaskCreate.due_date` in `app/models.py`.
   - *Implementation Agent:* Adds a Pydantic field validator or type `date | None`, updates tests in `tests/test_tasks.py`.
   - *Code Review Agent:* Confirms backwards compatibility and test coverage.

2. **Feature Request Scenario:**
   - *Issue:* "Add a `tags` list field to tasks so tasks can be categorized by label (e.g., `['backend', 'bug']`)."
   - *Implementation Agent:* Updates SQLite table schema in `app/database.py`, models in `app/models.py`, CRUD logic in `app/routes/tasks.py`, and adds comprehensive tests.

3. **Refactoring Scenario:**
   - *Issue:* "Support soft-deletion via an `is_deleted` column so deleted tasks can be restored if needed."
