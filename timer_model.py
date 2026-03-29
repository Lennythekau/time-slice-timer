import time


class TimerModel:
    UNSET = -1

    def __init__(self):
        """
        Creates a new `TimerModel`.
        """
        self.__is_paused = True

    def reset(self, time_limit: int = UNSET):
        """
        :param time_limit: Time limit in seconds
        """
        self.__remaining_time: float = time_limit
        self.__is_paused = True
        self.__previous_start_time: float = TimerModel.UNSET

    def start(self, time_limit: int):
        """
        :param time_limit: Time limit in seconds
        """
        self.reset(time_limit)
        self.unpause()

    def pause(self):
        self.__is_paused = True
        time_spent = time.time() - self.__previous_start_time
        self.__remaining_time -= time_spent

    def unpause(self):
        self.__is_paused = False
        self.__previous_start_time = time.time()

    def get_remaining_time(self) -> float:
        if self.__is_paused:
            return self.__remaining_time

        time_spent = time.time() - self.__previous_start_time
        return self.__remaining_time - time_spent

    def is_finished(self):
        return self.get_remaining_time() <= 0
