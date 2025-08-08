from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class MinecraftDataModel(BaseModel):
    """Base type for a pydantic based class holding Minecraft-Data."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=False,  # only allow population by alias names
        from_attributes=True,
        extra="forbid",
    )
