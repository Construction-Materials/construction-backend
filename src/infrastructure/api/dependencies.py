"""
FastAPI dependencies for Recipe AI Extractor.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from src.infrastructure.database.connection import get_async_db

from src.shared.exceptions import EntityNotFoundError

# Security
security = HTTPBearer()

def get_processing_job_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> ProcessingJobRepositoryImpl:
    """Get processing job repository."""
    return ProcessingJobRepositoryImpl(db)


def get_user_use_cases(
    user_repo: Annotated[UserRepositoryImpl, Depends(get_user_repository)]
) -> UserUseCases:
    """Get user use cases."""
    return UserUseCases(user_repo)


def get_recipe_use_cases(
    recipe_repo: Annotated[RecipeRepositoryImpl, Depends(get_recipe_repository)],
    user_repo: Annotated[UserRepositoryImpl, Depends(get_user_repository)],
    catalog_item_repo: Annotated[CatalogItemRepositoryImpl, Depends(get_catalog_item_repository)],
    recipe_item_repo: Annotated[RecipeItemRepositoryImpl, Depends(get_recipe_item_repository)]
) -> RecipeUseCases:
    """Get recipe use cases."""
    return RecipeUseCases(recipe_repo, user_repo, catalog_item_repo, recipe_item_repo)
