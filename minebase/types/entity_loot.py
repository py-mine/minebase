from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class EntityItemDrop(MinecraftDataModel):
    """Minecraft-Data for an entity item drop information.

    Attributes:
        item: The name of the item being dropped (guaranteed unique)
        metadata: The metadata of the item being dropped (Bedrock Edition)
        drop_chance: The percent chance of the item drop to occur
        stack_size_range: The min/max number of items in this item drop stack
        player_kill: If a player kill is required
    """

    item: str
    metadata: int | None = Field(ge=0, le=127, default=None)
    drop_chance: float
    stack_size_range: tuple[int, int]
    player_kill: bool | None = None


@final
class EntityLootData(MinecraftDataModel):
    """Minecraft-Data for entity loot information.

    Attributes:
        entity: The name of the entity (guaranteed unique)
        drops: The list of item drops
    """

    entity: str
    drops: list[EntityItemDrop]
