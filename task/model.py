from dataclasses import dataclass, field
from typing import ClassVar

from tag.model import EMPTY_TAG, Tag


@dataclass
class Task:
    UNSET_ID: ClassVar[int] = -1

    task_id: int
    parent: Task | None
    description: str
    tag: Tag = EMPTY_TAG
    sub_tasks: list[Task] = field(default_factory=list)

    def is_process(self):
        return self.parent is None
