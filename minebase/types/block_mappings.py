from __future__ import annotations

from typing import Any, final

from minebase.types._base import MinecraftDataModel


@final
class BlockMappingEditionData(MinecraftDataModel):
    """Minecraft-Data for a block mapping in a specific Minecraft edition (bedrock/java)."""

    name: str
    # States can hold nested dicts, or various key-value pairs, where the value type
    # differs wildly (for some keys, it's a bool, for others, it's an int, etc.)
    # It's not feasible for us to create a model with all possible states, as there's
    # just way too many, so this uses the permissive `Any` type for the dict values.
    states: dict[str, Any]


@final
class BlockMappingData(MinecraftDataModel):
    """Minecraft-Data showing how Bedrock edition blocks map to corresponding Java edition blocks.

    Attributes:
        pc: Java edition block data
        pe: Bedrock edition block data
    """

    pc: BlockMappingEditionData
    pe: BlockMappingEditionData
