"""
RecipeItem Domain Entity.
"""

from typing import Optional
from uuid import UUID, uuid4

from src.domain.value_objects.quantity import Quantity
from src.shared.exceptions import ValidationError


class RecipeItem:
    """Recipe item domain entity linking Recipe and CatalogItem."""
    
    def __init__(
        self,
        recipe_item_id: Optional[UUID] = None,
        recipe_id: UUID = None,
        item_id: UUID = None,
        quantity: Optional[Quantity] = None
    ):
        """Initialize RecipeItem entity."""
        if recipe_id is None:
            raise ValidationError("Recipe ID is required for recipe item")
        
        if item_id is None:
            raise ValidationError("Item ID is required for recipe item")
        
        self._id = recipe_item_id or uuid4()
        self._recipe_id = recipe_id
        self._item_id = item_id
        self._quantity = quantity
    
    @property
    def id(self) -> UUID:
        """Get recipe item ID."""
        return self._id
    
    @property
    def recipe_id(self) -> UUID:
        """Get recipe ID."""
        return self._recipe_id
    
    @property
    def item_id(self) -> UUID:
        """Get catalog item ID."""
        return self._item_id
    
    @property
    def quantity(self) -> Optional[Quantity]:
        """Get quantity."""
        return self._quantity
    
    def set_quantity(self, quantity: Quantity) -> None:
        """Set quantity."""
        if quantity is None:
            raise ValidationError("Quantity cannot be None")
        
        self._quantity = quantity
    
    def __eq__(self, other) -> bool:
        """Check equality with another recipe item."""
        if not isinstance(other, RecipeItem):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for recipe item."""
        return hash(self._id)
