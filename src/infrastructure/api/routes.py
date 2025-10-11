"""
FastAPI routes for Recipe AI Extractor.
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Recipe AI Extractor API"}

# TODO: Add specific route modules here
# from .users import router as users_router
# from .recipes import router as recipes_router
# from .processing_jobs import router as jobs_router

# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(recipes_router, prefix="/recipes", tags=["recipes"])
# api_router.include_router(jobs_router, prefix="/jobs", tags=["processing-jobs"])
