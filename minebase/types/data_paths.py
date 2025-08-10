from __future__ import annotations

from typing import final

from minebase.types._base import MinecraftDataModel


@final
class DataPaths(MinecraftDataModel):
    """Strucutre of the `dataPaths.json` manifest file.

    Attributes:
        pc: PC (Java) edition version to data paths mapping.
        bedrock: Bedrock edition version to data paths mapping.
    """

    pc: dict[str, dict[str, str]]
    bedrock: dict[str, dict[str, str]]
