"""
Recipe DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl
from decimal import Decimal


class RecipeIngredientDTO(BaseModel):
    """DTO for recipe ingredient."""
    name: str = Field(..., min_length=1, max_length=255, description="Ingredient name")
    quantity_value: Decimal = Field(..., ge=0, description="Quantity value")
    quantity_unit: str = Field(..., min_length=1, max_length=50, description="Quantity unit")


class RecipeCreateDTO(BaseModel):
    """DTO for creating a new recipe."""
    title: str = Field(..., min_length=1, max_length=255, description="Recipe title")
    external_url: Optional[HttpUrl] = Field(None, description="Source URL")
    image_url: Optional[HttpUrl] = Field(None, description="Recipe image URL")
    preparation_steps: str = Field(default="", description="Preparation steps")
    prep_time_minutes: int = Field(default=0, ge=0, description="Preparation time in minutes")
    ingredients: Optional[List[RecipeIngredientDTO]] = Field(default=[], description="Recipe ingredients")


class RecipeUpdateDTO(BaseModel):
    """DTO for updating recipe."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Recipe title")
    external_url: Optional[HttpUrl] = Field(None, description="Source URL")
    image_url: Optional[HttpUrl] = Field(None, description="Recipe image URL")
    preparation_steps: Optional[str] = Field(None, description="Preparation steps")
    prep_time_minutes: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")


class RecipeResponseDTO(BaseModel):
    """DTO for recipe response."""
    recipe_id: UUID = Field(..., description="Recipe ID")
    user_id: UUID = Field(..., description="Owner user ID")
    title: str = Field(..., description="Recipe title")
    external_url: Optional[str] = Field(None, description="Source URL")
    image_url: Optional[str] = Field(None, description="Recipe image URL")
    preparation_steps: str = Field(..., description="Preparation steps")
    prep_time_minutes: int = Field(..., description="Preparation time in minutes")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class RecipeListResponseDTO(BaseModel):
    """DTO for recipe list response."""
    recipes: List[RecipeResponseDTO] = Field(..., description="List of recipes")
    total: int = Field(..., description="Total number of recipes")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class RecipeSearchDTO(BaseModel):
    """DTO for recipe search."""
    query: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")


class RecipeIngredientResponseDTO(BaseModel):
    """DTO for recipe ingredient response."""
    recipe_item_id: UUID = Field(..., description="Recipe item ID")
    ingredient_name: str = Field(..., description="Ingredient name")
    quantity_value: Decimal = Field(..., description="Quantity value")
    quantity_unit: str = Field(..., description="Quantity unit")
    
    class Config:
        from_attributes = True


class RecipeIngredientsResponseDTO(BaseModel):
    """DTO for recipe ingredients list response."""
    recipe_id: UUID = Field(..., description="Recipe ID")
    ingredients: List[RecipeIngredientResponseDTO] = Field(..., description="List of ingredients")
    total: int = Field(..., description="Total number of ingredients")
