from __future__ import annotations

from typing import final

from pydantic import field_validator

from minebase.types._base import MinecraftDataModel


@final
class SoundData(MinecraftDataModel):
    """Minecraft-Data for a single sound entry.

    Each entry maps a unique integer ID to a specific Minecraft sound,
    identified by a namespaced string. This can include:

    - Block Sounds (e.g., 'block.stone.place')
    - Entity Sounds (e.g., 'entity.snowman.shoot')
    - Ambient Sounds (e.g., 'ambient.cave')
    - Item sounds (e.g., 'item.bucket.fill_lava')
    - Music tracks (e.g., 'music.credits')
    - Music disks (e.g., 'music_disc.cat', or 'record.cat' in older versions)
    - UI sounds (e.g., 'ui.button.click')
    - Weather sounds (e.g., 'weather.rain')
    - Events (e.g., 'event.raid.horn')
    - Particles (e.g., 'particle.soul_escape')
    - Enchantments (e.g. 'enchant.thorns.hit')

    Attributes:
        id: Unique identifier for the sound entry.
        name: Namespaced string representing the sound in Minecraft.
    """

    id: int
    name: str

    @field_validator("name")
    @classmethod
    def name_namespace(cls, name: str) -> str:
        """Validated that the sound `name` has one of the expected namespaces."""
        if name == "intentionally_empty":
            return name

        try:
            namespace, _ = name.split(".", maxsplit=1)
        except ValueError as exc:
            raise ValueError(f"Sound name {name} isn't namespaced") from exc

        namespaces = {
            "block",
            "entity",
            "ambient",
            "item",
            "music",
            "record",
            "ui",
            "weather",
            "music_disc",
            "event",
            "particle",
            "enchant",
        }

        if namespace not in namespaces:
            raise ValueError(f"Sound name {name} doesn't belong to any of the expected name-spaces: {namespaces}")

        return name
