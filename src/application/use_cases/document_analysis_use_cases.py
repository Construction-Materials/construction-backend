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
        prompt = """Przeanalizuj ten dokument/zdjęcie i wyciągnij WSZYSTKIE materiały (produkty, towary, składniki) z ich ilościami.

Materiałem może być: cement, cegły, drewno, stal, farba, gips, piasek, żwir, kafelki, rury, kable, druty, śruby, gwoździe, izolacja, płyty, deski, blachy, beton, zaprawa, klej, silikon, folia, papa, dachówka, okna, drzwi, i każdy inny produkt/towar wymieniony w dokumencie.

Zwróć dane WYŁĄCZNIE w następującym formacie JSON:
{
  "materials": [
    {
      "name": "nazwa materiału",
      "unit": "jednostka",
      "quantity": liczba_ilości
    }
  ]
}

Przykłady poprawnego formatu:
{
  "materials": [
    {"name": "Cement", "unit": "kilograms", "quantity": 100},
    {"name": "Cegły", "unit": "pieces", "quantity": 500},
    {"name": "Drewno", "unit": "cubic_meters", "quantity": 2.5}
  ]
}

Wymagania:
- Wyciągnij WSZYSTKIE materiały/produkty widoczne w dokumencie - nawet jeśli nie jesteś w 100% pewien, spróbuj wyciągnąć to co widzisz
- Pole "name" - nazwa materiału/produktu (wymagane, użyj dokładnie takiej nazwy jak w dokumencie)
- Pole "unit" - jednostka miary, MUSI być DOKŁADNIE jedną z poniższych wartości (wymagane):
  * "meters" - metry (m, metr, metrów)
  * "kilograms" - kilogramy (kg, kilogram, kilogramów)
  * "cubic_meters" - metry sześcienne (m³, m3, metr sześcienny)
  * "cubic_centimeters" - centymetry sześcienne (cm³, cm3, centymetr sześcienny)
  * "cubic_millimeters" - milimetry sześcienne (mm³, mm3, milimetr sześcienny)
  * "liters" - litry (l, L, litr, litrów)
  * "pieces" - sztuki (szt, sztuk, sztuka, pcs, pieces)
  * "other" - inne jednostki (użyj tylko gdy nie pasuje żadna z powyższych)
  
  WAŻNE: Użyj dokładnie jednej z powyższych wartości. Jeśli jednostka z dokumentu to np. "km" (kilometry), użyj "meters". Jeśli to "g" (gramy), użyj "kilograms". Jeśli to "ml" (mililitry), użyj "liters" lub "other" w zależności od kontekstu.
- Pole "quantity" - ilość materiału jako liczba (wymagane, jeśli nie ma ilości użyj 0)
  * UWAGA: Jeśli w dokumencie ilość jest zapisana z przecinkiem (np. "100,5"), zamień przecinek na kropkę (100.5)
  * Przykłady: "100,5" -> 100.5, "50,25" -> 50.25, "2,75" -> 2.75
- Jeśli w dokumencie nie ma żadnych materiałów/produktów, zwróć pustą tablicę: {"materials": []}

Ważne - interpretacja kolumn i danych:
- Dokument może mieć kolumny o różnych nazwach (np. "ilość", "quantity", "qty", "ilość sztuk", "ilość kg", "nazwa", "materiał", "produkt", "towar", "artykuł", "pozycja", itp.)
- Spróbuj z kontekstu zidentyfikować, które kolumny odpowiadają wymaganym polom:
  * Kolumna z nazwą materiału/produktu -> "name"
  * Kolumna z ilością/liczbą -> "quantity" (pamiętaj o zamianie przecinka na kropkę)
  * Kolumna z jednostką miary lub jednostka wywnioskowana z kontekstu -> "unit"
- Jeśli jednostka nie jest podana bezpośrednio, spróbuj wywnioskować ją z kontekstu:
  * "100 kg" lub "100kg" -> unit: "kilograms", quantity: 100
  * "50 szt" lub "50szt" -> unit: "pieces", quantity: 50
  * "2 m3" lub "2m3" -> unit: "cubic_meters", quantity: 2
  * "10 m" lub "10m" -> unit: "meters", quantity: 10
  * "5 l" lub "5l" -> unit: "liters", quantity: 5
  * "100,5 kg" -> unit: "kilograms", quantity: 100.5
- Jeśli widzisz listę produktów/materiałów w dokumencie (nawet w formie tekstowej), wyciągnij je wszystkie
- Jeśli nie możesz jednoznacznie zidentyfikować pola, użyj najlepszego dopasowania na podstawie kontekstu
- NIE zwracaj pustej tablicy jeśli widzisz jakiekolwiek materiały/produkty w dokumencie - zawsze spróbuj je wyciągnąć

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

