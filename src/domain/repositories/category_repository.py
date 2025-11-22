"""
Category Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.category import Category


class CategoryRepository(ABC):
    """Category repository interface."""
    
    @abstractmethod
    async def create(self, category: Category) -> Category:
        """Create a new category."""
        pass
    
    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID."""
        pass
    
    @abstractmethod
    async def update(self, category: Category) -> Category:
        """Update existing category."""
        pass
    
    @abstractmethod
    async def delete(self, category_id: UUID) -> bool:
        """Delete category by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Category]:
        """List all categories with pagination."""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Category]:
        """Search categories by name."""
        pass
    
    @abstractmethod
    async def count_all(self) -> int:
        """Count total number of categories."""
        pass
