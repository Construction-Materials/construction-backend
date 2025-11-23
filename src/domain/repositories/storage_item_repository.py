"""
StorageItem Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.storage_item import StorageItem


class StorageItemRepository(ABC):
    """StorageItem repository interface."""
    
    @abstractmethod
    async def create(self, storage_item: StorageItem) -> StorageItem:
        """Create a new storage item."""
        pass
    
    @abstractmethod
    async def create_bulk(self, storage_items: List[StorageItem]) -> List[StorageItem]:
        """Create multiple storage items at once."""
        pass
    
    @abstractmethod
    async def get_by_ids(self, storage_id: UUID, material_id: UUID) -> Optional[StorageItem]:
        """Get storage item by storage ID and material ID."""
        pass
    
    @abstractmethod
    async def update(self, storage_item: StorageItem) -> StorageItem:
        """Update existing storage item."""
        pass
    
    @abstractmethod
    async def delete(self, storage_id: UUID, material_id: UUID) -> bool:
        """Delete storage item by storage ID and material ID."""
        pass
    
    @abstractmethod
    async def get_by_storage_id(self, storage_id: UUID, limit: int = 100, offset: int = 0) -> List[StorageItem]:
        """Get storage items by storage ID."""
        pass
    
    @abstractmethod
    async def get_by_material_id(self, material_id: UUID, limit: int = 100, offset: int = 0) -> List[StorageItem]:
        """Get storage items by material ID."""
        pass
    
    @abstractmethod
    async def count_all(self) -> int:
        """Count total number of storage items."""
        pass
    
    @abstractmethod
    async def get_materials_by_storage_id(self, storage_id: UUID) -> List[dict]:
        """Get materials with details by storage ID."""
        pass

