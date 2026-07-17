from __future__ import annotations

from typing import Annotated, Any, Literal, Union, final

from pydantic import Field, RootModel, field_validator, model_validator
from typing_extensions import TypeAlias

from minebase.types._base import MinecraftDataModel

# region: Java


@final
class JavaRecipeResult(MinecraftDataModel):
    """Represents the output item produced by a crafting recipe.

    Attributes:
        id: The numerical item ID of the resulting item.
        count: The quantity of the resulting item produced by the recipe.
        metadata: Metadata value associated with the resulting item, or None if the item has no metadata.
    """

    id: int
    count: int
    metadata: int | None = None


@final
class JavaRecipeIngredientItem(MinecraftDataModel):
    """Represents a single ingredient item in a crafting recipe.

    Attributes:
        id: The numerical item ID of the ingredient.
        metadata: Metadata value associated with the ingredient item, or None if the ingredient has no metadata.

    Notes:
        Ingredient items can be specified either as:
        - A simple integer representing the `id`.
        - A structure containing both `id` and `metadata` values.

        When provided as an integer, it will be automatically converted into
        the structured form with `metadata` set to None.
    """

    id: int
    metadata: int | None

    @model_validator(mode="before")
    @classmethod
    def convert_pure_int_id(cls, obj: object) -> Any:
        """Convert integer form into structured form.

        A recipe ingredient item can be specified as a simple integer (id), or as a structure of
        {id: int, metadata: int}. This method converts the simple int into a structure that pydantic
        can work with.
        """
        if isinstance(obj, int):
            return {"id": obj, "metadata": None}

        return obj


@final
class JavaShapelessRecipe(MinecraftDataModel):
    """Minecraft-Data for a shapeless recipe.

    This represents a crafting recipe that does not require the items to be placed in any
    specific order in the crafting grid.

    Attributes:
        result: The item that will be created when this recipe is crafted.
        ingredients: A list of ingredient items required for the recipe. Must contain at least one item.
    """

    result: JavaRecipeResult
    ingredients: list[JavaRecipeIngredientItem] = Field(min_length=1)


@final
class JavaShapedRecipe(MinecraftDataModel):
    """Minecraft-Data for a shaped recipe.

    This represents a crafting recipe that requires the items to be put in a specific order/shape.

    Attributes:
        result: The item that will be created with this recipe
        in_shape:
            The 2D grid of ingredients as they are placed into the crafting table slots,
            represented as a list of rows containing `JavaRecipeIngredientItem` instances or `None` (gaps).
            Each row corresponds to one horizontal row of the crafting grid.
        out_shape:
            The 2D grid representing the remaining items in the crafting grid after the recipe
            is completed. For example, items with containers (like milk buckets) may leave behind
            their empty container (e.g., an empty bucket) in the same slot. Slots where nothing remains
            are represented as `None`.
    """

    result: JavaRecipeResult
    in_shape: list[list[JavaRecipeIngredientItem | None]]
    out_shape: list[list[JavaRecipeIngredientItem | None]] | None = None

    @field_validator("in_shape", "out_shape")
    @classmethod
    def validate_shape(
        cls,
        v: list[list[JavaRecipeIngredientItem | None]] | None,
    ) -> list[list[JavaRecipeIngredientItem | None]] | None:
        """Validate that the shape follows the expected pattern.

        - There must be at least 1 row
        - There must be at most 3 rows
        - There must be at least 1 item in each row
        - There must be at most 3 items in each row
        - All rows must have the same length
        """
        if v is None:
            return v

        if len(v) < 1:
            raise ValueError("A shape must have at least 1 row")
        if len(v) > 3:
            raise ValueError("A shape must have at most 3 rows")

        if len(v[0]) < 1:
            raise ValueError("A shape must have at least 1 item in each row")
        if len(v[0]) > 3:
            raise ValueError("A shape must have at most 3 items in each row")

        row_len = len(v[0])
        if not all(len(row) == row_len for row in v):
            raise ValueError("A shape must have the same row length for all rows")

        return v


@final
class JavaRecipesData(RootModel[dict[int, list["JavaShapedRecipe | JavaShapelessRecipe"]]]): ...


# endregion
# region: Bedrock


@final
class BedrockListEndNBTData(MinecraftDataModel):
    """Represents an NBT list of type `end`.

    This is a special case in the NBT format indicating an empty list.
    In Bedrock's JSON-like representation, this is modeled as a list with zero elements.

    This type can be treated as a simple indicator that the list is empty. It doesn't
    contain any useful data.
    """

    type: Literal["end"]
    value: list[object] = Field(max_length=0)  # This is likely just a placeholder value to include something


@final
class BedrockCompoundListNBTData(MinecraftDataModel):
    """Represents an NBT list data.

    Each element in `value` is a dictionary mapping NBT tag names to nested `BedrockNBT` values.
    """

    type: Literal["compound"]
    value: list[dict[str, BedrockNBT]]


@final
class BedrockListNBTData(MinecraftDataModel):
    """Represents a generic NBT list tag.

    This tag indicates that the inner compound tag is going to be a list of NBTs,
    or an end indicator NBT (in case of an empty list)
    """

    type: Literal["list"]
    value: BedrockCompoundListNBTData | BedrockListEndNBTData


@final
class BedrockByteNBTData(MinecraftDataModel):
    """Represents an NBT (unsigned) byte tag."""

    type: Literal["byte"]
    value: int = Field(ge=0, le=255)


@final
class BedrockByteArrayNBTData(MinecraftDataModel):
    """Represents an NBT byte array tag (contains a list of unsigned bytes)."""

    type: Literal["byteArray"]
    value: list[Annotated[int, Field(ge=0, le=255)]]


@final
class BedrockIntNBTData(MinecraftDataModel):
    """Represents an NBT integer (signed, 4 byte number) tag."""

    type: Literal["int"]
    value: int = Field(ge=-(2**31), le=2**31 - 1)


class BedrockCompoundNBTData(MinecraftDataModel):
    """Represents a standard NBT compound tag.

    Each key is the tag name, and each value is another NBT tag.
    """

    type: Literal["compound"]
    value: dict[str, BedrockNBT]


@final
class BedrockRootCompoundNBTData(BedrockCompoundNBTData):
    """Represents the root NBT compound tag for a Bedrock file.

    The root compound NBT matches the simple compound NBT, but includes
    a name string. However, this string always seems to be empty.
    """

    type: Literal["compound"]
    name: Literal[""]
    value: dict[str, BedrockNBT]


@final
class BedrockRootNBTData(MinecraftDataModel):
    """Represents the top-level structure of a Bedrock Named Binary Tag (NBT)."""

    version: Literal[1]
    nbt: BedrockRootCompoundNBTData


BedrockNBT: TypeAlias = Annotated[
    Union[
        BedrockCompoundNBTData,
        BedrockByteNBTData,
        BedrockListNBTData,
        BedrockIntNBTData,
        BedrockByteArrayNBTData,
    ],
    Field(discriminator="type"),
]


@final
class BedrockRecipeItem(MinecraftDataModel):
    """Represents an item used as an ingredient or produced as output in a Bedrock recipe.

    Attributes:
        name: The item name or identifier (e.g., "minecraft:planks").
        count: The number of this item required or produced.
        metadata: Optional metadata value for the item, or None if not applicable.
        nbt: Optional NBT data associated with the item. If None, the item has no NBT data.
    """

    name: str
    count: int = Field(ge=1)
    metadata: int | None = None
    nbt: BedrockRootNBTData | None = None


@final
class BedrockRecipeData(MinecraftDataModel):
    """Minecraft-Data for a crafting or processing recipe in Minecraft: Bedrock Edition.

    Attributes:
        name: Internal recipe name identifier (guaranteed unique).
        type: The type of crafting or processing station where the recipe applies.
        ingredients: A list of `BedrockRecipeItem` objects representing the required ingredients.
        input:
            A 2D grid of integers referencing ingredient positions in `ingredients` (1-based index),
            with 0 meaning a gap. Used only for shaped recipes. May be None for shapeless recipes
            or non-crafting recipes.
        output: A list of `BedrockRecipeItem` objects representing the produced items.
        priority:
            An optional priority value (currently only observed as 0).

            The exact meaning is unclear in Bedrock recipe data.
    """

    name: str
    type: Literal[
        "multi",
        "cartography_table",
        "stonecutter",
        "crafting_table",
        "crafting_table_shapeless",
        "shulker_box",
        "furnace",
        "blast_furnace",
        "smoker",
        "soul_campfire",
        "campfire",
        "smithing_table",
    ]
    ingredients: list[BedrockRecipeItem] = Field(min_length=1)
    input: list[list[int]] | None = None
    output: list[BedrockRecipeItem] = Field(min_length=1)
    priority: Literal[0] | None = None

    @model_validator(mode="after")
    def validate_input(self) -> BedrockRecipeData:
        """Validate that the input shape only references the available ingredients."""
        if self.input is None:
            return self

        max_ingredient_id = len(self.ingredients)
        if not all(0 <= ingredient_id <= max_ingredient_id for shape_row in self.input for ingredient_id in shape_row):
            raise ValueError("Recipe input shape references unknown ingredients")

        return self


@final
class BedrockRecipesData(RootModel[dict[int, BedrockRecipeData]]): ...


# endregion
