from typing import NamedTuple


class Tag(NamedTuple):
    tag_id: int
    name: str

    def __hash__(self):
        return hash(self.tag_id)
