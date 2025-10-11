"""
CatalogItem Domain Entity.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.shared.exceptions import ValidationError


class CatalogItem:
    """Catalog item domain entity for unique ingredients."""
    
    def __init__(
        self,
        item_id: Optional[UUID] = None,
        name: str = "",
        last_used: Optional[datetime] = None
    ):
        """Initialize CatalogItem entity."""
        self._id = item_id or uuid4()
        self._name = name
        self._last_used = last_used
    
    @property
    def id(self) -> UUID:
        """Get item ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get item name."""
        return self._name
    
    @property
    def last_used(self) -> Optional[datetime]:
        """Get last used timestamp."""
        return self._last_used
    
    def set_name(self, name: str) -> None:
        """Set item name with validation."""
        if not name or not name.strip():
            raise ValidationError("Item name cannot be empty")
        
        self._name = name.strip()
    
    def update_last_used(self) -> None:
        """Update last used timestamp to now."""
        self._last_used = datetime.utcnow()
    
    def __eq__(self, other) -> bool:
        """Check equality with another catalog item."""
        if not isinstance(other, CatalogItem):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for catalog item."""
        return hash(self._id)
