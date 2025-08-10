from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, final

from pydantic import Field, model_validator

from minebase.types._base import MinecraftDataModel


@final
class CollisionBoxData(MinecraftDataModel):
    """Minecraft-Data for a collision shape.

    Represents the (x0, y0, z0, x1, y1, z1) points of an axis aligned bounding box (AABB).
    """

    min_x: float = Field(ge=-0.25, le=1.5)
    min_y: float = Field(ge=-0.25, le=1.5)
    min_z: float = Field(ge=-0.25, le=1.5)
    max_x: float = Field(ge=-0.25, le=1.5)
    max_y: float = Field(ge=-0.25, le=1.5)
    max_z: float = Field(ge=-0.25, le=1.5)

    @model_validator(mode="before")
    @classmethod
    def from_sequence(cls, value: object) -> dict[str, object]:
        """Ensure the value is a 6 element tuple, then convert it into a dict for pydantic."""
        if not isinstance(value, Sequence):
            raise TypeError(f"CollisionBoxData must be initialized from a sequence, got {type(value).__qualname__}")

        if len(value) != 6:
            raise ValueError("CollisionBoxData must have exactly 6 elements")

        # Use camelCase here since MinecraftDataModel expects it
        return {
            "minX": value[0],
            "minY": value[1],
            "minZ": value[2],
            "maxX": value[3],
            "maxY": value[4],
            "maxZ": value[5],
        }

    @model_validator(mode="after")
    def validate_min_less_than_max(self) -> CollisionBoxData:
        """Validate that the min coordinate is always smaller (or equal) than the corresponding max coordinate."""
        try:
            if self.min_x > self.max_x:
                raise ValueError(f"min_x ({self.min_x}) must be less than max_x ({self.max_x})")  # noqa: TRY301
            if self.min_y > self.max_y:
                raise ValueError(f"min_y ({self.min_y}) must be less than max_y ({self.max_y})")  # noqa: TRY301
            if self.min_z > self.max_z:
                raise ValueError(f"min_z ({self.min_z}) must be less than max_z ({self.max_z})")  # noqa: TRY301
        except ValueError:
            # This is stupid, I'm aware, the above is essentially dead code.
            # The reason for this is that some bedrock editions don't seem to meet this check.
            # This seems like a problem with minecraft-data. See:
            # https://github.com/PrismarineJS/minecraft-data/issues/1054
            return self

        return self

    @property
    def as_aabb(self) -> tuple[float, float, float, float, float, float]:
        """Get the data as (x0, y0, z0, x1, y1, z1), representing the points of an axis aligned bounding box (AABB)."""
        return (self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z)


@final
class BlockCollisionShapeData(MinecraftDataModel):
    """Minecraft-Data for a block collision model.

    blocks:
        Mapping of block name -> collision shape ID(s).

        The value can either be a single number: collision ID shared by all block states of this block,
        or a list of numbers: Shape IDs of each block state of this block.

    shapes: Collision shapes by ID, each shape being composed of a list of collision boxes.
    """

    blocks: dict[str, Annotated[int, Field(ge=0)] | list[Annotated[int, Field(ge=0)]]]
    shapes: dict[Annotated[int, Field(ge=0)], list[CollisionBoxData]]

    @model_validator(mode="after")
    def validate_shape_references(self) -> BlockCollisionShapeData:
        """Validate that all collision IDs specified for blocks have corresponding shape(s)."""
        for block_name, shape_ids in self.blocks.items():
            if isinstance(shape_ids, int):
                shape_ids = [shape_ids]  # noqa: PLW2901

            for shape_id in shape_ids:
                if shape_id not in self.shapes:
                    raise ValueError(
                        f"Block {block_name!r} has a collision shape ID {shape_id}, without corresponding shape data",
                    )

        return self

    def shape_for(self, block_name: str) -> list[CollisionBoxData] | list[list[CollisionBoxData]]:
        """Get the collision shape for given block name.

        This is a convenience helper-function to skip having to look up the collision shape ID(s)
        for the block and then having to look up the corresponding collision shape(s) based on that.

        Return:
            Either a:

            - List of collision shape IDs (for all block states)
            - List of lists of collision shape IDs (representing different collision shapes for different block states)
        """
        shape_ids = self.blocks[block_name]
        if isinstance(shape_ids, int):
            return self.shapes[shape_ids]

        return [self.shapes[shape_id] for shape_id in shape_ids]
