"""
Document Analysis Use Cases for Application Layer.
"""

from typing import Dict, Any
from uuid import UUID
import base64
import json

from openai import OpenAI
from src.shared.config import settings
from src.shared.exceptions import ValidationError


class DocumentAnalysisUseCases:
    """Document analysis use cases implementation."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is not configured")
        self._client = OpenAI(api_key=settings.openai_api_key)
    
    async def analyze_document(
        self, 
        file_content: bytes, 
        file_name: str,
        construction_id: UUID
    ) -> Dict[str, Any]:
        """
        Analyze document (image or PDF) using OpenAI Vision API.
        
        Args:
            file_content: Binary content of the file
            file_name: Name of the file
            construction_id: ID of the construction this document is associated with
        
        Returns:
            Dictionary with extracted data in JSON format
        """
        # Validate file type
        file_extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf']
        
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f"Nieobsługiwany typ pliku: {file_extension}. "
                f"Dozwolone typy: {', '.join(allowed_extensions)}"
            )
        
        # Prepare file for OpenAI API
        if file_extension == 'pdf':
            # For PDF, we need to use a different approach
            # OpenAI Vision API doesn't directly support PDF, so we'll need to convert it
            # For now, we'll raise an error and suggest using images
            raise ValidationError(
                "PDF nie jest obecnie obsługiwany. Proszę przekonwertować PDF na obraz."
            )
        
        # Encode image to base64
        base64_image = base64.b64encode(file_content).decode('utf-8')
        
        # Determine MIME type
        mime_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        mime_type = mime_type_map.get(file_extension, 'image/jpeg')
        
        # Prepare prompt for OpenAI
        prompt = """Przeanalizuj ten dokument/zdjęcie i wyciągnij wszystkie dostępne dane. 
Zwróć dane w formacie JSON. Jeśli dokument zawiera informacje o materiałach, 
zamówieniach, kosztach, datach, lub innych danych związanych z budową, 
uwzględnij je w odpowiedzi. Jeśli nie możesz wyciągnąć konkretnych danych, 
zwróć opis tego, co widzisz w dokumencie.

Odpowiedź powinna być wyłącznie w formacie JSON, bez dodatkowych komentarzy."""

        try:
            # Call OpenAI Vision API
            response = self._client.chat.completions.create(
                model="gpt-4o",  # Using gpt-4o which supports vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Extract JSON response
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If response is not valid JSON, wrap it
                extracted_data = {
                    "raw_response": response_text,
                    "error": "Odpowiedź nie jest w formacie JSON"
                }
            
            # Add metadata
            result = {
                "construction_id": str(construction_id),
                "file_name": file_name,
                "extracted_data": extracted_data
            }
            
            return result
            
        except Exception as e:
            raise ValidationError(f"Błąd podczas analizy dokumentu: {str(e)}")

