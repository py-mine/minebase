from __future__ import annotations

from typing import final

from pydantic import Field, field_validator

from minebase.types._base import MinecraftDataModel


@final
class EnchantmentCostCoefficients(MinecraftDataModel):
    """Minecraft-Data for the cost equation's coefficients a * level + b."""

    a: int = Field(ge=0)
    b: int


@final
class EnchantmentData(MinecraftDataModel):
    """Minecraft-Data for an enchantment.

    Attributes:
        id: The unique identifier for an enchantment
        name: The name of an enchantment (guaranteed unique)
        display_name: The name of an enchantment, as displayed in the GUI
        max_level: Max cost equation's coefficients a * level + b.
        min_level: Min cost equation's coefficients a * level + b.
        category: The category of enchantable items
        weight: Weight of the rarity of the enchantment
        treasure_only: Can only be found in a treasure, not created
        curse: Is a curse, not an enchantment
        tradable: Can this enchantment be traded
        discoverable: Can this enchantment be discovered
        exclude: List on enchantments (names) not compatible
    """

    id: int = Field(ge=0)
    name: str
    display_name: str
    max_level: int = Field(ge=1, le=5)
    min_cost: EnchantmentCostCoefficients
    max_cost: EnchantmentCostCoefficients
    category: str
    weight: int = Field(ge=1, le=10)
    treasure_only: bool
    curse: bool
    tradeable: bool
    discoverable: bool
    exclude: list[str] | None = None

    @field_validator("exclude")
    @classmethod
    def ensure_unique_items(cls, v: list[str]) -> list[str]:
        """Make sure that items in given list are unique."""
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v
