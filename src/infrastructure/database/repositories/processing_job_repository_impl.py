"""
ProcessingJob Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from src.domain.entities.processing_job import ProcessingJob
from src.domain.repositories.processing_job_repository import ProcessingJobRepository
from src.domain.value_objects.job_status import JobStatus
from src.infrastructure.database.models import ProcessingJobModel
from src.shared.exceptions import DatabaseError


class ProcessingJobRepositoryImpl(ProcessingJobRepository):
    """Processing job repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, job: ProcessingJob) -> ProcessingJob:
        """Create a new processing job."""
        try:
            job_model = ProcessingJobModel(
                job_id=job.id,
                user_id=job.user_id,
                submitted_url=job.submitted_url,
                status=job.status.value,
                error_message=job.error_message,
                result_recipe_id=job.result_recipe_id,
                created_at=job.created_at,
                completed_at=job.completed_at
            )
            
            self._session.add(job_model)
            await self._session.commit()
            await self._session.refresh(job_model)
            
            return self._to_domain(job_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create processing job: {str(e)}") from e
    
    async def get_by_id(self, job_id: UUID) -> Optional[ProcessingJob]:
        """Get processing job by ID."""
        try:
            result = await self._session.execute(
                select(ProcessingJobModel).where(ProcessingJobModel.job_id == job_id)
            )
            job_model = result.scalar_one_or_none()
            
            return self._to_domain(job_model) if job_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get processing job by ID: {str(e)}") from e
    
    async def update(self, job: ProcessingJob) -> ProcessingJob:
        """Update existing processing job."""
        try:
            result = await self._session.execute(
                select(ProcessingJobModel).where(ProcessingJobModel.job_id == job.id)
            )
            job_model = result.scalar_one_or_none()
            
            if not job_model:
                raise DatabaseError(f"Processing job with ID {job.id} not found")
            
            job_model.status = job.status.value
            job_model.error_message = job.error_message
            job_model.result_recipe_id = job.result_recipe_id
            job_model.completed_at = job.completed_at
            
            await self._session.commit()
            await self._session.refresh(job_model)
            
            return self._to_domain(job_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update processing job: {str(e)}") from e
    
    async def delete(self, job_id: UUID) -> bool:
        """Delete processing job by ID."""
        try:
            result = await self._session.execute(
                delete(ProcessingJobModel).where(ProcessingJobModel.job_id == job_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete processing job: {str(e)}") from e
    
    async def list_by_user(self, user_id: UUID, limit: int = 100, offset: int = 0) -> List[ProcessingJob]:
        """List processing jobs by user with pagination."""
        try:
            result = await self._session.execute(
                select(ProcessingJobModel)
                .where(ProcessingJobModel.user_id == user_id)
                .offset(offset)
                .limit(limit)
                .order_by(ProcessingJobModel.created_at.desc())
            )
            job_models = result.scalars().all()
            
            return [self._to_domain(job_model) for job_model in job_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list processing jobs by user: {str(e)}") from e
    
    async def list_by_status(self, status: JobStatus, limit: int = 100, offset: int = 0) -> List[ProcessingJob]:
        """List processing jobs by status with pagination."""
        try:
            result = await self._session.execute(
                select(ProcessingJobModel)
                .where(ProcessingJobModel.status == status.value)
                .offset(offset)
                .limit(limit)
                .order_by(ProcessingJobModel.created_at.desc())
            )
            job_models = result.scalars().all()
            
            return [self._to_domain(job_model) for job_model in job_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list processing jobs by status: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[ProcessingJob]:
        """List all processing jobs with pagination."""
        try:
            result = await self._session.execute(
                select(ProcessingJobModel)
                .offset(offset)
                .limit(limit)
                .order_by(ProcessingJobModel.created_at.desc())
            )
            job_models = result.scalars().all()
            
            return [self._to_domain(job_model) for job_model in job_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list processing jobs: {str(e)}") from e
    
    async def get_active_jobs(self, limit: int = 100) -> List[ProcessingJob]:
        """Get active processing jobs (PENDING or PROCESSING)."""
        try:
            result = await self._session.execute(
                select(ProcessingJobModel)
                .where(ProcessingJobModel.status.in_([JobStatus.PENDING.value, JobStatus.PROCESSING.value]))
                .limit(limit)
                .order_by(ProcessingJobModel.created_at.asc())
            )
            job_models = result.scalars().all()
            
            return [self._to_domain(job_model) for job_model in job_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get active processing jobs: {str(e)}") from e
    
    def _to_domain(self, job_model: ProcessingJobModel) -> ProcessingJob:
        """Convert SQLAlchemy model to domain entity."""
        return ProcessingJob(
            job_id=job_model.job_id,
            user_id=job_model.user_id,
            submitted_url=job_model.submitted_url,
            status=JobStatus.from_string(job_model.status),
            error_message=job_model.error_message,
            result_recipe_id=job_model.result_recipe_id,
            created_at=job_model.created_at,
            completed_at=job_model.completed_at
        )
