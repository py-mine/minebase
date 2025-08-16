from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class MinecraftDataModel(BaseModel):
    """Base type for a pydantic based class holding Minecraft-Data.

    This type is reserved for internal use, and it is not a guaranteed base class
    for all minecraft-data models. It is a helper class that includes pre-configured
    model config for automatic field conversion from camelCase to snakeCase and to
    prevent unexpected extra attributes or class population without using the camelCase
    aliases.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=False,  # only allow population by alias names
        from_attributes=True,
        extra="forbid",
    )
