from datetime import datetime
from typing import NamedTuple

from tag.model import Tag


class RunningTimeSlice(NamedTuple):
    """
    A time slice that hasn't finished yet.
    """

    description: str
    tag: Tag
    duration: int


class TimeSlice(NamedTuple):
    """
    A time slice that has been finished, and thus has already been added to the database.
    """

    time_slice_id: int
    date: datetime
    description: str
    tag: Tag
    duration: int

    def __hash__(self):
        return hash(self.time_slice_id)
