# API dla Dodawania Przepisów ze Składnikami

## Przegląd

Endpoint `POST /api/v1/recipes/` został rozszerzony o możliwość jednoczesnego dodawania składników do przepisu. System automatycznie:

- **Znajduje istniejące składniki** w katalogu na podstawie nazwy
- **Tworzy nowe składniki** jeśli nie istnieją w katalogu
- **Łączy składniki z przepisem** poprzez `RecipeItem` z określoną ilością

## Endpoint

```
POST /api/v1/recipes/
```

### Wymagania

- **Autoryzacja:** Wymagana (Bearer token)
- **Content-Type:** `application/json`

### Struktura Request Body

```json
{
  "title": "Nazwa przepisu",
  "external_url": "https://example.com/recipe" (opcjonalne),
  "image_url": "https://example.com/image.jpg" (opcjonalne),
  "preparation_steps": "Kroki przygotowania" (opcjonalne),
  "prep_time_minutes": 30 (opcjonalne),
  "ingredients": [
    {
      "name": "Nazwa składnika",
      "quantity_value": 250.0,
      "quantity_unit": "g"
    }
  ] (opcjonalne)
}
```

### Pola

#### Podstawowe pola przepisu

- `title` (wymagane): Nazwa przepisu (1-255 znaków)
- `external_url` (opcjonalne): URL źródła przepisu
- `image_url` (opcjonalne): URL zdjęcia przepisu
- `preparation_steps` (opcjonalne): Kroki przygotowania (domyślnie "")
- `prep_time_minutes` (opcjonalne): Czas przygotowania w minutach (domyślnie 0)

#### Składniki (opcjonalne)

- `ingredients` (opcjonalne): Lista składników
  - `name` (wymagane): Nazwa składnika (1-255 znaków)
  - `quantity_value` (wymagane): Wartość ilości (≥ 0)
  - `quantity_unit` (wymagane): Jednostka ilości (1-50 znaków)

### Przykład Request

```json
{
  "title": "Tort czekoladowy",
  "external_url": "https://example.com/tort-czekoladowy",
  "preparation_steps": "1. Wymieszaj składniki\n2. Piecz w 180°C przez 45 minut",
  "prep_time_minutes": 90,
  "ingredients": [
    {
      "name": "Mąka pszenna",
      "quantity_value": 200,
      "quantity_unit": "g"
    },
    {
      "name": "Cukier",
      "quantity_value": 150,
      "quantity_unit": "g"
    },
    {
      "name": "Jajka",
      "quantity_value": 3,
      "quantity_unit": "szt"
    },
    {
      "name": "Masło",
      "quantity_value": 100,
      "quantity_unit": "g"
    }
  ]
}
```

### Response

**Status Code:** `201 Created`

```json
{
  "recipe_id": "770e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Tort czekoladowy",
  "external_url": "https://example.com/tort-czekoladowy",
  "image_url": null,
  "preparation_steps": "1. Wymieszaj składniki\n2. Piecz w 180°C przez 45 minut",
  "prep_time_minutes": 90,
  "created_at": "2024-03-15T13:10:00"
}
```

## Logika działania

### 1. Walidacja użytkownika

System sprawdza czy użytkownik istnieje w bazie danych.

### 2. Tworzenie przepisu

Tworzony jest nowy przepis z podanymi danymi.

### 3. Przetwarzanie składników

Dla każdego składnika w liście `ingredients`:

#### a) Wyszukiwanie składnika w katalogu

```python
existing_item = await catalog_item_repository.get_by_name(ingredient.name)
```

#### b) Tworzenie nowego składnika (jeśli nie istnieje)

```python
if not existing_item:
    new_item = CatalogItem(name=ingredient.name)
    catalog_item = await catalog_item_repository.create(new_item)
else:
    catalog_item = existing_item
```

#### c) Tworzenie połączenia przepis-składnik

```python
recipe_item = RecipeItem(
    recipe_id=recipe_id,
    item_id=catalog_item.id,
    quantity=Quantity(ingredient.quantity_value, ingredient.quantity_unit)
)
await recipe_item_repository.create(recipe_item)
```

## Przykłady użycia

### Przepis bez składników

```json
{
  "title": "Prosty przepis",
  "preparation_steps": "Wymieszaj składniki"
}
```

### Przepis z jednym składnikiem

```json
{
  "title": "Jajecznica",
  "ingredients": [
    {
      "name": "Jajka",
      "quantity_value": 2,
      "quantity_unit": "szt"
    }
  ]
}
```

### Przepis z wieloma składnikami

```json
{
  "title": "Spaghetti Carbonara",
  "ingredients": [
    {
      "name": "Makaron spaghetti",
      "quantity_value": 400,
      "quantity_unit": "g"
    },
    {
      "name": "Jajka",
      "quantity_value": 4,
      "quantity_unit": "szt"
    },
    {
      "name": "Parmezan",
      "quantity_value": 100,
      "quantity_unit": "g"
    },
    {
      "name": "Boczek",
      "quantity_value": 200,
      "quantity_unit": "g"
    }
  ]
}
```

## Obsługiwane jednostki

System obsługuje różne jednostki miary:

- **Wagi:** g, kg, dag
- **Objętości:** ml, l, szklanka, łyżka, łyżeczka
- **Ilości:** szt, sztuka, sztuk
- **Inne:** szczypta, ząbek, plaster

## Błędy

### 400 Bad Request

- Nieprawidłowa struktura JSON
- Brak wymaganych pól
- Nieprawidłowe wartości (np. ujemna ilość)

### 401 Unauthorized

- Brak tokenu autoryzacji
- Nieprawidłowy token

### 422 Unprocessable Entity

- Błędy walidacji Pydantic
- Nieprawidłowe formaty danych

## Uwagi techniczne

- **Transakcyjność:** Cała operacja (przepis + składniki) jest wykonywana w jednej transakcji
- **Duplikaty:** System automatycznie wykrywa i używa istniejących składników o tej samej nazwie
- **Wielkość liter:** Nazwy składników są porównywane z uwzględnieniem wielkości liter
- **Walidacja:** Wszystkie dane są walidowane przez Pydantic przed zapisem
