"""
FastAPI routes for Recipe AI Extractor.
"""

from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .users import router as users_router
from .recipes import router as recipes_router
from .processing_jobs import router as jobs_router
from .catalog_items import router as catalog_items_router
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
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(recipes_router, prefix="/recipes", tags=["recipes"])
api_router.include_router(jobs_router, prefix="/processing-jobs", tags=["processing-jobs"])
api_router.include_router(catalog_items_router, prefix="/catalog-items", tags=["catalog-items"])

# Exception handlers are added to the main app in main.py
