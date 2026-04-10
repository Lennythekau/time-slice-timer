from tag.repo import TagRepo
from time_slice.repo import TimeSliceRepo
from PySide6.QtWidgets import QVBoxLayout
from stats.todays_totals_table import TodaysTotalsTable
from PySide6 import QtWidgets


class StatsDialog(QtWidgets.QDialog):
    def __init__(self, time_slice_repo: TimeSliceRepo, tag_repo: TagRepo):
        super().__init__()
        self.__layout = QVBoxLayout(self)
        self.__todays_totals_table = TodaysTotalsTable(time_slice_repo, tag_repo)
        self.__layout.addWidget(self.__todays_totals_table)
