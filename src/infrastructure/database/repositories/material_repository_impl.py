"""
Material Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from src.domain.entities.materials import Materials
from src.domain.repositories.material_repository import MaterialRepository
from src.infrastructure.database.models import MaterialModel, StorageItemModel, StorageModel
from src.shared.exceptions import DatabaseError


class MaterialRepositoryImpl(MaterialRepository):
    """Material repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, material: Materials) -> Materials:
        """Create a new material."""
        try:
            material_model = MaterialModel(
                material_id=material.id,
                category_id=material.category_id,
                name=material.name,
                description=material.description,
                unit=material.unit,
                created_at=material.created_at
            )
            
            self._session.add(material_model)
            await self._session.commit()
            await self._session.refresh(material_model)
            
            return self._to_domain(material_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create material: {str(e)}") from e
    
    async def get_by_id(self, material_id: UUID) -> Optional[Materials]:
        """Get material by ID."""
        try:
            result = await self._session.execute(
                select(MaterialModel).where(MaterialModel.material_id == material_id)
            )
            material_model = result.scalar_one_or_none()
            
            return self._to_domain(material_model) if material_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get material by ID: {str(e)}") from e
    
    async def update(self, material: Materials) -> Materials:
        """Update existing material."""
        try:
            result = await self._session.execute(
                select(MaterialModel).where(MaterialModel.material_id == material.id)
            )
            material_model = result.scalar_one_or_none()
            
            if not material_model:
                raise DatabaseError(f"Material with ID {material.id} not found")
            
            material_model.category_id = material.category_id
            material_model.name = material.name
            material_model.description = material.description
            material_model.unit = material.unit
            
            await self._session.commit()
            await self._session.refresh(material_model)
            
            return self._to_domain(material_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update material: {str(e)}") from e
    
    async def delete(self, material_id: UUID) -> bool:
        """Delete material by ID."""
        try:
            result = await self._session.execute(
                delete(MaterialModel).where(MaterialModel.material_id == material_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete material: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Materials]:
        """List all materials with pagination."""
        try:
            result = await self._session.execute(
                select(MaterialModel)
                .offset(offset)
                .limit(limit)
                .order_by(MaterialModel.created_at.desc())
            )
            material_models = result.scalars().all()
            
            return [self._to_domain(material_model) for material_model in material_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list materials: {str(e)}") from e
    
    async def get_by_category_id(self, category_id: UUID, limit: int = 100, offset: int = 0) -> List[Materials]:
        """Get materials by category ID."""
        try:
            result = await self._session.execute(
                select(MaterialModel)
                .where(MaterialModel.category_id == category_id)
                .offset(offset)
                .limit(limit)
                .order_by(MaterialModel.created_at.desc())
            )
            material_models = result.scalars().all()
            
            return [self._to_domain(material_model) for material_model in material_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get materials by category ID: {str(e)}") from e
    
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Materials]:
        """Search materials by name."""
        try:
            result = await self._session.execute(
                select(MaterialModel)
                .where(MaterialModel.name.ilike(f"%{name}%"))
                .offset(offset)
                .limit(limit)
                .order_by(MaterialModel.created_at.desc())
            )
            material_models = result.scalars().all()
            
            return [self._to_domain(material_model) for material_model in material_models]
        except Exception as e:
            raise DatabaseError(f"Failed to search materials by name: {str(e)}") from e
    
    async def count_all(self) -> int:
        """Count total number of materials."""
        try:
            result = await self._session.execute(
                select(func.count(MaterialModel.material_id))
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count materials: {str(e)}") from e
    
    async def get_by_construction_id(self, construction_id: UUID, limit: int = 100, offset: int = 0) -> List[Materials]:
        """Get materials by construction ID (through storages)."""
        try:
            result = await self._session.execute(
                select(MaterialModel)
                .join(StorageItemModel, MaterialModel.material_id == StorageItemModel.material_id)
                .join(StorageModel, StorageItemModel.storage_id == StorageModel.storage_id)
                .where(StorageModel.construction_id == construction_id)
                .distinct()
                .offset(offset)
                .limit(limit)
                .order_by(MaterialModel.name)
            )
            material_models = result.scalars().all()
            
            return [self._to_domain(material_model) for material_model in material_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get materials by construction ID: {str(e)}") from e
    
    def _to_domain(self, material_model: MaterialModel) -> Materials:
        """Convert SQLAlchemy model to domain entity."""
        return Materials(
            material_id=material_model.material_id,
            category_id=material_model.category_id,
            name=material_model.name,
            description=material_model.description,
            unit=material_model.unit,
            created_at=material_model.created_at
        )

