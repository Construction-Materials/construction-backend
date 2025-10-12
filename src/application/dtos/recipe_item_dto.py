"""
RecipeItem DTOs for Application Layer.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal


class QuantityDTO(BaseModel):
    """DTO for quantity value object."""
    value: Decimal = Field(..., ge=0, description="Quantity value")
    unit: str = Field(..., min_length=1, max_length=50, description="Quantity unit")


class RecipeItemCreateDTO(BaseModel):
    """DTO for creating a new recipe item."""
    recipe_id: UUID = Field(..., description="Recipe ID")
    item_id: UUID = Field(..., description="Catalog item ID")
    quantity: QuantityDTO = Field(..., description="Quantity with unit")


class RecipeItemUpdateDTO(BaseModel):
    """DTO for updating recipe item."""
    quantity: Optional[QuantityDTO] = Field(None, description="Quantity with unit")


class RecipeItemResponseDTO(BaseModel):
    """DTO for recipe item response."""
    recipe_item_id: UUID = Field(..., description="Recipe item ID")
    recipe_id: UUID = Field(..., description="Recipe ID")
    item_id: UUID = Field(..., description="Catalog item ID")
    quantity: Optional[QuantityDTO] = Field(None, description="Quantity with unit")
    
    class Config:
        from_attributes = True


class RecipeItemListResponseDTO(BaseModel):
    """DTO for recipe item list response."""
    items: List[RecipeItemResponseDTO] = Field(..., description="List of recipe items")
    total: int = Field(..., description="Total number of items")
