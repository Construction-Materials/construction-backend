"""
Storage DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class StorageCreateDTO(BaseModel):
    """DTO for creating a new storage."""
    construction_id: UUID = Field(..., description="Construction ID")
    name: str = Field(..., min_length=1, max_length=100, description="Storage name")


class StorageUpdateDTO(BaseModel):
    """DTO for updating storage."""
    construction_id: Optional[UUID] = Field(None, description="Construction ID")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Storage name")


class StorageResponseDTO(BaseModel):
    """DTO for storage response."""
    storage_id: UUID = Field(..., description="Storage ID")
    construction_id: UUID = Field(..., description="Construction ID")
    name: str = Field(..., description="Storage name")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Enables to create instances from SQLAlchemy models."""
        from_attributes = True 


class StorageListResponseDTO(BaseModel):
    """DTO for storage list response."""
    storages: List[StorageResponseDTO] = Field(..., description="List of storages")
    total: int = Field(..., description="Total number of storages")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class StorageSearchDTO(BaseModel):
    """DTO for storage search."""
    query: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    construction_id: Optional[UUID] = Field(None, description="Filter by construction ID")

