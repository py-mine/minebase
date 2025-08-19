from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class BlockItemDrop(MinecraftDataModel):
    """Minecraft-Data for an entity item drop information.

    Attributes:
        item: The name of the item being dropped (guaranteed unique)
        metadata: The metadata of the item being dropped (Bedrock Edition)
        drop_chance: The percent chance of the item drop to occur
        stack_size_range: The min/max number of items in this item drop stack
        block_age: The required age of the block for the item drop to occur
        silk_touch: If silk touch is required
        no_silk_touch: If not having silk touch is required
    """

    item: str
    metadata: int | None = Field(ge=0, le=127, default=None)
    drop_chance: float
    stack_size_range: tuple[int | None, int | None]
    block_age: float | None = None
    silk_touch: bool | None = None
    no_silk_touch: bool | None = None


@final
class BlockLootData(MinecraftDataModel):
    """Minecraft-Data for block loot information.

    Attributes:
        block: The name of the block (guaranteed unique)
        states: The states of the block (Bedrock Edition)
        drops: The list of item drops
    """

    block: str
    states: object | None = None
    drops: list[BlockItemDrop]
