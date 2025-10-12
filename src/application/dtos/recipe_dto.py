"""
Recipe DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl


class RecipeCreateDTO(BaseModel):
    """DTO for creating a new recipe."""
    title: str = Field(..., min_length=1, max_length=255, description="Recipe title")
    external_url: Optional[HttpUrl] = Field(None, description="Source URL")
    preparation_steps: str = Field(default="", description="Preparation steps")
    prep_time_minutes: int = Field(default=0, ge=0, description="Preparation time in minutes")


class RecipeUpdateDTO(BaseModel):
    """DTO for updating recipe."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Recipe title")
    external_url: Optional[HttpUrl] = Field(None, description="Source URL")
    preparation_steps: Optional[str] = Field(None, description="Preparation steps")
    prep_time_minutes: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")


class RecipeResponseDTO(BaseModel):
    """DTO for recipe response."""
    recipe_id: UUID = Field(..., description="Recipe ID")
    user_id: UUID = Field(..., description="Owner user ID")
    title: str = Field(..., description="Recipe title")
    external_url: Optional[str] = Field(None, description="Source URL")
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
