from dataclasses import dataclass, field
from typing import NamedTuple

from tag.model import EMPTY_TAG, Tag


class TaskDraft(NamedTuple):
    parent: Task | None = None
    description: str = ""
    tag: Tag = EMPTY_TAG
    position: int = -1


@dataclass
class Task:
    task_id: int
    parent: Task | None = field(repr=False, compare=False)
    description: str
    tag: Tag = EMPTY_TAG
    sub_tasks: list[Task] = field(default_factory=list, repr=False, compare=False)
    position: int = 0
