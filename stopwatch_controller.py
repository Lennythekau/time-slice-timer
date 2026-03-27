from timer_model import TimerModel


class StopwatchController:
    def __init__(self, timer_model: TimerModel):
        self.__timer_model = timer_model

    def start(self, duration: int):
        self.__timer_model.start(duration)

    def unpause(self):
        self.__timer_model.unpause()

    def pause(self):
        self.__timer_model.pause()

    def cancel(self):
        self.__timer_model.reset()

    def get_remaining_time(self):
        return self.__timer_model.get_remaining_time()
