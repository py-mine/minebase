from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class ParticleData(MinecraftDataModel):
    """Minecraft-Data for a particle.

    Attributes:
        id: The unique identifier for a particle
        name: The name of a particle
    """

    id: int = Field(ge=0)
    name: str
