"""
Construction API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.construction_dto import (
    ConstructionCreateDTO,
    ConstructionUpdateDTO,
    ConstructionResponseDTO,
    ConstructionListResponseDTO,
    ConstructionSearchDTO
)
from src.application.use_cases.construction_use_cases import ConstructionUseCases
from src.infrastructure.api.dependencies import get_construction_use_cases

router = APIRouter()


@router.get("/public", response_model=List[ConstructionResponseDTO])
async def list_constructions_public(
    limit: int = 100,
    offset: int = 0,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """List all constructions (public endpoint for testing)."""
    result = await construction_use_cases.list_all_constructions(limit=limit, offset=offset)
    return result.constructions


@router.post("/", response_model=ConstructionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_construction(
    construction_dto: ConstructionCreateDTO,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Create a new construction."""
    return await construction_use_cases.create_construction(construction_dto)


@router.get("/{construction_id}", response_model=ConstructionResponseDTO)
async def get_construction(
    construction_id: UUID,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Get construction by ID."""
    return await construction_use_cases.get_construction_by_id(construction_id)


@router.put("/{construction_id}", response_model=ConstructionResponseDTO)
async def update_construction(
    construction_id: UUID,
    construction_dto: ConstructionUpdateDTO,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Update construction."""
    return await construction_use_cases.update_construction(construction_id, construction_dto)


@router.delete("/{construction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_construction(
    construction_id: UUID,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Delete construction."""
    await construction_use_cases.delete_construction(construction_id)


@router.get("/", response_model=ConstructionListResponseDTO)
async def list_constructions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """List all constructions."""
    return await construction_use_cases.list_all_constructions(limit=limit, offset=offset)


@router.get("/search", response_model=ConstructionListResponseDTO)
async def search_constructions(
    query: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: str = Query(None, description="Filter by status (active, in_progress, inactive, archived, deleted)"),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Search constructions by name and optionally filter by status."""
    from src.application.dtos.construction_dto import ConstructionStatus
    
    status_enum = None
    if status:
        try:
            status_enum = ConstructionStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Valid values: {[s.value for s in ConstructionStatus]}"
            )
    
    search_dto = ConstructionSearchDTO(query=query, page=page, size=size, status=status_enum)
    return await construction_use_cases.search_constructions(search_dto)

