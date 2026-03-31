from time_slice.model import RunningTimeSlice
from stopwatch.model import StopwatchModel


class UserSession:
    def __init__(self, stopwatch: StopwatchModel):
        self.stopwatch = stopwatch
        self.current_time_slice: RunningTimeSlice | None = None
