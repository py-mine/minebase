from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Literal, cast, overload

from minebase.types._base import MinecraftValidationContext
from minebase.types.common_data import CommonData
from minebase.types.data_paths import DataPaths
from minebase.types.mcdata import BedrockMinecraftData, PcMinecraftData

DATA_SUBMODULE_PATH = Path(__file__).parent / "data"
DATA_PATH = DATA_SUBMODULE_PATH / "data"


class Edition(Enum):
    """Available minecraft-data editions."""

    PC = "pc"
    BEDROCK = "bedrock"


def _validate_data() -> None:
    """Validate that the minecraft-data submodule is present."""
    if not DATA_SUBMODULE_PATH.is_dir():
        # should never happen (unless the submodule wasn't even included in the
        # package installation)
        raise ValueError(f"minecraft-data submodule not found (missing {DATA_SUBMODULE_PATH})")

    if not DATA_PATH.is_dir():
        # This can happen, if the submodule wasn't pulled (non-recursive clone)
        raise ValueError(f"minecraft-data submodule not initialized (missing {DATA_PATH})")


def _load_data_paths() -> DataPaths:
    """Load the data paths file, containing info on where to find the resources for specific versions."""
    file = DATA_PATH / "dataPaths.json"
    if not file.is_file():
        raise ValueError(f"minecraft-data submodule didn't contain data paths manifest (missing {file})")

    with file.open("rb") as fp:
        data = cast("DataPaths", json.load(fp))

    return DataPaths.model_validate(data)


def _load_version_manifest(version: str, edition: Edition = Edition.PC) -> dict[str, str]:
    """Load the data paths manifest for given version (if it exists)."""
    manifest = _load_data_paths()
    edition_info = manifest.pc if edition is Edition.PC else manifest.bedrock
    try:
        return edition_info[version]
    except KeyError as exc:
        raise ValueError(f"Version {version} doesn't exist for edition {edition.name}") from exc


def supported_versions(edition: Edition = Edition.PC) -> list[str]:
    """Get a list of all supported minecraft versions."""
    # We prefer versions from common data, as they're in a list, guaranteed to be
    # ordered as they were released
    data = load_common_data(edition)
    versions = data.versions

    # This is just for a sanity check
    manifest = _load_data_paths()
    edition_info = getattr(manifest, edition.value)
    manifest_versions = set(edition_info.keys())

    # These versions are present in the manifest, but aren't in the common data versions.
    # I have no idea why, they're perfectly loadable. We can't just naively insert them
    # as we want the versions list to be ordered. For now, as a hack, we remove these to
    # pass the check below, trying to load these would work, but they won't be listed as
    # supported from this function.
    # https://github.com/PrismarineJS/minecraft-data/issues/1064
    manifest_versions.remove("1.16.5")
    manifest_versions.remove("1.21")
    manifest_versions.remove("1.21.6")

    if set(versions) != set(manifest_versions) or len(versions) != len(manifest_versions):
        raise ValueError(
            f"Data integrity error: common versions don't match manifest versions: "
            f"{versions=} != {manifest_versions=}",
        )

    return versions


@overload
def load_version(version: str, edition: Literal[Edition.PC] = Edition.PC) -> PcMinecraftData: ...


@overload
def load_version(version: str, edition: Literal[Edition.BEDROCK]) -> BedrockMinecraftData: ...


def load_version(version: str, edition: Edition = Edition.PC) -> PcMinecraftData | BedrockMinecraftData:
    """Load minecraft-data for given `version` and `edition`."""
    _validate_data()
    version_data = _load_version_manifest(version, edition)

    data: dict[str, Any] = {}
    for field, dir_suffix in version_data.items():
        dir_path = DATA_PATH.joinpath(*dir_suffix.split("/"))

        # Skip yaml files, we currently don't support loading them
        if field in {"proto", "types"}:
            continue

        file = dir_path / (field + ".json")

        if not file.is_file():
            raise ValueError(f"Unable to load {field!r} for {edition.name}/{version} (missing {file})")

        with file.open("rb") as fp:
            data[field] = json.load(fp)

    validation_context = MinecraftValidationContext(version=version, edition=edition, versions=supported_versions())

    if edition is Edition.PC:
        return PcMinecraftData.model_validate(data, context=validation_context)

    return BedrockMinecraftData.model_validate(data, context=validation_context)


def load_common_data(edition: Edition = Edition.PC) -> CommonData:
    """Load the common data from minecraft-data for given `edition`."""
    _validate_data()
    common_dir = DATA_PATH / edition.value / "common"
    if not common_dir.is_dir():
        raise ValueError(f"minecraft-data submodule didn't contain the common data for {edition.name} edition")

    data: dict[str, Any] = {}
    for file in common_dir.iterdir():
        if not file.is_file() or file.suffix != ".json":
            raise ValueError(f"Found an unexpected entry in common directory: {file}")

        with file.open("rb") as fp:
            data[file.stem] = json.load(fp)

    return CommonData.model_validate(data)
