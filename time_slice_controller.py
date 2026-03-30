from db.repository import Repository
from time_slice import RunningTimeSlice
from user_session import UserSession


class TimeSliceController:
    def __init__(self, user_session: UserSession, repo: Repository):
        self.__user_session = user_session
        self.__repo = repo

    def start_slice(self, slice: RunningTimeSlice):
        seconds = slice.duration * 60
        self.__user_session.current_time_slice = slice
        self.__user_session.stopwatch.start(seconds)

    def on_slice_finished(self):
        slice = self.__user_session.current_time_slice
        assert slice is not None
        self.__repo.add_slice(slice)

        # Finished with current time slice, so now there is no current time slice.
        self.__user_session.current_time_slice = None
