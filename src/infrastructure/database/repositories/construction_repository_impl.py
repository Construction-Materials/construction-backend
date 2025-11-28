"""
Construction Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from src.domain.entities.construction import Construction
from src.domain.repositories.construction_repository import ConstructionRepository
from src.infrastructure.database.models import ConstructionModel, StorageItemModel
from src.shared.exceptions import DatabaseError


class ConstructionRepositoryImpl(ConstructionRepository):
    """Construction repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, construction: Construction) -> Construction:
        """Create a new construction."""
        try:
            construction_model = ConstructionModel(
                construction_id=construction.id,
                name=construction.name,
                description=construction.description,
                address=construction.address,
                start_date=construction.start_date,
                status=construction.status,
                img_url=construction.img_url,
                created_at=construction.created_at
            )
            
            self._session.add(construction_model)
            await self._session.commit()
            await self._session.refresh(construction_model)
            
            return self._to_domain(construction_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create construction: {str(e)}") from e
    
    async def get_by_id(self, construction_id: UUID) -> Optional[Construction]:
        """Get construction by ID."""
        try:
            result = await self._session.execute(
                select(ConstructionModel).where(ConstructionModel.construction_id == construction_id)
            )
            construction_model = result.scalar_one_or_none()
            
            return self._to_domain(construction_model) if construction_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get construction by ID: {str(e)}") from e
    
    async def update(self, construction: Construction) -> Construction:
        """Update existing construction."""
        try:
            result = await self._session.execute(
                select(ConstructionModel).where(ConstructionModel.construction_id == construction.id)
            )
            construction_model = result.scalar_one_or_none()
            
            if not construction_model:
                raise DatabaseError(f"Construction with ID {construction.id} not found")
            
            construction_model.name = construction.name
            construction_model.description = construction.description
            construction_model.address = construction.address
            construction_model.start_date = construction.start_date
            construction_model.status = construction.status
            construction_model.img_url = construction.img_url
            
            await self._session.commit()
            await self._session.refresh(construction_model)
            
            return self._to_domain(construction_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update construction: {str(e)}") from e
    
    async def delete(self, construction_id: UUID) -> bool:
        """Delete construction by ID."""
        try:
            result = await self._session.execute(
                delete(ConstructionModel).where(ConstructionModel.construction_id == construction_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete construction: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Construction]:
        """List all constructions with pagination."""
        try:
            result = await self._session.execute(
                select(ConstructionModel)
                .offset(offset)
                .limit(limit)
                .order_by(ConstructionModel.created_at.desc())
            )
            construction_models = result.scalars().all()
            
            return [self._to_domain(construction_model) for construction_model in construction_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list constructions: {str(e)}") from e
    
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Construction]:
        """Search constructions by name."""
        try:
            result = await self._session.execute(
                select(ConstructionModel)
                .where(ConstructionModel.name.ilike(f"%{name}%"))
                .offset(offset)
                .limit(limit)
                .order_by(ConstructionModel.created_at.desc())
            )
            construction_models = result.scalars().all()
            
            return [self._to_domain(construction_model) for construction_model in construction_models]
        except Exception as e:
            raise DatabaseError(f"Failed to search constructions by name: {str(e)}") from e
    
    async def get_by_name(self, name: str) -> Optional[Construction]:
        """Get construction by exact name match (case-insensitive)."""
        try:
            result = await self._session.execute(
                select(ConstructionModel)
                .where(func.lower(ConstructionModel.name) == func.lower(name))
                .limit(1)
            )
            construction_model = result.scalar_one_or_none()
            
            return self._to_domain(construction_model) if construction_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get construction by name: {str(e)}") from e
    
    async def count_all(self) -> int:
        """Count total number of constructions."""
        try:
            result = await self._session.execute(
                select(func.count(ConstructionModel.construction_id))
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count constructions: {str(e)}") from e
    
    async def get_statistics(self, from_date: Optional[datetime] = None) -> List[dict]:
        """Get statistics for all constructions."""
        try:
            now = datetime.now(timezone.utc)
            
            # Buduj warunek join - jeśli podano from_date, dodaj go do warunku join
            join_condition = ConstructionModel.construction_id == StorageItemModel.construction_id
            if from_date is not None:
                join_condition = join_condition & (StorageItemModel.created_at >= from_date)
            
            query = select(
                ConstructionModel.construction_id,
                ConstructionModel.name.label('construction_name'),
                func.coalesce(
                    func.count(func.distinct(StorageItemModel.material_id)),
                    0
                ).label('total_items'),
                func.coalesce(func.sum(StorageItemModel.quantity_value), 0.0).label('total_quantity')
            ).outerjoin(
                StorageItemModel, 
                join_condition
            ).group_by(
                ConstructionModel.construction_id, 
                ConstructionModel.name
            ).order_by(ConstructionModel.name)
            
            result = await self._session.execute(query)
            rows = result.all()
            
            statistics = []
            for row in rows:
                # Obsługa total_items - count może zwrócić 0 lub None
                total_items = 0
                if row.total_items is not None:
                    total_items = int(row.total_items)
                
                # Obsługa total_quantity - sum może zwrócić None lub 0
                total_quantity = 0.0
                if row.total_quantity is not None:
                    total_quantity = float(row.total_quantity)
                
                statistics.append({
                    'construction_id': row.construction_id,
                    'construction_name': row.construction_name or None,
                    'total_items': total_items,
                    'total_quantity': total_quantity,
                    'measured_at': now,
                    'last_sync_at': now
                })
            
            return statistics
        except Exception as e:
            raise DatabaseError(f"Failed to get construction statistics: {str(e)}") from e
    
    def _to_domain(self, construction_model: ConstructionModel) -> Construction:
        """Convert SQLAlchemy model to domain entity."""
        from src.domain.value_objects.construction_status import ConstructionStatus
        return Construction(
            construction_id=construction_model.construction_id,
            name=construction_model.name,
            description=construction_model.description,
            address=construction_model.address,
            start_date=construction_model.start_date,
            status=ConstructionStatus(construction_model.status),
            img_url=construction_model.img_url,
            created_at=construction_model.created_at
        )

