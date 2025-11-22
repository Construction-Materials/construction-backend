"""
Unit Enum Value Object.
"""

from enum import Enum


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

