"""
StorageItem Domain Entity.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from src.shared.exceptions import ValidationError


class StorageItem:
    """StorageItem domain entity."""
    
    def __init__(
        self,
        construction_id: UUID,
        material_id: UUID,
        quantity_value: Decimal,
        created_at: Optional[datetime] = None
    ):
        """Initialize StorageItem entity."""
        if construction_id is None:
            raise ValidationError("Construction ID is required for storage item")
        if material_id is None:
            raise ValidationError("Material ID is required for storage item")
        if quantity_value is None or quantity_value < 0:
            raise ValidationError("Quantity value must be non-negative")
        
        self._construction_id = construction_id
        self._material_id = material_id
        self._quantity_value = quantity_value
        self._created_at = created_at or datetime.utcnow()
    
    @property
    def construction_id(self) -> UUID:
        """Get construction ID."""
        return self._construction_id
    
    @property
    def material_id(self) -> UUID:
        """Get material ID."""
        return self._material_id
    
    @property
    def quantity_value(self) -> Decimal:
        """Get quantity value."""
        return self._quantity_value
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    def set_quantity_value(self, quantity_value: Decimal) -> None:
        """Set quantity value with validation."""
        if quantity_value is None or quantity_value < 0:
            raise ValidationError("Quantity value must be non-negative")
        self._quantity_value = quantity_value
    
    def __eq__(self, other) -> bool:
        """Check equality with another storage item."""
        if not isinstance(other, StorageItem):
            return False
        return self._construction_id == other._construction_id and self._material_id == other._material_id
    
    def __hash__(self) -> int:
        """Hash for storage item."""
        return hash((self._construction_id, self._material_id))

