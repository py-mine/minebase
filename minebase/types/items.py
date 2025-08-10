from __future__ import annotations

from typing import final

from pydantic import Field, model_validator

from minebase.types._base import MinecraftDataModel


@final
class ItemVariationData(MinecraftDataModel):
    """Minecraft-Data for an item variation.

    Certain items have multiple variations that are distinguished through a metadata number.
    For example, coal (id 263) has a charcoal variation with metadata=1 (making it 263:1).
    These sub-items don't have their own entry in the items data, they're only tracked as
    variations of the parent item.

    Attributes:
        metadata:
            The metadata number to distinguish this variation from the parent.

            Each variation must have a metadata value.
        display_name:
            The item name as shown in the GUI.

            Each variation must have it's own display name that differs from the parent item
        id:
            The unique identifier of the item.

            Most variations don't have their own ID, and instead only contain metadata to
            distinguish them from the parent, however, some variations are given their own
            item ID, even though they're still only considered a variation of the parent.
        name:
            The minecraft name of an item (guaranteed to be unique).

            Many variations aren't given a name and instead share the same item name with
            the parent item, and are distinguished only by metadata. However, some do have
            their own unique name, even though they're still only considered a variation
            of the parent.
        enchant_categories: Which enchant categories apply to this item variation
        stack_size: What is the stack size of this item variation

    """

    metadata: int = Field(ge=0)
    display_name: str
    enchant_categories: list[str] | None = None
    stack_size: int | None = Field(ge=0, le=64, default=None)
    id: int | None = Field(ge=0, default=None)
    name: str | None = None


@final
class ItemsData(MinecraftDataModel):
    """Minecraft-Data about an item.

    Attributes:
        id: The unique identifier of the item
        name: The minecraft name of an item (guaranteed to be unique)
        display_name: The item name as shown in the GUI
        stack_size: The maximum amount that can be in a single stack for this item (usually 64)
        enchant_categories: Which enchant categories apply to this item
        repair_with: Items (item names) that this item can be combined with in an anvil for repair
        max_durability: The maximum amount of durability points for this item
        block_state_id: The unique identifier of the block that will be placed from this block item.
        variations: Variantions of this item (e.g. for coral, there's Tube Coral, Brain Coral, Bubble Coral, ...)
        metadata: Number used primarily to distinguish item variations (e.g. tall grass 150:1 vs fern 150:2)
    """

    id: int = Field(ge=0)
    name: str
    display_name: str
    stack_size: int = Field(ge=0)
    enchant_categories: list[str] | None = None
    repair_with: list[str] | None = None
    max_durability: int | None = Field(ge=0, default=None)
    variations: list[ItemVariationData] | None = None
    block_state_id: int | None = Field(ge=0, default=None)
    metadata: int | None = Field(ge=0, default=None)

    @model_validator(mode="before")
    @classmethod
    def strip_durability(cls, data: dict[str, object]) -> dict[str, object]:
        """Remove the redundant `durability` field, if present.

        The minecraft-data dataset includes both `max_durability` and `durability`, however, these fields
        always match, since this is the data for new items only. This makes the durability field entirely
        redundant; strip it.
        """
        if "durability" not in data:
            return data

        if "maxDurability" not in data:
            raise ValueError("Found durability field without max_durability")

        if data["durability"] != data["maxDurability"]:
            raise ValueError("The durability field doesn't match max_durability")

        del data["durability"]
        return data

    @model_validator(mode="before")
    @classmethod
    def rename_fixed_with(cls, data: dict[str, object]) -> dict[str, object]:
        """Rename the `fixed_with` field to `repair_with`.

        These fields mean the same thing, however, the minecraft-data dataset includes one
        single version (bedrock 1.17.10), where for some reason, the field name `fixed_with`
        is used instead of `repair_with`. For a simpler user-facing API, this renames that
        field back to `repair_with`.

        This will get addressed with: https://github.com/PrismarineJS/minecraft-data/pull/1052
        after which this method can be removed.
        """
        if "fixedWith" not in data:
            return data

        if "repairWith" in data:
            raise ValueError("Found item with both fixed_with and repair_with field")

        data["repairWith"] = data.pop("fixedWith")
        return data
