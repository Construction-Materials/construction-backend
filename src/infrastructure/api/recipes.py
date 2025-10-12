"""
Recipe API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.recipe_dto import (
    RecipeCreateDTO, RecipeUpdateDTO, RecipeResponseDTO, 
    RecipeListResponseDTO, RecipeSearchDTO, RecipeIngredientsResponseDTO
)
from src.application.use_cases.recipe_use_cases import RecipeUseCases
from src.infrastructure.api.dependencies import get_recipe_use_cases, get_current_user

router = APIRouter()


@router.get("/public", response_model=List[RecipeResponseDTO])
async def list_recipes_public(
    limit: int = 100,
    offset: int = 0,
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """List all recipes (public endpoint for testing)."""
    result = await recipe_use_cases.list_all_recipes(limit=limit, offset=offset)
    return result.recipes


@router.post("/", response_model=RecipeResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_dto: RecipeCreateDTO,
    current_user: dict = Depends(get_current_user),
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Create a new recipe."""
    return await recipe_use_cases.create_recipe(current_user["user_id"], recipe_dto)


@router.get("/{recipe_id}", response_model=RecipeResponseDTO)
async def get_recipe(
    recipe_id: UUID,
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Get recipe by ID."""
    return await recipe_use_cases.get_recipe_by_id(recipe_id)


@router.get("/{recipe_id}/ingredients", response_model=RecipeIngredientsResponseDTO)
async def get_recipe_ingredients(
    recipe_id: UUID,
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Get ingredients for a specific recipe."""
    return await recipe_use_cases.get_recipe_ingredients(recipe_id)


@router.put("/{recipe_id}", response_model=RecipeResponseDTO)
async def update_recipe(
    recipe_id: UUID,
    recipe_dto: RecipeUpdateDTO,
    current_user: dict = Depends(get_current_user),
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Update recipe."""
    # TODO: Add authorization check to ensure user owns the recipe
    return await recipe_use_cases.update_recipe(recipe_id, recipe_dto)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: UUID,
    current_user: dict = Depends(get_current_user),
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Delete recipe."""
    # TODO: Add authorization check to ensure user owns the recipe
    await recipe_use_cases.delete_recipe(recipe_id)


@router.get("/", response_model=RecipeListResponseDTO)
async def list_recipes(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """List all recipes."""
    return await recipe_use_cases.list_all_recipes(limit=limit, offset=offset)


@router.get("/user/{user_id}", response_model=RecipeListResponseDTO)
async def get_user_recipes(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Get recipes by user."""
    return await recipe_use_cases.get_user_recipes(user_id, limit=limit, offset=offset)


@router.get("/my/recipes", response_model=RecipeListResponseDTO)
async def get_my_recipes(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Get current user's recipes."""
    return await recipe_use_cases.get_user_recipes(current_user["user_id"], limit=limit, offset=offset)


@router.get("/search", response_model=RecipeListResponseDTO)
async def search_recipes(
    query: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    recipe_use_cases: RecipeUseCases = Depends(get_recipe_use_cases)
):
    """Search recipes by title."""
    search_dto = RecipeSearchDTO(query=query, page=page, size=size)
    return await recipe_use_cases.search_recipes(search_dto)
