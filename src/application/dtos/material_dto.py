"""
Material DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from src.domain.value_objects.unit_enum import UnitEnum


class MaterialCreateDTO(BaseModel):
    """DTO for creating a new material."""
    category_id: UUID = Field(..., description="Category ID")
    name: str = Field(..., min_length=1, max_length=100, description="Material name")
    description: str = Field(default="", description="Material description")
    unit: UnitEnum = Field(
        default=UnitEnum.OTHER,
        description="Material unit"
    )


class MaterialUpdateDTO(BaseModel):
    """DTO for updating material."""
    category_id: Optional[UUID] = Field(None, description="Category ID")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Material name")
    description: Optional[str] = Field(None, description="Material description")
    unit: Optional[UnitEnum] = Field(None, description="Material unit")


class MaterialResponseDTO(BaseModel):
    """DTO for material response."""
    material_id: UUID = Field(..., description="Material ID")
    category_id: UUID = Field(..., description="Category ID")
    name: str = Field(..., description="Material name")
    description: str = Field(..., description="Material description")
    unit: UnitEnum = Field(..., description="Material unit")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Enables to create instances from SQLAlchemy models."""
        from_attributes = True


class MaterialListResponseDTO(BaseModel):
    """DTO for material list response."""
    materials: List[MaterialResponseDTO] = Field(..., description="List of materials")
    total: int = Field(..., description="Total number of materials")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class MaterialSearchDTO(BaseModel):
    """DTO for material search."""
    query: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    category_id: Optional[UUID] = Field(None, description="Filter by category ID")

