"""
Construction Status Value Object.
"""

from enum import Enum


class ConstructionStatus(str, Enum):
    """Construction status enum."""
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"
    COMPLETED = "completed"
    PLANNED = "planned"


