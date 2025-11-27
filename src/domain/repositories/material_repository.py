"""
Material Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.materials import Materials


class MaterialRepository(ABC):
    """Material repository interface."""
    
    @abstractmethod
    async def create(self, material: Materials) -> Materials:
        """Create a new material."""
        pass
    
    @abstractmethod
    async def create_bulk(self, materials: List[Materials]) -> List[Materials]:
        """Create multiple materials at once."""
        pass
    
    @abstractmethod
    async def get_by_id(self, material_id: UUID) -> Optional[Materials]:
        """Get material by ID."""
        pass
    
    @abstractmethod
    async def update(self, material: Materials) -> Materials:
        """Update existing material."""
        pass
    
    @abstractmethod
    async def delete(self, material_id: UUID) -> bool:
        """Delete material by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Materials]:
        """List all materials with pagination."""
        pass
    
    @abstractmethod
    async def get_by_category_id(self, category_id: UUID, limit: int = 100, offset: int = 0) -> List[Materials]:
        """Get materials by category ID."""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Materials]:
        """Search materials by name."""
        pass
    
    @abstractmethod
    async def count_all(self) -> int:
        """Count total number of materials."""
        pass
    
    @abstractmethod
    async def get_by_construction_id(self, construction_id: UUID, limit: int = 100, offset: int = 0) -> List[Materials]:
        """Get materials by construction ID (through storages)."""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Materials]:
        """Get material by exact name match (case-insensitive)."""
        pass

