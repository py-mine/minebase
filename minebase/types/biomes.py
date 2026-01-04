from __future__ import annotations

from typing import Literal, final

from pydantic import Field, model_validator

from minebase.types._base import MinecraftDataModel


@final
class BiomeClimateData(MinecraftDataModel):
    """Minecraft-Data about the climate in a Biome.

    This controls the ideal parameter ranges for Minecraft's multi-noise biome generation system.

    Attributes:
        temperature: Controls hot/cold climate preference (-1.0 to 1.0)
        humidity: Controls dry/wet climate preference (-1.0 to 1.0)
        altitude: Controls low/high terrain preference (affects hills/valleys)
        weirdness: Controls terrain "strangeness" (also known as "ridges", -1.0 to 1.0)
        offset: Fine-tuning parameter for biome selection priority/weight
    """

    temperature: float = Field(ge=-1, le=1)
    humidity: float = Field(ge=-1, le=1)
    altitude: Literal[0]  # not sure what the constraints here should be, minecraft-data only uses 0
    weirdness: float = Field(ge=-1, le=1)
    offset: float


@final
class BiomeData(MinecraftDataModel):
    """Minecraft-Data about a Biome.

    Attributes:
        id: The unique identifier for a biome
        name: The name of a biome
        category: Category to which this biome belongs to (e.g. "forest", "ocean", ...)
        temperature: The base temperature in a biome.
        precipitation: The type of precipitation (none, rain or snow) [before 1.19.4]
        has_precipitation: True if a biome has any precipitation (rain or snow) [1.19.4+]
        dimension: The dimension of a biome: overworld, nether or end (or the_end on bedrock)
        display_name: The display name of a biome
        color: The color in a biome
        rainfall: How much rain there is in a biome [before 1.19.4]
        depth: Depth corresponds approximately to the terrain height.
        climates: Climate data for the biome
        name_legacy: Legacy name of the biome used in older versions.
        parent: The name of the parent biome
        child: ID of a variant biome
    """

    id: int
    name: str
    category: str
    temperature: float = Field(ge=-1, le=2)
    precipitation: Literal["none", "rain", "snow"] | None = None
    # For some reason, this field actually uses snake_case, not camelCase
    has_precipitation: bool | None = Field(alias="has_precipitation", default=None)
    dimension: Literal["overworld", "nether", "end", "the_end"]
    display_name: str
    color: int
    rainfall: float | None = Field(ge=0, le=1, default=None)
    depth: float | None = Field(default=None)
    climates: list[BiomeClimateData] | None = Field(min_length=1, default=None)
    name_legacy: str | None = Field(alias="name_legacy", default=None)  # also uses snake_case for some reason
    parent: str | None = None
    child: int | None = Field(ge=0, default=None)

    @model_validator(mode="before")
    @classmethod
    def rename_has_percipitation(cls, data: dict[str, object]) -> dict[str, object]:
        """Rename the typo field has_percipitation to has_precipitation.

        This is a mistake in the minecraft-data dataset which is only present for a single
        minecraft version (bedrock 1.21.60), this function renames it back to standardize
        our data models.

        This will get addressed with: https://github.com/PrismarineJS/minecraft-data/issues/1048
        after which this method can be removed.
        """
        if "has_percipitation" not in data:
            return data

        if "has_precipitation" in data:
            raise ValueError("Found biome with both has_percipitation and has_precipitation fields")

        data["has_precipitation"] = data.pop("has_percipitation")
        return data
