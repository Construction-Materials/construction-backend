"""
FastAPI routes for Recipe AI Extractor.
"""

from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .constructions import router as constructions_router
from .materials import router as materials_router
from .error_handlers import (
    recipe_extractor_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from src.shared.exceptions import RecipeExtractorException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Create main API router
api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Recipe AI Extractor API"}

# Include specific route modules
api_router.include_router(constructions_router, prefix="/constructions", tags=["constructions"])
api_router.include_router(materials_router, prefix="/materials", tags=["materials"])

# Exception handlers are added to the main app in main.py
