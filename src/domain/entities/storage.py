"""
Storage Domain Entity.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.shared.exceptions import ValidationError


class Storage:
    """Storage domain entity."""
    
    def __init__(
        self,
        storage_id: Optional[UUID] = None,
        construction_id: UUID = None,
        name: str = "",
        created_at: Optional[datetime] = None
    ):
        """Initialize Storage entity."""
        if name is None:
            raise ValidationError("Name is required for storage")
        if construction_id is None:
            raise ValidationError("Construction ID is required for storage")
        
        self._id = storage_id or uuid4()
        self._construction_id = construction_id
        self._name = name
        self._created_at = created_at or datetime.utcnow()
    
    @property
    def id(self) -> UUID:
        """Get storage ID."""
        return self._id
    
    @property
    def construction_id(self) -> UUID:
        """Get construction ID."""
        return self._construction_id
    
    @property
    def name(self) -> str:
        """Get storage name."""
        return self._name
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    def set_name(self, name: str) -> None:
        """Set storage name with validation."""
        if not name or not name.strip():
            raise ValidationError("Storage name cannot be empty")
        self._name = name.strip()
    
    def set_construction_id(self, construction_id: UUID) -> None:
        """Set construction ID."""
        if construction_id is None:
            raise ValidationError("Construction ID cannot be None")
        self._construction_id = construction_id
    
    def __eq__(self, other) -> bool:
        """Check equality with another storage."""
        if not isinstance(other, Storage):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for storage."""
        return hash(self._id)

