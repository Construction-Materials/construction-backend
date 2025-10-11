"""
Recipe AI Extractor - Main Application Entry Point

FastAPI application with Hexagonal Architecture for recipe extraction using AI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.infrastructure.database.connection import init_database
from src.infrastructure.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_database()
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Recipe AI Extractor",
        description="Backend API for extracting recipes using AI with Hexagonal Architecture",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend URLs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Create application instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Recipe AI Extractor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
