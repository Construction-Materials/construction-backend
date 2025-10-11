"""
Recipe Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.recipe import Recipe


class RecipeRepository(ABC):
    """Recipe repository interface."""
    
    @abstractmethod
    async def create(self, recipe: Recipe) -> Recipe:
        """Create a new recipe."""
        pass
    
    @abstractmethod
    async def get_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        """Get recipe by ID."""
        pass
    
    @abstractmethod
    async def update(self, recipe: Recipe) -> Recipe:
        """Update existing recipe."""
        pass
    
    @abstractmethod
    async def delete(self, recipe_id: UUID) -> bool:
        """Delete recipe by ID."""
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: UUID, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """List recipes by user with pagination."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """List all recipes with pagination."""
        pass
    
    @abstractmethod
    async def search_by_title(self, title: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """Search recipes by title."""
        pass
