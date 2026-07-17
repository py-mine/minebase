from __future__ import annotations

import re
from typing import Annotated, Literal, final
from uuid import UUID

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_pascal
from pydantic.types import Base64Bytes, Base64Str, UuidVersion

from minebase.types._base import MinecraftDataModel, _merge_base_config  # pyright: ignore[reportPrivateUsage]

# This allows any hex color with 1, 6 or 8 hex digits. This is a bit non-standard
# as in CSS, we can have 3, 4, 6 or 8. However, from observing the values present
# in minecraft-data, these seem to be the only values being used, with the 1 digit
# color being #0. For now, let's be strict and not allow 3/4 digit colors, we don't
# know what standard is being used here, let's be restrictive, we can allow those if
# we see a violation.
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{1}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


@final
class AnimatedSkinImageData(MinecraftDataModel):
    """Minecraft-Data for an animated skin image data (Bedrock only)."""

    # For some reason, these fields are in PascalCase...
    model_config = _merge_base_config(ConfigDict(alias_generator=to_pascal))

    type: Literal[1]
    image_width: Literal[32]
    image_height: Literal[64]
    frames: Literal[2]
    animation_expression: Literal[1]
    image: Base64Bytes


@final
class SkinPieceTintColorsData(MinecraftDataModel):
    """Minecraft-Data for a skin piece color (Bedrock only)."""

    # For some reason, these fields are in PascalCase...
    model_config = _merge_base_config(ConfigDict(alias_generator=to_pascal))

    colors: list[Annotated[str, Field(pattern=_HEX_COLOR_RE)]]
    piece_type: str


@final
class SkinPersonaPiecesData(MinecraftDataModel):
    """Minecraft-Data for skin persona pieces (Bedrock only)."""

    # For some reason, these fields are in PascalCase...
    model_config = _merge_base_config(ConfigDict(alias_generator=to_pascal))

    is_default: Literal[True]
    pack_id: Annotated[UUID, UuidVersion(4)]
    piece_id: Annotated[UUID, UuidVersion(4)]
    piece_type: str
    product_id: Literal[""]


@final
class SteveData(MinecraftDataModel):
    """Minecraft-Data for a steve (Bedrock only)."""

    # For some reason, these fields are in PascalCase...
    model_config = _merge_base_config(ConfigDict(alias_generator=to_pascal))

    animated_image_data: list[AnimatedSkinImageData]
    arm_size: Literal["wide"]
    cape_data: Literal[""]
    cape_id: Literal[""]
    cape_image_height: Literal[0]
    cape_image_width: Literal[0]
    cape_on_classic_skin: Literal[False]
    persona_pieces: list[SkinPersonaPiecesData]
    persona_skin: Literal[True]
    piece_tint_colors: list[SkinPieceTintColorsData]
    premium_skin: Literal[False]
    skin_animation_data: Literal[""]
    skin_color: str = Field(pattern=_HEX_COLOR_RE)
    skin_id: str
    skin_image_height: Literal[256]
    skin_image_width: Literal[256]
    skin_resource_patch: Base64Str
    skin_data: Base64Bytes
    skin_geometry_data: Base64Str
    skin_geometry_engine_version: str | None = None
    skin_geometry_data_engine_version: str | None = None
