"""
RecipeItem Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from decimal import Decimal

from src.domain.entities.recipe_item import RecipeItem
from src.domain.repositories.recipe_item_repository import RecipeItemRepository
from src.domain.value_objects.quantity import Quantity
from src.infrastructure.database.models import RecipeItemModel
from src.shared.exceptions import DatabaseError


class RecipeItemRepositoryImpl(RecipeItemRepository):
    """Recipe item repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, recipe_item: RecipeItem) -> RecipeItem:
        """Create a new recipe item."""
        try:
            recipe_item_model = RecipeItemModel(
                recipe_item_id=recipe_item.id,
                recipe_id=recipe_item.recipe_id,
                item_id=recipe_item.item_id,
                quantity_value=recipe_item.quantity.value if recipe_item.quantity else Decimal('0'),
                quantity_unit=recipe_item.quantity.unit if recipe_item.quantity else ""
            )
            
            self._session.add(recipe_item_model)
            await self._session.commit()
            await self._session.refresh(recipe_item_model)
            
            return self._to_domain(recipe_item_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create recipe item: {str(e)}") from e
    
    async def get_by_id(self, recipe_item_id: UUID) -> Optional[RecipeItem]:
        """Get recipe item by ID."""
        try:
            result = await self._session.execute(
                select(RecipeItemModel).where(RecipeItemModel.recipe_item_id == recipe_item_id)
            )
            recipe_item_model = result.scalar_one_or_none()
            
            return self._to_domain(recipe_item_model) if recipe_item_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get recipe item by ID: {str(e)}") from e
    
    async def get_by_recipe_id(self, recipe_id: UUID) -> List[RecipeItem]:
        """Get all recipe items for a recipe."""
        try:
            result = await self._session.execute(
                select(RecipeItemModel).where(RecipeItemModel.recipe_id == recipe_id)
            )
            recipe_item_models = result.scalars().all()
            
            return [self._to_domain(recipe_item_model) for recipe_item_model in recipe_item_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get recipe items by recipe ID: {str(e)}") from e
    
    async def update(self, recipe_item: RecipeItem) -> RecipeItem:
        """Update existing recipe item."""
        try:
            result = await self._session.execute(
                select(RecipeItemModel).where(RecipeItemModel.recipe_item_id == recipe_item.id)
            )
            recipe_item_model = result.scalar_one_or_none()
            
            if not recipe_item_model:
                raise DatabaseError(f"Recipe item with ID {recipe_item.id} not found")
            
            recipe_item_model.quantity_value = recipe_item.quantity.value if recipe_item.quantity else Decimal('0')
            recipe_item_model.quantity_unit = recipe_item.quantity.unit if recipe_item.quantity else ""
            
            await self._session.commit()
            await self._session.refresh(recipe_item_model)
            
            return self._to_domain(recipe_item_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update recipe item: {str(e)}") from e
    
    async def delete(self, recipe_item_id: UUID) -> bool:
        """Delete recipe item by ID."""
        try:
            result = await self._session.execute(
                delete(RecipeItemModel).where(RecipeItemModel.recipe_item_id == recipe_item_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete recipe item: {str(e)}") from e
    
    async def delete_by_recipe_id(self, recipe_id: UUID) -> int:
        """Delete all recipe items for a recipe."""
        try:
            result = await self._session.execute(
                delete(RecipeItemModel).where(RecipeItemModel.recipe_id == recipe_id)
            )
            await self._session.commit()
            
            return result.rowcount
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete recipe items by recipe ID: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[RecipeItem]:
        """List all recipe items with pagination."""
        try:
            result = await self._session.execute(
                select(RecipeItemModel)
                .offset(offset)
                .limit(limit)
            )
            recipe_item_models = result.scalars().all()
            
            return [self._to_domain(recipe_item_model) for recipe_item_model in recipe_item_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list recipe items: {str(e)}") from e
    
    def _to_domain(self, recipe_item_model: RecipeItemModel) -> RecipeItem:
        """Convert SQLAlchemy model to domain entity."""
        quantity = None
        if recipe_item_model.quantity_value and recipe_item_model.quantity_unit:
            quantity = Quantity(
                value=recipe_item_model.quantity_value,
                unit=recipe_item_model.quantity_unit
            )
        
        return RecipeItem(
            recipe_item_id=recipe_item_model.recipe_item_id,
            recipe_id=recipe_item_model.recipe_id,
            item_id=recipe_item_model.item_id,
            quantity=quantity
        )
