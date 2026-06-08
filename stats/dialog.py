from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout

from stats.todays_totals_table import TodaysTotalsTable
from tag.service import TagService
from time_slice.service import TimeSliceService
from user_session import UserSession


class StatsDialog(QtWidgets.QDialog):
    def __init__(
        self,
        user_session: UserSession,
        tag_service: TagService,
        time_slice_service: TimeSliceService,
    ):
        super().__init__()
        self.__layout = QVBoxLayout(self)
        self.__todays_totals_table = TodaysTotalsTable(
            user_session, tag_service, time_slice_service
        )
        self.__layout.addWidget(self.__todays_totals_table)
