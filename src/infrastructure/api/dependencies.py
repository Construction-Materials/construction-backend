"""
FastAPI dependencies for Recipe AI Extractor.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from src.infrastructure.database.connection import get_async_db
from src.infrastructure.database.repositories.construction_repository_impl import ConstructionRepositoryImpl
from src.infrastructure.database.repositories.material_repository_impl import MaterialRepositoryImpl
from src.infrastructure.database.repositories.storage_repository_impl import StorageRepositoryImpl
from src.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from src.application.use_cases.construction_use_cases import ConstructionUseCases
from src.application.use_cases.material_use_cases import MaterialUseCases
from src.application.use_cases.storage_use_cases import StorageUseCases
from src.application.use_cases.category_use_cases import CategoryUseCases

from src.shared.exceptions import EntityNotFoundError

# Security
security = HTTPBearer()


def get_construction_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> ConstructionRepositoryImpl:
    """Get construction repository."""
    return ConstructionRepositoryImpl(db)


def get_construction_use_cases(
    construction_repo: Annotated[ConstructionRepositoryImpl, Depends(get_construction_repository)]
) -> ConstructionUseCases:
    """Get construction use cases."""
    return ConstructionUseCases(construction_repo)


def get_material_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> MaterialRepositoryImpl:
    """Get material repository."""
    return MaterialRepositoryImpl(db)


def get_material_use_cases(
    material_repo: Annotated[MaterialRepositoryImpl, Depends(get_material_repository)]
) -> MaterialUseCases:
    """Get material use cases."""
    return MaterialUseCases(material_repo)


def get_storage_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> StorageRepositoryImpl:
    """Get storage repository."""
    return StorageRepositoryImpl(db)


def get_storage_use_cases(
    storage_repo: Annotated[StorageRepositoryImpl, Depends(get_storage_repository)]
) -> StorageUseCases:
    """Get storage use cases."""
    return StorageUseCases(storage_repo)


def get_category_repository(db: Annotated[AsyncSession, Depends(get_async_db)]) -> CategoryRepositoryImpl:
    """Get category repository."""
    return CategoryRepositoryImpl(db)


def get_category_use_cases(
    category_repo: Annotated[CategoryRepositoryImpl, Depends(get_category_repository)]
) -> CategoryUseCases:
    """Get category use cases."""
    return CategoryUseCases(category_repo)

