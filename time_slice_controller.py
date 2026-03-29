from typing import TYPE_CHECKING

from db.time_slice_repository import TimeSliceRepository
from time_slice import RunningTimeSlice
from user_session import UserSession

# We just need this for the type hint, without this if check, we would have a circular dependency.
if TYPE_CHECKING:
    from new_slice_form import NewSliceForm


class TimeSliceController:
    def __init__(self, user_session: UserSession, repo: TimeSliceRepository):
        self.__user_session = user_session
        self.__repo = repo

    def start_time_slice(self, form_data: NewSliceForm.Data):
        time_slice = RunningTimeSlice(
            description=form_data.description,
            tag=form_data.tag,
            duration=form_data.duration,
        )

        self.__user_session.start_time_slice(time_slice)

    def get_tag_names(self):
        return self.__user_session.settings["tag_names"]

    def finish_time_slice(self):
        time_slice = self.__user_session.get_current_time_slice()
        assert time_slice is not None
        self.__repo.add(*time_slice)

    def get_todays_totals(self):
        totals = {tag: 0 for tag in self.__user_session.settings["tag_names"]}

        for tag, total in self.__repo.get_times_by_tag():
            totals[tag] = total

        return totals
