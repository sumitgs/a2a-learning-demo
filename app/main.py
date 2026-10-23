"""FastAPI application entrypoint for Task Tracker API."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.database import init_db
from app.routes import health, tasks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    # Initialize SQLite database and tables
    init_db()
    yield


def create_app() -> FastAPI:
    """Application factory for Task Tracker API."""
    application = FastAPI(
        title="Task Tracker API",
        description=(
            "A lightweight Task Tracker REST API sandbox for learning multi-agent "
            "software development workflows using LangGraph and the A2A protocol."
        ),
        version=__version__,
        lifespan=lifespan,
    )

    # Enable CORS for local development and sandbox integrations
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    application.include_router(health.router)
    application.include_router(tasks.router, prefix="/api/v1")
    # Also support direct /tasks path for convenience
    application.include_router(tasks.router)

    @application.get("/", tags=["root"])
    def root():
        """Welcome and discovery endpoint."""
        return {
            "app": settings.app_name,
            "version": __version__,
            "docs_url": "/docs",
            "health_url": "/health",
            "tasks_url": "/api/v1/tasks",
        }

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
