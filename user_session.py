from time_slice import RunningTimeSlice
from stopwatch.model import StopwatchModel


class UserSession:
    def __init__(self, stopwatch: StopwatchModel):
        self.stopwatch = stopwatch
        self.__current_time_slice: RunningTimeSlice | None = None

    def start_time_slice(self, time_slice: RunningTimeSlice):
        self.__current_time_slice = time_slice

        # *60 because minutes to seconds.
        self.stopwatch.start(self.__current_time_slice.duration * 60)

    def get_time_slice(self):
        return self.__current_time_slice
