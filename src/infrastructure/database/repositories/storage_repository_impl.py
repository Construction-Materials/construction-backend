"""
Storage Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from src.domain.entities.storage import Storage
from src.domain.repositories.storage_repository import StorageRepository
from src.infrastructure.database.models import StorageModel
from src.shared.exceptions import DatabaseError


class StorageRepositoryImpl(StorageRepository):
    """Storage repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, storage: Storage) -> Storage:
        """Create a new storage."""
        try:
            storage_model = StorageModel(
                storage_id=storage.id,
                construction_id=storage.construction_id,
                name=storage.name,
                created_at=storage.created_at
            )
            
            self._session.add(storage_model)
            await self._session.commit()
            await self._session.refresh(storage_model)
            
            return self._to_domain(storage_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create storage: {str(e)}") from e
    
    async def get_by_id(self, storage_id: UUID) -> Optional[Storage]:
        """Get storage by ID."""
        try:
            result = await self._session.execute(
                select(StorageModel).where(StorageModel.storage_id == storage_id)
            )
            storage_model = result.scalar_one_or_none()
            
            return self._to_domain(storage_model) if storage_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get storage by ID: {str(e)}") from e
    
    async def update(self, storage: Storage) -> Storage:
        """Update existing storage."""
        try:
            result = await self._session.execute(
                select(StorageModel).where(StorageModel.storage_id == storage.id)
            )
            storage_model = result.scalar_one_or_none()
            
            if not storage_model:
                raise DatabaseError(f"Storage with ID {storage.id} not found")
            
            storage_model.construction_id = storage.construction_id
            storage_model.name = storage.name
            
            await self._session.commit()
            await self._session.refresh(storage_model)
            
            return self._to_domain(storage_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update storage: {str(e)}") from e
    
    async def delete(self, storage_id: UUID) -> bool:
        """Delete storage by ID."""
        try:
            result = await self._session.execute(
                delete(StorageModel).where(StorageModel.storage_id == storage_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete storage: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Storage]:
        """List all storages with pagination."""
        try:
            result = await self._session.execute(
                select(StorageModel)
                .offset(offset)
                .limit(limit)
                .order_by(StorageModel.created_at.desc())
            )
            storage_models = result.scalars().all()
            
            return [self._to_domain(storage_model) for storage_model in storage_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list storages: {str(e)}") from e
    
    async def get_by_construction_id(self, construction_id: UUID, limit: int = 100, offset: int = 0) -> List[Storage]:
        """Get storages by construction ID."""
        try:
            result = await self._session.execute(
                select(StorageModel)
                .where(StorageModel.construction_id == construction_id)
                .offset(offset)
                .limit(limit)
                .order_by(StorageModel.created_at.desc())
            )
            storage_models = result.scalars().all()
            
            return [self._to_domain(storage_model) for storage_model in storage_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get storages by construction ID: {str(e)}") from e
    
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Storage]:
        """Search storages by name."""
        try:
            result = await self._session.execute(
                select(StorageModel)
                .where(StorageModel.name.ilike(f"%{name}%"))
                .offset(offset)
                .limit(limit)
                .order_by(StorageModel.created_at.desc())
            )
            storage_models = result.scalars().all()
            
            return [self._to_domain(storage_model) for storage_model in storage_models]
        except Exception as e:
            raise DatabaseError(f"Failed to search storages by name: {str(e)}") from e
    
    async def count_all(self) -> int:
        """Count total number of storages."""
        try:
            result = await self._session.execute(
                select(func.count(StorageModel.storage_id))
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count storages: {str(e)}") from e
    
    def _to_domain(self, storage_model: StorageModel) -> Storage:
        """Convert SQLAlchemy model to domain entity."""
        return Storage(
            storage_id=storage_model.storage_id,
            construction_id=storage_model.construction_id,
            name=storage_model.name,
            created_at=storage_model.created_at
        )

