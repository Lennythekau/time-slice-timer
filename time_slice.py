from typing import NamedTuple
from datetime import datetime


class TimeSlice(NamedTuple):
    time_slice_id: int
    date: datetime
    description: str
    tag: str
    duration: int
