"""
Category DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class CategoryCreateDTO(BaseModel):
    """DTO for creating a new category."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")


class CategoryUpdateDTO(BaseModel):
    """DTO for updating category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")


class CategoryResponseDTO(BaseModel):
    """DTO for category response."""
    category_id: UUID = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Enables to create instances from SQLAlchemy models."""
        from_attributes = True 


class CategoryListResponseDTO(BaseModel):
    """DTO for category list response."""
    categories: List[CategoryResponseDTO] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class CategorySearchDTO(BaseModel):
    """DTO for category search."""
    query: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")

