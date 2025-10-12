"""
Recipe Use Cases for Application Layer.
"""

from typing import List
from uuid import UUID

from src.domain.entities.recipe import Recipe
from src.domain.entities.catalog_item import CatalogItem
from src.domain.entities.recipe_item import RecipeItem
from src.domain.repositories.recipe_repository import RecipeRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.catalog_item_repository import CatalogItemRepository
from src.domain.repositories.recipe_item_repository import RecipeItemRepository
from src.domain.value_objects.quantity import Quantity
from src.application.dtos.recipe_dto import (
    RecipeCreateDTO, RecipeUpdateDTO, RecipeResponseDTO, 
    RecipeListResponseDTO, RecipeSearchDTO, RecipeIngredientDTO,
    RecipeIngredientsResponseDTO, RecipeIngredientResponseDTO
)
from src.shared.exceptions import EntityNotFoundError, ValidationError


class RecipeUseCases:
    """Recipe use cases implementation."""
    
    def __init__(
        self, 
        recipe_repository: RecipeRepository, 
        user_repository: UserRepository,
        catalog_item_repository: CatalogItemRepository,
        recipe_item_repository: RecipeItemRepository
    ):
        self._recipe_repository = recipe_repository
        self._user_repository = user_repository
        self._catalog_item_repository = catalog_item_repository
        self._recipe_item_repository = recipe_item_repository
    
    async def create_recipe(self, user_id: UUID, recipe_dto: RecipeCreateDTO) -> RecipeResponseDTO:
        """Create a new recipe."""
        # Verify user exists
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        # Create domain entity
        recipe = Recipe(
            user_id=user_id,
            title=recipe_dto.title,
            external_url=str(recipe_dto.external_url) if recipe_dto.external_url else None,
            preparation_steps=recipe_dto.preparation_steps,
            prep_time_minutes=recipe_dto.prep_time_minutes
        )
        
        # Save to repository
        created_recipe = await self._recipe_repository.create(recipe)
        
        # Process ingredients if provided
        if recipe_dto.ingredients:
            await self._process_recipe_ingredients(created_recipe.id, recipe_dto.ingredients)
        
        return RecipeResponseDTO(
            recipe_id=created_recipe.id,
            user_id=created_recipe.user_id,
            title=created_recipe.title,
            external_url=created_recipe.external_url,
            preparation_steps=created_recipe.preparation_steps,
            prep_time_minutes=created_recipe.prep_time_minutes,
            created_at=created_recipe.created_at
        )
    
    async def get_recipe_by_id(self, recipe_id: UUID) -> RecipeResponseDTO:
        """Get recipe by ID."""
        recipe = await self._recipe_repository.get_by_id(recipe_id)
        if not recipe:
            raise EntityNotFoundError("Recipe", str(recipe_id))
        
        return RecipeResponseDTO(
            recipe_id=recipe.id,
            user_id=recipe.user_id,
            title=recipe.title,
            external_url=recipe.external_url,
            preparation_steps=recipe.preparation_steps,
            prep_time_minutes=recipe.prep_time_minutes,
            created_at=recipe.created_at
        )
    
    async def update_recipe(self, recipe_id: UUID, recipe_dto: RecipeUpdateDTO) -> RecipeResponseDTO:
        """Update recipe."""
        recipe = await self._recipe_repository.get_by_id(recipe_id)
        if not recipe:
            raise EntityNotFoundError("Recipe", str(recipe_id))
        
        # Update fields if provided
        if recipe_dto.title is not None:
            recipe.set_title(recipe_dto.title)
        
        if recipe_dto.external_url is not None:
            recipe.set_external_url(str(recipe_dto.external_url))
        
        if recipe_dto.preparation_steps is not None:
            recipe.set_preparation_steps(recipe_dto.preparation_steps)
        
        if recipe_dto.prep_time_minutes is not None:
            recipe.set_prep_time(recipe_dto.prep_time_minutes)
        
        # Save changes
        updated_recipe = await self._recipe_repository.update(recipe)
        
        return RecipeResponseDTO(
            recipe_id=updated_recipe.id,
            user_id=updated_recipe.user_id,
            title=updated_recipe.title,
            external_url=updated_recipe.external_url,
            preparation_steps=updated_recipe.preparation_steps,
            prep_time_minutes=updated_recipe.prep_time_minutes,
            created_at=updated_recipe.created_at
        )
    
    async def delete_recipe(self, recipe_id: UUID) -> bool:
        """Delete recipe."""
        recipe = await self._recipe_repository.get_by_id(recipe_id)
        if not recipe:
            raise EntityNotFoundError("Recipe", str(recipe_id))
        
        return await self._recipe_repository.delete(recipe_id)
    
    async def get_user_recipes(self, user_id: UUID, limit: int = 100, offset: int = 0) -> RecipeListResponseDTO:
        """Get recipes by user."""
        # Verify user exists
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        recipes = await self._recipe_repository.list_by_user(user_id, limit=limit, offset=offset)
        
        return RecipeListResponseDTO(
            recipes=[
                RecipeResponseDTO(
                    recipe_id=recipe.id,
                    user_id=recipe.user_id,
                    title=recipe.title,
                    external_url=recipe.external_url,
                    image_url=recipe.image_url,
                    preparation_steps=recipe.preparation_steps,
                    prep_time_minutes=recipe.prep_time_minutes,
                    created_at=recipe.created_at
                )
                for recipe in recipes
            ],
            total=len(recipes),
            page=(offset // limit) + 1,
            size=limit
        )
    
    async def search_recipes(self, search_dto: RecipeSearchDTO) -> RecipeListResponseDTO:
        """Search recipes by title."""
        recipes = await self._recipe_repository.search_by_title(
            title=search_dto.query,
            limit=search_dto.size,
            offset=(search_dto.page - 1) * search_dto.size
        )
        
        return RecipeListResponseDTO(
            recipes=[
                RecipeResponseDTO(
                    recipe_id=recipe.id,
                    user_id=recipe.user_id,
                    title=recipe.title,
                    external_url=recipe.external_url,
                    image_url=recipe.image_url,
                    preparation_steps=recipe.preparation_steps,
                    prep_time_minutes=recipe.prep_time_minutes,
                    created_at=recipe.created_at
                )
                for recipe in recipes
            ],
            total=len(recipes),
            page=search_dto.page,
            size=search_dto.size
        )
    
    async def list_all_recipes(self, limit: int = 100, offset: int = 0) -> RecipeListResponseDTO:
        """List all recipes."""
        recipes = await self._recipe_repository.list_all(limit=limit, offset=offset)
        
        return RecipeListResponseDTO(
            recipes=[
                RecipeResponseDTO(
                    recipe_id=recipe.id,
                    user_id=recipe.user_id,
                    title=recipe.title,
                    external_url=recipe.external_url,
                    image_url=recipe.image_url,
                    preparation_steps=recipe.preparation_steps,
                    prep_time_minutes=recipe.prep_time_minutes,
                    created_at=recipe.created_at
                )
                for recipe in recipes
            ],
            total=len(recipes),
            page=(offset // limit) + 1,
            size=limit
        )
    
    async def _process_recipe_ingredients(self, recipe_id: UUID, ingredients: List[RecipeIngredientDTO]) -> None:
        """Process recipe ingredients - find or create catalog items and link them."""
        for ingredient in ingredients:
            # Find or create catalog item
            catalog_item = await self._find_or_create_catalog_item(ingredient.name)
            
            # Create quantity value object
            quantity = Quantity(ingredient.quantity_value, ingredient.quantity_unit)
            
            # Create recipe item
            recipe_item = RecipeItem(
                recipe_id=recipe_id,
                item_id=catalog_item.id,
                quantity=quantity
            )
            
            # Save recipe item
            await self._recipe_item_repository.create(recipe_item)
    
    async def _find_or_create_catalog_item(self, name: str) -> CatalogItem:
        """Find existing catalog item by name or create new one."""
        # Normalize name for consistent searching and storage
        normalized_name = name.strip().lower()
        
        # Try to find existing item with normalized name
        existing_item = await self._catalog_item_repository.get_by_name(normalized_name)
        if existing_item:
            return existing_item
        
        # Create new catalog item with normalized name
        new_item = CatalogItem(name=normalized_name)
        return await self._catalog_item_repository.create(new_item)
    
    async def get_recipe_ingredients(self, recipe_id: UUID) -> RecipeIngredientsResponseDTO:
        """Get ingredients for a specific recipe."""
        # Verify recipe exists
        recipe = await self._recipe_repository.get_by_id(recipe_id)
        if not recipe:
            raise EntityNotFoundError("Recipe", str(recipe_id))
        
        # Get recipe items (ingredients) for this recipe
        recipe_items = await self._recipe_item_repository.get_by_recipe_id(recipe_id)
        
        # Convert to response DTOs
        ingredients = []
        for item in recipe_items:
            # Get catalog item details
            catalog_item = await self._catalog_item_repository.get_by_id(item.item_id)
            if catalog_item:
                ingredients.append(RecipeIngredientResponseDTO(
                    recipe_item_id=item.id,
                    ingredient_name=catalog_item.name,
                    quantity_value=item.quantity.value if item.quantity else 0,
                    quantity_unit=item.quantity.unit if item.quantity else ""
                ))
        
        return RecipeIngredientsResponseDTO(
            recipe_id=recipe_id,
            ingredients=ingredients,
            total=len(ingredients)
        )
