"""
Material API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.material_dto import (
    MaterialCreateDTO,
    MaterialUpdateDTO,
    MaterialResponseDTO,
    MaterialListResponseDTO,
    MaterialSearchDTO
)
from src.application.use_cases.material_use_cases import MaterialUseCases
from src.infrastructure.api.dependencies import get_material_use_cases

router = APIRouter()


@router.get("/public", response_model=List[MaterialResponseDTO])
async def list_materials_public(
    limit: int = 100,
    offset: int = 0,
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """List all materials (public endpoint for testing)."""
    result = await material_use_cases.list_all_materials(limit=limit, offset=offset)
    return result.materials


@router.post("/", response_model=MaterialResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_material(
    material_dto: MaterialCreateDTO,
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """Create a new material."""
    return await material_use_cases.create_material(material_dto)


@router.get("/{material_id}", response_model=MaterialResponseDTO)
async def get_material(
    material_id: UUID,
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """Get material by ID."""
    return await material_use_cases.get_material_by_id(material_id)


@router.put("/{material_id}", response_model=MaterialResponseDTO)
async def update_material(
    material_id: UUID,
    material_dto: MaterialUpdateDTO,
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """Update material."""
    return await material_use_cases.update_material(material_id, material_dto)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: UUID,
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """Delete material."""
    await material_use_cases.delete_material(material_id)


@router.get("/", response_model=MaterialListResponseDTO)
async def list_materials(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """List all materials."""
    return await material_use_cases.list_all_materials(limit=limit, offset=offset)


@router.get("/category/{category_id}", response_model=MaterialListResponseDTO)
async def get_materials_by_category(
    category_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """Get materials by category ID."""
    return await material_use_cases.get_materials_by_category(category_id, limit=limit, offset=offset)


@router.get("/search", response_model=MaterialListResponseDTO)
async def search_materials(
    query: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    category_id: str = Query(None, description="Filter by category ID (UUID)"),
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """Search materials by name and optionally filter by category."""
    category_uuid = None
    if category_id:
        try:
            category_uuid = UUID(category_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category ID format: {category_id}"
            )
    
    search_dto = MaterialSearchDTO(query=query, page=page, size=size, category_id=category_uuid)
    return await material_use_cases.search_materials(search_dto)


@router.get("/by-construction/{construction_id}", response_model=MaterialListResponseDTO)
async def get_materials_by_construction(
    construction_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """Get materials by construction ID."""
    return await material_use_cases.get_materials_by_construction(construction_id, limit=limit, offset=offset)

