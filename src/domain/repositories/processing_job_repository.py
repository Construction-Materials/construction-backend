"""
ProcessingJob Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.processing_job import ProcessingJob
from src.domain.value_objects.job_status import JobStatus


class ProcessingJobRepository(ABC):
    """Processing job repository interface."""
    
    @abstractmethod
    async def create(self, job: ProcessingJob) -> ProcessingJob:
        """Create a new processing job."""
        pass
    
    @abstractmethod
    async def get_by_id(self, job_id: UUID) -> Optional[ProcessingJob]:
        """Get processing job by ID."""
        pass
    
    @abstractmethod
    async def update(self, job: ProcessingJob) -> ProcessingJob:
        """Update existing processing job."""
        pass
    
    @abstractmethod
    async def delete(self, job_id: UUID) -> bool:
        """Delete processing job by ID."""
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: UUID, limit: int = 100, offset: int = 0) -> List[ProcessingJob]:
        """List processing jobs by user with pagination."""
        pass
    
    @abstractmethod
    async def list_by_status(self, status: JobStatus, limit: int = 100, offset: int = 0) -> List[ProcessingJob]:
        """List processing jobs by status with pagination."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[ProcessingJob]:
        """List all processing jobs with pagination."""
        pass
    
    @abstractmethod
    async def get_active_jobs(self, limit: int = 100) -> List[ProcessingJob]:
        """Get active processing jobs (PENDING or PROCESSING)."""
        pass
