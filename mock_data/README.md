# Mock Data - Dane Testowe

Ten katalog zawiera przykładowe dane testowe dla aplikacji Construction Manager w formacie JSON, skupione na instalacjach elektrycznych i instalacjach na budowie.

## Struktura plików

### categories.json

Zawiera 8 kategorii materiałów elektrycznych i instalacyjnych:

- `id` - UUID kategorii
- `name` - nazwa kategorii

Kategorie obejmują: Przewody i kable, Osprzęt elektryczny, Rozdzielnice i bezpieczniki, Oświetlenie, Puszki i korytka, Gniazda i wyłączniki, Instalacje niskiego napięcia, Akcesoria instalacyjne.

### constructions.json

Zawiera 6 konstrukcji/budów związanych z instalacjami elektrycznymi:

- `id` - UUID konstrukcji
- `name` - nazwa konstrukcji/budowy
- `description` - opis konstrukcji (zawiera szczegóły instalacji elektrycznej)
- `status` - status konstrukcji (active, in_progress, inactive, archived, deleted)
- `created_at` - data utworzenia (ISO 8601)

Przykłady: instalacje elektryczne w domach, modernizacje instalacji biurowych, instalacje oświetlenia przemysłowego, remonty instalacji mieszkaniowych, instalacje garażowe, instalacje zewnętrzne.

### materials.json

Zawiera 26 materiałów elektrycznych i instalacyjnych z następującymi polami:

- `id` - UUID materiału
- `category_id` - UUID kategorii (foreign key do categories)
- `name` - nazwa materiału
- `description` - opis materiału
- `unit` - jednostka miary (meters, kilograms, cubic_meters, liters, pieces, other)
- `created_at` - data utworzenia (ISO 8601)

Materiały obejmują: przewody i kable (YDY, YKY), rozdzielnice, wyłączniki różnicowoprądowe i nadprądowe, lampy LED, puszki podtynkowe, korytka kablowe, gniazda, wyłączniki światła, transformatory, akcesoria instalacyjne.

### storages.json

Zawiera 6 magazynów z następującymi polami:

- `id` - UUID magazynu
- `construction_id` - UUID konstrukcji (foreign key do constructions)
- `name` - nazwa magazynu
- `created_at` - data utworzenia (ISO 8601)

Magazyny są przypisane do konkretnych konstrukcji związanych z instalacjami elektrycznymi.

### storage_items.json

Zawiera 50+ pozycji magazynowych z następującymi polami:

- `storage_id` - UUID magazynu (foreign key do storages)
- `material_id` - UUID materiału (foreign key do materials)
- `quantity_value` - wartość ilości (Decimal)

Pozycje magazynowe zawierają materiały elektryczne w odpowiednich ilościach dla każdego magazynu.

## Powiązania między encjami

- **Categories → Materials**: Jedna kategoria może mieć wiele materiałów
- **Constructions → Storages**: Jedna konstrukcja może mieć wiele magazynów
- **Storages → StorageItems**: Jeden magazyn może mieć wiele pozycji
- **Materials → StorageItems**: Jeden materiał może być w wielu magazynach

## Przykładowe użycie

```python
import json

# Wczytanie danych kategorii
with open('mock_data/categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

# Wczytanie konstrukcji
with open('mock_data/constructions.json', 'r', encoding='utf-8') as f:
    constructions = json.load(f)

# Znalezienie materiałów w kategorii przewodów
category_id = "aa0e8400-e29b-41d4-a716-446655440001"
category_materials = [m for m in materials if m['category_id'] == category_id]
```

## Uwagi

- Daty są w formacie ISO 8601 (UTC)
- UUID są w formacie standardowym
- Nazwy materiałów i konstrukcji są w języku polskim
- Ilości materiałów są realistyczne dla polskich instalacji elektrycznych
- Statusy konstrukcji: active, in_progress, inactive, archived, deleted
- Jednostki miary: meters (przewody, kable, korytka), pieces (osprzęt, lampy, puszki), liters (nie używane w danych elektrycznych)
- Wszystkie dane są związane z instalacjami elektrycznymi i instalacjami na budowie
