from typing import NamedTuple


class TimeSliceFormData(NamedTuple):
    description: str
    tag: str
    duration_minutes: int
