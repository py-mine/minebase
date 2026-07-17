from __future__ import annotations

from typing import final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class TintDataStringKeyEntry(MinecraftDataModel):
    """Represents a single tint mapping using string keys.

    Each entry associates one or more identifiers (e.g., biome names or block types)
    with a specific color.

    Attributes:
        keys: One or more string identifiers that this tint applies to.
        color: The color value for the given keys, as an RGB integer.
    """

    keys: list[str] = Field(min_length=1)
    color: int


@final
class TintDataIntegerKeyEntry(MinecraftDataModel):
    """Represents a single tint mapping using integer keys.

    Each entry associates one or more integer identifiers with a specific color.

    Attributes:
        keys: One or more integer identifiers that this tint applies to.
        color: The color value for the given keys, typically as an RGB integer.
    """

    keys: list[int] = Field(min_length=1)
    color: int


@final
class TintGroupIntegerKeys(MinecraftDataModel):
    """A group of tints where each entry uses integer keys.

    Each entry in `data` specifies a set of integer keys as identifiers and the
    corresponding color to use. The `default` field specifies a fallback color if
    no keys match.

    Attributes:
        data: List of integer-keyed tint entries.
        default: Fallback color if no keys match. Optional.
    """

    data: list[TintDataIntegerKeyEntry] = Field(min_length=1)
    default: int | None = None


@final
class TintGroupStringKeys(MinecraftDataModel):
    """A group of tints where each entry uses string keys.

    Each entry in `data` specifies a set of string keys (e.g., biome names) and the
    corresponding color to use. The `default` field specifies a fallback color if
    no keys match.

    Attributes:
        data: List of string-keyed tint entries.
        default: Fallback color if no keys match. Optional.
    """

    # The `data` key should have min_length=1, however, currently, there is an entry
    # in minecraft-data that does not conform to that (pc/1.21.4). Once this will get
    # addressed, we should enforce min_lenght=1 here.
    # https://github.com/PrismarineJS/minecraft-data/issues/1055
    data: list[TintDataStringKeyEntry] = Field(min_length=0)
    default: int | None = None


@final
class TintData(MinecraftDataModel):
    """Complete collection of Minecraft tints for different block or biome types.

    Each attribute represents a tint group for a specific category, mapping keys
    to colors with an optional default.

    Attributes:
        grass: Tint data for grass blocks.
        foliage: Tint data for leaves and other foliage.
        water: Tint data for water blocks and biomes.
        redstone: Tint data for redstone dust depending on the signal strength level (as int keys).
        constant: Tint data that remains constant across certain blocks.
    """

    grass: TintGroupStringKeys
    foliage: TintGroupStringKeys
    water: TintGroupStringKeys
    redstone: TintGroupIntegerKeys
    constant: TintGroupStringKeys
