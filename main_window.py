from PySide6 import QtGui
from PySide6 import QtWidgets

import app_info
from db.time_slice_repository import TimeSliceRepository
from new_slice_form import NewSliceForm
from stopwatch import Stopwatch
from times_up_dialog import TimesUpDialog
from todays_totals_table import TodaysTotalsTable
from user_session import UserSession


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, user_session: UserSession, repo: TimeSliceRepository):
        super().__init__()

        self.__user_session = user_session
        self.__repo = repo

        self.__make_ui()

        QtGui.QShortcut(QtGui.QKeySequence("Alt+s"), self).activated.connect(
            self.__toggle_todays_totals_table
        )

        self.__user_session.timer.finished += self.__on_timer_finished

    def __make_ui(self):
        self.setWindowTitle(app_info.APP_NAME)

        self.setCentralWidget(QtWidgets.QWidget())
        self.__layout = QtWidgets.QVBoxLayout(self.centralWidget())
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.__layout.setSpacing(0)

        self.__new_slice_form = NewSliceForm(self.__user_session, self.__repo)

        self.__stopwatch = Stopwatch(self.__user_session, self.__repo)
        self.__stopwatch.setEnabled(False)

        self.__todays_totals_table = TodaysTotalsTable(self.__repo)

        self.__layout.addWidget(self.__new_slice_form)
        self.__layout.addWidget(self.__stopwatch)
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

    def __on_timer_finished(self, _):
        TimesUpDialog(self).open()
