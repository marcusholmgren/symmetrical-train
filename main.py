"""
FastAPI application for text classification news management.
Uses Tortoise ORM with SQLite database and Hugging Face dataset for seed data.
"""

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db, close_db
from app.routes.news import router as news_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Symmetrical Train - News Classification API",
    description="API for managing news text classifications using data from Hugging Face",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(news_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Symmetrical Train News Classification API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
