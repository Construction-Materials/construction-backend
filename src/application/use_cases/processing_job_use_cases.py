"""
ProcessingJob Use Cases for Application Layer.
"""

from typing import List
from uuid import UUID

from src.domain.entities.processing_job import ProcessingJob
from src.domain.repositories.processing_job_repository import ProcessingJobRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.job_status import JobStatus
from src.application.dtos.processing_job_dto import (
    ProcessingJobCreateDTO, ProcessingJobResponseDTO, 
    ProcessingJobListResponseDTO, ProcessingJobStatusUpdateDTO
)
from src.shared.exceptions import EntityNotFoundError, ValidationError, BusinessRuleViolationError


class ProcessingJobUseCases:
    """Processing job use cases implementation."""
    
    def __init__(self, job_repository: ProcessingJobRepository, user_repository: UserRepository):
        self._job_repository = job_repository
        self._user_repository = user_repository
    
    async def create_processing_job(self, user_id: UUID, job_dto: ProcessingJobCreateDTO) -> ProcessingJobResponseDTO:
        """Create a new processing job."""
        # Verify user exists
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        # Create domain entity
        job = ProcessingJob(
            user_id=user_id,
            submitted_url=str(job_dto.submitted_url)
        )
        
        # Save to repository
        created_job = await self._job_repository.create(job)
        
        return ProcessingJobResponseDTO(
            job_id=created_job.id,
            user_id=created_job.user_id,
            submitted_url=created_job.submitted_url,
            status=created_job.status.value,
            error_message=created_job.error_message,
            result_recipe_id=created_job.result_recipe_id,
            created_at=created_job.created_at,
            completed_at=created_job.completed_at
        )
    
    async def get_job_by_id(self, job_id: UUID) -> ProcessingJobResponseDTO:
        """Get processing job by ID."""
        job = await self._job_repository.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError("ProcessingJob", str(job_id))
        
        return ProcessingJobResponseDTO(
            job_id=job.id,
            user_id=job.user_id,
            submitted_url=job.submitted_url,
            status=job.status.value,
            error_message=job.error_message,
            result_recipe_id=job.result_recipe_id,
            created_at=job.created_at,
            completed_at=job.completed_at
        )
    
    async def update_job_status(self, job_id: UUID, status_dto: ProcessingJobStatusUpdateDTO) -> ProcessingJobResponseDTO:
        """Update job status."""
        job = await self._job_repository.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError("ProcessingJob", str(job_id))
        
        # Validate status transition
        new_status = JobStatus.from_string(status_dto.status.value)
        
        if new_status == JobStatus.PROCESSING:
            if job.status != JobStatus.PENDING:
                raise BusinessRuleViolationError("Can only start processing from PENDING status")
            job.start_processing()
        
        elif new_status == JobStatus.COMPLETED:
            if job.status != JobStatus.PROCESSING:
                raise BusinessRuleViolationError("Can only complete from PROCESSING status")
            if not status_dto.result_recipe_id:
                raise ValidationError("Result recipe ID is required for completion")
            job.complete_processing(status_dto.result_recipe_id)
        
        elif new_status == JobStatus.FAILED:
            if job.status not in [JobStatus.PENDING, JobStatus.PROCESSING]:
                raise BusinessRuleViolationError("Can only fail from PENDING or PROCESSING status")
            if not status_dto.error_message:
                raise ValidationError("Error message is required for failure")
            job.fail_processing(status_dto.error_message)
        
        # Save changes
        updated_job = await self._job_repository.update(job)
        
        return ProcessingJobResponseDTO(
            job_id=updated_job.id,
            user_id=updated_job.user_id,
            submitted_url=updated_job.submitted_url,
            status=updated_job.status.value,
            error_message=updated_job.error_message,
            result_recipe_id=updated_job.result_recipe_id,
            created_at=updated_job.created_at,
            completed_at=updated_job.completed_at
        )
    
    async def get_user_jobs(self, user_id: UUID, limit: int = 100, offset: int = 0) -> ProcessingJobListResponseDTO:
        """Get processing jobs by user."""
        # Verify user exists
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        jobs = await self._job_repository.list_by_user(user_id, limit=limit, offset=offset)
        
        return ProcessingJobListResponseDTO(
            jobs=[
                ProcessingJobResponseDTO(
                    job_id=job.id,
                    user_id=job.user_id,
                    submitted_url=job.submitted_url,
                    status=job.status.value,
                    error_message=job.error_message,
                    result_recipe_id=job.result_recipe_id,
                    created_at=job.created_at,
                    completed_at=job.completed_at
                )
                for job in jobs
            ],
            total=len(jobs),
            page=(offset // limit) + 1,
            size=limit
        )
    
    async def get_jobs_by_status(self, status: JobStatus, limit: int = 100, offset: int = 0) -> ProcessingJobListResponseDTO:
        """Get processing jobs by status."""
        jobs = await self._job_repository.list_by_status(status, limit=limit, offset=offset)
        
        return ProcessingJobListResponseDTO(
            jobs=[
                ProcessingJobResponseDTO(
                    job_id=job.id,
                    user_id=job.user_id,
                    submitted_url=job.submitted_url,
                    status=job.status.value,
                    error_message=job.error_message,
                    result_recipe_id=job.result_recipe_id,
                    created_at=job.created_at,
                    completed_at=job.completed_at
                )
                for job in jobs
            ],
            total=len(jobs),
            page=(offset // limit) + 1,
            size=limit
        )
    
    async def get_active_jobs(self, limit: int = 100) -> List[ProcessingJobResponseDTO]:
        """Get active processing jobs."""
        jobs = await self._job_repository.get_active_jobs(limit=limit)
        
        return [
            ProcessingJobResponseDTO(
                job_id=job.id,
                user_id=job.user_id,
                submitted_url=job.submitted_url,
                status=job.status.value,
                error_message=job.error_message,
                result_recipe_id=job.result_recipe_id,
                created_at=job.created_at,
                completed_at=job.completed_at
            )
            for job in jobs
        ]
    
    async def delete_job(self, job_id: UUID) -> bool:
        """Delete processing job."""
        job = await self._job_repository.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError("ProcessingJob", str(job_id))
        
        return await self._job_repository.delete(job_id)
