"""
Job Status Value Object for ProcessingJob entity.
"""

from enum import Enum
from typing import Optional


class JobStatus(Enum):
    """Processing job status enumeration."""
    
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
    @classmethod
    def from_string(cls, status: str) -> "JobStatus":
        """Create JobStatus from string."""
        try:
            return cls(status.upper())
        except ValueError:
            raise ValueError(f"Invalid job status: {status}")
    
    def is_terminal(self) -> bool:
        """Check if status is terminal (COMPLETED or FAILED)."""
        return self in [JobStatus.COMPLETED, JobStatus.FAILED]
    
    def is_active(self) -> bool:
        """Check if status is active (PENDING or PROCESSING)."""
        return self in [JobStatus.PENDING, JobStatus.PROCESSING]
