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
from src.application.use_cases.construction_use_cases import ConstructionUseCases

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

