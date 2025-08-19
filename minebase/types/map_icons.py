from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class MapIconData(MinecraftDataModel):
    """Minecraft-Data for a map icon.

    This contains a list of icons that can show up on a map, e.g. a player indicator,
    markers, X target for treasure maps, etc.

    Attributes:
        id: The unique identifier for a map icon
        name: The name of a map icon
        appearance: Description of the map icon's appearance
        visible_in_item_frame: Visibility in item frames
    """

    id: int = Field(ge=0)
    name: str
    appearance: str | None = None
    visible_in_item_frame: bool
