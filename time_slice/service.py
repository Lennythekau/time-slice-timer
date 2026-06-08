from dataclasses import dataclass, field
from datetime import date

from lib.event import Event
from time_slice.model import RunningTimeSlice, TimeSlice
from time_slice.repo import TimeSliceRepo
from user_session import UserSession

# TODO: remove event listeners when we aren't listening


@dataclass
class TimeSliceService:
    __session: UserSession
    __repo: TimeSliceRepo

    time_slice_started: Event[RunningTimeSlice] = field(
        init=False, default_factory=Event
    )
    time_slice_paused: Event[None] = field(init=False, default_factory=Event)

    time_slice_cancelled: Event[RunningTimeSlice] = field(
        init=False, default_factory=Event
    )

    time_slice_finished: Event[TimeSlice] = field(init=False, default_factory=Event)

    def __post_init__(self):
        self.__session.stopwatch.paused += lambda _: self.pause_slice()
        self.__session.stopwatch.cancelled += lambda _: self.cancel_slice()
        self.__session.stopwatch.finished += lambda _: self.finish_slice()

    def start_slice(self, slice: RunningTimeSlice):
        # We've already started a time slice
        if self.__session.current_time_slice is not None:
            print("time slice already started")
            return

        seconds = slice.duration * 60
        self.__session.current_time_slice = slice

        self.__session.stopwatch.reset()
        self.__session.stopwatch.start(seconds)
        self.time_slice_started.invoke(slice)

    def pause_slice(self):
        if self.__session.current_time_slice is None:
            print("time slice doesn't exist")
            return

        self.time_slice_paused.invoke(None)

    def cancel_slice(self):
        if self.__session.current_time_slice is None:
            print("time slice already stopped")
            return

        self.time_slice_cancelled.invoke(self.__session.current_time_slice)

    def finish_slice(self):
        running_slice = self.__session.current_time_slice
        assert running_slice is not None
        time_slice = self.__repo.add_slice(running_slice)

        # Finished with current time slice, so now there is no current time slice.
        self.__session.current_time_slice = None

        self.time_slice_finished.invoke(time_slice)

    def get_times_by_tag(self):
        return self.__repo.get_times_by_tag(date.today())
