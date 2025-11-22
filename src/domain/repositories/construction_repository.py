"""
Construction Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.construction import Construction



class ConstructionRepository(ABC):
    """Construction repository interface."""
    
    @abstractmethod
    async def create(self, construction: Construction) -> Construction:
        """Create a new construction."""
        pass
    
    @abstractmethod
    async def get_by_id(self, construction_id: UUID) -> Optional[Construction]:
        """Get construction by ID."""
        pass
    
    @abstractmethod
    async def update(self, construction: Construction) -> Construction:
        """Update existing construction."""
        pass
    
    @abstractmethod
    async def delete(self, construction_id: UUID) -> bool:
        """Delete construction by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Construction]:
        """List all constructions with pagination."""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Construction]:
        """Search constructions by name."""
        pass
    
    @abstractmethod
    async def count_all(self) -> int:
        """Count total number of constructions."""
        pass