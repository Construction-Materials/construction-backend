"""
Quantity Value Object for RecipeItem entity.
"""

from decimal import Decimal
from typing import Optional
from src.shared.exceptions import ValidationError


class Quantity:
    """Value object representing a quantity with value and unit."""
    
    def __init__(self, value: Decimal, unit: str):
        """Initialize quantity with value and unit."""
        if value < 0:
            raise ValidationError("Quantity value cannot be negative")
        
        if not unit or not unit.strip():
            raise ValidationError("Quantity unit cannot be empty")
        
        self._value = value
        self._unit = unit.strip()
    
    @property
    def value(self) -> Decimal:
        """Get quantity value."""
        return self._value
    
    @property
    def unit(self) -> str:
        """Get quantity unit."""
        return self._unit
    
    def __str__(self) -> str:
        """String representation of quantity."""
        return f"{self._value} {self._unit}"
    
    def __eq__(self, other) -> bool:
        """Check equality with another quantity."""
        if not isinstance(other, Quantity):
            return False
        return self._value == other._value and self._unit == other._unit
    
    def __hash__(self) -> int:
        """Hash for quantity."""
        return hash((self._value, self._unit))
    
    @classmethod
    def from_string(cls, quantity_str: str) -> "Quantity":
        """Create quantity from string like '250 g' or '1.5 cups'."""
        try:
            parts = quantity_str.strip().split(' ', 1)
            if len(parts) != 2:
                raise ValidationError("Invalid quantity format. Expected 'value unit'")
            
            value = Decimal(parts[0])
            unit = parts[1]
            return cls(value, unit)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid quantity format: {quantity_str}") from e
