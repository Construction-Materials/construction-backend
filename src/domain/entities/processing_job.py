"""
ProcessingJob Domain Entity.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.domain.value_objects.job_status import JobStatus
from src.shared.exceptions import ValidationError


class ProcessingJob:
    """Processing job domain entity for AI extraction tasks."""
    
    def __init__(
        self,
        job_id: Optional[UUID] = None,
        user_id: UUID = None,
        submitted_url: str = "",
        status: JobStatus = JobStatus.PENDING,
        error_message: Optional[str] = None,
        result_recipe_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        """Initialize ProcessingJob entity."""
        if user_id is None:
            raise ValidationError("User ID is required for processing job")
        
        self._id = job_id or uuid4()
        self._user_id = user_id
        self._submitted_url = submitted_url
        self._status = status
        self._error_message = error_message
        self._result_recipe_id = result_recipe_id
        self._created_at = created_at or datetime.utcnow()
        self._completed_at = completed_at
    
    @property
    def id(self) -> UUID:
        """Get job ID."""
        return self._id
    
    @property
    def user_id(self) -> UUID:
        """Get user ID."""
        return self._user_id
    
    @property
    def submitted_url(self) -> str:
        """Get submitted URL."""
        return self._submitted_url
    
    @property
    def status(self) -> JobStatus:
        """Get job status."""
        return self._status
    
    @property
    def error_message(self) -> Optional[str]:
        """Get error message."""
        return self._error_message
    
    @property
    def result_recipe_id(self) -> Optional[UUID]:
        """Get result recipe ID."""
        return self._result_recipe_id
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def completed_at(self) -> Optional[datetime]:
        """Get completion timestamp."""
        return self._completed_at
    
    def set_submitted_url(self, url: str) -> None:
        """Set submitted URL with validation."""
        if not url or not url.strip():
            raise ValidationError("Submitted URL cannot be empty")
        
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            raise ValidationError("Submitted URL must start with http:// or https://")
        
        self._submitted_url = url
    
    def start_processing(self) -> None:
        """Start processing the job."""
        if self._status != JobStatus.PENDING:
            raise ValidationError("Can only start processing from PENDING status")
        
        self._status = JobStatus.PROCESSING
    
    def complete_processing(self, recipe_id: UUID) -> None:
        """Complete processing with result recipe ID."""
        if self._status != JobStatus.PROCESSING:
            raise ValidationError("Can only complete processing from PROCESSING status")
        
        self._status = JobStatus.COMPLETED
        self._result_recipe_id = recipe_id
        self._completed_at = datetime.utcnow()
    
    def fail_processing(self, error_message: str) -> None:
        """Fail processing with error message."""
        if self._status not in [JobStatus.PENDING, JobStatus.PROCESSING]:
            raise ValidationError("Can only fail processing from PENDING or PROCESSING status")
        
        self._status = JobStatus.FAILED
        self._error_message = error_message
        self._completed_at = datetime.utcnow()
    
    def is_terminal(self) -> bool:
        """Check if job is in terminal state."""
        return self._status.is_terminal()
    
    def is_active(self) -> bool:
        """Check if job is active."""
        return self._status.is_active()
    
    def __eq__(self, other) -> bool:
        """Check equality with another processing job."""
        if not isinstance(other, ProcessingJob):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for processing job."""
        return hash(self._id)
