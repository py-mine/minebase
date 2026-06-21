from __future__ import annotations

from typing import final

from pydantic import model_validator

from minebase.types._base import MinecraftDataModel


@final
class MinecraftAttributeData(MinecraftDataModel):
    """Minecraft-Data for an attribute.

    Attributes in Minecraft define various character, entity, or item properties
    that can influence gameplay mechanics, such as health, attack damage, movement
    speed, armor, and more. Each attribute has a defined range, a default value,
    and a canonical resource identifier used internally by the game.

    Examples of attributes include:
        - "minecraft:generic.max_health" with default 20.0, min 1.0, max 1024.0
        - "minecraft:attack_damage" with default 2.0, min 0.0, max 2048.0
        - "minecraft:generic.armor_toughness" with default 0.0, min 0.0, max 20.0
        - "minecraft:movement_speed" with default 0.7, min 0.0, max 1024.0

    Attributes:
        name:
            The common or friendly name of the attribute (e.g., "attackDamage", "maxHealth").
        resource:
            The official Mojang resource name identifying the attribute in data files and the game code.

            Typically formatted as `minecraft:generic.[name]` or `generic.[name]` for legacy identifiers.
        default: The default value for this attribute
        min: The minimum permissible value for this attribute. Enforced by the game.
        max: The maximum permissible value for this attribute. Enforced by the game.
    """

    name: str
    resource: str
    default: float
    min: float
    max: float

    @model_validator(mode="after")
    def valid_default(self) -> MinecraftAttributeData:
        """Enforce that the default value is within the expected min-max bounds."""
        if self.min <= self.default <= self.max:
            return self

        raise ValueError("The default value is outside of the min-max bounds")
