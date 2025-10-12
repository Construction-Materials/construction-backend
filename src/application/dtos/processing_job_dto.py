"""
ProcessingJob DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class JobStatusDTO(str, Enum):
    """Job status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProcessingJobCreateDTO(BaseModel):
    """DTO for creating a new processing job."""
    submitted_url: HttpUrl = Field(..., description="URL to process")


class ProcessingJobResponseDTO(BaseModel):
    """DTO for processing job response."""
    job_id: UUID = Field(..., description="Job ID")
    user_id: UUID = Field(..., description="User ID")
    submitted_url: str = Field(..., description="Submitted URL")
    status: JobStatusDTO = Field(..., description="Job status")
    error_message: Optional[str] = Field(None, description="Error message")
    result_recipe_id: Optional[UUID] = Field(None, description="Result recipe ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    class Config:
        from_attributes = True


class ProcessingJobListResponseDTO(BaseModel):
    """DTO for processing job list response."""
    jobs: List[ProcessingJobResponseDTO] = Field(..., description="List of processing jobs")
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


class ProcessingJobStatusUpdateDTO(BaseModel):
    """DTO for updating job status."""
    status: JobStatusDTO = Field(..., description="New job status")
    error_message: Optional[str] = Field(None, description="Error message")
    result_recipe_id: Optional[UUID] = Field(None, description="Result recipe ID")
