from dataclasses import dataclass, field
from typing import ClassVar

from tag.model import Tag


@dataclass
class Task:
    UNSET_ID: ClassVar[int] = -1

    task_id: int
    parent: Task | None
    description: str
    tag: Tag | None = None
    sub_tasks: list[Task] = field(default_factory=list)

    def is_process(self):
        return self.parent is None
