"""
Catalog Items API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.catalog_item_dto import (
    CatalogItemCreateDTO, CatalogItemUpdateDTO, CatalogItemResponseDTO,
    CatalogItemListResponseDTO, CatalogItemSearchDTO, CatalogItemSimpleDTO,
    CatalogItemSimpleListResponseDTO
)
from src.application.use_cases.catalog_item_use_cases import CatalogItemUseCases
from src.infrastructure.api.dependencies import get_catalog_item_use_cases

router = APIRouter()


@router.get("/public", response_model=List[CatalogItemResponseDTO])
async def list_catalog_items_public(
    limit: int = 100,
    offset: int = 0,
    catalog_item_use_cases: CatalogItemUseCases = Depends(get_catalog_item_use_cases)
):
    """List all catalog items (public endpoint for testing)."""
    result = await catalog_item_use_cases.list_catalog_items(limit=limit, offset=offset)
    return result.items


@router.post("/", response_model=CatalogItemResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_catalog_item(
    item_dto: CatalogItemCreateDTO,
    catalog_item_use_cases: CatalogItemUseCases = Depends(get_catalog_item_use_cases)
):
    """Create a new catalog item."""
    return await catalog_item_use_cases.create_catalog_item(item_dto)


@router.get("/search", response_model=CatalogItemListResponseDTO)
async def search_catalog_items(
    name: str = Query(..., min_length=1, description="Search term for catalog item name"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    catalog_item_use_cases: CatalogItemUseCases = Depends(get_catalog_item_use_cases)
):
    """Search catalog items by name."""
    search_dto = CatalogItemSearchDTO(
        query=name,
        page=(offset // limit) + 1,
        size=limit
    )
    return await catalog_item_use_cases.search_catalog_items(search_dto)


@router.get("/", response_model=CatalogItemSimpleListResponseDTO)
async def list_catalog_items(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    catalog_item_use_cases: CatalogItemUseCases = Depends(get_catalog_item_use_cases)
):
    """List all catalog items (sorted by last_used, without last_used field)."""
    return await catalog_item_use_cases.list_catalog_items_simple(limit=limit, offset=offset)


@router.get("/{item_id}", response_model=CatalogItemResponseDTO)
async def get_catalog_item(
    item_id: UUID,
    catalog_item_use_cases: CatalogItemUseCases = Depends(get_catalog_item_use_cases)
):
    """Get catalog item by ID."""
    return await catalog_item_use_cases.get_catalog_item(item_id)


@router.put("/{item_id}", response_model=CatalogItemResponseDTO)
async def update_catalog_item(
    item_id: UUID,
    item_dto: CatalogItemUpdateDTO,
    catalog_item_use_cases: CatalogItemUseCases = Depends(get_catalog_item_use_cases)
):
    """Update catalog item."""
    return await catalog_item_use_cases.update_catalog_item(item_id, item_dto)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog_item(
    item_id: UUID,
    catalog_item_use_cases: CatalogItemUseCases = Depends(get_catalog_item_use_cases)
):
    """Delete catalog item."""
    await catalog_item_use_cases.delete_catalog_item(item_id)
