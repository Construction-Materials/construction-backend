#!/usr/bin/env python3
"""
Database seeding script for Recipe AI Extractor.
Loads mock data into the main database for development.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mock_data.data_loader import load_mock_data, reset_mock_data
from src.infrastructure.database.connection import init_database
import asyncio


async def setup_database():
    """Initialize database tables."""
    print("🔧 Inicjalizacja bazy danych...")
    await init_database()
    print("✅ Baza danych zainicjalizowana")


def main():
    """Main seeding function."""
    print("🌱 Construction Manager - Database Seeding")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "reset":
            print("🔄 Resetowanie bazy danych...")
            asyncio.run(setup_database())
            reset_mock_data()
            print("✅ Baza danych zresetowana z mock data")
            
        elif command == "clear":
            print("🗑️ Czyszczenie bazy danych...")
            from mock_data.data_loader import MockDataLoader, create_database_session
            session = create_database_session()
            try:
                loader = MockDataLoader(session)
                loader.clear_all_data()
                print("✅ Baza danych wyczyszczona")
            finally:
                session.close()
                
        elif command == "help":
            print_help()
            
        else:
            print(f"❌ Nieznana komenda: {command}")
            print_help()
    else:
        # Default: load mock data
        print("🔄 Ładowanie mock data...")
        asyncio.run(setup_database())
        load_mock_data()
        print("✅ Mock data załadowane pomyślnie!")
        print("\n🚀 Możesz teraz uruchomić aplikację:")
        print("   python main.py")
        print("\n📊 Dostępne endpointy:")
        print("   GET /api/v1/users")
        print("   GET /api/v1/recipes")
        print("   GET /api/v1/catalog-items")


def print_help():
    """Print help information."""
    print("🌱 Database Seeding Script")
    print("=" * 30)
    print("Użycie:")
    print("  python seed_database.py          # Załaduj mock data")
    print("  python seed_database.py reset   # Wyczyść i załaduj ponownie")
    print("  python seed_database.py clear   # Wyczyść bazę danych")
    print("  python seed_database.py help    # Pokaż tę pomoc")
    print("\nPrzykłady:")
    print("  # Pierwsze uruchomienie")
    print("  python seed_database.py")
    print("  python main.py")
    print("\n  # Reset danych")
    print("  python seed_database.py reset")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Błąd: {e}")
        sys.exit(1)
