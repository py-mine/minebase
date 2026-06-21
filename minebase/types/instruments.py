from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class InstrumentData(MinecraftDataModel):
    """Minecraft-Data for an instrument.

    An instrument controls the behavior of a note block.

    Attributes:
        id: The unique identifier for an instrument
        name: The name of an instrument
        sound: The sound ID played by this instrument
    """

    id: int = Field(ge=0)
    name: str
    sound: str | None = None
