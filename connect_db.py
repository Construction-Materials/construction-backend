"""
Skrypt do interaktywnego połączenia z bazą danych SQLite.
Uruchom: python connect_db.py
"""

import sqlite3
from pathlib import Path

# Ścieżka do bazy danych
db_path = Path(__file__).parent / "construction_manager.db"

# Połącz z bazą
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row  # Umożliwia dostęp do kolumn przez nazwę

cursor = conn.cursor()

print("Połączono z bazą danych!")
print(f"Lokalizacja: {db_path}\n")

# Przykładowe zapytania
print("=== Lista tabel ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

print("\n=== Przykładowe dane z constructions ===")
cursor.execute("SELECT * FROM constructions LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(dict(row))



# Możesz teraz wykonywać własne zapytania:
# cursor.execute("SELECT * FROM constructions WHERE name LIKE '%test%';")
# results = cursor.fetchall()

# Pamiętaj o zamknięciu połączenia
conn.close()

