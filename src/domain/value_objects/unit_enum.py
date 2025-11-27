"""
Unit Enum Value Object.
"""

from enum import Enum
from typing import Optional


class UnitEnum(str, Enum):
    """Unit enum for materials."""
    METERS = "meters"
    KILOGRAMS = "kilograms"
    CUBIC_METERS = "cubic_meters"
    CUBIC_CENTIMETERS = "cubic_centimeters"
    CUBIC_MILLIMETERS = "cubic_millimeters"
    LITERS = "liters"
    PIECES = "pieces"
    OTHER = "other"

    @classmethod
    def normalize(cls, unit: str) -> "UnitEnum":
        """
        Normalize unit string to UnitEnum.
        
        Accepts various formats like:
        - "kg", "kilogram", "kilograms" -> KILOGRAMS
        - "m", "meter", "meters" -> METERS
        - "m3", "m³", "cubic_meter", "cubic_meters" -> CUBIC_METERS
        - "l", "litre", "liter", "liters" -> LITERS
        - "szt", "sztuk", "piece", "pieces" -> PIECES
        etc.
        """
        if not unit:
            return cls.OTHER
        
        unit_lower = unit.lower().strip()
        
        # Map common variations to enum values
        unit_mapping = {
            # Meters
            "m": cls.METERS,
            "meter": cls.METERS,
            "metr": cls.METERS,
            "meters": cls.METERS,
            "metrów": cls.METERS,
            "metrow": cls.METERS,
            "km": cls.METERS,  # kilometers -> meters
            "kilometer": cls.METERS,
            "kilometr": cls.METERS,
            "kilometers": cls.METERS,
            "kilometrów": cls.METERS,
            "cm": cls.METERS,  # centimeters -> meters
            "centimeter": cls.METERS,
            "centymetr": cls.METERS,
            "centimeters": cls.METERS,
            "centymetrów": cls.METERS,
            "mm": cls.METERS,  # millimeters -> meters
            "millimeter": cls.METERS,
            "milimetr": cls.METERS,
            "millimeters": cls.METERS,
            "milimetrów": cls.METERS,
            
            # Kilograms
            "kg": cls.KILOGRAMS,
            "kilogram": cls.KILOGRAMS,
            "kilograms": cls.KILOGRAMS,
            "kilogramów": cls.KILOGRAMS,
            "kilogramow": cls.KILOGRAMS,
            "g": cls.KILOGRAMS,  # grams -> kilograms
            "gram": cls.KILOGRAMS,
            "grams": cls.KILOGRAMS,
            "gramów": cls.KILOGRAMS,
            "gramow": cls.KILOGRAMS,
            "t": cls.KILOGRAMS,  # tons -> kilograms
            "ton": cls.KILOGRAMS,
            "tona": cls.KILOGRAMS,
            "tons": cls.KILOGRAMS,
            "tony": cls.KILOGRAMS,
            
            # Cubic meters
            "m3": cls.CUBIC_METERS,
            "m³": cls.CUBIC_METERS,
            "cubic_meter": cls.CUBIC_METERS,
            "cubic_meters": cls.CUBIC_METERS,
            "metr_sześcienny": cls.CUBIC_METERS,
            "metr_szescienny": cls.CUBIC_METERS,
            "metry_sześcienne": cls.CUBIC_METERS,
            "metry_szescienne": cls.CUBIC_METERS,
            
            # Cubic centimeters
            "cm3": cls.CUBIC_CENTIMETERS,
            "cm³": cls.CUBIC_CENTIMETERS,
            "cubic_centimeter": cls.CUBIC_CENTIMETERS,
            "cubic_centimeters": cls.CUBIC_CENTIMETERS,
            "centymetr_sześcienny": cls.CUBIC_CENTIMETERS,
            "centymetr_szescienny": cls.CUBIC_CENTIMETERS,
            
            # Cubic millimeters
            "mm3": cls.CUBIC_MILLIMETERS,
            "mm³": cls.CUBIC_MILLIMETERS,
            "cubic_millimeter": cls.CUBIC_MILLIMETERS,
            "cubic_millimeters": cls.CUBIC_MILLIMETERS,
            "milimetr_sześcienny": cls.CUBIC_MILLIMETERS,
            "milimetr_szescienny": cls.CUBIC_MILLIMETERS,
            
            # Liters
            "l": cls.LITERS,
            "litre": cls.LITERS,
            "liter": cls.LITERS,
            "liters": cls.LITERS,
            "litrów": cls.LITERS,
            "litrow": cls.LITERS,
            "l.": cls.LITERS,
            "l ": cls.LITERS,
            # Milliliters -> liters
            "ml": cls.LITERS,
            "ml.": cls.LITERS,
            "ml ": cls.LITERS,
            "milliliter": cls.LITERS,
            "milliliters": cls.LITERS,
            "mililitr": cls.LITERS,
            "mililitrów": cls.LITERS,
            "mililitrow": cls.LITERS,
            "mililitry": cls.LITERS,
            "ml³": cls.LITERS,
            "ml3": cls.LITERS,
            "millilitre": cls.LITERS,
            "millilitres": cls.LITERS,
            
            # Pieces
            "szt": cls.PIECES,
            "szt.": cls.PIECES,
            "sztuk": cls.PIECES,
            "sztuka": cls.PIECES,
            "sztuki": cls.PIECES,
            "piece": cls.PIECES,
            "pieces": cls.PIECES,
            "pcs": cls.PIECES,
            "pcs.": cls.PIECES,
            "pc": cls.PIECES,
            "pc.": cls.PIECES,
        }
        
        # Try exact match first
        if unit_lower in unit_mapping:
            return unit_mapping[unit_lower]
        
        # Try to match enum value directly
        try:
            return cls(unit_lower)
        except ValueError:
            pass
        
        # If no match found, return OTHER
        return cls.OTHER

