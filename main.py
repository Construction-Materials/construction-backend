"""
Recipe AI Extractor - Main Application Entry Point

FastAPI application with Hexagonal Architecture for recipe extraction using AI.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from mangum import Mangum

from src.infrastructure.database.connection import init_database
from src.infrastructure.api.routes import api_router
from src.infrastructure.api.error_handlers import (
    recipe_extractor_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from src.shared.exceptions import RecipeExtractorException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


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
        title="Construction Manager",
        description="Backend API for managing construction projects with Hexagonal Architecture",
        version="1.0.0",
        lifespan=lifespan,
        redirect_slashes=False
    )
    
    # CORS is handled by Lambda Function URL configuration

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Add exception handlers
    app.add_exception_handler(RecipeExtractorException, recipe_extractor_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    return app


# Create application instance
app = create_app()
handler = Mangum(app, lifespan="off")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Construction Manager API",
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
