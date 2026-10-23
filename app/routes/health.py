"""Health check endpoint."""

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, status

from app import __version__
from app.config import settings
from app.database import get_db

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Application health check",
)
def health_check(db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    """Verify application health and database connectivity."""
    db_status = "ok"
    try:
        db.execute("SELECT 1;").fetchone()
    except Exception as exc:
        db_status = f"unhealthy: {exc}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "app": settings.app_name,
        "version": __version__,
        "environment": settings.app_env,
        "database": db_status,
    }
