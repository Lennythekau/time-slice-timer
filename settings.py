"""For now, you have to manually edit the file contents."""

import pathlib
import tomllib
from typing import TypedDict, cast


import pathlib


class TagConfig(TypedDict):
    name: str
    duration: int


class Settings(TypedDict):
    default_duration: int
    tags: list[TagConfig]
    tag_names: list[str]


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


def get_settings_or_defaults(path: pathlib.Path) -> Settings:
    try:
        with open(path, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        with open(path, "w") as f:
            contents = __DEFAULT_SETTINGS_FILE_CONTENTS
            f.write(contents)

    raw_settings = cast(Settings, tomllib.loads(contents))
    raw_settings["tag_names"] = list(config["name"] for config in raw_settings["tags"])

    return raw_settings
