from dataclasses import dataclass, field
from datetime import date

from lib.event import Event, Event0
from time_slice.model import RunningTimeSlice
from time_slice.repo import TimeSliceRepo
from user_session import UserSession


@dataclass
class TimeSliceService:
    __session: UserSession
    __repo: TimeSliceRepo

    slice_started: Event[RunningTimeSlice] = field(
        init=False, default_factory=Event[RunningTimeSlice]
    )
    slice_paused: Event0 = field(init=False, default_factory=Event0)
    slice_cancelled: Event0 = field(init=False, default_factory=Event0)
    slice_finished: Event0 = field(init=False, default_factory=Event0)

    def __post_init__(self):
        self.__session.stopwatch.paused += self.pause_slice
        self.__session.stopwatch.cancelled += self.cancel_slice
        self.__session.stopwatch.finished += self.finish_slice

    def start_slice(self, slice: RunningTimeSlice):
        # We've already started a time slice
        if self.__session.current_time_slice is not None:
            print("time slice already started")
            return

        seconds = slice.duration * 60
        self.__session.current_time_slice = slice

        self.__session.stopwatch.reset()
        self.__session.stopwatch.start(seconds)

        self.slice_started(slice)

    def pause_slice(self):
        if self.__session.current_time_slice is None:
            print("time slice doesn't exist")
            return

        # We don't need to pause the stopwatch, it's already paused.
        self.slice_paused()

    def cancel_slice(self):
        if self.__session.current_time_slice is None:
            print("time slice already stopped")
            return

        self.__session.current_time_slice = None
        self.slice_cancelled()

    def finish_slice(self):

        # this will happen because we don't remove the event listeners yet...
        if self.__session.current_time_slice is None:
            print("time slice doesn't exist")
            return

        running_slice = self.__session.current_time_slice
        self.__repo.add_slice(running_slice)

        # Finished with current time slice, so now there is no current time slice.
        self.__session.current_time_slice = None

        self.slice_finished()

    def get_times_by_tag(self):
        return self.__repo.get_times_by_tag(date.today())

    def get_total_time(self):
        return self.__repo.get_total_time(date.today())
