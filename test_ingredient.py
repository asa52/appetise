"""
Test suite for the Ingredient class from model.py.

All tests are parameterized to minimize code duplication while ensuring
comprehensive coverage of valid and invalid inputs.
"""

import pytest
from pydantic import ValidationError
from pint import Quantity

from model import Ingredient, ureg


@pytest.mark.parametrize(
    "name,quantity,unit",
    [
        ("Flour", 100.0, ureg.gram),
        ("Salt", 0.5, ureg.teaspoon),
        ("Eggs", 3.0, ureg.dimensionless),
        ("Olive Oil", 30.0, ureg.milliliter),
    ],
)
def test_create_ingredient_valid(name, quantity, unit):
    """Test creating ingredient with valid name, quantity, and unit."""
    ingredient = Ingredient(name=name, quantity=quantity, unit=unit)
    assert ingredient.name == name
    assert ingredient.quantity == quantity
    assert ingredient.unit == unit


@pytest.mark.parametrize(
    "quantity",
    [
        0.000000000000000000000001,  # Very small
        1,  # Integer
        100000000000000000000000.0,  # Very large
    ],
)
def test_create_ingredient_various_quantities(quantity):
    """Test creating ingredient with various valid quantities."""
    ingredient = Ingredient(name="Test", quantity=quantity, unit=ureg.gram)
    assert ingredient.quantity == quantity


@pytest.mark.parametrize(
    "unit",
    [
        ureg.kilogram,
        ureg.teaspoon,
        ureg.dimensionless,
    ],
)
def test_create_ingredient_various_units(unit):
    """Test creating ingredient with various unit types."""
    ingredient = Ingredient(name="Test", quantity=1.0, unit=unit)
    assert ingredient.unit == unit


@pytest.mark.parametrize(
    "name",
    [
        "Salt and Pepper",
        "Olive oil",
        "Garlic",
        "A",  # Single character
        "Very Long Ingredient Name That Should Still Work",
    ],
)
def test_create_ingredient_various_names(name):
    """Test creating ingredient with various name formats."""
    ingredient = Ingredient(name=name, quantity=1.0, unit=ureg.gram)
    assert ingredient.name == name


@pytest.mark.parametrize(
    "quantity,expected_error",
    [
        (0.0, "greater than 0"),  # Zero quantity
        (-1.0, "greater than 0"),  # Negative quantity
        (-0.001, "greater than 0"),  # Small negative
        (-100.0, "greater than 0"),  # Large negative
    ],
)
def test_create_ingredient_invalid_quantity(quantity, expected_error):
    """Test that invalid quantities raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Ingredient(name="Test", quantity=quantity, unit=ureg.gram)
    assert expected_error in str(exc_info.value).lower()


@pytest.mark.parametrize(
    "unit",
    [
        "gram",  # String instead of Unit
        "ml",  # String representation
        "bananas",  # Invalid unit
        123,  # Integer
        None,  # None value
        [],  # List
        {},  # Dict
    ],
)
def test_create_ingredient_invalid_unit_type(unit):
    """Test that invalid unit types raise ValidationError."""
    with pytest.raises(ValidationError):
        Ingredient(name="Test", quantity=1.0, unit=unit)


@pytest.mark.parametrize(
    "missing_field",
    [
        "name",
        "quantity",
        "unit",
    ],
)
def test_create_ingredient_missing_required_fields(missing_field):
    """Test that missing required fields raise ValidationError."""
    valid_data = {
        "name": "Test",
        "quantity": 1.0,
        "unit": ureg.gram,
    }
    valid_data.pop(missing_field)

    with pytest.raises(ValidationError):
        Ingredient(**valid_data)


@pytest.mark.parametrize(
    "quantity",
    [
        [],  # List
        {},  # Dict
        None,  # None
    ],
)
def test_create_ingredient_invalid_quantity_type(quantity):
    """Test that invalid quantity types raise ValidationError."""
    with pytest.raises(ValidationError):
        Ingredient(name="Test", quantity=quantity, unit=ureg.gram)


@pytest.mark.parametrize(
    "name",
    [
        123,  # Integer
        1.0,  # Float
        "123",
        [],  # List
        {},  # Dict
        None,  # None
        "",
        "+_::I)()",
    ],
)
def test_create_ingredient_invalid_name_type(name):
    """Test that invalid name types raise ValidationError."""
    with pytest.raises(ValidationError):
        Ingredient(name=name, quantity=1.0, unit=ureg.gram)


@pytest.mark.parametrize(
    "name,quantity,unit,expected_pattern",
    [
        ("Salt", 0.5, ureg.teaspoon, "0.5 teaspoon of Salt"),
        ("Eggs", 3.0, ureg.dimensionless, "3.0 Eggs"),
    ],
)
def test_ingredient_str_representation(name, quantity, unit, expected_pattern):
    """Test that __str__ returns expected format."""
    ingredient = Ingredient(name=name, quantity=quantity, unit=unit)
    result = str(ingredient)
    assert result == expected_pattern


@pytest.mark.parametrize(
    "name,quantity,unit",
    [
        ("Flour", 100.0, ureg.gram),
        ("Butter 293084", 2.0, ureg.tablespoon),
        ("Eggs", 3.0, ureg.dimensionless),
    ],
)
def test_to_quantity_returns_quantity_object(name, quantity, unit):
    """Test that to_quantity returns a Pint Quantity object."""
    ingredient = Ingredient(name=name, quantity=quantity, unit=unit)
    result = ingredient.to_quantity()
    assert isinstance(result, Quantity)
    assert result.magnitude == quantity
    assert result.units == unit
