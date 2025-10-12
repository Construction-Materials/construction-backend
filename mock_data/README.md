# Mock Data - Dane Testowe

Ten katalog zawiera przykładowe dane testowe dla aplikacji RecepieScraperBackend w formacie JSON.

## Struktura plików

### users.json

Zawiera 7 użytkowników z następującymi polami:

- `id` - UUID użytkownika
- `email` - adres email
- `password_hash` - hash hasła (bcrypt)
- `is_admin` - czy użytkownik jest administratorem
- `created_at` - data utworzenia (ISO 8601)

### catalog_items.json

Zawiera 10 składników z następującymi polami:

- `id` - UUID składnika
- `name` - nazwa składnika
- `last_used` - data ostatniego użycia (ISO 8601)

### recipes.json

Zawiera 8 przepisów z następującymi polami:

- `id` - UUID przepisu
- `user_id` - UUID właściciela przepisu (foreign key do users)
- `title` - tytuł przepisu
- `external_url` - zewnętrzny URL (może być null)
- `preparation_steps` - kroki przygotowania
- `prep_time_minutes` - czas przygotowania w minutach
- `created_at` - data utworzenia (ISO 8601)

### recipe_items.json

Zawiera 33 połączenia przepis-składnik z następującymi polami:

- `id` - UUID połączenia
- `recipe_id` - UUID przepisu (foreign key do recipes)
- `item_id` - UUID składnika (foreign key do catalog_items)
- `quantity` - obiekt z ilością:
  - `value` - wartość liczbowa
  - `unit` - jednostka miary

## Powiązania między encjami

- **Users → Recipes**: Jeden użytkownik może mieć wiele przepisów
- **Recipes → RecipeItems**: Jeden przepis może mieć wiele składników
- **CatalogItems → RecipeItems**: Jeden składnik może być w wielu przepisach

## Przykładowe użycie

```python
import json

# Wczytanie danych użytkowników
with open('mock_data/users.json', 'r', encoding='utf-8') as f:
    users = json.load(f)

# Wczytanie przepisów
with open('mock_data/recipes.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

# Znalezienie przepisów użytkownika
user_id = "550e8400-e29b-41d4-a716-446655440002"
user_recipes = [r for r in recipes if r['user_id'] == user_id]
```

## Uwagi

- Wszystkie hasła to przykładowy hash bcrypt dla hasła "password123"
- Daty są w formacie ISO 8601 (UTC)
- UUID są w formacie standardowym
- Nazwy składników i przepisów są w języku polskim
- Ilości składników są realistyczne dla polskiej kuchni
