"""For now, you have to manually edit the file contents."""

import pathlib
import tomllib
from typing import TypedDict, cast


import pathlib


class TagSettings(TypedDict):
    name: str
    duration: int


class Settings(TypedDict):
    default_duration: int
    tags: list[TagSettings]


__DEFAULT_SETTINGS_FILE_CONTENTS = """
# The default amount of time allocated to a time slice, in minutes
default_duration = 20

# Format:
# [[tags]]
# name = "tag-name"
# duration = number
#
# The duration is optional. If it isn't provided, it will fall back on the default duration.


[[tags]]
name = "Blender"
duration = 30

[[tags]]
name = "Godot"

[[tags]]
name = "Musescore"
"""

__CURRENT_DIRECTORY = pathlib.Path(__file__).resolve().parent


def get_settings_or_get_defaults() -> Settings:

    path = __CURRENT_DIRECTORY / "data" / "settings.toml"
    try:
        with open(path, "r") as f:
            contents = f.read()
            return cast(Settings, tomllib.loads(contents))
    except FileNotFoundError as err:
        with open(path, "w") as f:
            f.write(__DEFAULT_SETTINGS_FILE_CONTENTS)
        return cast(Settings, tomllib.loads(__DEFAULT_SETTINGS_FILE_CONTENTS))


def get_tag_names(settings: Settings):
    return (tag["name"] for tag in settings["tags"])


def get_tag_name_list(settings: Settings):
    return list(get_tag_names(settings))
