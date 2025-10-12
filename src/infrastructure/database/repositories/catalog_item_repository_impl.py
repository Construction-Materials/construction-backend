"""
CatalogItem Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from datetime import datetime

from src.domain.entities.catalog_item import CatalogItem
from src.domain.repositories.catalog_item_repository import CatalogItemRepository
from src.infrastructure.database.models import CatalogItemModel
from src.shared.exceptions import DatabaseError


class CatalogItemRepositoryImpl(CatalogItemRepository):
    """Catalog item repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, item: CatalogItem) -> CatalogItem:
        """Create a new catalog item."""
        try:
            item_model = CatalogItemModel(
                item_id=item.id,
                name=item.name,
                last_used=item.last_used
            )
            
            self._session.add(item_model)
            await self._session.commit()
            await self._session.refresh(item_model)
            
            return self._to_domain(item_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create catalog item: {str(e)}") from e
    
    async def get_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        """Get catalog item by ID."""
        try:
            result = await self._session.execute(
                select(CatalogItemModel).where(CatalogItemModel.item_id == item_id)
            )
            item_model = result.scalar_one_or_none()
            
            return self._to_domain(item_model) if item_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get catalog item by ID: {str(e)}") from e
    
    async def get_by_name(self, name: str) -> Optional[CatalogItem]:
        """Get catalog item by name."""
        try:
            result = await self._session.execute(
                select(CatalogItemModel).where(CatalogItemModel.name == name)
            )
            item_model = result.scalar_one_or_none()
            
            return self._to_domain(item_model) if item_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get catalog item by name: {str(e)}") from e
    
    async def update(self, item: CatalogItem) -> CatalogItem:
        """Update existing catalog item."""
        try:
            result = await self._session.execute(
                select(CatalogItemModel).where(CatalogItemModel.item_id == item.id)
            )
            item_model = result.scalar_one_or_none()
            
            if not item_model:
                raise DatabaseError(f"Catalog item with ID {item.id} not found")
            
            item_model.name = item.name
            item_model.last_used = item.last_used
            
            await self._session.commit()
            await self._session.refresh(item_model)
            
            return self._to_domain(item_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update catalog item: {str(e)}") from e
    
    async def delete(self, item_id: UUID) -> bool:
        """Delete catalog item by ID."""
        try:
            result = await self._session.execute(
                delete(CatalogItemModel).where(CatalogItemModel.item_id == item_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete catalog item: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[CatalogItem]:
        """List all catalog items with pagination."""
        try:
            result = await self._session.execute(
                select(CatalogItemModel)
                .offset(offset)
                .limit(limit)
                .order_by(CatalogItemModel.last_used.desc().nulls_last(), CatalogItemModel.name)
            )
            item_models = result.scalars().all()
            
            return [self._to_domain(item_model) for item_model in item_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list catalog items: {str(e)}") from e
    
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[CatalogItem]:
        """Search catalog items by name."""
        try:
            result = await self._session.execute(
                select(CatalogItemModel)
                .where(CatalogItemModel.name.ilike(f"%{name}%"))
                .offset(offset)
                .limit(limit)
                .order_by(CatalogItemModel.last_used.desc().nulls_last(), CatalogItemModel.name)
            )
            item_models = result.scalars().all()
            
            return [self._to_domain(item_model) for item_model in item_models]
        except Exception as e:
            raise DatabaseError(f"Failed to search catalog items by name: {str(e)}") from e
    
    async def exists_by_name(self, name: str) -> bool:
        """Check if catalog item exists by name."""
        try:
            result = await self._session.execute(
                select(CatalogItemModel.item_id).where(CatalogItemModel.name == name)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise DatabaseError(f"Failed to check catalog item existence: {str(e)}") from e
    
    async def count_all(self) -> int:
        """Count total number of catalog items."""
        try:
            result = await self._session.execute(
                select(func.count(CatalogItemModel.item_id))
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count catalog items: {str(e)}") from e
    
    def _to_domain(self, item_model: CatalogItemModel) -> CatalogItem:
        """Convert SQLAlchemy model to domain entity."""
        return CatalogItem(
            item_id=item_model.item_id,
            name=item_model.name,
            last_used=item_model.last_used
        )
