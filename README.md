# Recipe AI Extractor Backend

Backend API dla **The Recipe AI Extractor** - aplikacji do automatycznego ekstrahowania przepisów z linków (TikTok, Instagram) za pomocą AI.

## Architektura

Projekt wykorzystuje **Hexagonal Architecture (Ports & Adapters)** z następującymi warstwami:

- **Domain**: Encje domenowe, Value Objects, Repository interfaces
- **Application**: Use Cases, DTOs, walidacja biznesowa
- **Infrastructure**: Adaptery (SQLAlchemy, FastAPI), external services
- **Shared**: Wspólne utilities, exceptions, config

## Struktura Projektu

```
RecepieScraperBackend/
├── src/
│   ├── domain/              # Core business logic
│   │   ├── entities/        # User, Recipe, CatalogItem, RecipeItem, ProcessingJob
│   │   ├── value_objects/   # JobStatus, Quantity
│   │   └── repositories/     # Repository interfaces (ports)
│   ├── application/         # Use cases & business rules
│   │   ├── use_cases/       # UserUseCases, RecipeUseCases, ProcessingJobUseCases
│   │   └── dtos/            # Data Transfer Objects
│   ├── infrastructure/      # Adapters & implementations
│   │   ├── database/        # SQLAlchemy models & repository impl
│   │   └── api/             # FastAPI routes & controllers
│   └── shared/              # Common utilities, exceptions
├── tests/                   # Test files
├── alembic/                 # Database migrations
└── main.py                  # Application entry point
```

## Schemat Bazy Danych (5 Znormalizowanych Tabel)

1. **User** - Profile użytkowników z autoryzacją
2. **Recipe** - Przepisy z krokami przygotowania
3. **CatalogItem** - Katalog unikalnych składników (minimalizuje redundancję)
4. **RecipeItem** - Junction table łącząca Recipe ↔ CatalogItem + ilości
5. **ProcessingJob** - Dziennik zadań asynchronicznych dla AI extraction

## Technologie

- **Backend**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL (dev: SQLite)
- **Migrations**: Alembic
- **Testing**: pytest, pytest-asyncio
- **AI Integration**: Gemini API / OpenAI
- **Serverless**: AWS Lambda (Python 3.11)

## Setup

1. **Instalacja zależności:**

```bash
pip install -r requirements.txt
```

2. **Konfiguracja środowiska:**

```bash
cp env.example .env
# Edytuj .env z odpowiednimi wartościami
```

3. **Migracje bazy danych:**

```bash
alembic upgrade head
```

4. **Uruchomienie aplikacji:**

```bash
python main.py
```

API będzie dostępne pod adresem: `http://localhost:8000`

## API Endpoints

### Users

- `POST /api/v1/users/` - Utwórz użytkownika
- `GET /api/v1/users/me` - Pobierz dane aktualnego użytkownika
- `GET /api/v1/users/{user_id}` - Pobierz użytkownika po ID
- `PUT /api/v1/users/{user_id}` - Aktualizuj użytkownika
- `DELETE /api/v1/users/{user_id}` - Usuń użytkownika
- `POST /api/v1/users/login` - Logowanie
- `POST /api/v1/users/change-password` - Zmiana hasła

### Recipes

- `POST /api/v1/recipes/` - Utwórz przepis
- `GET /api/v1/recipes/{recipe_id}` - Pobierz przepis po ID
- `PUT /api/v1/recipes/{recipe_id}` - Aktualizuj przepis
- `DELETE /api/v1/recipes/{recipe_id}` - Usuń przepis
- `GET /api/v1/recipes/` - Lista przepisów
- `GET /api/v1/recipes/my/recipes` - Moje przepisy
- `GET /api/v1/recipes/search` - Wyszukaj przepisy

### Processing Jobs

- `POST /api/v1/processing-jobs/` - Utwórz zadanie przetwarzania
- `GET /api/v1/processing-jobs/{job_id}` - Pobierz zadanie po ID
- `PUT /api/v1/processing-jobs/{job_id}/status` - Aktualizuj status zadania
- `GET /api/v1/processing-jobs/` - Lista zadań użytkownika
- `GET /api/v1/processing-jobs/active` - Aktywne zadania (admin)

## Dokumentacja API

Automatyczna dokumentacja Swagger/OpenAPI dostępna pod:

- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

## Testy

```bash
# Uruchomienie testów
pytest

# Z coverage
pytest --cov=src tests/
```

## Następne Kroki

1. ✅ **Etap 1**: Web API & Hexagonal Architecture
2. 🔄 **Etap 2**: SSR Frontend & Job Scheduling (Celery + Redis)
3. 🔄 **Etap 3**: SPA Frontend Support
4. 🔄 **Etap 4**: Cloud Integration (AWS Lambda)
