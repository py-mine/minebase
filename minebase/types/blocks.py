from __future__ import annotations

from typing import Any, Literal, cast, final

from pydantic import Field, model_validator

from minebase.types._base import MinecraftDataModel


@final
class BlockVariationData(MinecraftDataModel):
    """Minecraft-Data for a block variation."""

    metadata: int = Field(ge=0)
    display_name: str
    description: str | None = None


@final
class JavaBlockStateData(MinecraftDataModel):
    """Minecraft-Data for a block state.

    Attributes:
        name: The name of the property
        type: The type of the property
        values: The possible values of the property
        num_values: The number of possible values
    """

    name: str
    type: Literal["enum", "bool", "int", "direction"]
    values: list[str] | None = None
    num_values: int = Field(ge=1, alias="num_values")  # for some reason, this is snake_cased


@final
class BlockDropItem(MinecraftDataModel):
    """Minecraft-Data for a specific item drop from a block.

    Attributes:
        id: The unique identifier of the dropped item.
        metadata: Metadata information of the dropped item.
    """

    id: int = Field(ge=0)
    metadata: int | None = Field(ge=0, default=None)

    @model_validator(mode="before")
    @classmethod
    def from_int(cls, v: object) -> object:
        """Allow shorthand 'int' (meaning just id) for drop option by wrapping it."""
        if isinstance(v, int):
            return {"id": v}
        return v


@final
class BlockDropData(MinecraftDataModel):
    """Minecraft-Data for a block drop.

    Attributes:
        min_count: Minimum number or chance, default: 1
        max_count: Maximum number or chance, default: minCount
        drop: Details about the dropped item.
    """

    min_count: float = Field(ge=0, default=1)
    max_count: float = Field(ge=0)
    drop: BlockDropItem

    @classmethod
    def _default_max_count(cls, data: object) -> object:
        """Populate max_count from min_count when it is missing.

        The `max_count` field should default to the value of the `min_count` field, if it's
        not explicitly specified.
        """
        if not isinstance(data, dict):
            return data

        data = cast("dict[Any, Any]", data)  # explicitly make the type unknown, to prevent pyright complaints

        if "maxCount" not in data:
            data["maxCount"] = data.get("minCount", 1)

        return data

    @classmethod
    def _from_int(cls, v: object) -> object:
        """Allow shorthand 'int', meaning just an int drop (count=1) by wrapping it."""
        if isinstance(v, int):
            return {"drop": v}
        return v

    @model_validator(mode="before")
    @classmethod
    def pre_validator(cls, v: object) -> object:
        """Run all before validation logic."""
        v = cls._from_int(v)
        return cls._default_max_count(v)

    @model_validator(mode="after")
    def check_bounds(self) -> BlockDropData:
        """Ensure logical bounds between min_count and max_count."""
        if self.max_count < self.min_count:
            raise ValueError("max_count must be greater than or equal to min_count")
        return self


@final
class BlockData(MinecraftDataModel):
    """Minecraft-Data for a specific block.

    Attributes:
        id: The unique identifier for a block
        name: The name of the block (guaranteed unique)
        display_name: The name of the block as shown in the GUI
        hardness: Hardness value of a block
        stack_size: Stack size for a block
        diggable: Can this block be digged?
        bounding_box: The bounding box of a block
        material: Material of a block
        harvest_tools:
            Using one of these tools is required to harvest a block.

            Without that, you get a 3.33x time penalty.
        variations: The list of variations of this block
        states:
            The list of states of this block.

            This field is only present on Java edition, for Bedrock, block states
            are tracked in a standalone key outside of block data.
        transparent: Is this block transparent?
        emit_light: Light level emitted by this block (0-15)
        filter_light: Light filtered by this block (0-15)
        min_state_id: Minimum state id
        max_state_id: Maximum state id
        default_state: Default state id
        resistence: Blast resistance
    """

    id: int = Field(ge=0)
    name: str
    display_name: str
    hardness: float | None = Field(ge=-1)
    stack_size: int = Field(ge=0)
    diggable: bool
    bounding_box: Literal["block", "empty"]
    material: str | None = None
    harvest_tools: dict[int, bool] | None = None
    variations: list[BlockVariationData] | None = None
    states: list[JavaBlockStateData] | None = None
    drops: list[BlockDropData]
    transparent: bool
    emit_light: int = Field(ge=0, le=15)
    filter_light: int = Field(ge=0, le=15)
    min_state_id: int | None = Field(ge=0, default=None)
    max_state_id: int | None = Field(ge=0, default=None)
    default_state: int | None = Field(ge=0, default=None)
    resistance: float | None = Field(ge=-1, default=None)
