"""
Construction Domain Entity.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from src.shared.exceptions import ValidationError
from src.domain.value_objects.construction_status import ConstructionStatus


class Construction:
    """Construction domain entity."""
    
    def __init__(
        self,
        construction_id: Optional[UUID] = None,
        name: str = "",
        description: str = "",
        address: str = "",
        status: ConstructionStatus = ConstructionStatus.INACTIVE,
        created_at: Optional[datetime] = None
    ):
        """Initialize Construction entity."""
        if name is None:
            raise ValidationError("Name is required for construction")
        
        self._id = construction_id or uuid4()
        self._name = name
        self._description = description
        self._address = address
        self._status = status
        self._created_at = created_at or datetime.utcnow()
    
    @property
    def id(self) -> UUID:
        """Get construction ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get construction name."""
        return self._name
    
    @property
    def description(self) -> str:
        """Get construction description."""
        return self._description
    
    @property
    def address(self) -> str:
        """Get construction address."""
        return self._address
    
    @property
    def status(self) -> ConstructionStatus:
        """Get construction status."""
        return self._status
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def set_status(self, status: ConstructionStatus) -> None:
        """Set construction status."""
        self._status = status
    
    @property
    def set_name(self, name: str) -> None:
        """Set construction name with validation."""
        if not name or not name.strip():
            raise ValidationError("Construction name cannot be empty")
        
        self._name = name.strip()
    
    def set_description(self, description: str) -> None:
        """Set construction description with validation."""
        if not description or not description.strip():
            raise ValidationError("Construction description cannot be empty")
        
        self._description = description.strip()
    
    def set_address(self, address: str) -> None:
        """Set construction address."""
        self._address = address.strip() if address else ""
    
    def set_status(self, status: ConstructionStatus) -> None:
        """Set construction status."""
        self._status = status   
    
    def __eq__(self, other) -> bool:
        """Check equality with another recipe."""
        if not isinstance(other, Recipe):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for recipe."""
        return hash(self._id)
