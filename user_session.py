from settings import Settings
from time_slice import RunningTimeSlice
from timer_model import TimerModel


class UserSession:
    def __init__(self, timer: TimerModel, settings: Settings):
        self.timer = timer
        self.settings = settings
        self.__current_time_slice: RunningTimeSlice | None = None

    def start_time_slice(self, time_slice: RunningTimeSlice):
        self.__current_time_slice = time_slice

        # *60 because minutes to seconds.
        self.timer.start(self.__current_time_slice.duration * 60)

    def get_current_time_slice(self):
        return self.__current_time_slice
