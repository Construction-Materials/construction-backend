"""
Category Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from src.domain.entities.category import Category
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.database.models import CategoryModel
from src.shared.exceptions import DatabaseError


class CategoryRepositoryImpl(CategoryRepository):
    """Category repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, category: Category) -> Category:
        """Create a new category."""
        try:
            category_model = CategoryModel(
                category_id=category.id,
                name=category.name,
                created_at=category.created_at
            )
            
            self._session.add(category_model)
            await self._session.commit()
            await self._session.refresh(category_model)
            
            return self._to_domain(category_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create category: {str(e)}") from e
    
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID."""
        try:
            result = await self._session.execute(
                select(CategoryModel).where(CategoryModel.category_id == category_id)
            )
            category_model = result.scalar_one_or_none()
            
            return self._to_domain(category_model) if category_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get category by ID: {str(e)}") from e
    
    async def update(self, category: Category) -> Category:
        """Update existing category."""
        try:
            result = await self._session.execute(
                select(CategoryModel).where(CategoryModel.category_id == category.id)
            )
            category_model = result.scalar_one_or_none()
            
            if not category_model:
                raise DatabaseError(f"Category with ID {category.id} not found")
            
            category_model.name = category.name
            
            await self._session.commit()
            await self._session.refresh(category_model)
            
            return self._to_domain(category_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update category: {str(e)}") from e
    
    async def delete(self, category_id: UUID) -> bool:
        """Delete category by ID."""
        try:
            result = await self._session.execute(
                delete(CategoryModel).where(CategoryModel.category_id == category_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete category: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Category]:
        """List all categories with pagination."""
        try:
            result = await self._session.execute(
                select(CategoryModel)
                .offset(offset)
                .limit(limit)
                .order_by(CategoryModel.created_at.desc())
            )
            category_models = result.scalars().all()
            
            return [self._to_domain(category_model) for category_model in category_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list categories: {str(e)}") from e
    
    async def search_by_name(self, name: str, limit: int = 100, offset: int = 0) -> List[Category]:
        """Search categories by name."""
        try:
            result = await self._session.execute(
                select(CategoryModel)
                .where(CategoryModel.name.ilike(f"%{name}%"))
                .offset(offset)
                .limit(limit)
                .order_by(CategoryModel.created_at.desc())
            )
            category_models = result.scalars().all()
            
            return [self._to_domain(category_model) for category_model in category_models]
        except Exception as e:
            raise DatabaseError(f"Failed to search categories by name: {str(e)}") from e
    
    async def count_all(self) -> int:
        """Count total number of categories."""
        try:
            result = await self._session.execute(
                select(func.count(CategoryModel.category_id))
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count categories: {str(e)}") from e
    
    def _to_domain(self, category_model: CategoryModel) -> Category:
        """Convert SQLAlchemy model to domain entity."""
        return Category(
            category_id=category_model.category_id,
            name=category_model.name,
            created_at=category_model.created_at
        )

