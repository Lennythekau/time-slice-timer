from dataclasses import dataclass, field

from tag.model import Tag
from task.model import Task
from time_slice.model import RunningTimeSlice
from time_slice.stopwatch.model import Stopwatch


@dataclass
class UserSession:
    stopwatch: Stopwatch
    current_time_slice: RunningTimeSlice | None = None

    tags: dict[int, Tag] = field(default_factory=dict)
    processes: list[Task] = field(default_factory=list)
