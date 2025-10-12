#!/usr/bin/env python3
"""
Przykład użycia API do dodawania przepisu ze składnikami.

Ten skrypt demonstruje jak używać nowego endpointu do tworzenia przepisów
z automatycznym dodawaniem składników.
"""

import requests
import json
from decimal import Decimal

# Konfiguracja API
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = "550e8400-e29b-41d4-a716-446655440001"  # Przykładowy token użytkownika

def create_recipe_with_ingredients():
    """Tworzy przepis ze składnikami."""
    
    # Przykład 1: Tort czekoladowy
    recipe_data = {
        "title": "Tort czekoladowy",
        "external_url": "https://example.com/tort-czekoladowy",
        "preparation_steps": "1. Wymieszaj suche składniki\n2. Dodaj mokre składniki\n3. Piecz w 180°C przez 45 minut",
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
            },
            {
                "name": "Kakao",
                "quantity_value": 50,
                "quantity_unit": "g"
            },
            {
                "name": "Proszek do pieczenia",
                "quantity_value": 1,
                "quantity_unit": "łyżeczka"
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recipes/",
            headers=headers,
            json=recipe_data
        )
        
        if response.status_code == 201:
            recipe = response.json()
            print("✅ Przepis utworzony pomyślnie!")
            print(f"ID przepisu: {recipe['recipe_id']}")
            print(f"Tytuł: {recipe['title']}")
            print(f"Czas przygotowania: {recipe['prep_time_minutes']} minut")
            return recipe['recipe_id']
        else:
            print(f"❌ Błąd: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd połączenia: {e}")
        return None

def create_simple_recipe():
    """Tworzy prosty przepis bez składników."""
    
    recipe_data = {
        "title": "Prosty przepis",
        "preparation_steps": "Wymieszaj wszystkie składniki razem"
    }
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recipes/",
            headers=headers,
            json=recipe_data
        )
        
        if response.status_code == 201:
            recipe = response.json()
            print("✅ Prosty przepis utworzony!")
            print(f"ID: {recipe['recipe_id']}")
            return recipe['recipe_id']
        else:
            print(f"❌ Błąd: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd połączenia: {e}")
        return None

def create_recipe_with_existing_ingredients():
    """Tworzy przepis używając składników, które mogą już istnieć w katalogu."""
    
    recipe_data = {
        "title": "Jajecznica",
        "preparation_steps": "1. Rozgrzej patelnię\n2. Wbij jajka\n3. Smaż mieszając",
        "prep_time_minutes": 5,
        "ingredients": [
            {
                "name": "Jajka",  # Ten składnik może już istnieć
                "quantity_value": 2,
                "quantity_unit": "szt"
            },
            {
                "name": "Masło",  # Ten składnik może już istnieć
                "quantity_value": 1,
                "quantity_unit": "łyżka"
            },
            {
                "name": "Sól",
                "quantity_value": 1,
                "quantity_unit": "szczypta"
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recipes/",
            headers=headers,
            json=recipe_data
        )
        
        if response.status_code == 201:
            recipe = response.json()
            print("✅ Jajecznica utworzona!")
            print(f"ID: {recipe['recipe_id']}")
            print("System automatycznie:")
            print("- Znajdzie istniejące składniki (Jajka, Masło)")
            print("- Utworzy nowe składniki (Sól)")
            print("- Połączy wszystko z przepisem")
            return recipe['recipe_id']
        else:
            print(f"❌ Błąd: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd połączenia: {e}")
        return None

def check_recipe(recipe_id):
    """Sprawdza utworzony przepis."""
    
    try:
        response = requests.get(f"{BASE_URL}/recipes/{recipe_id}")
        
        if response.status_code == 200:
            recipe = response.json()
            print(f"\n📋 Szczegóły przepisu:")
            print(f"Tytuł: {recipe['title']}")
            print(f"Kroki: {recipe['preparation_steps']}")
            print(f"Czas: {recipe['prep_time_minutes']} minut")
            return True
        else:
            print(f"❌ Nie można pobrać przepisu: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd połączenia: {e}")
        return False

if __name__ == "__main__":
    print("🍳 Przykład użycia API do dodawania przepisów ze składnikami\n")
    
    print("1. Tworzenie tortu czekoladowego ze składnikami...")
    recipe_id = create_recipe_with_ingredients()
    
    if recipe_id:
        print("\n2. Sprawdzanie utworzonego przepisu...")
        check_recipe(recipe_id)
    
    print("\n3. Tworzenie prostego przepisu bez składników...")
    simple_recipe_id = create_simple_recipe()
    
    print("\n4. Tworzenie jajecznicy z istniejącymi składnikami...")
    scrambled_recipe_id = create_recipe_with_existing_ingredients()
    
    print("\n✅ Przykłady zakończone!")
    print("\n💡 Wskazówki:")
    print("- System automatycznie znajdzie istniejące składniki")
    print("- Nowe składniki zostaną utworzone w katalogu")
    print("- Wszystko jest połączone w jednej transakcji")
    print("- Można tworzyć przepisy bez składników")
