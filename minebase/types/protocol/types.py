from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, Any, Literal, Union, cast, final

from pydantic import BeforeValidator, Field, field_validator, model_validator
from typing_extensions import Self

from minebase.types._base import MinecraftDataModel


def normalize_types(v: Any) -> Any:
    """Normalize raw protocol type definitions into a consistent tagged-union format.

    Converts raw protocol type entries from the Minecraft data files into a form
    suitable for Pydantic validation. The returned objects always have a `kind`
    key indicating which concrete type class should be used.

    The function handles:
        - The string `"native"` -> {"kind": "native"}
        - Any other plain string -> {"kind": "alias", "target": <string>}
        - Tuple-like pairs -> {"kind": v[0], "data": v[1]}

    Args:
        v: Arbitrary raw input data representing a protocol type.

    Returns:
        A normalized dictionary with at least a `kind` key, or the original
        value if normalization is not possible (so Pydantic can raise later).
    """
    if v == "native":
        return {"kind": "native"}

    # Any other pure string values act as aliases for other types
    if isinstance(v, str):
        return {"kind": "alias", "target": v}

    # We generally always expect the value to be either str or tuple[str, Any]
    # if that's not the case, we just return the value back, so that pydantic
    # will fail somewhere and produce a better traceback pointing us to where the
    # error occurred, instead of raising from here
    if not isinstance(v, Sequence) or isinstance(v, bytes) or len(v) != 2:
        return v

    # Anything else will be stored under the 'data' key (most frequently this will be for lists)
    return {"kind": v[0], "data": v[1]}


class ProtocolTypeNode(MinecraftDataModel):
    """Base class for all protocol type value definitions."""

    @staticmethod
    def _flatten_data(v: dict[str, Any]) -> dict[str, Any]:
        """Flatten a `{'kind': ..., 'data': {...}}` structure into a single dict.

        This is used by `@model_validator(mode="before")` methods across
        the protocol type classes to make Pydantic parsing more uniform.
        """
        return {"kind": v["kind"], **v["data"]}


@final
class NamedContainerField(MinecraftDataModel):
    """A named field within a container type.

    Attributes:
        name: Field name as defined in the protocol specification.
        type: Type of the field, which may itself be a complex protocol type.
        anon: Discriminator indicating this is a named field, not an anonymous one (always False).
    """

    name: str
    type: ProtocolTypeValue
    anon: Literal[False] = False

    @field_validator("type", mode="before")
    @classmethod
    def normalize_enum_type_field(cls, v: Any) -> Any:
        """Normalize the malformed `_enum_type` field generated for Bedrock `packet_available_commands`.

        In several Bedrock protocol versions, the `_enum_type` field inside the
        `packet_available_commands` container is incorrectly serialized as a one-element
        list `["enum_size_based_on_values_len"]` instead of a plain string
        `"enum_size_based_on_values_len"`. This validator converts the malformed
        representation into the expected string form to maintain type consistency.

        This is a temporary workaround until the underlying issue in
        `minecraft-data` is resolved.

        Related issue: https://github.com/PrismarineJS/minecraft-data/issues/1101
        """
        if not isinstance(v, list):
            return v

        # Cast with explicit Any to avoid unknown type pyright warnings
        v = cast("list[Any]", v)

        if len(v) == 1 and v[0] == "enum_size_based_on_values_len":
            return "enum_size_based_on_values_len"

        return v


@final
class AnonContainerField(MinecraftDataModel):
    """An anonymous (unnamed) field within a container type.

    Attributes:
        name: Field name (only here for consistency with `NamedContainerField`, always `None`)
        type: Type of the field, which may itself be a complex protocol type.
        anon: Discriminator indicating this is an anonymous field, not a named one (always `True`).
    """

    name: None = None
    type: ProtocolTypeValue
    anon: Literal[True]


ContainerField = Annotated[
    Union[
        AnonContainerField,
        NamedContainerField,
    ],
    Field(discriminator="anon"),
]


@final
class ProtocolTypeValueNative(ProtocolTypeNode):
    """A basic "native" type that can't be further described using other composite types."""

    kind: Literal["native"]


@final
class ProtocolTypeValueAlias(ProtocolTypeNode):
    """A type that aliases another primary type (e.g. `'optvarint': 'varint'`).

    The corresponding primary type can then be looked up by the `target` type name
    in the root types dictionary of the protocol data.
    """

    kind: Literal["alias"]
    target: str


@final
class ProtocolTypeValueArray(ProtocolTypeNode):
    """A length-prefixed array type representing a repeated sequence of elements.

    Minecraft protocol arrays begin with a count field describing the number of
    elements to follow, where the count itself can use various integer encodings
    such as `varint`, `i16`, `li32`, or similar numeric aliases.

    Attributes:
        count_type: Alias of the numeric type used to encode the array length.
        type: Type definition describing each array element.
    """

    kind: Literal["array"]
    count_type: ProtocolTypeValueAliasType | None = None
    count: str | None = None
    type: ProtocolTypeValue

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class BitfieldField(MinecraftDataModel):
    """A single component of a packed bitfield value.

    Each bitfield element defines a named slice within an integer, representing a fixed-width signed or
    unsigned subfield. Bitfield structures are commonly used to encode multiple small properties or
    coordinates within a single numeric value.

    Example:
        For a 64-bit block position encoded as:
        - 26 bits for `x`
        - 12 bits for `y`
        - 26 bits for `z`

        the resulting bitfield splits the integer into named components.

    Attributes:
        name: The field name.
        size: The number of bits allocated to this subfield.
        signed: Whether the subfield uses signed integer interpretation.
    """

    name: str
    size: int
    signed: bool


@final
class ProtocolTypeValueBitfield(ProtocolTypeNode):
    """A packed bitfield structure combining multiple named subfields.

    Bitfield types describe how a single integer value is split into several logical components, each
    defined by a `BitfieldField` entry. These are used in various protocol definitions where space
    efficiency matters; for example, block positions, flags, or compact command metadata.

    Attributes:
        fields: A list of subfield definitions describing bit layout and meaning.
    """

    kind: Literal["bitfield"]
    fields: list[BitfieldField]

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return {"kind": v["kind"], "fields": v["data"]}


@final
class ProtocolTypeValueBitflags(ProtocolTypeNode):
    """A set of named boolean flags stored within an integer bitmask.

    Bitflag types describe how individual on/off states (flags) are packed into a single underlying
    integer, of type specified by `type`, which determines the bit width and encoding, such as `u8`,
    `lu16`, `zigzag64`, or `varint`.

    Each flag corresponds to one or more bits in a numeric value. When the integer's bit at a given
    position is set, the corresponding flag is considered active.

    Flags can be defined in two equivalent forms:
      * **Sequential form:** A list of flag names, where bit positions are assigned incrementally
        starting from 0.
      * **Explicit mask form:** A mapping of flag names to bitmask integers.
        The integer values represent actual bit masks (powers of two) or combinations thereof, where
        the presence of a bit indicates that flag's activation.

    This structure is widely used across the Minecraft protocol to encode compact state sets, including
    player movement inputs, entity status, permission capabilities, or UI actions.

    Notes:
        - Integer values like `1`, `2`, `4`, `8` correspond to bit positions 0-3
          (2^0, 2^1, 2^2, 2^3).
        - Some flags use combined or offset masks (e.g. `65537` = bits 0 and 16)
          for internal protocol grouping.

    Attributes:
        type: The numeric type or alias defining the width and encoding of the mask.
        flags:
            Either a sequential list of flag names or an explicit mapping of names to integer
            bit masks.
        big:
            This is a bool flag that indicates a JavaScript `bigint` type should be used to store
            the value of this number. It can essentially be ignored, as it's possible to figure
            that out based on the `type` attribute already and is JS specific.

            Ref: <https://github.com/PrismarineJS/minecraft-data/issues/1101>
    """

    kind: Literal["bitflags"]
    type: ProtocolTypeValueAliasType
    flags: dict[str, int] | list[str]
    big: Literal[True] | None = None

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueBuffer(ProtocolTypeNode):
    """A contiguous sequence of raw bytes (binary buffer).

    This type represents an opaque binary payload whose length may be either fixed (using `count`)
    or prefixed by another numeric type (using `count_type`). It is used throughout the protocol for
    data such as NBT blobs, cryptographic signatures, or custom payloads.

    Length determination modes:
      * **Dynamic length** - `count_type` specifies the type of integer
        that precedes the buffer and encodes its size (e.g. `varint`,
        `li16`, `zigzag32`).
      * **Fixed length** - `count` gives an explicit byte size.

    Attributes:
        count_type: Optional alias of a numeric type that encodes the buffer length.
        count: Optional fixed length of the buffer in bytes.
    """

    kind: Literal["buffer"]
    count_type: ProtocolTypeValueAliasType | None = None
    count: int | None = None

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)

    @model_validator(mode="after")
    def validate_exclusive_count(self) -> Self:
        """Buffers should either have a `count_type` or a `count`, never both."""
        # Use simple XNOR check to ensure both count & count_type aren't none/set
        if not ((self.count_type is None) ^ (self.count is None)):
            raise ValueError(f"Got {self.count_type=} and {self.count=}, which are mutually exclusive")
        return self


@final
class ProtocolTypeValueContainer(ProtocolTypeNode):
    """A composite type composed of multiple sequential fields.

    This type defines a structured group of protocol fields that are serialized in the declared order.
    Each field may be either named or anonymous, where named fields contribute to the resulting
    object's schema, and anonymous fields are used for inline or conditional subtypes.

    Containers function similarly to structs in binary protocols: their fields appear consecutively in
    the stream, and each subfield's own type determines how its data is read or written. This type is
    used extensively to describe higher-level entities such as packets, scoreboard entries, and nested
    switch-based variants.

    Field types:
      * **Named fields** - Have an explicit `name` and a `type`.
        Example: `{"name": "position", "type": "vec3f"}`
      * **Anonymous fields** - Have no name (`anon=True`) and are included for inlined containers,
        switches, or conditional payloads.

    Attributes:
        fields:
            Ordered list of `ContainerField` objects representing all contained subfields, both named
            and anonymous.
    """

    kind: Literal["container"]
    fields: list[ContainerField]

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return {"kind": v["kind"], "fields": v["data"]}

    @field_validator("fields", mode="before")
    @classmethod
    def add_anon_discriminator(cls, v: Any) -> Any:
        """Add `anon` field to all items in `fields` to provide a pydantic discriminator."""
        if not isinstance(v, list):
            return v  # let pydantic deal with this

        v = cast("list[Any]", v)

        for field in v:
            if not isinstance(field, dict):
                continue  # let pydantic deal with these

            if "anon" not in field:
                field["anon"] = False

        return v


@final
class ProtocolTypeValueEntityMetadataLoop(ProtocolTypeNode):
    """A looped sequence of entity metadata entries terminated by a sentinel value.

    This type defines a variable-length list of entity metadata elements. Each element describes one
    property of an entity, such as its pose, custom name, or flags. Entries are read repeatedly using
    the specified `type` definition until a terminating byte (`end_val`) is encountered.

    Decoding process:
      1. Repeatedly parse one metadata entry using `type`.
      2. Stop when the next byte equals `end_val` (e.g., 127 or 255).

    Attributes:
        end_val: Integer sentinel value marking the end of the metadata list.
        type: Protocol type used to decode each metadata entry (typically
            a container or alias referencing `entityMetadataEntry`).
    """

    kind: Literal["entityMetadataLoop"]
    end_val: int
    type: ProtocolTypeValue

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueMapper(ProtocolTypeNode):
    """A value-to-name mapping that converts numeric codes into symbolic identifiers.

    The `mapper` type defines a lookup table mapping between raw integer values (read according to the
    specified `type`) and their corresponding symbolic names used within the protocol. This structure
    serves the same role as an enumeration but is defined explicitly in data rather than as a fixed
    constant.

    The underlying `type` determines how the numeric code is read from the stream, typically as
    `varint`, `u8`, or `zigzag32`. After decoding that value, the resulting number (or hex literal) is
    resolved through the `mappings` table to yield a human-readable string identifier.

    Many protocol definitions use this for mapping internal IDs to meaning, such as packet types,
    entity events, sounds, particles, and interactions.


    Notes:
      * Keys in `mappings` are usually a stringified decimal, but sometimes also hexadecimal strings.
        (Hexadecimal keys such as `"0x8E"` occur in some `u8`-based mappers.)

    Attributes:
        type: Underlying alias type describing how numeric codes are encoded.
        mappings:
            Dictionary mapping raw numeric (or hex) string keys to their symbolic string identifiers.
    """

    kind: Literal["mapper"]
    type: ProtocolTypeValueAliasType
    mappings: dict[str, str]

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValuePstring(ProtocolTypeNode):
    """A length-prefixed string type with a configurable count field and encoding.

    The `pstring` type (Pascal-style string) represents a textual value prefixed by its length.
    The length is read using the specified `count_type`, which determines how many bytes are used for
    the length prefix and how it is interpreted (for example, as `varint` or `li16`).

    After reading the length value, that many bytes are read and decoded using the given `encoding`
    (if specified) or UTF-8 by default.

    Notes:
      * when `encoding` is omitted, UTF-8 is assumed.

    Attributes:
        encoding: Optional name of the string encoding (e.g. `"latin1"`). If `None`, UTF-8 is assumed.
        count_type: Underlying alias type specifying how the string length is encoded.
    """

    kind: Literal["pstring"]
    encoding: str | None = None
    count_type: ProtocolTypeValueAliasType

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueOption(ProtocolTypeNode):
    """An optional wrapper type indicating that a value may be present or absent.

    The `option` type represents a field whose presence is conditional. It wraps another type
    definition (`type`) and adds a presence indicator in the serialized format (e.g., a preceding
    boolean or similar flag) to signal whether the value exists.

    When the flag is false, no further bytes for the inner type are read or written; when true, the
    contained type is serialized normally. This allows protocol structures to express optional
    fields in a compact, self-describing way.

    Attributes:
        type:
            The underlying value type to serialize when the option is present.

            Can be any valid protocol type (e.g. `string`, `UUID`, container, or another composite type).
    """

    kind: Literal["option"]
    type: ProtocolTypeValue

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return {"kind": v["kind"], "type": v["data"]}


@final
class ProtocolTypeValueSwitch(ProtocolTypeNode):
    """A conditional branch type that selects one of several field definitions at runtime.

    The `switch` type defines a dynamic structure whose format depends on the value of another
    field. It acts like a schema-level conditional: based on the value of `compare_to` field,
    one of the mapped entries in `fields` is used for serialization or deserialization. If no
    explicit branch matches and a `default` is defined, that type is used instead.

    This construct enables compact representation of polymorphic protocol data, such as variant
    packets, conditional properties, or optional subfields.
    """

    kind: Literal["switch"]
    compare_to: str
    fields: dict[str, ProtocolTypeValue]
    default: ProtocolTypeValue | None = None

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueRegistryEntryHolder(ProtocolTypeNode):
    """A wrapper type for values that can appear either as a reference or as an inline definition.

    The `registryEntryHolder` type describes a field that can represent data in two
    interchangeable forms:

    - **Primary form** - a single field named by `base_name`, usually a reference to a globally
      registered element (for example, a sound ID, pattern ID, or variant name).
    - **Fallback form** - the field defined by `otherwise`, providing a full inline structure
      when the value is not represented by a registry reference.

    Although commonly used with registry-backed identifiers, the concept is general: this type
    indicates that the field prefers a compact, single-value representation (`base_name`) but
    can fall back to an expanded structure (`otherwise`) when needed.


    Attributes:
        base_name: Name of the preferred (usually reference-like) field.
        otherwise:
            Field definition used when the preferred representation is not present, typically
            containing a full inline structure.
    """

    kind: Literal["registryEntryHolder"]
    base_name: str
    otherwise: NamedContainerField

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueRegistryEntryHolderSet(ProtocolTypeNode):
    """A generic two-variant container type with a primary and fallback representation.

    The `registryEntryHolderSet` type defines a structure that may take one of two alternate forms,
    distinguished not by an explicit discriminator but by which of the two contained field variants
    applies in a given context. It provides a flexible encoding mechanism for data that can appear
    in either a canonical ("base") form or a secondary ("otherwise") fallback form.

    The two variants are described by:
      * `base` - the primary field definition that represents the preferred or modern structure for
        this data.
      * `otherwise` - an alternate field definition that encodes the same semantic concept in a
        different, typically legacy, representation.

    The exact meaning of these two branches depends on how this type is used in higher-level
    protocol definitions. Implementations are expected to select one of the two forms during
    serialization or deserialization based on the field's runtime shape or registry context.

    Attributes:
        base: Field definition describing the primary variant of the container.
        otherwise: Field definition describing the fallback or alternate variant.
    """

    kind: Literal["registryEntryHolderSet"]
    base: NamedContainerField
    otherwise: NamedContainerField

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueEntityMetadataItem(ProtocolTypeNode):
    """A parameterized switch referring to the global `entityMetadataItem` definition.

    The `entityMetadataItem` type acts as a template reference to the top-level
    `"entityMetadataItem"` switch in the protocol schema. This switch describes all possible
    entity metadata value types and maps their symbolic names (such as `"byte"`, `"int"`,
    `"string"`, `"pose"`, or `"particle"`) to concrete protocol types.

    When a field uses `["entityMetadataItem", {"compareTo": "type"}]`, it instructs the parser
    to resolve the top-level `entityMetadataItem` switch, replacing its `$compareTo`
    placeholder with the provided field value (from `"type"` in this case). The resulting
    resolved switch determines which value structure to decode based on the metadata type
    mapping defined by the preceding field.

    In effect, this type delegates decoding of metadata values to the global definition while
    binding it to a specific discriminator within the local container.

    Attributes:
        compare_to:
            The name of the field whose value should replace `$compareTo` in the top-level
            `entityMetadataItem` switch, typically `"type"`.
    """

    kind: Literal["entityMetadataItem"]
    compare_to: str

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueCount(ProtocolTypeNode):
    """A dynamic count field representing the size of another data structure.

    The `count` type is used to store or compute the length of another field, typically an array
    or nested container. It mirrors the `count` attribute found in array definitions, but in reverse:
    rather than *using* a count to determine how many elements to read, it *produces* a count value
    that reflects the size of a referenced field elsewhere in the same container.

    In other words, this type defines an integer field whose value equals the number of elements
    within the structure named by `count_for`. It is primarily used in packet formats that must
    redundantly store both a variable-length array and its dimensions as separate integer fields.

    Note:
        This structure is currently only found in early Bedrock Edition versions (0.14 & 0.15).
    """

    kind: Literal["count"]
    type: ProtocolTypeValueAliasType
    count_for: str

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueEncapsulated(ProtocolTypeNode):
    """A length-prefixed encapsulation of another type's serialized data.

    The `encapsulated` type wraps a nested structure by first writing its total byte length
    (encoded using the specified `length_type`), followed by the serialized contents of another
    protocol type. It is used when the protocol needs to embed variable-length binary sections
    or isolate sub-records whose size must be known before reading.

    This construct behaves similarly to a framed payload or a prefixed buffer: it allows a
    decoder to skip, copy, or reparse the enclosed section without interpreting its contents
    directly. The inner data type is referenced via the `type` field, which names another
    protocol type such as `"LoginTokens"`, `"ItemExtraDataWithBlockingTick"`, or similar
    container. The definition of this referenced type can be found in the top-level protocol
    definitions.

    Attributes:
        length_type:
            Alias of the numeric type used to encode the total byte length of
            the encapsulated section (for example, `"varint"`).
        type:
            Alias referencing the inner type whose serialized form is wrapped
            by this encapsulation.
    """

    kind: Literal["encapsulated"]
    length_type: ProtocolTypeValueAliasType
    type: ProtocolTypeValueAliasType

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


@final
class ProtocolTypeValueParticleData(ProtocolTypeNode):
    """A parameterized switch template used for particle-specific data selection.

    The `particleData` type acts as an indirect reference to a global switch definition that
    maps particle IDs to their corresponding parameter layouts. It does not itself contain case
    data; instead, it provides the value of `compare_to`, which replaces the `$compareTo`
    placeholder in the global `particleData` switch.

    In other words, this type instructs the deserializer to resolve its layout by applying the
    top-level `particleData` definition, substituting `compareTo = <field>` (typically
    `"particleId"`). The referenced global switch then determines the correct per-particle
    container schema.

    Attributes:
        compare_to:
            The name of the field whose value (e.g. `"particleId"`) should be substituted into
            the global `particleData` switch definition to determine which particle-specific
            data layout applies.
    """

    kind: Literal["particleData"]
    compare_to: str

    @model_validator(mode="before")
    @classmethod
    def root_validator(cls, v: dict[str, Any]) -> Any:
        return cls._flatten_data(v)


ProtocolTypeValue = Annotated[
    Annotated[
        Union[
            ProtocolTypeValueNative,
            ProtocolTypeValueAlias,
            ProtocolTypeValueArray,
            ProtocolTypeValueBitfield,
            ProtocolTypeValueBitflags,
            ProtocolTypeValueBuffer,
            ProtocolTypeValueContainer,
            ProtocolTypeValueEntityMetadataLoop,
            ProtocolTypeValueMapper,
            ProtocolTypeValuePstring,
            ProtocolTypeValueSwitch,
            ProtocolTypeValueOption,
            ProtocolTypeValueRegistryEntryHolder,
            ProtocolTypeValueRegistryEntryHolderSet,
            ProtocolTypeValueEntityMetadataItem,
            ProtocolTypeValueCount,
            ProtocolTypeValueEncapsulated,
            ProtocolTypeValueParticleData,
        ],
        Field(discriminator="kind"),
    ],
    BeforeValidator(normalize_types),
]

ProtocolTypeValueAliasType = Annotated[ProtocolTypeValueAlias, BeforeValidator(normalize_types)]
