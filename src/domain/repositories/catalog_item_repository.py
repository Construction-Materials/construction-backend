"""
CatalogItem Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.catalog_item import CatalogItem


class CatalogItemRepository(ABC):
    """Catalog item repository interface."""
    
    @abstractmethod
    async def create(self, item: CatalogItem) -> CatalogItem:
        """Create a new catalog item."""
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        """Get catalog item by ID."""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[CatalogItem]:
        """Get catalog item by name."""
        pass
    
    @abstractmethod
    async def update(self, item: CatalogItem) -> CatalogItem:
        """Update existing catalog item."""
        pass
    
    @abstractmethod
    async def delete(self, item_id: UUID) -> bool:
        """Delete catalog item by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[CatalogItem]:
        """List all catalog items with pagination."""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[CatalogItem]:
        """Search catalog items by name."""
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """Check if catalog item exists by name."""
        pass
