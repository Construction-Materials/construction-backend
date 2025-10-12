"""
ProcessingJob API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.application.dtos.processing_job_dto import (
    ProcessingJobCreateDTO, ProcessingJobResponseDTO, 
    ProcessingJobListResponseDTO, ProcessingJobStatusUpdateDTO,
    JobStatusDTO
)
from src.application.use_cases.processing_job_use_cases import ProcessingJobUseCases
from src.domain.value_objects.job_status import JobStatus
from src.infrastructure.api.dependencies import get_processing_job_use_cases, get_current_user

router = APIRouter()


@router.post("/", response_model=ProcessingJobResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_processing_job(
    job_dto: ProcessingJobCreateDTO,
    current_user: dict = Depends(get_current_user),
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """Create a new processing job."""
    return await job_use_cases.create_processing_job(current_user["user_id"], job_dto)


@router.get("/{job_id}", response_model=ProcessingJobResponseDTO)
async def get_processing_job(
    job_id: UUID,
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """Get processing job by ID."""
    return await job_use_cases.get_job_by_id(job_id)


@router.put("/{job_id}/status", response_model=ProcessingJobResponseDTO)
async def update_job_status(
    job_id: UUID,
    status_dto: ProcessingJobStatusUpdateDTO,
    current_user: dict = Depends(get_current_user),
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """Update job status (admin only)."""
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await job_use_cases.update_job_status(job_id, status_dto)


@router.get("/", response_model=ProcessingJobListResponseDTO)
async def list_processing_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """List processing jobs for current user."""
    return await job_use_cases.get_user_jobs(current_user["user_id"], limit=limit, offset=offset)


@router.get("/user/{user_id}", response_model=ProcessingJobListResponseDTO)
async def get_user_jobs(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """Get processing jobs by user (admin only)."""
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await job_use_cases.get_user_jobs(user_id, limit=limit, offset=offset)


@router.get("/status/{status}", response_model=ProcessingJobListResponseDTO)
async def get_jobs_by_status(
    status: JobStatusDTO,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """Get processing jobs by status (admin only)."""
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    job_status = JobStatus.from_string(status.value)
    return await job_use_cases.get_jobs_by_status(job_status, limit=limit, offset=offset)


@router.get("/active", response_model=List[ProcessingJobResponseDTO])
async def get_active_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """Get active processing jobs (admin only)."""
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await job_use_cases.get_active_jobs(limit=limit)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_processing_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    job_use_cases: ProcessingJobUseCases = Depends(get_processing_job_use_cases)
):
    """Delete processing job."""
    # TODO: Add authorization check to ensure user owns the job or is admin
    await job_use_cases.delete_job(job_id)
