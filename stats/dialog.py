from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

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
        self.__time_slice_service = time_slice_service

        self.__layout = QVBoxLayout(self)
        self.__todays_totals_table = TodaysTotalsTable(
            user_session, tag_service, time_slice_service
        )
        self.__total_time = QLabel()
        self.__update_total_time()
        time_slice_service.slice_finished += self.__update_total_time

        self.__layout.addWidget(self.__todays_totals_table)
        self.__layout.addWidget(
            self.__total_time, alignment=Qt.AlignmentFlag.AlignCenter
        )

    def __update_total_time(self):
        total = self.__time_slice_service.get_total_time()
        self.__total_time.setText(f"{total} minutes")
