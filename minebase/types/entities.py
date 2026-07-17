from __future__ import annotations

from enum import Enum
from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class EntityCategory(str, Enum):
    """Minecraft-Data enumeration of the possible semantic entity categories."""

    BLOCKS = "Blocks"
    DROPS = "Drops"
    GENERIC = "Generic"
    HOSTILE_MOBS = "Hostile mobs"
    IMMOBILE = "Immobile"
    NPCS = "NPCs"
    PASSIVE_MOBS = "Passive mobs"
    PROJECTILES = "Projectiles"
    UNKNOWN = "UNKNOWN"
    VEHICLES = "Vehicles"


@final
class EntityType(str, Enum):
    """Minecraft-Data enumeration of the possible entity types."""

    BLANK = ""
    UNKNOWN = "UNKNOWN"
    AMBIENT = "ambient"
    ANIMAL = "animal"
    HOSTILE = "hostile"
    LIVING = "living"
    MOB = "mob"
    OBJECT = "object"
    OTHER = "other"
    PASSIVE = "passive"
    PLAYER = "player"
    PROJECTILE = "projectile"
    WATER_CREATURE = "water_creature"


@final
class EntityData(MinecraftDataModel):
    """Minecraft-Data for an entity.

    Attributes:
        id: The unique identifier for an entity
        internal_id: The internal id of an entity; used in eggs metadata for example
        name: The name of an entity (guaranteed unique)
        display_name: The name of an entity as displayed in the GUI
        type: The type of an entity
        category: The semantic category of an entity
        width: The width of the entity
        height: The height of the entity
        length: The length of the entity
        offset: The offset of the entity
        metadata_keys: The pc metadata keys of an entity (naming is via mc code, with data_ and id_ prefixes stripped)
    """

    id: int = Field(ge=0)
    internal_id: int | None = Field(ge=0, default=None)
    name: str
    display_name: str
    type: EntityType
    category: EntityCategory | None = None
    width: float | None
    height: float | None
    length: float | None = None
    offset: float | None = None
    metadata_keys: list[str] | None = None
