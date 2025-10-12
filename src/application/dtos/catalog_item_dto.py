"""
CatalogItem DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class CatalogItemCreateDTO(BaseModel):
    """DTO for creating a new catalog item."""
    name: str = Field(..., min_length=1, max_length=100, description="Item name")


class CatalogItemUpdateDTO(BaseModel):
    """DTO for updating catalog item."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Item name")


class CatalogItemResponseDTO(BaseModel):
    """DTO for catalog item response."""
    item_id: UUID = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    last_used: Optional[datetime] = Field(None, description="Last used timestamp")
    
    class Config:
        from_attributes = True


class CatalogItemListResponseDTO(BaseModel):
    """DTO for catalog item list response."""
    items: List[CatalogItemResponseDTO] = Field(..., description="List of catalog items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class CatalogItemSearchDTO(BaseModel):
    """DTO for catalog item search."""
    query: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
