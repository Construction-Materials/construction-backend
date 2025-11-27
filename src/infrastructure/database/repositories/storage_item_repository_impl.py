"""
StorageItem Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_

from src.domain.entities.storage_item import StorageItem
from src.domain.repositories.storage_item_repository import StorageItemRepository
from src.infrastructure.database.models import StorageItemModel, MaterialModel, CategoryModel
from src.shared.exceptions import DatabaseError


class StorageItemRepositoryImpl(StorageItemRepository):
    """StorageItem repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, storage_item: StorageItem) -> StorageItem:
        """Create a new storage item."""
        try:
            storage_item_model = StorageItemModel(
                construction_id=storage_item.construction_id,
                material_id=storage_item.material_id,
                quantity_value=storage_item.quantity_value,
                created_at=storage_item.created_at
            )
            
            self._session.add(storage_item_model)
            await self._session.commit()
            await self._session.refresh(storage_item_model)
            
            return self._to_domain(storage_item_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create storage item: {str(e)}") from e
    
    async def create_bulk(self, storage_items: List[StorageItem]) -> List[StorageItem]:
        """Create multiple storage items at once."""
        try:
            storage_item_models = [
                StorageItemModel(
                    construction_id=storage_item.construction_id,
                    material_id=storage_item.material_id,
                    quantity_value=storage_item.quantity_value,
                    created_at=storage_item.created_at
                )
                for storage_item in storage_items
            ]
            
            self._session.add_all(storage_item_models)
            await self._session.commit()
            
            # Refresh all models to get database-generated values
            for storage_item_model in storage_item_models:
                await self._session.refresh(storage_item_model)
            
            return [self._to_domain(storage_item_model) for storage_item_model in storage_item_models]
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create storage items in bulk: {str(e)}") from e
    
    async def get_by_ids(self, construction_id: UUID, material_id: UUID) -> Optional[StorageItem]:
        """Get storage item by construction ID and material ID."""
        try:
            result = await self._session.execute(
                select(StorageItemModel).where(
                    and_(
                        StorageItemModel.construction_id == construction_id,
                        StorageItemModel.material_id == material_id
                    )
                )
            )
            storage_item_model = result.scalar_one_or_none()
            
            return self._to_domain(storage_item_model) if storage_item_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get storage item by IDs: {str(e)}") from e
    
    async def update(self, storage_item: StorageItem) -> StorageItem:
        """Update existing storage item."""
        try:
            result = await self._session.execute(
                select(StorageItemModel).where(
                    and_(
                        StorageItemModel.construction_id == storage_item.construction_id,
                        StorageItemModel.material_id == storage_item.material_id
                    )
                )
            )
            storage_item_model = result.scalar_one_or_none()
            
            if not storage_item_model:
                raise DatabaseError(
                    f"Storage item with construction_id {storage_item.construction_id} "
                    f"and material_id {storage_item.material_id} not found"
                )
            
            storage_item_model.quantity_value = storage_item.quantity_value
            
            await self._session.commit()
            await self._session.refresh(storage_item_model)
            
            return self._to_domain(storage_item_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update storage item: {str(e)}") from e
    
    async def delete(self, construction_id: UUID, material_id: UUID) -> bool:
        """Delete storage item by construction ID and material ID."""
        try:
            result = await self._session.execute(
                delete(StorageItemModel).where(
                    and_(
                        StorageItemModel.construction_id == construction_id,
                        StorageItemModel.material_id == material_id
                    )
                )
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete storage item: {str(e)}") from e
    
    async def get_by_construction_id(self, construction_id: UUID, limit: int = 100, offset: int = 0) -> List[StorageItem]:
        """Get storage items by construction ID."""
        try:
            result = await self._session.execute(
                select(StorageItemModel)
                .where(StorageItemModel.construction_id == construction_id)
                .offset(offset)
                .limit(limit)
                .order_by(StorageItemModel.created_at.desc())
            )
            storage_item_models = result.scalars().all()
            
            return [self._to_domain(storage_item_model) for storage_item_model in storage_item_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get storage items by construction ID: {str(e)}") from e
    
    async def get_by_material_id(self, material_id: UUID, limit: int = 100, offset: int = 0) -> List[StorageItem]:
        """Get storage items by material ID."""
        try:
            result = await self._session.execute(
                select(StorageItemModel)
                .where(StorageItemModel.material_id == material_id)
                .offset(offset)
                .limit(limit)
                .order_by(StorageItemModel.created_at.desc())
            )
            storage_item_models = result.scalars().all()
            
            return [self._to_domain(storage_item_model) for storage_item_model in storage_item_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get storage items by material ID: {str(e)}") from e
    
    async def count_all(self) -> int:
        """Count total number of storage items."""
        try:
            result = await self._session.execute(
                select(func.count()).select_from(StorageItemModel)
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count storage items: {str(e)}") from e
    
    async def get_materials_by_construction_id(self, construction_id: UUID) -> List[dict]:
        """Get materials with details by construction ID."""
        try:
            result = await self._session.execute(
                select(
                    StorageItemModel.construction_id,
                    StorageItemModel.material_id,
                    MaterialModel.name,
                    CategoryModel.name.label('category_name'),
                    MaterialModel.description,
                    MaterialModel.unit,
                    StorageItemModel.quantity_value,
                    StorageItemModel.created_at
                )
                .join(StorageItemModel, MaterialModel.material_id == StorageItemModel.material_id)
                .join(CategoryModel, MaterialModel.category_id == CategoryModel.category_id)
                .where(StorageItemModel.construction_id == construction_id)
                .order_by(MaterialModel.name)
            )
            rows = result.all()
            
            return [
                {
                    'construction_id': row.construction_id,
                    'material_id': row.material_id,
                    'name': row.name,
                    'category': row.category_name,
                    'description': row.description,
                    'unit': row.unit,
                    'quantity_value': row.quantity_value,
                    'created_at': row.created_at
                }
                for row in rows
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to get materials by construction ID: {str(e)}") from e
    
    async def upsert(self, storage_item: StorageItem) -> StorageItem:
        """Create or update storage item. If exists, adds quantity_value to existing."""
        try:
            existing = await self.get_by_ids(storage_item.construction_id, storage_item.material_id)
            
            if existing:
                # Update: add new quantity to existing
                new_quantity = existing.quantity_value + storage_item.quantity_value
                existing.set_quantity_value(new_quantity)
                return await self.update(existing)
            else:
                # Create new
                return await self.create(storage_item)
        except Exception as e:
            raise DatabaseError(f"Failed to upsert storage item: {str(e)}") from e
    
    async def upsert_bulk(self, storage_items: List[StorageItem]) -> List[StorageItem]:
        """Create or update multiple storage items. If exists, adds quantity_value to existing."""
        try:
            result_items = []
            
            for storage_item in storage_items:
                existing = await self.get_by_ids(storage_item.construction_id, storage_item.material_id)
                
                if existing:
                    # Update: add new quantity to existing
                    new_quantity = existing.quantity_value + storage_item.quantity_value
                    existing.set_quantity_value(new_quantity)
                    updated = await self.update(existing)
                    result_items.append(updated)
                else:
                    # Create new
                    created = await self.create(storage_item)
                    result_items.append(created)
            
            return result_items
        except Exception as e:
            raise DatabaseError(f"Failed to upsert storage items in bulk: {str(e)}") from e
    
    def _to_domain(self, storage_item_model: StorageItemModel) -> StorageItem:
        """Convert SQLAlchemy model to domain entity."""
        return StorageItem(
            construction_id=storage_item_model.construction_id,
            material_id=storage_item_model.material_id,
            quantity_value=storage_item_model.quantity_value,
            created_at=storage_item_model.created_at
        )

