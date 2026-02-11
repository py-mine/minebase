from __future__ import annotations

from typing import Annotated, Literal, Union, final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class BedrockBlockStateStringData(MinecraftDataModel):
    """Minecraft-Data for a Bedrock edition block state inner data for a string."""

    type: Literal["string"]
    value: str


@final
class BedrockBlockStateBytesData(MinecraftDataModel):
    """Minecraft-Data for a Bedrock edition block state inner data for a byte (unsigned)."""

    type: Literal["byte"]
    value: int = Field(ge=0, le=255)


@final
class BedrockBlockStateIntData(MinecraftDataModel):
    """Minecraft-Data for a Bedrock edition block state inner data for an integer (signed, 4 byte number)."""

    type: Literal["int"]
    value: int = Field(ge=-(2**31), le=2**31 - 1)


BedrockBlockStateInnerData = Annotated[
    Union[BedrockBlockStateIntData, BedrockBlockStateBytesData, BedrockBlockStateStringData],
    Field(discriminator="type"),
]


@final
class BedrockBlockStateData(MinecraftDataModel):
    """Minecraft-Data for block states (Bedrock only).

    In Java edition, block states are tracked under the blocks key, not as a separate
    key.

    Note:
        These data doesn't have a JSON schema to follow for the structure, so the
        structure here is mostly just designed to match the underlying data. The
        schema is expected to be added later on to minecraft-data; See:
        https://github.com/PrismarineJS/minecraft-data/issues/1060
    """

    name: str
    states: dict[str, BedrockBlockStateInnerData]
    version: int | None = None
