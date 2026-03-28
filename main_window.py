from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import Slot

import app_info
from db.time_slice_repository import TimeSliceRepository
from new_slice_form import NewSliceForm
from settings import Settings
from stopwatch import Stopwatch
from stopwatch_controller import StopwatchController
from times_up_dialog import TimesUpDialog
from todays_totals_table import TodaysTotalsTable


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        settings: Settings,
        stopwatch_controller: StopwatchController,
        time_slice_repo: TimeSliceRepository,
    ):
        super().__init__()

        self.settings = settings
        self.repo = time_slice_repo

        self.setWindowTitle(app_info.APP_NAME)

        self.setCentralWidget(QtWidgets.QWidget())
        self.__layout = QtWidgets.QVBoxLayout(self.centralWidget())
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.__layout.setSpacing(0)

        self.__new_slice_form = NewSliceForm(settings)
        self.__new_slice_form.submitted.connect(self.__on_new_slice_form_submitted)

        self.__stopwatch = Stopwatch(stopwatch_controller)
        self.__stopwatch.setEnabled(False)

        self.__stopwatch.started.connect(self.__on_stopwatch_started)
        self.__stopwatch.cancelled.connect(self.__on_stopwatch_cancelled)
        self.__stopwatch.finished.connect(self.__on_stopwatch_finished)

        self.__todays_totals_table = TodaysTotalsTable()
        self.__todays_totals_table.update_times(self.__get_todays_totals())

        self.__layout.addWidget(self.__new_slice_form)
        self.__layout.addWidget(self.__stopwatch)
        self.__layout.addWidget(
            self.__todays_totals_table,
        )

        # self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)  # type: ignore
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

        QtGui.QShortcut(QtGui.QKeySequence("Alt+s"), self).activated.connect(
            self.__toggle_todays_totals_table
        )

    def __toggle_todays_totals_table(self):
        self.__todays_totals_table.setVisible(
            not self.__todays_totals_table.isVisible()
        )

    def __get_todays_totals(self):
        totals = {tag: 0 for tag in self.settings["tag_names"]}

        for tag, total in self.repo.get_times_by_tag():
            totals[tag] = total

        return totals

    def __on_new_slice_form_submitted(self, data: NewSliceForm.Data):
        self.__stopwatch.setEnabled(True)
        self.form_data = data
        self.__stopwatch.start(data.duration)

    @Slot()
    def __on_stopwatch_started(self):
        self.__new_slice_form.setEnabled(False)

    @Slot()
    def __on_stopwatch_cancelled(self):
        self.__new_slice_form.setEnabled(True)
        self.__stopwatch.setEnabled(False)

    @Slot()
    def __on_stopwatch_finished(self):
        self.__new_slice_form.setEnabled(True)
        self.__stopwatch.setEnabled(False)
        self.repo.add(*self.form_data)
        self.__todays_totals_table.update_times(self.__get_todays_totals())

        TimesUpDialog(self).open()
