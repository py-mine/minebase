from __future__ import annotations

import re
from typing import Literal, final

from pydantic import Field

from minebase.types._base import MinecraftDataModel

_MC_VERSION_RE = re.compile(r"([0-9]+\.[0-9]+(\.[0-9]+)?[a-z]?(-pre[0-9]+)?)|([0-9]{2}w[0-9]{2}[a-z])")
_MAJOR_VERSION_RE = re.compile(r"[0-9]+\.[0-9]+[a-z]?")


@final
class VersionData(MinecraftDataModel):
    """Minecraft-Data for a specific Minecraft version."""

    version: int
    minecraft_version: str = Field(pattern=_MC_VERSION_RE)
    major_version: str = Field(pattern=_MAJOR_VERSION_RE)
    release_type: Literal["release", "snapshot"] | None = None
