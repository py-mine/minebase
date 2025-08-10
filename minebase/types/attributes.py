from __future__ import annotations

from typing import final

from pydantic import model_validator

from minebase.types._base import MinecraftDataModel


@final
class MinecraftAttributeData(MinecraftDataModel):
    """Minecraft-Data for an attribute.

    Attributes:
        name: The name of this attribute
        resource: The Mojang name of an attribute (usually generic.[name] or minecraft:generic.[name]
        min: The minimum value of an attribute
        max: The maximum value of an attribute
        default: The default value of an attribute
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
