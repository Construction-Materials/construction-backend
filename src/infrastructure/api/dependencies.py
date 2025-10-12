"""
FastAPI dependencies for Recipe AI Extractor.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from src.infrastructure.database.connection import get_async_db
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.database.repositories.recipe_repository_impl import RecipeRepositoryImpl
from src.infrastructure.database.repositories.catalog_item_repository_impl import CatalogItemRepositoryImpl
from src.infrastructure.database.repositories.recipe_item_repository_impl import RecipeItemRepositoryImpl
from src.infrastructure.database.repositories.processing_job_repository_impl import ProcessingJobRepositoryImpl
from src.application.use_cases.user_use_cases import UserUseCases
from src.application.use_cases.recipe_use_cases import RecipeUseCases
from src.application.use_cases.processing_job_use_cases import ProcessingJobUseCases
from src.application.use_cases.catalog_item_use_cases import CatalogItemUseCases
from src.shared.exceptions import EntityNotFoundError

# Security
security = HTTPBearer()


def get_user_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> UserRepositoryImpl:
    """Get user repository."""
    return UserRepositoryImpl(db)


def get_recipe_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> RecipeRepositoryImpl:
    """Get recipe repository."""
    return RecipeRepositoryImpl(db)


def get_catalog_item_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> CatalogItemRepositoryImpl:
    """Get catalog item repository."""
    return CatalogItemRepositoryImpl(db)


def get_recipe_item_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> RecipeItemRepositoryImpl:
    """Get recipe item repository."""
    return RecipeItemRepositoryImpl(db)


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


def get_processing_job_use_cases(
    job_repo: Annotated[ProcessingJobRepositoryImpl, Depends(get_processing_job_repository)],
    user_repo: Annotated[UserRepositoryImpl, Depends(get_user_repository)]
) -> ProcessingJobUseCases:
    """Get processing job use cases."""
    return ProcessingJobUseCases(job_repo, user_repo)


def get_catalog_item_use_cases(
    catalog_item_repo: Annotated[CatalogItemRepositoryImpl, Depends(get_catalog_item_repository)]
) -> CatalogItemUseCases:
    """Get catalog item use cases."""
    return CatalogItemUseCases(catalog_item_repo)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)]
) -> dict:
    """Get current authenticated user."""
    # TODO: Implement JWT token validation
    # For now, return a mock user
    try:
        # This is a placeholder - implement proper JWT validation
        user_id = UUID(credentials.credentials)
        user = await user_use_cases.get_user_by_id(user_id)
        return {
            "user_id": user.user_id,
            "email": user.email,
            "is_admin": user.is_admin
        }
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
