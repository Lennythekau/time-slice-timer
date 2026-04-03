from typing import NamedTuple


class Tag(NamedTuple):
    tag_id: int | None
    name: str

    def __hash__(self):
        return hash(self.tag_id)


EMPTY_TAG = Tag(None, "")
