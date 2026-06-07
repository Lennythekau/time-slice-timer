from typing import NamedTuple


class Tag(NamedTuple):
    tag_id: int | None
    name: str


EMPTY_TAG = Tag(None, "")
