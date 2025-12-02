# Construction Manager Backend

Backend API dla **Construction Manager** - aplikacji do zarządzania projektami budowlanymi, materiałami i magazynami.

## Architektura

Projekt wykorzystuje **Hexagonal Architecture (Ports & Adapters)** z następującymi warstwami:

- **Domain**: Encje domenowe, Value Objects, Repository interfaces
- **Application**: Use Cases, DTOs, walidacja biznesowa
- **Infrastructure**: Adaptery (SQLAlchemy, FastAPI), external services
- **Shared**: Wspólne utilities, exceptions, config

## Struktura Projektu

```
construction-backend/
├── src/
│   ├── domain/              # Core business logic
│   │   ├── entities/        # Construction, Material, Category, StorageItem
│   │   ├── value_objects/   # ConstructionStatus, UnitEnum
│   │   └── repositories/     # Repository interfaces (ports)
│   ├── application/         # Use cases & business rules
│   │   ├── use_cases/       # ConstructionUseCases, MaterialUseCases, CategoryUseCases, StorageItemUseCases
│   │   └── dtos/            # Data Transfer Objects
│   ├── infrastructure/      # Adapters & implementations
│   │   ├── database/        # SQLAlchemy models & repository impl
│   │   └── api/             # FastAPI routes & controllers
│   └── shared/              # Common utilities, exceptions, config
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── mock_data/               # Mock data for testing
└── main.py                  # Application entry point
```

## Schemat Bazy Danych

1. **Category** - Kategorie materiałów
2. **Construction** - Projekty budowlane (budowy)
3. **Material** - Materiały budowlane z przypisaną kategorią
4. **StorageItem** - Pozycje magazynowe (łączy Construction ↔ Material + ilości)

## Technologie

- **Backend**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0+
- **Database**: SQLite
- **Migrations**: Alembic
- **Testing**: pytest
- **AI Integration**: OpenAI API (analiza dokumentów)
- **File Uploads**: Lokalne przechowywanie plików

## Setup

1. **Utworzenie wirtualnego środowiska:**

```bash
python -m venv venv
```

2. **Aktywacja wirtualnego środowiska:**

```bash
# Na macOS/Linux:
source venv/bin/activate

# Na Windows:
venv\Scripts\activate
```

3. **Instalacja zależności:**

```bash
pip install -r requirements.txt
```

4. **Konfiguracja środowiska:**

```bash
cp env.example .env
# Edytuj .env z odpowiednimi wartościami (opcjonalnie)
```

Aplikacja używa **SQLite** jako bazy danych - nie wymaga dodatkowej konfiguracji!

5. **Migracje bazy danych:**

```bash
alembic upgrade head
```

6. **Uruchomienie aplikacji:**

```bash
python main.py
```

API będzie dostępne pod adresem: `http://localhost:8000`

## API Endpoints

### Constructions (Budowy)

- `GET /api/v1/constructions/` - Lista wszystkich budów (z paginacją)
- `GET /api/v1/constructions/public` - Lista wszystkich budów (public endpoint)
- `GET /api/v1/constructions/{construction_id}` - Pobierz budowę po ID
- `POST /api/v1/constructions/` - Utwórz nową budowę (obsługuje JSON i multipart/form-data z plikiem)
- `PUT /api/v1/constructions/{construction_id}` - Aktualizuj budowę
- `DELETE /api/v1/constructions/{construction_id}` - Usuń budowę
- `GET /api/v1/constructions/search` - Wyszukaj budowy (z filtrowaniem po statusie)
- `GET /api/v1/constructions/statistics` - Pobierz statystyki dla wszystkich budów
- `POST /api/v1/constructions/{construction_id}/analyze-document` - Analizuj dokument (zdjęcie/PDF) używając AI
- `POST /api/v1/constructions/{construction_id}/upload-image` - Prześlij zdjęcie dla budowy
- `GET /api/v1/constructions/images/{filename}` - Pobierz zdjęcie budowy

### Materials (Materiały)

- `GET /api/v1/materials/` - Lista wszystkich materiałów (z paginacją)
- `GET /api/v1/materials/public` - Lista wszystkich materiałów (public endpoint)
- `GET /api/v1/materials/{material_id}` - Pobierz materiał po ID
- `POST /api/v1/materials/` - Utwórz nowy materiał
- `POST /api/v1/materials/bulk` - Utwórz wiele materiałów jednocześnie
- `PUT /api/v1/materials/{material_id}` - Aktualizuj materiał
- `DELETE /api/v1/materials/{material_id}` - Usuń materiał
- `GET /api/v1/materials/search` - Wyszukaj materiały (z filtrowaniem po kategorii)
- `GET /api/v1/materials/category/{category_id}` - Pobierz materiały po kategorii
- `GET /api/v1/materials/by-construction/{construction_id}` - Pobierz materiały dla danej budowy

### Storage Items (Pozycje magazynowe)

- `GET /api/v1/storage-items/construction/{construction_id}` - Pobierz pozycje magazynowe dla budowy
- `GET /api/v1/storage-items/construction/{construction_id}/materials` - Pobierz listę materiałów z informacjami dla budowy
- `GET /api/v1/storage-items/construction/{construction_id}/material/{material_id}` - Pobierz pozycję magazynową po ID budowy i materiału
- `POST /api/v1/storage-items/` - Utwórz nową pozycję magazynową
- `POST /api/v1/storage-items/construction/{construction_id}/bulk` - Utwórz wiele pozycji magazynowych dla budowy
- `PUT /api/v1/storage-items/construction/{construction_id}/material/{material_id}` - Aktualizuj pozycję magazynową
- `DELETE /api/v1/storage-items/construction/{construction_id}/material/{material_id}` - Usuń pozycję magazynową
- `GET /api/v1/storage-items/material/{material_id}` - Pobierz pozycje magazynowe dla materiału

### Categories (Kategorie)

- `GET /api/v1/categories/` - Lista wszystkich kategorii (z paginacją)
- `GET /api/v1/categories/public` - Lista wszystkich kategorii (public endpoint)
- `GET /api/v1/categories/{category_id}` - Pobierz kategorię po ID
- `POST /api/v1/categories/` - Utwórz nową kategorię
- `PUT /api/v1/categories/{category_id}` - Aktualizuj kategorię
- `DELETE /api/v1/categories/{category_id}` - Usuń kategorię
- `GET /api/v1/categories/search` - Wyszukaj kategorie

### Health Check

- `GET /` - Root endpoint z informacjami o API
- `GET /health` - Health check endpoint
- `GET /api/v1/health` - Health check endpoint API

## Dokumentacja API

### Automatyczna dokumentacja

- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

### Szczegółowa dokumentacja

- [Catalog Items API](docs/CATALOG_ITEMS_API.md) - Kompletna dokumentacja API dla składników
- [Recipe Ingredients API](docs/RECIPE_INGREDIENTS_API.md) - Dokumentacja API dla składników przepisów
- [Recipe with Ingredients API](docs/RECIPE_WITH_INGREDIENTS_API.md) - Dokumentacja API dla przepisów ze składnikami

## Testy

```bash
# Uruchomienie testów
pytest

# Z coverage
pytest --cov=src tests/
```

## Funkcjonalności

- Zarządzanie budowami (CRUD)
- Zarządzanie materiałami budowlanymi (CRUD)
- Zarządzanie kategoriami materiałów (CRUD)
- Zarządzanie pozycjami magazynowymi (CRUD)
- Wyszukiwanie i filtrowanie
- Analiza dokumentów z użyciem AI (OpenAI)
- Upload i przechowywanie zdjęć budów
- Statystyki dla budów
- Bulk operations (masowe operacje)

## Następne Kroki

1. **Etap 1**: Web API & Hexagonal Architecture (zakończony)
2. **Etap 2**: SSR Frontend & Job Scheduling (Celery + Redis)
3. **Etap 3**: SPA Frontend Support
4. **Etap 4**: Cloud Integration (AWS Lambda)
