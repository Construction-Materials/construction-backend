"""
Material Use Cases for Application Layer.
"""

from typing import List
from uuid import UUID

from src.domain.entities.materials import Materials
from src.domain.repositories.material_repository import MaterialRepository
from src.domain.value_objects.unit_enum import UnitEnum
from src.application.dtos.material_dto import (
    MaterialCreateDTO,
    MaterialUpdateDTO,
    MaterialResponseDTO,
    MaterialListResponseDTO,
    MaterialSearchDTO
)
from src.shared.exceptions import EntityNotFoundError, ValidationError


class MaterialUseCases:
    """Material use cases implementation."""
    
    def __init__(self, material_repository: MaterialRepository):
        self._material_repository = material_repository
    
    async def create_material(self, material_dto: MaterialCreateDTO) -> MaterialResponseDTO:
        """Create a new material."""
        # Create domain entity
        material = Materials(
            category_id=material_dto.category_id,
            name=material_dto.name,
            description=material_dto.description,
            unit=material_dto.unit
        )
        
        # Save to repository
        created_material = await self._material_repository.create(material)
        
        return MaterialResponseDTO(
            material_id=created_material.id,
            category_id=created_material.category_id,
            name=created_material.name,
            description=created_material.description,
            unit=created_material.unit,
            created_at=created_material.created_at
        )
    
    async def get_material_by_id(self, material_id: UUID) -> MaterialResponseDTO:
        """Get material by ID."""
        material = await self._material_repository.get_by_id(material_id)
        if not material:
            raise EntityNotFoundError("Material", str(material_id))
        
        return MaterialResponseDTO(
            material_id=material.id,
            category_id=material.category_id,
            name=material.name,
            description=material.description,
            unit=material.unit,
            created_at=material.created_at
        )
    
    async def update_material(self, material_id: UUID, material_dto: MaterialUpdateDTO) -> MaterialResponseDTO:
        """Update material."""
        material = await self._material_repository.get_by_id(material_id)
        if not material:
            raise EntityNotFoundError("Material", str(material_id))
        
        # Update fields if provided
        if material_dto.category_id is not None:
            material._category_id = material_dto.category_id
        
        if material_dto.name is not None:
            material._name = material_dto.name.strip()
        
        if material_dto.description is not None:
            material.set_description(material_dto.description)
        
        if material_dto.unit is not None:
            material._unit = material_dto.unit
        
        # Save changes
        updated_material = await self._material_repository.update(material)
        
        return MaterialResponseDTO(
            material_id=updated_material.id,
            category_id=updated_material.category_id,
            name=updated_material.name,
            description=updated_material.description,
            unit=updated_material.unit,
            created_at=updated_material.created_at
        )
    
    async def delete_material(self, material_id: UUID) -> bool:
        """Delete material."""
        material = await self._material_repository.get_by_id(material_id)
        if not material:
            raise EntityNotFoundError("Material", str(material_id))
        
        return await self._material_repository.delete(material_id)
    
    async def list_all_materials(self, limit: int = 100, offset: int = 0) -> MaterialListResponseDTO:
        """List all materials."""
        materials = await self._material_repository.list_all(limit=limit, offset=offset)
        total = await self._material_repository.count_all()
        
        return MaterialListResponseDTO(
            materials=[
                MaterialResponseDTO(
                    material_id=material.id,
                    category_id=material.category_id,
                    name=material.name,
                    description=material.description,
                    unit=material.unit,
                    created_at=material.created_at
                )
                for material in materials
            ],
            total=total,
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def get_materials_by_category(self, category_id: UUID, limit: int = 100, offset: int = 0) -> MaterialListResponseDTO:
        """Get materials by category."""
        materials = await self._material_repository.get_by_category_id(category_id, limit=limit, offset=offset)
        total = len(materials)  # Można dodać count_by_category_id jeśli potrzebne
        
        return MaterialListResponseDTO(
            materials=[
                MaterialResponseDTO(
                    material_id=material.id,
                    category_id=material.category_id,
                    name=material.name,
                    description=material.description,
                    unit=material.unit,
                    created_at=material.created_at
                )
                for material in materials
            ],
            total=total,
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def search_materials(self, search_dto: MaterialSearchDTO) -> MaterialListResponseDTO:
        """Search materials by name and optionally filter by category."""
        # Search by name
        materials = await self._material_repository.search_by_name(
            name=search_dto.query,
            limit=search_dto.size,
            offset=(search_dto.page - 1) * search_dto.size
        )
        
        # Filter by category if provided
        if search_dto.category_id:
            materials = [
                m for m in materials 
                if m.category_id == search_dto.category_id
            ]
        
        total = len(materials)
        
        return MaterialListResponseDTO(
            materials=[
                MaterialResponseDTO(
                    material_id=material.id,
                    category_id=material.category_id,
                    name=material.name,
                    description=material.description,
                    unit=material.unit,
                    created_at=material.created_at
                )
                for material in materials
            ],
            total=total,
            page=search_dto.page,
            size=search_dto.size
        )

