"""
Category API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.category_dto import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
    CategoryResponseDTO,
    CategoryListResponseDTO,
    CategorySearchDTO
)
from src.application.use_cases.category_use_cases import CategoryUseCases
from src.infrastructure.api.dependencies import get_category_use_cases

router = APIRouter()


@router.get("/public", response_model=List[CategoryResponseDTO])
async def list_categories_public(
    limit: int = 100,
    offset: int = 0,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """List all categories (public endpoint for testing)."""
    result = await category_use_cases.list_all_categories(limit=limit, offset=offset)
    return result.categories


@router.post("/", response_model=CategoryResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_dto: CategoryCreateDTO,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """Create a new category."""
    return await category_use_cases.create_category(category_dto)


@router.get("/{category_id}", response_model=CategoryResponseDTO)
async def get_category(
    category_id: UUID,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """Get category by ID."""
    return await category_use_cases.get_category_by_id(category_id)


@router.put("/{category_id}", response_model=CategoryResponseDTO)
async def update_category(
    category_id: UUID,
    category_dto: CategoryUpdateDTO,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """Update category."""
    return await category_use_cases.update_category(category_id, category_dto)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """Delete category."""
    await category_use_cases.delete_category(category_id)


@router.get("/", response_model=CategoryListResponseDTO)
async def list_categories(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """List all categories."""
    return await category_use_cases.list_all_categories(limit=limit, offset=offset)


@router.get("/search", response_model=CategoryListResponseDTO)
async def search_categories(
    query: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """Search categories by name."""
    search_dto = CategorySearchDTO(
        query=query, 
        page=page, 
        size=size
    )
    return await category_use_cases.search_categories(search_dto)

