from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class FoodVariation(MinecraftDataModel):
    """Minecraft-Data for a food item variation."""

    metadata: int = Field(ge=0)
    display_name: str


@final
class FoodData(MinecraftDataModel):
    """Minecraft-Data for a food.

    Attributes:
        id: The associated item ID for this food item
        display_name: The name of the food item as shown in the GUI
        name: The name of the food item (guaranteed unique)
        stack_size: The stack size for this food item
        food_points: The amount of food (hunger) points the food item replenishes
        saturation: The amount of saturation points the food restores (food_points + saturation_ratio)
        saturation_ratio:
            The 'saturation modifier' in Minecraft code, used to determine how much saturation an item has
        effective_quality: food_points + saturation
        variations: All variations of this food item
    """

    id: int = Field(ge=0)
    display_name: str
    name: str
    stack_size: int = Field(ge=1, le=64)
    food_points: float = Field(ge=0)
    saturation: float = Field(ge=0)
    saturation_ratio: float = Field(ge=0)
    effective_quality: float = Field(ge=0)
    variations: list[FoodVariation] | None = None
