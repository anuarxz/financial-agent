"""Main entry point for the Financial Agent API."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.api import router
from src.api.dependencies import get_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup: Initialize database schema
    db = get_db_connection()
    db.initialize_schema()
    print("Database schema initialized")

    yield

    # Shutdown: cleanup if needed
    print("Shutting down...")


app = FastAPI(
    title="Financial Agent API",
    description="AI-powered financial assistant for managing expenses, savings, and investments",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1", tags=["agent"])


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Financial Agent API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
