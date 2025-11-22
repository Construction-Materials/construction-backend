"""
Category Domain Entity.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from src.shared.exceptions import ValidationError

class Category:
    """Category domain entity."""
    
    def __init__(
        self,
        category_id: Optional[UUID] = None,
        name: str = "",
        created_at: Optional[datetime] = None
    ):
        """Initialize Category entity."""
        if name is None:
            raise ValidationError("Name is required for category")
        
        self._id = category_id or uuid4()
        self._name = name
        self._created_at = created_at or datetime.utcnow()
    
    @property
    def id(self) -> UUID:
        """Get category ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get category name."""
        return self._name
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def set_name(self, name: str) -> None:
        """Set construction name with validation."""
        if not name or not name.strip():
            raise ValidationError("Construction name cannot be empty")
        
        self._name = name.strip()
    
    def __eq__(self, other) -> bool:
        """Check equality with another category."""
        if not isinstance(other, Category):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for category."""
        return hash(self._id)
