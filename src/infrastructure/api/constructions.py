"""
Construction API endpoints.
"""

import os
import shutil
import base64
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Request
from uuid import UUID
from rapidfuzz import fuzz

from src.shared.config import settings

from src.application.dtos.construction_dto import (
    ConstructionCreateDTO,
    ConstructionUpdateDTO,
    ConstructionResponseDTO,
    ConstructionListResponseDTO,
    ConstructionSearchDTO
)
from src.application.dtos.material_dto import MaterialSearchDTO
from src.application.use_cases.construction_use_cases import ConstructionUseCases
from src.application.use_cases.document_analysis_use_cases import DocumentAnalysisUseCases
from src.application.use_cases.material_use_cases import MaterialUseCases
from src.infrastructure.api.dependencies import get_construction_use_cases, get_document_analysis_use_cases, get_material_use_cases

router = APIRouter()


@router.get("/public", response_model=List[ConstructionResponseDTO])
async def list_constructions_public(
    limit: int = 100,
    offset: int = 0,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """List all constructions (public endpoint for testing)."""
    result = await construction_use_cases.list_all_constructions(limit=limit, offset=offset)
    return result.constructions


@router.post("/", response_model=ConstructionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_construction(
    request: Request,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """
    Utwórz nową construction.
    
    Obsługuje dwa formaty:
    1. JSON (Content-Type: application/json) - standardowy ConstructionCreateDTO
    2. Multipart/form-data - z opcjonalnym plikiem zdjęcia
    
    Jeśli przesłasz plik w multipart/form-data, zostanie on zapisany i img_url zostanie ustawiony automatycznie.
    """
    content_type = request.headers.get("content-type", "")
    
    if "multipart/form-data" in content_type:
        # Obsługa multipart/form-data z plikiem
        form = await request.form()
        
        name = form.get("name")
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pole 'name' jest wymagane"
            )
        
        description = form.get("description", "")
        address = form.get("address", "")
        start_date_str = form.get("start_date")
        status_str = form.get("status", "inactive")
        img_url = form.get("img_url")
        file = form.get("file")
        
        from datetime import datetime
        from src.application.dtos.construction_dto import ConstructionStatus
        
        # Parsuj start_date jeśli podano
        parsed_start_date = None
        if start_date_str:
            try:
                parsed_start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nieprawidłowy format start_date. Użyj formatu ISO (np. 2024-01-01T00:00:00)"
                )
        
        # Parsuj status
        try:
            status_enum = ConstructionStatus(status_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nieprawidłowy status: {status_str}. Dozwolone wartości: {[s.value for s in ConstructionStatus]}"
            )
        
        # Jeśli przesłano plik, zapisz go
        final_img_url = img_url
        temp_file_path = None
        upload_dir = None
        is_base64_image = False
        
        # Sprawdź czy img_url zawiera base64 image
        if img_url and isinstance(img_url, str) and img_url.startswith("data:image/"):
            is_base64_image = True
            try:
                # Parsuj base64 (format: data:image/jpeg;base64,/9j/4AAQ...)
                header, encoded = img_url.split(",", 1)
                # Wyciągnij typ obrazu z headera
                mime_type = header.split(";")[0].split(":")[1]  # image/jpeg
                file_extension_map = {
                    "image/jpeg": "jpg",
                    "image/jpg": "jpg",
                    "image/png": "png",
                    "image/gif": "gif",
                    "image/webp": "webp"
                }
                file_extension = file_extension_map.get(mime_type, "jpg")
                
                # Dekoduj base64
                file_content = base64.b64decode(encoded)
                
                # Sprawdź rozmiar
                max_size = settings.max_upload_size_mb * 1024 * 1024
                if len(file_content) > max_size:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Obraz base64 jest za duży. Maksymalny rozmiar: {settings.max_upload_size_mb}MB"
                    )
                
                # Utwórz katalog jeśli nie istnieje
                upload_dir = Path(settings.constructions_images_dir)
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                # Generuj tymczasową nazwę pliku
                temp_file_name = f"temp_base64.{file_extension}"
                temp_file_path = upload_dir / temp_file_name
                
                # Zapisz plik tymczasowo
                with open(temp_file_path, "wb") as buffer:
                    buffer.write(file_content)
                
                # Ustaw final_img_url na None, bo będzie ustawiony później
                final_img_url = None
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Nieprawidłowy format base64 image: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Błąd podczas przetwarzania base64 image: {str(e)}"
                )
        
        if file and hasattr(file, 'filename') and file.filename:
            # Walidacja typu pliku
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Nieobsługiwany typ pliku: {file_extension}. Dozwolone typy: {', '.join(allowed_extensions)}"
                )
            
            # Sprawdź rozmiar pliku
            max_size = settings.max_upload_size_mb * 1024 * 1024
            file_content = await file.read()
            
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plik jest za duży. Maksymalny rozmiar: {settings.max_upload_size_mb}MB"
                )
            
            # Utwórz katalog jeśli nie istnieje
            upload_dir = Path(settings.constructions_images_dir)
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generuj tymczasową nazwę pliku
            temp_file_name = f"temp_{file.filename}"
            temp_file_path = upload_dir / temp_file_name
            
            # Zapisz plik tymczasowo
            try:
                with open(temp_file_path, "wb") as buffer:
                    buffer.write(file_content)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Błąd podczas zapisywania pliku: {str(e)}"
                )
        
        # Utwórz DTO
        construction_dto = ConstructionCreateDTO(
            name=name,
            description=description,
            address=address,
            start_date=parsed_start_date,
            status=status_enum,
            img_url=final_img_url
        )
        
        # Utwórz construction
        created_construction = await construction_use_cases.create_construction(construction_dto)
        
        # Jeśli był plik lub base64 image, zmień nazwę na właściwą i zaktualizuj img_url
        if (file and hasattr(file, 'filename') and file.filename and temp_file_path) or (is_base64_image and temp_file_path):
            final_file_name = f"{created_construction.construction_id}_{file.filename}"
            final_file_path = upload_dir / final_file_name
            
            try:
                # Określ nazwę pliku
                if is_base64_image:
                    # Dla base64 użyj construction_id i rozszerzenia z pliku
                    file_extension = temp_file_path.suffix
                    final_file_name = f"{created_construction.construction_id}{file_extension}"
                else:
                    final_file_name = f"{created_construction.construction_id}_{file.filename}"
                
                final_file_path = upload_dir / final_file_name
                
                # Zmień nazwę pliku
                if temp_file_path.exists():
                    temp_file_path.rename(final_file_path)
                
                # Generuj URL
                image_url = f"/api/v1/constructions/images/{final_file_name}"
                
                # Zaktualizuj construction z img_url
                update_dto = ConstructionUpdateDTO(img_url=image_url)
                created_construction = await construction_use_cases.update_construction(
                    created_construction.construction_id,
                    update_dto
                )
            except Exception as e:
                # Jeśli błąd, usuń tymczasowy plik
                if temp_file_path and temp_file_path.exists():
                    temp_file_path.unlink()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Błąd podczas aktualizacji img_url: {str(e)}"
                )
        
        return created_construction
    else:
        # Obsługa JSON (standardowy ConstructionCreateDTO)
        body = await request.json()
        construction_dto = ConstructionCreateDTO(**body)
        return await construction_use_cases.create_construction(construction_dto)


@router.get("/{construction_id}", response_model=ConstructionResponseDTO)
async def get_construction(
    construction_id: UUID,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Get construction by ID."""
    return await construction_use_cases.get_construction_by_id(construction_id)


@router.put("/{construction_id}", response_model=ConstructionResponseDTO)
async def update_construction(
    construction_id: UUID,
    construction_dto: ConstructionUpdateDTO,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Update construction."""
    return await construction_use_cases.update_construction(construction_id, construction_dto)


@router.delete("/{construction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_construction(
    construction_id: UUID,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Delete construction."""
    await construction_use_cases.delete_construction(construction_id)


@router.get("/", response_model=ConstructionListResponseDTO)
async def list_constructions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """List all constructions."""
    return await construction_use_cases.list_all_constructions(limit=limit, offset=offset)


@router.get("/search", response_model=ConstructionListResponseDTO)
async def search_constructions(
    query: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: str = Query(None, description="Filter by status (active, in_progress, inactive, archived, deleted)"),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Search constructions by name and optionally filter by status."""
    from src.application.dtos.construction_dto import ConstructionStatus
    
    status_enum = None
    if status:
        try:
            status_enum = ConstructionStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Valid values: {[s.value for s in ConstructionStatus]}"
            )
    
    search_dto = ConstructionSearchDTO(query=query, page=page, size=size, status=status_enum)
    return await construction_use_cases.search_constructions(search_dto)


@router.post("/{construction_id}/analyze-document", status_code=status.HTTP_200_OK)
async def analyze_document(
    construction_id: UUID,
    file: UploadFile = File(..., description="Plik do analizy (zdjęcie lub PDF)"),
    document_analysis_use_cases: DocumentAnalysisUseCases = Depends(get_document_analysis_use_cases),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases),
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """
    Analizuj dokument (zdjęcie lub PDF) używając OpenAI API.
    
    Przyjmuje plik oraz construction_id i zwraca wyciągnięte dane w formacie JSON.
    Dla każdego materiału sprawdza czy istnieje w bazie i czy jednostka się zgadza.
    Jeśli jednostka się nie zgadza, użytkownik będzie musiał ręcznie wpisać ilość.
    """
    # Sprawdź czy construction istnieje
    try:
        await construction_use_cases.get_construction_by_id(construction_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Construction o ID {construction_id} nie został znaleziony"
        )
    
    # Wczytaj zawartość pliku
    file_content = await file.read()
    
    # Analizuj dokument
    result = await document_analysis_use_cases.analyze_document(
        file_content=file_content,
        file_name=file.filename or "unknown",
        construction_id=construction_id
    )
    
    # Sprawdź materiały w bazie i zgodność jednostek
    if "extracted_data" in result and "materials" in result["extracted_data"]:
        materials = result["extracted_data"]["materials"]
        enriched_materials = []
        
        for material in materials:
            material_name = material.get("name", "")
            document_unit = material.get("unit", "")
            quantity = material.get("quantity", 0)
            
            # Szukaj materiału w bazie po nazwie
            try:
                # Najpierw sprawdź czy jest idealny match (dokładna nazwa)
                all_materials = await material_use_cases.list_all_materials(limit=1000, offset=0)
                matching_material = None
                
                for db_material in all_materials.materials:
                    if db_material.name.lower() == material_name.lower():
                        matching_material = db_material
                        break
                
                if matching_material:
                    # Materiał istnieje w bazie - idealny match
                    # Unit może być UnitEnum lub string
                    material_unit = matching_material.unit.value if hasattr(matching_material.unit, 'value') else str(matching_material.unit)
                    unit_matches = (material_unit == document_unit)
                    
                    enriched_material = {
                        **material,
                        "material_id": str(matching_material.material_id),
                        "material_exists": True,
                        "material_unit": material_unit,
                        "unit_matches": unit_matches,
                        "can_use_quantity": unit_matches,  # Jeśli unit się zgadza, można użyć quantity
                        "suggested_materials": []  # Brak sugestii, bo jest idealny match
                    }
                else:
                    # Materiał nie istnieje w bazie - szukaj podobnych
                    search_dto = MaterialSearchDTO(query=material_name, page=1, size=5)
                    similar_materials_result = await material_use_cases.search_materials(search_dto)
                    
                    # Przygotuj listę sugerowanych materiałów z filtrowaniem po score
                    suggested_materials = []
                    material_name_lower = material_name.lower()
                    
                    for suggested in similar_materials_result.materials[:5]:  # Top 5
                        suggested_name_lower = suggested.name.lower()
                        
                        # Oblicz score podobieństwa używając różnych metod fuzzy matching
                        ratio_score = fuzz.ratio(material_name_lower, suggested_name_lower)
                        partial_score = fuzz.partial_ratio(material_name_lower, suggested_name_lower)
                        token_sort_score = fuzz.token_sort_ratio(material_name_lower, suggested_name_lower)
                        token_set_score = fuzz.token_set_ratio(material_name_lower, suggested_name_lower)
                        
                        # Użyj najwyższego wyniku
                        max_score = max(ratio_score, partial_score, token_sort_score, token_set_score)
                        
                        # Filtruj tylko materiały z score >= 50 (0.5 = 50%)
                        if max_score >= 50:
                            suggested_unit = suggested.unit.value if hasattr(suggested.unit, 'value') else str(suggested.unit)
                            suggested_materials.append({
                                "material_id": str(suggested.material_id),
                                "name": suggested.name,
                                "unit": suggested_unit,
                                "description": suggested.description,
                                "similarity_score": max_score  # Dodaj score dla informacji
                            })
                    
                    enriched_material = {
                        **material,
                        "material_id": None,
                        "material_exists": False,
                        "material_unit": None,
                        "unit_matches": False,
                        "can_use_quantity": False,  # Nie można użyć, bo materiał nie istnieje
                        "suggested_materials": suggested_materials  # Tylko materiały z score >= 50%
                    }
                
                enriched_materials.append(enriched_material)
                
            except Exception as e:
                # W przypadku błędu, zwróć materiał bez dodatkowych informacji
                enriched_materials.append({
                    **material,
                    "material_id": None,
                    "material_exists": False,
                    "material_unit": None,
                    "unit_matches": False,
                    "can_use_quantity": False,
                    "error": f"Błąd podczas sprawdzania materiału: {str(e)}"
                })
        
        result["extracted_data"]["materials"] = enriched_materials
    
    return result


@router.post("/{construction_id}/upload-image", response_model=ConstructionResponseDTO)
async def upload_construction_image(
    construction_id: UUID,
    file: UploadFile = File(..., description="Zdjęcie construction (JPG, PNG, GIF, WEBP)"),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """
    Prześlij zdjęcie dla construction i zapisz je na dysku.
    
    Akceptuje pliki obrazów (JPG, PNG, GIF, WEBP) i zapisuje je w katalogu uploads/constructions/.
    Automatycznie aktualizuje pole img_url w construction.
    """
    # Sprawdź czy construction istnieje
    try:
        construction = await construction_use_cases.get_construction_by_id(construction_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Construction o ID {construction_id} nie został znaleziony"
        )
    
    # Walidacja typu pliku
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nieobsługiwany typ pliku: {file_extension}. Dozwolone typy: {', '.join(allowed_extensions)}"
        )
    
    # Sprawdź rozmiar pliku (max 10MB)
    max_size = settings.max_upload_size_mb * 1024 * 1024
    file_content = await file.read()
    
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plik jest za duży. Maksymalny rozmiar: {settings.max_upload_size_mb}MB"
        )
    
    # Utwórz katalog jeśli nie istnieje
    upload_dir = Path(settings.constructions_images_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generuj unikalną nazwę pliku
    file_name = f"{construction_id}_{file.filename}"
    file_path = upload_dir / file_name
    
    # Zapisz plik na dysku
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas zapisywania pliku: {str(e)}"
        )
    
    # Generuj URL do pliku (względny URL)
    image_url = f"/api/v1/constructions/images/{file_name}"
    
    # Zaktualizuj construction z nowym img_url
    update_dto = ConstructionUpdateDTO(img_url=image_url)
    updated_construction = await construction_use_cases.update_construction(construction_id, update_dto)
    
    return updated_construction


@router.get("/images/{filename}")
async def get_construction_image(filename: str):
    """
    Pobierz zdjęcie construction z dysku.
    """
    file_path = Path(settings.constructions_images_dir) / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zdjęcie nie zostało znalezione"
        )
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        media_type="image/jpeg"  # FastAPI automatycznie wykryje typ na podstawie rozszerzenia
    )

