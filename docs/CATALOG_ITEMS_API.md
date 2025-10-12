# Catalog Items API Documentation

## Przegląd

API dla zarządzania składnikami (catalog items) w systemie Recipe AI Extractor. Składniki są posortowane według ostatniego użycia, co ułatwia znajdowanie najczęściej używanych składników.

## Endpointy

### 1. Lista składników (z paginacją)

**`GET /api/v1/catalog-items/`**

Pobiera listę składników z zaawansowaną paginacją i sortowaniem.

#### Parametry zapytania:

- `limit` (int, opcjonalny): Liczba elementów na stronie (domyślnie: 20, max: 100)
- `offset` (int, opcjonalny): Liczba elementów do pominięcia (domyślnie: 0)

#### Przykład żądania:

```http
GET /api/v1/catalog-items/?limit=10&offset=0
```

#### Przykład odpowiedzi:

```json
{
  "items": [
    {
      "item_id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Mąka pszenna"
    },
    {
      "item_id": "660e8400-e29b-41d4-a716-446655440002",
      "name": "Jajka"
    }
  ],
  "total": 11,
  "page": 1,
  "size": 10,
  "has_next": true,
  "has_prev": false,
  "links": {
    "next": "/api/v1/catalog-items?limit=10&offset=10"
  }
}
```

#### Sortowanie:

Składniki są sortowane według:

1. **`last_used`** (malejąco) - najpierw ostatnio używane
2. **`name`** (alfabetycznie) - jako drugie kryterium

### 2. Publiczna lista składników

**`GET /api/v1/catalog-items/public`**

Pobiera wszystkie składniki bez paginacji (dla prostych przypadków użycia).

#### Przykład odpowiedzi:

```json
[
  {
    "item_id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Mąka pszenna"
  },
  {
    "item_id": "660e8400-e29b-41d4-a716-446655440002",
    "name": "Jajka"
  }
]
```

### 3. Wyszukiwanie składników

**`GET /api/v1/catalog-items/search`**

Wyszukuje składniki po nazwie z sortowaniem według ostatniego użycia.

#### Parametry zapytania:

- `name` (string, wymagany): Termin wyszukiwania (min. 1 znak)
- `limit` (int, opcjonalny): Liczba wyników (domyślnie: 20, max: 100)
- `offset` (int, opcjonalny): Offset dla paginacji (domyślnie: 0)

#### Przykład żądania:

```http
GET /api/v1/catalog-items/search?name=Mąka&limit=5
```

#### Przykład odpowiedzi:

```json
{
  "items": [
    {
      "item_id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Mąka pszenna"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 5,
  "has_next": false,
  "has_prev": false,
  "links": {}
}
```

### 4. Tworzenie składnika

**`POST /api/v1/catalog-items/`**

Tworzy nowy składnik w katalogu.

#### Przykład żądania:

```json
{
  "name": "Nowy składnik"
}
```

#### Przykład odpowiedzi:

```json
{
  "item_id": "a048094b-c798-4de6-a5ba-1893c4d6ccb5",
  "name": "Nowy składnik",
  "last_used": null
}
```

### 5. Pobieranie składnika

**`GET /api/v1/catalog-items/{item_id}`**

Pobiera szczegóły konkretnego składnika.

#### Przykład odpowiedzi:

```json
{
  "item_id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Mąka pszenna",
  "last_used": "2024-03-15T10:30:00"
}
```

### 6. Aktualizacja składnika

**`PUT /api/v1/catalog-items/{item_id}`**

Aktualizuje nazwę składnika.

#### Przykład żądania:

```json
{
  "name": "Nowa nazwa składnika"
}
```

#### Przykład odpowiedzi:

```json
{
  "item_id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Nowa nazwa składnika",
  "last_used": "2024-03-15T10:30:00"
}
```

### 7. Usuwanie składnika

**`DELETE /api/v1/catalog-items/{item_id}`**

Usuwa składnik z katalogu.

#### Odpowiedź:

```
HTTP 204 No Content
```

## Struktury danych

### CatalogItemSimpleDTO

```json
{
  "item_id": "string (UUID)",
  "name": "string"
}
```

### CatalogItemResponseDTO

```json
{
  "item_id": "string (UUID)",
  "name": "string",
  "last_used": "string (ISO datetime) | null"
}
```

### CatalogItemSimpleListResponseDTO

```json
{
  "items": "CatalogItemSimpleDTO[]",
  "total": "number",
  "page": "number",
  "size": "number",
  "has_next": "boolean",
  "has_prev": "boolean",
  "links": {
    "next": "string (URL) | undefined",
    "prev": "string (URL) | undefined"
  }
}
```

## Paginacja

### Parametry:

- **`limit`**: Liczba elementów na stronie (1-100)
- **`offset`**: Liczba elementów do pominięcia

### Nawigacja:

- **`has_next`**: Czy istnieje następna strona
- **`has_prev`**: Czy istnieje poprzednia strona
- **`links`**: Gotowe URL-e do nawigacji

### Przykłady nawigacji:

```javascript
// Strona 1
GET /api/v1/catalog-items?limit=10&offset=0

// Strona 2
GET /api/v1/catalog-items?limit=10&offset=10

// Strona 3
GET /api/v1/catalog-items?limit=10&offset=20
```

## Sortowanie

Składniki są automatycznie sortowane według:

1. **Ostatniego użycia** (malejąco) - najpierw najczęściej używane
2. **Nazwy** (alfabetycznie) - jako drugie kryterium

## Błędy

### 400 Bad Request

```json
{
  "error": "ValidationError",
  "message": "Request validation failed",
  "details": [...]
}
```

### 404 Not Found

```json
{
  "error": "EntityNotFoundError",
  "message": "Catalog item not found"
}
```

### 409 Conflict

```json
{
  "error": "ValidationError",
  "message": "Catalog item with name 'Mąka pszenna' already exists"
}
```

## Przykłady użycia

### Pobieranie wszystkich składników

```javascript
// Opcja 1: Duży limit
const response = await fetch("/api/v1/catalog-items?limit=1000&offset=0");
const data = await response.json();

// Opcja 2: Endpoint public
const response = await fetch("/api/v1/catalog-items/public");
const items = await response.json();
```

### Nawigacja z paginacją

```javascript
const response = await fetch("/api/v1/catalog-items?limit=10&offset=0");
const data = await response.json();

// Sprawdź czy można iść dalej
if (data.has_next) {
  const nextUrl = data.links.next;
  const nextResponse = await fetch(nextUrl);
  const nextData = await nextResponse.json();
}
```

### Wyszukiwanie

```javascript
const searchTerm = "Mąka";
const response = await fetch(
  `/api/v1/catalog-items/search?name=${encodeURIComponent(searchTerm)}`
);
const results = await response.json();
```

## Uwagi

- Wszystkie endpointy zwracają składniki posortowane według ostatniego użycia
- Endpoint `/public` nie zawiera informacji o paginacji
- Główne endpointy zawierają pełną informację o paginacji
- Sortowanie jest automatyczne i nie można go zmienić
- Nazwy składników muszą być unikalne
