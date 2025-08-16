from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel
from minebase.types.attributes import MinecraftAttributeData
from minebase.types.biomes import BiomeData
from minebase.types.block_collision_shapes import BlockCollisionShapeData
from minebase.types.block_loot import BlockLootData
from minebase.types.blocks import BlockData
from minebase.types.effects import EffectData
from minebase.types.enchantments import EnchantmentData
from minebase.types.entities import EntityData
from minebase.types.entity_loot import EntityLootData
from minebase.types.foods import FoodData
from minebase.types.instruments import InstrumentData
from minebase.types.items import ItemsData
from minebase.types.map_icons import MapIconData
from minebase.types.recipes import BedrockRecipesData, JavaRecipesData
from minebase.types.sounds import SoundData
from minebase.types.tints import TintData
from minebase.types.version import VersionData
from minebase.types.windows import WindowData


class BaseMinecraftData(MinecraftDataModel):
    """Minecraft-Data for a specific game version.

    Attributes:
        biomes:
        items;
        version:
        attributes:
        windows:
        enchantments:
        language: Language string translations into the en_US language.
        block_collision_shapes:
        instruments:
        materials:
        entities:
        effects:
        entity_loot:
        block_loot:
    """

    biomes: list[BiomeData] | None = None
    items: list[ItemsData] | None = None
    version: VersionData
    attributes: list[MinecraftAttributeData] | None = None
    windows: list[WindowData] | None = None
    enchantments: list[EnchantmentData] | None = None
    language: dict[str, str] | None = None
    block_collision_shapes: BlockCollisionShapeData | None = None
    instruments: list[InstrumentData] | None = None
    materials: dict[str, dict[int, float]] | None = None
    entities: list[EntityData] | None = None
    effects: list[EffectData] | None = None
    entity_loot: list[EntityLootData] | None = None
    block_loot: list[BlockLootData] | None = None


@final
class PcMinecraftData(BaseMinecraftData):
    foods: list[FoodData] | None = None
    tints: TintData | None = None
    map_icons: list[MapIconData] | None = None
    sounds: list[SoundData] | None = None
    blocks: list[BlockData]
    protocol: dict
    particles: list | None = None
    protocol_comments: dict | None = None
    commands: dict | None = None
    login_packet: dict | None = None
    recipes: JavaRecipesData | None = None


@final
class BedrockMinecraftData(BaseMinecraftData):
    blocks: list[BlockData] | None = None
    protocol: dict | None = None
    steve: dict | None = None
    block_states: list | None = None
    blocks_b2j: dict | None = Field(alias="blocksB2J", default=None)
    blocks_j2b: dict | None = Field(alias="blocksJ2B", default=None)
    block_mappings: list | None = None
    recipes: BedrockRecipesData | None = None
