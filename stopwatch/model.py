import time

from lib.event import Event


class StopwatchModel:
    UNSET = -1

    def __init__(self):
        """
        Creates a new `TimerModel`.
        """
        self.is_paused = True
        self.is_finished = False

        self.started = Event[int]()
        self.paused = Event[None]()
        self.resumed = Event[None]()

        self.finished = Event[None]()
        self.cancelled = Event[None]()

    def reset(self, time_limit: int = UNSET):
        """
        :param time_limit: Time limit in seconds
        """
        self.__remaining_time: float = time_limit
        self.is_paused = True
        self.is_finished = False
        self.__previous_start_time: float = StopwatchModel.UNSET

    def start(self, time_limit: int):
        """
        :param time_limit: Time limit in seconds
        """
        self.reset(time_limit)
        self.resume()

        self.started.invoke(time_limit)

    def pause(self):
        self.is_paused = True
        time_spent = time.time() - self.__previous_start_time
        self.__remaining_time -= time_spent

        self.paused.invoke(None)

    def resume(self):
        self.is_paused = False
        self.__previous_start_time = time.time()

        self.resumed.invoke(None)

    def cancel(self):
        self.reset()
        self.cancelled.invoke(None)

    def __get_remaining_time(self) -> float:
        if self.is_paused:
            return self.__remaining_time

        time_spent = time.time() - self.__previous_start_time
        time_left = self.__remaining_time - time_spent
        return time_left

    def update_time(self):

        time_left = self.__get_remaining_time()

        if self.is_finished:
            return 0

        if time_left <= 0:
            self.is_paused = True
            self.is_finished = True
            self.finished.invoke(None)

        return time_left
