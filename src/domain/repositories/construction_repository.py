"""
ConstructionItem Repository Interface (Port).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.construction_item import ConstructionItem


class ConstructionItemRepository(ABC):
    """Construction item repository interface."""
    
    @abstractmethod
    async def create(self, item: ConstructionItem) -> ConstructionItem:
        """Create a new construction item."""
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[ConstructionItem]: