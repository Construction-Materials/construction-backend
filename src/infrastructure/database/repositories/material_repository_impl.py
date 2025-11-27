"""
Material Repository Implementation (Adapter).
"""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from rapidfuzz import fuzz

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
    
    async def create_bulk(self, materials: List[Materials]) -> List[Materials]:
        """Create multiple materials at once."""
        try:
            material_models = [
                MaterialModel(
                    material_id=material.id,
                    category_id=material.category_id,
                    name=material.name,
                    description=material.description,
                    unit=material.unit,
                    created_at=material.created_at
                )
                for material in materials
            ]
            
            self._session.add_all(material_models)
            await self._session.commit()
            
            # Refresh all models to get database-generated values
            for material_model in material_models:
                await self._session.refresh(material_model)
            
            return [self._to_domain(material_model) for material_model in material_models]
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create materials in bulk: {str(e)}") from e
    
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
        """Search materials by name using fuzzy matching and sort by relevance."""
        try:
            # Pobierz wszystkie materiały (lub większy zbiór) do analizy fuzzy matching
            # Nie używamy ILIKE jako wstępnego filtru, bo może pominąć dobre dopasowania
            # (np. "Pomadka długotrwała" nie znajdzie "Pomadka" przez ILIKE)
            result = await self._session.execute(
                select(MaterialModel)
                .limit(500)  # Pobierz więcej materiałów do analizy fuzzy
            )
            material_models = result.scalars().all()
            
            if not material_models:
                return []
            
            # Oblicz podobieństwo dla każdego materiału używając fuzzy matching
            materials_with_scores: List[Tuple[Materials, float]] = []
            search_name_lower = name.lower()
            
            for material_model in material_models:
                material = self._to_domain(material_model)
                material_name_lower = material.name.lower()
                
                # Oblicz podobieństwo używając różnych metod fuzzy matching
                # ratio() - porównuje całe stringi
                ratio_score = fuzz.ratio(search_name_lower, material_name_lower)
                
                # partial_ratio() - najlepsze dopasowanie częściowe (lepsze dla dłuższych nazw)
                # Np. "Pomadka długotrwała 03" vs "Pomadka" - znajdzie "Pomadka"
                partial_score = fuzz.partial_ratio(search_name_lower, material_name_lower)
                
                # token_sort_ratio() - ignoruje kolejność słów
                token_sort_score = fuzz.token_sort_ratio(search_name_lower, material_name_lower)
                
                # token_set_ratio() - najlepsze dla różnej długości stringów
                token_set_score = fuzz.token_set_ratio(search_name_lower, material_name_lower)
                
                # Użyj najwyższego wyniku z wszystkich metod
                max_score = max(ratio_score, partial_score, token_sort_score, token_set_score)
                
                # Filtruj tylko materiały z score >= 30% (aby pominąć całkowicie niepasujące)
                if max_score >= 30:
                    materials_with_scores.append((material, max_score))
            
            # Sortuj po trafności (similarity score) - najwyższe najpierw
            materials_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Zastosuj offset i limit
            start_idx = offset
            end_idx = offset + limit
            
            # Zwróć tylko materiały (bez score)
            sorted_materials = [material for material, _ in materials_with_scores[start_idx:end_idx]]
            
            return sorted_materials
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

