"""Test loading of the actual minecraft-data repository.

This suite essentially acts as integration tests, as it just blindly runs
the load functions without checking the expected results, simply testing
whether the loading succeeded.
"""

import pytest

from minebase import (
    Edition,
    _load_data_paths,  # pyright: ignore[reportPrivateUsage]
    _validate_data,  # pyright: ignore[reportPrivateUsage]
    load_common_data,
    load_version,
)


def test_data_submodule_is_initialized() -> None:
    """Ensure the minecraft-data submodule is present and initialized."""
    _validate_data()


@pytest.mark.parametrize("edition", Edition.__members__.values())
def test_load_common_data_for_each_edition(edition: Edition) -> None:
    """Ensure common data exists and is loadable for each edition."""
    data = load_common_data(edition)
    assert isinstance(data, dict)
    assert data, f"No common data found for edition {edition}"


@pytest.mark.parametrize("edition", Edition.__members__.values())
def test_all_versions_loadable(edition: Edition) -> None:
    """Iterate over every version defined in dataPaths.json and ensure it loads."""
    manifest = _load_data_paths()
    if edition.value not in manifest:
        pytest.skip(f"Edition {edition.value} not present in dataPaths.json")

    versions = manifest[edition.value]
    assert versions, f"No versions listed for edition {edition}"

    failed_versions: list[tuple[str, Exception]] = []

    for version in versions:
        try:
            result = load_version(version, edition)
            assert isinstance(result, dict)
        except Exception as exc:  # noqa: PERF203,BLE001
            failed_versions.append((version, exc))

    if failed_versions:
        fails = "\n".join(f"{v}: {err}" for v, err in failed_versions)
        pytest.fail(f"{len(failed_versions)} version(s) failed to load for {edition.name}:\n{fails}")
