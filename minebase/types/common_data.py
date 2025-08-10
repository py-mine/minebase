from __future__ import annotations

from typing import Literal, final

from pydantic import model_validator

from minebase.types._base import MinecraftDataModel


@final
class LegacyData(MinecraftDataModel):
    """Minecraft-Data for Legacy mappings (id -> name).

    Attributes:
        blocks: Mapping of block IDs to their names.
        items: Mapping of item IDs to their names.
    """

    blocks: dict[str, str]
    items: dict[str, str]


@final
class FeatureValueData(MinecraftDataModel):
    """Minecraft-Data of a sub-feature and the versions in which it is supported.

    Certain features have multiple values / variants / sub-features, this represents such a sub-feature.

    Attributes:
        value: The feature's value, which may be a string or integer.
        versions: Inclusive version range in which this value applies, as a tuple (start_version, end_version).
        version: Single version in which this value applies.
    """

    value: str | int
    versions: tuple[str, str] | None = None
    version: str | None = None

    @model_validator(mode="after")
    def check_version_xor_versions(self) -> FeatureValueData:
        """Validate that exactly one of `version` or `versions` is set."""
        if self.version is not None and self.versions is not None:
            raise ValueError("Cannot specify both 'version' and 'versions'")
        if self.version is None and self.versions is None:
            raise ValueError("Must specify either 'version' or 'versions'")
        return self


@final
class FeatureData(MinecraftDataModel):
    """Minecraft-Data for a feature.

    Attributes:
        name: The name of the feature.
        description: Human-readable description of the feature.
        versions: Inclusive version range in which this feature applies, as a tuple (start_version, end_version).
        version: Single version in which this feature applies.
        values: Possible sub-features / variants of this feature that can each apply for different versions.
    """

    name: str
    description: str
    versions: tuple[str, str] | None = None
    version: str | None = None
    values: list[FeatureValueData] | None = None

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> FeatureData:
        """Validate that exactly one of `version`, `versions`, or `values` is set."""
        fields: dict[str, object] = {"version": self.version, "versions": self.versions, "values": self.values}

        # Count non-None fields
        provided_fields = sum(1 for value in fields.values() if value is not None)

        if provided_fields == 0:
            raise ValueError("Must provide exactly one of: 'version', 'versions', or 'values'")
        if provided_fields > 1:
            raise ValueError("Cannot provide more than one of: 'version', 'versions', or 'values'")
        return self


@final
class ProtocolVersionData(MinecraftDataModel):
    """Minecraft-Data about a protocol version.

    Attributes:
        minecraft_version: The version of Minecraft that uses this protocol version.
        version: The protocol version number.
        data_version: Internal data version number.
        uses_netty:
            Whether this protocol version uses Netty networking.

            In version 1.7.2 of the PC (Java) edition, the protocol numbers were reset to 0
            as the protocol was rewritten to use Netty.

            This field is only present for PC versions.
        major_version: The major Minecraft version identifier (e.g., '1.19').
        release_type: The release type, either 'snapshot' or 'release'.
    """

    minecraft_version: str
    version: int
    data_version: int | None = None
    uses_netty: bool | None = None
    major_version: str
    release_type: Literal["snapshot", "release"] | None = None


@final
class CommonData(MinecraftDataModel):
    """Minecraft-Data common across all Minecraft versions, or metadata information.

    Attributes:
        legacy: Legacy block and item ID mappings.
        versions: List of Minecraft version strings.
        features: List of feature definitions.
        protocol_versions: List of protocol version data entries.
    """

    legacy: LegacyData
    versions: list[str]
    features: list[FeatureData]
    protocol_versions: list[ProtocolVersionData]
