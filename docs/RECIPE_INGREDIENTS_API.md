# API dla Pobierania Składników Przepisu

## Przegląd

Endpoint `GET /api/v1/recipes/{recipe_id}/ingredients` pozwala na pobieranie listy składników dla konkretnego przepisu.

## Endpoint

```
GET /api/v1/recipes/{recipe_id}/ingredients
```

### Parametry

- `recipe_id` (UUID, wymagane): ID przepisu

### Wymagania

- **Autoryzacja:** Nie wymagana (publiczny endpoint)
- **Content-Type:** `application/json`

### Przykład Request

```http
GET /api/v1/recipes/770e8400-e29b-41d4-a716-446655440001/ingredients
```

### Response

**Status Code:** `200 OK`

```json
{
  "recipe_id": "770e8400-e29b-41d4-a716-446655440001",
  "ingredients": [
    {
      "recipe_item_id": "880e8400-e29b-41d4-a716-446655440001",
      "ingredient_name": "Mąka pszenna",
      "quantity_value": 200,
      "quantity_unit": "g"
    },
    {
      "recipe_item_id": "880e8400-e29b-41d4-a716-446655440002",
      "ingredient_name": "Cukier",
      "quantity_value": 150,
      "quantity_unit": "g"
    },
    {
      "recipe_item_id": "880e8400-e29b-41d4-a716-446655440003",
      "ingredient_name": "Jajka",
      "quantity_value": 3,
      "quantity_unit": "szt"
    }
  ],
  "total": 3
}
```

### Struktura Response

#### RecipeIngredientsResponseDTO

- `recipe_id` (UUID): ID przepisu
- `ingredients` (List[RecipeIngredientResponseDTO]): Lista składników
- `total` (int): Całkowita liczba składników

#### RecipeIngredientResponseDTO

- `recipe_item_id` (UUID): ID połączenia przepis-składnik
- `ingredient_name` (str): Nazwa składnika
- `quantity_value` (Decimal): Wartość ilości
- `quantity_unit` (str): Jednostka ilości

## Przykłady użycia

### 1. Pobieranie składników przepisu

```bash
curl -X GET "http://localhost:8000/api/v1/recipes/770e8400-e29b-41d4-a716-446655440001/ingredients"
```

### 2. Przepis bez składników

```json
{
  "recipe_id": "770e8400-e29b-41d4-a716-446655440001",
  "ingredients": [],
  "total": 0
}
```

### 3. Przepis z wieloma składnikami

```json
{
  "recipe_id": "770e8400-e29b-41d4-a716-446655440001",
  "ingredients": [
    {
      "recipe_item_id": "880e8400-e29b-41d4-a716-446655440001",
      "ingredient_name": "Mąka pszenna",
      "quantity_value": 200,
      "quantity_unit": "g"
    },
    {
      "recipe_item_id": "880e8400-e29b-41d4-a716-446655440002",
      "ingredient_name": "Cukier",
      "quantity_value": 150,
      "quantity_unit": "g"
    },
    {
      "recipe_item_id": "880e8400-e29b-41d4-a716-446655440003",
      "ingredient_name": "Jajka",
      "quantity_value": 3,
      "quantity_unit": "szt"
    },
    {
      "recipe_item_id": "880e8400-e29b-41d4-a716-446655440004",
      "ingredient_name": "Masło",
      "quantity_value": 100,
      "quantity_unit": "g"
    }
  ],
  "total": 4
}
```

## Błędy

### 404 Not Found

- Przepis o podanym ID nie istnieje

```json
{
  "detail": "Recipe with ID 770e8400-e29b-41d4-a716-446655440001 not found"
}
```

### 422 Unprocessable Entity

- Nieprawidłowy format UUID

```json
{
  "detail": [
    {
      "loc": ["path", "recipe_id"],
      "msg": "invalid input syntax for type uuid",
      "type": "value_error.uuid"
    }
  ]
}
```

## Uwagi techniczne

- **Wydajność:** Endpoint wykonuje JOIN między tabelami `recipe_items` i `catalog_items`
- **Sortowanie:** Składniki są zwracane w kolejności dodania do przepisu
- **Walidacja:** System sprawdza czy przepis istnieje przed pobieraniem składników
- **Pusty wynik:** Jeśli przepis nie ma składników, zwracana jest pusta lista

## Integracja z frontendem

### Pobieranie pełnych danych przepisu

```javascript
// 1. Pobierz podstawowe dane przepisu
const recipe = await fetch("/api/v1/recipes/123").then((r) => r.json());

// 2. Pobierz składniki przepisu
const ingredients = await fetch("/api/v1/recipes/123/ingredients").then((r) =>
  r.json()
);

// 3. Połącz dane
const fullRecipe = {
  ...recipe,
  ingredients: ingredients.ingredients,
};
```

### Przykład użycia w React

```jsx
const RecipeDetails = ({ recipeId }) => {
  const [recipe, setRecipe] = useState(null);
  const [ingredients, setIngredients] = useState([]);

  useEffect(() => {
    // Pobierz przepis
    fetch(`/api/v1/recipes/${recipeId}`)
      .then((r) => r.json())
      .then(setRecipe);

    // Pobierz składniki
    fetch(`/api/v1/recipes/${recipeId}/ingredients`)
      .then((r) => r.json())
      .then((data) => setIngredients(data.ingredients));
  }, [recipeId]);

  return (
    <div>
      <h1>{recipe?.title}</h1>
      <h2>Składniki:</h2>
      <ul>
        {ingredients.map((ingredient) => (
          <li key={ingredient.recipe_item_id}>
            {ingredient.ingredient_name} - {ingredient.quantity_value}{" "}
            {ingredient.quantity_unit}
          </li>
        ))}
      </ul>
    </div>
  );
};
```

## Porównanie z innymi endpointami

| Endpoint                        | Zwraca                   | Użycie                            |
| ------------------------------- | ------------------------ | --------------------------------- |
| `GET /recipes/{id}`             | Podstawowe dane przepisu | Wyświetlanie przepisu             |
| `GET /recipes/{id}/ingredients` | Składniki przepisu       | Lista składników                  |
| `GET /catalog-items/`           | Wszystkie składniki      | Katalog składników                |
| `POST /recipes/`                | Utworzony przepis        | Dodawanie przepisu ze składnikami |
