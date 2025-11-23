"""
Storage API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.storage_dto import (
    StorageCreateDTO,
    StorageUpdateDTO,
    StorageResponseDTO,
    StorageListResponseDTO,
    StorageSearchDTO
)
from src.application.use_cases.storage_use_cases import StorageUseCases
from src.infrastructure.api.dependencies import get_storage_use_cases

router = APIRouter()


@router.get("/public", response_model=List[StorageResponseDTO])
async def list_storages_public(
    limit: int = 100,
    offset: int = 0,
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """List all storages (public endpoint for testing)."""
    result = await storage_use_cases.list_all_storages(limit=limit, offset=offset)
    return result.storages


@router.post("/", response_model=StorageResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_storage(
    storage_dto: StorageCreateDTO,
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """Create a new storage."""
    return await storage_use_cases.create_storage(storage_dto)


@router.get("/{storage_id}", response_model=StorageResponseDTO)
async def get_storage(
    storage_id: UUID,
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """Get storage by ID."""
    return await storage_use_cases.get_storage_by_id(storage_id)


@router.put("/{storage_id}", response_model=StorageResponseDTO)
async def update_storage(
    storage_id: UUID,
    storage_dto: StorageUpdateDTO,
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """Update storage."""
    return await storage_use_cases.update_storage(storage_id, storage_dto)


@router.delete("/{storage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_storage(
    storage_id: UUID,
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """Delete storage."""
    await storage_use_cases.delete_storage(storage_id)


@router.get("/", response_model=StorageListResponseDTO)
async def list_storages(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """List all storages."""
    return await storage_use_cases.list_all_storages(limit=limit, offset=offset)


@router.get("/construction/{construction_id}", response_model=StorageListResponseDTO)
async def get_storages_by_construction(
    construction_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """Get storages by construction ID."""
    return await storage_use_cases.get_storages_by_construction_id(
        construction_id=construction_id,
        limit=limit,
        offset=offset
    )


@router.get("/search", response_model=StorageListResponseDTO)
async def search_storages(
    query: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    construction_id: UUID = Query(None, description="Filter by construction ID"),
    storage_use_cases: StorageUseCases = Depends(get_storage_use_cases)
):
    """Search storages by name and optionally filter by construction ID."""
    search_dto = StorageSearchDTO(
        query=query, 
        page=page, 
        size=size, 
        construction_id=construction_id
    )
    return await storage_use_cases.search_storages(search_dto)

