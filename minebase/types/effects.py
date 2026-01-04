from __future__ import annotations

from typing import Literal, final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class EffectData(MinecraftDataModel):
    """Minecraft-Data for an effect.

    Attributes:
        id: The unique identifier for an effect
        name: The name of an effect (guaranteed unique)
        display_name: The name of an effect as shown in the GUI
        type: Whether an effect is positive or negative
    """

    id: int = Field(ge=0)
    name: str
    display_name: str
    type: Literal["good", "bad"]
