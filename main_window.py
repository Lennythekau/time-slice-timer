from PySide6 import QtGui
from PySide6 import QtWidgets

import app_info
from db.repository import Repository
from new_slice_form import NewSliceForm
from stats.todays_totals_table import TodaysTotalsTable
from stopwatch.controller import StopwatchController
from stopwatch.widget import StopwatchWidget
from time_slice import RunningTimeSlice
from time_slice_controller import TimeSliceController
from times_up_dialog import TimesUpDialog
from user_session import UserSession


class MainWindow(QtWidgets.QMainWindow):

    def __init__(
        self,
        user_session: UserSession,
        repo: Repository,
        stopwatch_controller: StopwatchController,
        time_slice_controller: TimeSliceController,
    ):
        super().__init__()

        self.__user_session = user_session
        self.__stopwatch_controller = stopwatch_controller
        self.__time_slice_controller = time_slice_controller
        self.__repo = repo

        self.__make_ui()

        QtGui.QShortcut(QtGui.QKeySequence("Alt+s"), self).activated.connect(
            self.__toggle_todays_totals_table
        )

        self.__user_session.stopwatch.finished += self.__on_stopwatch_finished
        self.__user_session.stopwatch.cancelled += self.__on_stopwatch_cancelled

    def __make_ui(self):
        self.setWindowTitle(app_info.APP_NAME)

        self.setCentralWidget(QtWidgets.QWidget())
        self.__layout = QtWidgets.QVBoxLayout(self.centralWidget())
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.__layout.setSpacing(0)

        self.__new_slice_form = NewSliceForm(self.__user_session, self.__repo)
        self.__new_slice_form.submitted.connect(self.__on_new_slice_form_submitted)

        self.__stopwatch_widget = StopwatchWidget(
            self.__user_session.stopwatch, self.__stopwatch_controller
        )
        self.__stopwatch_widget.setEnabled(False)

        self.__todays_totals_table = TodaysTotalsTable(self.__repo)

        self.__layout.addWidget(self.__new_slice_form)
        self.__layout.addWidget(self.__stopwatch_widget)
        self.__layout.addWidget(
            self.__todays_totals_table,
        )

        # self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)  # type: ignore
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

    def __toggle_todays_totals_table(self):
        self.__todays_totals_table.setVisible(
            not self.__todays_totals_table.isVisible()
        )

    def __update_widget_enabledness(self, is_timer_running: bool):
        self.__stopwatch_widget.setEnabled(is_timer_running)
        self.__new_slice_form.setEnabled(not is_timer_running)

    def __on_new_slice_form_submitted(self, slice: RunningTimeSlice):
        self.__time_slice_controller.start_slice(slice)
        self.__stopwatch_controller.start(slice)
        self.__update_widget_enabledness(True)

    def __on_stopwatch_cancelled(self, _):
        self.__update_widget_enabledness(False)

    def __on_stopwatch_finished(self, _):
        self.__time_slice_controller.on_slice_finished()
        self.__update_widget_enabledness(False)
        TimesUpDialog(self).open()
