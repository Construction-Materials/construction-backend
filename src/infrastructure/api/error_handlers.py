"""
FastAPI error handlers for Recipe AI Extractor.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.shared.exceptions import (
    RecipeExtractorException, EntityNotFoundError, 
    ValidationError, BusinessRuleViolationError,
    ExternalServiceError, DatabaseError
)


async def recipe_extractor_exception_handler(request: Request, exc: RecipeExtractorException) -> JSONResponse:
    """Handle Recipe AI Extractor exceptions."""
    status_code = 500
    
    if isinstance(exc, EntityNotFoundError):
        status_code = 404
    elif isinstance(exc, ValidationError):
        status_code = 400
    elif isinstance(exc, BusinessRuleViolationError):
        status_code = 409
    elif isinstance(exc, ExternalServiceError):
        status_code = 502
    elif isinstance(exc, DatabaseError):
        status_code = 500
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "details": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": str(exc) if isinstance(exc, Exception) else None
        }
    )
