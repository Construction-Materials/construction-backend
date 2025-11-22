"""
Construction Use Cases for Application Layer.
"""

from typing import List
from uuid import UUID

from src.domain.entities.construction import Construction
from src.domain.repositories.construction_repository import ConstructionRepository
from src.application.dtos.construction_dto import (
    ConstructionCreateDTO,
    ConstructionUpdateDTO,
    ConstructionResponseDTO,
    ConstructionListResponseDTO,
    ConstructionSearchDTO,
    ConstructionStatus
)
from src.shared.exceptions import EntityNotFoundError, ValidationError


class ConstructionUseCases:
    """Construction use cases implementation."""
    
    def __init__(self, construction_repository: ConstructionRepository):
        self._construction_repository = construction_repository
    
    async def create_construction(self, construction_dto: ConstructionCreateDTO) -> ConstructionResponseDTO:
        """Create a new construction."""
        # Create domain entity
        from src.infrastructure.database.models import ConstructionStatus as ModelStatus
        construction = Construction(
            name=construction_dto.name,
            description=construction_dto.description,
            status=ModelStatus(construction_dto.status.value)
        )
        
        # Save to repository
        created_construction = await self._construction_repository.create(construction)
        
        return ConstructionResponseDTO(
            construction_id=created_construction.id,
            name=created_construction.name,
            description=created_construction.description,
            status=ConstructionStatus(created_construction.status),
            created_at=created_construction.created_at
        )
    
    async def get_construction_by_id(self, construction_id: UUID) -> ConstructionResponseDTO:
        """Get construction by ID."""
        construction = await self._construction_repository.get_by_id(construction_id)
        if not construction:
            raise EntityNotFoundError("Construction", str(construction_id))
        
        return ConstructionResponseDTO(
            construction_id=construction.id,
            name=construction.name,
            description=construction.description,
            status=ConstructionStatus(construction.status),
            created_at=construction.created_at
        )
    
    async def update_construction(self, construction_id: UUID, construction_dto: ConstructionUpdateDTO) -> ConstructionResponseDTO:
        """Update construction."""
        construction = await self._construction_repository.get_by_id(construction_id)
        if not construction:
            raise EntityNotFoundError("Construction", str(construction_id))
        
        # Update fields if provided
        if construction_dto.name is not None:
            construction._name = construction_dto.name.strip()
        
        if construction_dto.description is not None:
            construction.set_description(construction_dto.description)
        
        if construction_dto.status is not None:
            construction._status = construction_dto.status.value
        
        # Save changes
        updated_construction = await self._construction_repository.update(construction)
        
        return ConstructionResponseDTO(
            construction_id=updated_construction.id,
            name=updated_construction.name,
            description=updated_construction.description,
            status=ConstructionStatus(updated_construction.status),
            created_at=updated_construction.created_at
        )
    
    async def delete_construction(self, construction_id: UUID) -> bool:
        """Delete construction."""
        construction = await self._construction_repository.get_by_id(construction_id)
        if not construction:
            raise EntityNotFoundError("Construction", str(construction_id))
        
        return await self._construction_repository.delete(construction_id)
    
    async def list_all_constructions(self, limit: int = 100, offset: int = 0) -> ConstructionListResponseDTO:
        """List all constructions."""
        constructions = await self._construction_repository.list_all(limit=limit, offset=offset)
        total = await self._construction_repository.count_all()
        
        return ConstructionListResponseDTO(
            constructions=[
                ConstructionResponseDTO(
                    construction_id=construction.id,
                    name=construction.name,
                    description=construction.description,
                    status=ConstructionStatus(construction.status),
                    created_at=construction.created_at
                )
                for construction in constructions
            ],
            total=total,
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def search_constructions(self, search_dto: ConstructionSearchDTO) -> ConstructionListResponseDTO:
        """Search constructions by name and optionally filter by status."""
        # Search by name
        constructions = await self._construction_repository.search_by_name(
            name=search_dto.query,
            limit=search_dto.size,
            offset=(search_dto.page - 1) * search_dto.size
        )
        
        # Filter by status if provided
        if search_dto.status:
            constructions = [
                c for c in constructions 
                if ConstructionStatus(c.status) == search_dto.status
            ]
        
        total = len(constructions)
        
        return ConstructionListResponseDTO(
            constructions=[
                ConstructionResponseDTO(
                    construction_id=construction.id,
                    name=construction.name,
                    description=construction.description,
                    status=ConstructionStatus(construction.status),
                    created_at=construction.created_at
                )
                for construction in constructions
            ],
            total=total,
            page=search_dto.page,
            size=search_dto.size
        )

