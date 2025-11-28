"""
Construction DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from src.domain.value_objects.construction_status import ConstructionStatus


class ConstructionCreateDTO(BaseModel):
    """DTO for creating a new construction."""
    name: str = Field(..., min_length=1, max_length=100, description="Construction name")
    description: str = Field(default="", description="Construction description")
    address: str = Field(default="", max_length=255, description="Construction address")
    start_date: Optional[datetime] = Field(None, description="Construction start date")
    status: ConstructionStatus = Field(
        default=ConstructionStatus.INACTIVE,
        description="Construction status"
    )
    img_url: Optional[str] = Field(None, max_length=500, description="Construction image URL")


class ConstructionUpdateDTO(BaseModel):
    """DTO for updating construction."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Construction name")
    description: Optional[str] = Field(None, description="Construction description")
    address: Optional[str] = Field(None, max_length=255, description="Construction address")
    start_date: Optional[datetime] = Field(None, description="Construction start date")
    status: Optional[ConstructionStatus] = Field(None, description="Construction status")
    img_url: Optional[str] = Field(None, max_length=500, description="Construction image URL")


class ConstructionResponseDTO(BaseModel):
    """DTO for construction response."""
    construction_id: UUID = Field(..., description="Construction ID")
    name: str = Field(..., description="Construction name")
    description: str = Field(..., description="Construction description")
    address: str = Field(..., description="Construction address")
    start_date: Optional[datetime] = Field(None, description="Construction start date")
    status: ConstructionStatus = Field(..., description="Construction status")
    img_url: Optional[str] = Field(None, description="Construction image URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Enables to create instances from SQLAlchemy models."""
        from_attributes = True 


class ConstructionListResponseDTO(BaseModel):
    """DTO for construction list response."""
    constructions: List[ConstructionResponseDTO] = Field(..., description="List of constructions")
    total: int = Field(..., description="Total number of constructions")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class ConstructionSearchDTO(BaseModel):
    """DTO for construction search."""
    query: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    status: Optional[ConstructionStatus] = Field(None, description="Filter by status")


class ConstructionStatisticsDTO(BaseModel):
    """DTO for construction statistics."""
    construction_id: UUID = Field(..., description="Construction ID")
    construction_name: Optional[str] = Field(None, description="Construction name")
    total_items: int = Field(default=0, description="Total number of unique materials")
    total_quantity: float = Field(default=0.0, description="Total quantity of all materials")
    measured_at: datetime = Field(..., description="Measurement timestamp")
    last_sync_at: datetime = Field(..., description="Last synchronization timestamp")

    class Config:
        """Enables to create instances from SQLAlchemy models."""
        from_attributes = True

