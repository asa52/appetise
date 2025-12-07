from pydantic import BaseModel, Field
from typing import List, Optional
from pint import Unit, UnitRegistry, Quantity

# Initialize Pint unit registry
ureg = UnitRegistry()


class Ingredient(BaseModel):
    """
    Represents a single ingredient required for a recipe, including quantity details.

    This model serves as the core unit for both recipe requirements and kitchen inventory.
    """

    name: str = Field(
        ..., description="The common name of the ingredient (e.g., 'Flour', 'Milk')."
    )
    quantity: float = Field(
        ..., gt=0, description="The numerical amount of the ingredient."
    )
    unit: Unit = Field(
        ...,
        description="The measurement unit (e.g., 'grams', 'ml', 'cups', 'teaspoons') as a Pint unit.",
    )

    def __str__(self) -> str:
        """Returns a human-readable representation of the ingredient."""
        unit_str = (
            str(self.unit.units) if isinstance(self.unit, Quantity) else str(self.unit)
        )
        return f"{self.quantity} {unit_str} of {self.name}"

    def to_quantity(self) -> Quantity:
        """Returns a Pint Quantity object combining quantity and unit."""
        return self.quantity * self.unit


class Step(BaseModel):
    """
    Represents a single procedural step in a recipe.
    """

    order: int = Field(
        ..., ge=1, description="The sequential order of the step in the recipe."
    )
    description: str = Field(..., description="The detailed instruction for this step.")

    def __str__(self) -> str:
        """Returns a human-readable representation of the step."""
        return f"Step {self.order}: {self.description}"


class Recipe(BaseModel):
    """
    Represents a complete cooking recipe, including required ingredients and sequential steps.
    """

    recipe_id: Optional[str] = Field(
        None,
        description="Unique identifier for the recipe (used for database storage).",
    )
    name: str = Field(..., description="The title of the recipe.")
    description: Optional[str] = Field(
        None, description="A brief description or summary of the dish."
    )
    ingredients: List[Ingredient] = Field(
        ..., description="A list of ingredients required for the recipe."
    )
    steps: List[Step] = Field(
        ..., description="The sequential list of steps to follow."
    )
    prep_time_minutes: Optional[int] = Field(
        None, ge=0, description="Estimated preparation time in minutes."
    )
    cook_time_minutes: Optional[int] = Field(
        None, ge=0, description="Estimated cooking time in minutes."
    )

    def get_total_time(self) -> int:
        """
        Calculates the total time required for the recipe (prep + cook).

        Returns:
            int: The total time in minutes, or 0 if times are not specified.
        """
        prep = self.prep_time_minutes if self.prep_time_minutes is not None else 0
        cook = self.cook_time_minutes if self.cook_time_minutes is not None else 0
        return prep + cook


class InventoryItem(Ingredient):
    """
    Represents an ingredient currently held in the kitchen inventory.

    This class inherits from Ingredient (adhering to DRY) but may be used
    to hold additional inventory-specific data in the future (e.g., expiry_date).
    """

    # Inherits name, quantity, and unit from Ingredient.
    inventory_id: Optional[str] = Field(
        None, description="Unique identifier for this inventory record."
    )
    storage_location: Optional[str] = Field(
        None, description="Where the item is stored (e.g., 'Fridge', 'Pantry')."
    )
