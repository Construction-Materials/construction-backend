"""
Materials Domain Entity.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from src.shared.exceptions import ValidationError
from src.domain.value_objects.unit_enum import UnitEnum

class Materials:
    """Materials domain entity."""
    
    def __init__(
        self,
        material_id: Optional[UUID] = None,
        category_id: UUID = None,
        name: str = "",
        description: str = "",
        unit: UnitEnum = UnitEnum.OTHER,
        created_at: Optional[datetime] = None

    ):
        """Initialize Materials entity."""
        if name is None:
            raise ValidationError("Name is required for materials")
        
        self._id = material_id or uuid4()
        self._category_id = category_id
        self._name = name
        self._description = description
        self._unit = unit
        self._created_at = created_at or datetime.utcnow()
    
    @property
    def id(self) -> UUID:
        """Get material ID."""
        return self._id
    
    @property
    def category_id(self) -> UUID:
        """Get category ID."""
        return self._category_id
    
    @property
    def name(self) -> str:
        """Get material name."""
        return self._name
    
    @property
    def description(self) -> str:
        """Get material description."""
        return self._description
    
    @property
    def unit(self) -> UnitEnum:
        """Get material unit."""
        return self._unit
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    def set_name(self, name: str) -> None:
        """Set material name with validation."""
        if not name or not name.strip():
            raise ValidationError("Material name cannot be empty")
        self._name = name.strip()
    
    def set_description(self, description: str) -> None:
        """Set material description with validation."""
        # Pozwól na pusty string dla description
        self._description = description.strip() if description else ""
    
    def set_unit(self, unit: UnitEnum) -> None:
        """Set material unit."""
        self._unit = unit
    
    def set_category_id(self, category_id: UUID) -> None:
        """Set category ID."""
        self._category_id = category_id
    
    def __eq__(self, other) -> bool:
        """Check equality with another material."""
        if not isinstance(other, Materials):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for material."""
        return hash(self._id)