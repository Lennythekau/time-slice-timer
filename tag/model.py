from typing import NamedTuple


class Tag(NamedTuple):
    tag_id: int
    name: str


EMPTY_TAG = Tag(-1, "")
