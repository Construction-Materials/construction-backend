"""
StorageItem API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.storage_item_dto import (
    StorageItemCreateDTO,
    StorageItemUpdateDTO,
    StorageItemResponseDTO,
    StorageItemListResponseDTO
)
from src.application.use_cases.storage_item_use_cases import StorageItemUseCases
from src.infrastructure.api.dependencies import get_storage_item_use_cases

router = APIRouter()


@router.post("/", response_model=StorageItemResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_storage_item(
    storage_item_dto: StorageItemCreateDTO,
    storage_item_use_cases: StorageItemUseCases = Depends(get_storage_item_use_cases)
):
    """Create a new storage item."""
    return await storage_item_use_cases.create_storage_item(storage_item_dto)


@router.get("/storage/{storage_id}/material/{material_id}", response_model=StorageItemResponseDTO)
async def get_storage_item(
    storage_id: UUID,
    material_id: UUID,
    storage_item_use_cases: StorageItemUseCases = Depends(get_storage_item_use_cases)
):
    """Get storage item by storage ID and material ID."""
    return await storage_item_use_cases.get_storage_item_by_ids(storage_id, material_id)


@router.put("/storage/{storage_id}/material/{material_id}", response_model=StorageItemResponseDTO)
async def update_storage_item(
    storage_id: UUID,
    material_id: UUID,
    storage_item_dto: StorageItemUpdateDTO,
    storage_item_use_cases: StorageItemUseCases = Depends(get_storage_item_use_cases)
):
    """Update storage item."""
    return await storage_item_use_cases.update_storage_item(storage_id, material_id, storage_item_dto)


@router.delete("/storage/{storage_id}/material/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_storage_item(
    storage_id: UUID,
    material_id: UUID,
    storage_item_use_cases: StorageItemUseCases = Depends(get_storage_item_use_cases)
):
    """Delete storage item."""
    await storage_item_use_cases.delete_storage_item(storage_id, material_id)


@router.get("/storage/{storage_id}", response_model=StorageItemListResponseDTO)
async def get_storage_items_by_storage(
    storage_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    storage_item_use_cases: StorageItemUseCases = Depends(get_storage_item_use_cases)
):
    """Get storage items by storage ID."""
    return await storage_item_use_cases.get_storage_items_by_storage_id(
        storage_id=storage_id,
        limit=limit,
        offset=offset
    )


@router.get("/material/{material_id}", response_model=StorageItemListResponseDTO)
async def get_storage_items_by_material(
    material_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    storage_item_use_cases: StorageItemUseCases = Depends(get_storage_item_use_cases)
):
    """Get storage items by material ID."""
    return await storage_item_use_cases.get_storage_items_by_material_id(
        material_id=material_id,
        limit=limit,
        offset=offset
    )

