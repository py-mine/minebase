from __future__ import annotations

from typing import Literal, final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class WindowOpenedWithData(MinecraftDataModel):
    """Minecraft-Data for open_with attribute of a window.

    Attributes:
        id: The unique identifier of the block, item or the entity this window is opened with
        type: The type of the object that this window is opened with (block, item or entity)
    """

    id: int
    type: Literal["block", "item", "entity"]


@final
class WindowSlotsData(MinecraftDataModel):
    """Minecraft- Data for a slot or slot range in a window.

    Attributes:
        name: The name of the slot or slot range
        index: The position of the slot or begin of the slot range
        size: The size of the slot range
    """

    name: str
    index: int = Field(ge=0)
    size: int | None = Field(ge=0, default=None)


@final
class WindowData(MinecraftDataModel):
    """Minecraft-Data for a window.

    Attributes:
        id: The unique identifier for the window
        name: The default displayed name of the window
        slots: The slots displayed in the window
        properties: Names of the properties of the window
        opened_with: TODO
    """

    id: str
    name: str
    slots: list[WindowSlotsData] | None = Field(min_length=1, default=None)
    properties: list[str] | None = Field(min_length=1, default=None)
    opened_with: list[WindowOpenedWithData] | None = None
