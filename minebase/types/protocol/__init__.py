from typing import final

from minebase.types._base import MinecraftDataModel
from minebase.types.protocol.types import ProtocolTypeValue


@final
class ProtocolData(MinecraftDataModel):
    """Minecraft-Data for the protocol of given version."""

    types: dict[str, ProtocolTypeValue]
