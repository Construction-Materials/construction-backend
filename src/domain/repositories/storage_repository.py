"""
Storage Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.storage import Storage


class StorageRepository(ABC):
    """Storage repository interface."""
    
    @abstractmethod
    async def create(self, storage: Storage) -> Storage:
        """Create a new storage."""
        pass
    
    @abstractmethod
    async def get_by_id(self, storage_id: UUID) -> Optional[Storage]:
        """Get storage by ID."""
        pass
    
    @abstractmethod
    async def update(self, storage: Storage) -> Storage:
        """Update existing storage."""
        pass
    
    @abstractmethod
    async def delete(self, storage_id: UUID) -> bool:
        """Delete storage by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Storage]:
        """List all storages with pagination."""
        pass
    
    @abstractmethod
    async def get_by_construction_id(self, construction_id: UUID, limit: int = 100, offset: int = 0) -> List[Storage]:
        """Get storages by construction ID."""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Storage]:
        """Search storages by name."""
        pass
    
    @abstractmethod
    async def count_all(self) -> int:
        """Count total number of storages."""
        pass

