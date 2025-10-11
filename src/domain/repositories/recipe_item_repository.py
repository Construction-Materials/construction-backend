"""
RecipeItem Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.recipe_item import RecipeItem


class RecipeItemRepository(ABC):
    """Recipe item repository interface."""
    
    @abstractmethod
    async def create(self, recipe_item: RecipeItem) -> RecipeItem:
        """Create a new recipe item."""
        pass
    
    @abstractmethod
    async def get_by_id(self, recipe_item_id: UUID) -> Optional[RecipeItem]:
        """Get recipe item by ID."""
        pass
    
    @abstractmethod
    async def get_by_recipe_id(self, recipe_id: UUID) -> List[RecipeItem]:
        """Get all recipe items for a recipe."""
        pass
    
    @abstractmethod
    async def update(self, recipe_item: RecipeItem) -> RecipeItem:
        """Update existing recipe item."""
        pass
    
    @abstractmethod
    async def delete(self, recipe_item_id: UUID) -> bool:
        """Delete recipe item by ID."""
        pass
    
    @abstractmethod
    async def delete_by_recipe_id(self, recipe_id: UUID) -> int:
        """Delete all recipe items for a recipe."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[RecipeItem]:
        """List all recipe items with pagination."""
        pass
