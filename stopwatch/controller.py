from time_slice.model import RunningTimeSlice

from .model import StopwatchModel


class StopwatchController:
    """Very light wrapper around `StopwatchModel`."""

    def __init__(self, stopwatch: StopwatchModel):
        self.__stopwatch = stopwatch

    def start(self, slice: RunningTimeSlice):
        seconds = slice.duration * 60
        self.__stopwatch.start(seconds)

    def pause(self):
        self.__stopwatch.pause()

    def resume(self):
        self.__stopwatch.resume()

    def cancel(self):
        self.__stopwatch.cancel()
