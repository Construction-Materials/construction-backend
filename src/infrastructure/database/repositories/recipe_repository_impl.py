"""
Recipe Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import selectinload

from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import RecipeRepository
from src.infrastructure.database.models import RecipeModel
from src.shared.exceptions import DatabaseError


class RecipeRepositoryImpl(RecipeRepository):
    """Recipe repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, recipe: Recipe) -> Recipe:
        """Create a new recipe."""
        try:
            recipe_model = RecipeModel(
                recipe_id=recipe.id,
                user_id=recipe.user_id,
                title=recipe.title,
                external_url=recipe.external_url,
                preparation_steps=recipe.preparation_steps,
                prep_time_minutes=recipe.prep_time_minutes,
                created_at=recipe.created_at
            )
            
            self._session.add(recipe_model)
            await self._session.commit()
            await self._session.refresh(recipe_model)
            
            return self._to_domain(recipe_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create recipe: {str(e)}") from e
    
    async def get_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        """Get recipe by ID."""
        try:
            result = await self._session.execute(
                select(RecipeModel).where(RecipeModel.recipe_id == recipe_id)
            )
            recipe_model = result.scalar_one_or_none()
            
            return self._to_domain(recipe_model) if recipe_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get recipe by ID: {str(e)}") from e
    
    async def update(self, recipe: Recipe) -> Recipe:
        """Update existing recipe."""
        try:
            result = await self._session.execute(
                select(RecipeModel).where(RecipeModel.recipe_id == recipe.id)
            )
            recipe_model = result.scalar_one_or_none()
            
            if not recipe_model:
                raise DatabaseError(f"Recipe with ID {recipe.id} not found")
            
            recipe_model.title = recipe.title
            recipe_model.external_url = recipe.external_url
            recipe_model.preparation_steps = recipe.preparation_steps
            recipe_model.prep_time_minutes = recipe.prep_time_minutes
            
            await self._session.commit()
            await self._session.refresh(recipe_model)
            
            return self._to_domain(recipe_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update recipe: {str(e)}") from e
    
    async def delete(self, recipe_id: UUID) -> bool:
        """Delete recipe by ID."""
        try:
            result = await self._session.execute(
                delete(RecipeModel).where(RecipeModel.recipe_id == recipe_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete recipe: {str(e)}") from e
    
    async def list_by_user(self, user_id: UUID, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """List recipes by user with pagination."""
        try:
            result = await self._session.execute(
                select(RecipeModel)
                .where(RecipeModel.user_id == user_id)
                .offset(offset)
                .limit(limit)
                .order_by(RecipeModel.created_at.desc())
            )
            recipe_models = result.scalars().all()
            
            return [self._to_domain(recipe_model) for recipe_model in recipe_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list recipes by user: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """List all recipes with pagination."""
        try:
            result = await self._session.execute(
                select(RecipeModel)
                .offset(offset)
                .limit(limit)
                .order_by(RecipeModel.created_at.desc())
            )
            recipe_models = result.scalars().all()
            
            return [self._to_domain(recipe_model) for recipe_model in recipe_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list recipes: {str(e)}") from e
    
    async def search_by_title(self, title: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """Search recipes by title."""
        try:
            result = await self._session.execute(
                select(RecipeModel)
                .where(RecipeModel.title.ilike(f"%{title}%"))
                .offset(offset)
                .limit(limit)
                .order_by(RecipeModel.created_at.desc())
            )
            recipe_models = result.scalars().all()
            
            return [self._to_domain(recipe_model) for recipe_model in recipe_models]
        except Exception as e:
            raise DatabaseError(f"Failed to search recipes by title: {str(e)}") from e
    
    def _to_domain(self, recipe_model: RecipeModel) -> Recipe:
        """Convert SQLAlchemy model to domain entity."""
        return Recipe(
            recipe_id=recipe_model.recipe_id,
            user_id=recipe_model.user_id,
            title=recipe_model.title,
            external_url=recipe_model.external_url,
            preparation_steps=recipe_model.preparation_steps,
            prep_time_minutes=recipe_model.prep_time_minutes,
            created_at=recipe_model.created_at
        )
