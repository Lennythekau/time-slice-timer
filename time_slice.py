from typing import NamedTuple
from datetime import datetime


class RunningTimeSlice(NamedTuple):
    """
    A time slice that hasn't finished yet.
    """

    description: str
    tag: str
    duration: int


class TimeSlice(NamedTuple):
    """
    A time slice that has been finished, and thus has already been added to the database.
    """

    time_slice_id: int
    date: datetime
    description: str
    tag: str
    duration: int
