from typing import NamedTuple
from dataclasses import dataclass, field

from tag.model import EMPTY_TAG, Tag


class TaskDraft(NamedTuple):
    parent: Task | None = field(repr=False, compare=False, default=None)
    description: str = ""
    tag: Tag = EMPTY_TAG
    index: int = -1


@dataclass
class Task:
    task_id: int
    parent: Task | None = field(repr=False, compare=False)
    description: str
    tag: Tag = EMPTY_TAG
    sub_tasks: list[Task] = field(default_factory=list, repr=False, compare=False)
