"""
StorageItem DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class StorageItemCreateDTO(BaseModel):
    """DTO for creating a new storage item."""
    storage_id: UUID = Field(..., description="Storage ID")
    material_id: UUID = Field(..., description="Material ID")
    quantity_value: Decimal = Field(..., ge=0, description="Quantity value")


class StorageItemUpdateDTO(BaseModel):
    """DTO for updating storage item."""
    quantity_value: Optional[Decimal] = Field(None, ge=0, description="Quantity value")


class StorageItemResponseDTO(BaseModel):
    """DTO for storage item response."""
    storage_id: UUID = Field(..., description="Storage ID")
    material_id: UUID = Field(..., description="Material ID")
    quantity_value: Decimal = Field(..., description="Quantity value")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Enables to create instances from SQLAlchemy models."""
        from_attributes = True 


class StorageItemListResponseDTO(BaseModel):
    """DTO for storage item list response."""
    storage_items: List[StorageItemResponseDTO] = Field(..., description="List of storage items")
    total: int = Field(..., description="Total number of storage items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class StorageItemMaterialDTO(BaseModel):
    """DTO for storage item with material details."""
    storage_id: UUID = Field(..., description="Storage ID")
    material_id: UUID = Field(..., description="Material ID")
    name: str = Field(..., description="Material name")
    category: str = Field(..., description="Category name")
    description: str = Field(..., description="Material description")
    unit: str = Field(..., description="Material unit")
    quantity_value: Decimal = Field(..., description="Quantity value in storage")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Enables to create instances from SQLAlchemy models."""
        from_attributes = True


class StorageItemMaterialListResponseDTO(BaseModel):
    """DTO for storage item material list response."""
    materials: List[StorageItemMaterialDTO] = Field(..., description="List of materials with details")

