from task.repo import TaskRepo
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import Slot

import app_info
from stats.todays_totals_table import TodaysTotalsTable
from stopwatch.controller import StopwatchController
from stopwatch.widget import StopwatchWidget
from tag.controller import TagController
from tag.dialog import TagDialog
from tag.repo import TagRepo
from task.dialog import TasksDialog
from user_session import UserSession

from .controller import TimeSliceController
from .form import NewSliceForm
from .model import RunningTimeSlice
from .repo import TimeSliceRepo
from .times_up_dialog import TimesUpDialog


class TimeSliceWindow(QtWidgets.QMainWindow):

    def __init__(
        self,
        user_session: UserSession,
        time_slice_repo: TimeSliceRepo,
        tag_repo: TagRepo,
        task_repo: TaskRepo,
        stopwatch_controller: StopwatchController,
        time_slice_controller: TimeSliceController,
        tag_view_controller: TagController,
    ):
        super().__init__()

        self.__user_session = user_session
        self.__stopwatch_controller = stopwatch_controller
        self.__time_slice_controller = time_slice_controller
        self.__tag_controller = tag_view_controller
        self.__time_slice_repo = time_slice_repo
        self.__tag_repo = tag_repo
        self.__task_repo = task_repo

        self.__make_ui()

        QtGui.QShortcut(QtGui.QKeySequence("Alt+s"), self).activated.connect(
            self.__toggle_todays_totals_table
        )
        QtGui.QShortcut(QtGui.QKeySequence("Alt+t"), self).activated.connect(
            self.__show_tag_dialog
        )
        QtGui.QShortcut(QtGui.QKeySequence("Alt+k"), self).activated.connect(
            self.__show_task_dialog
        )

        self.__user_session.stopwatch.finished += self.__on_stopwatch_finished
        self.__user_session.stopwatch.cancelled += self.__on_stopwatch_cancelled

    def __make_ui(self):
        self.setWindowTitle(app_info.APP_NAME)

        self.__tag_dialog: TagDialog | None = None
        self.__tasks_dialog: TasksDialog | None = None

        self.setCentralWidget(QtWidgets.QWidget())
        self.__layout = QtWidgets.QVBoxLayout(self.centralWidget())
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.__layout.setSpacing(0)

        self.__new_slice_form = NewSliceForm(self.__user_session, self.__tag_repo)
        self.__new_slice_form.submitted.connect(self.__on_new_slice_form_submitted)

        self.__stopwatch_widget = StopwatchWidget(
            self.__user_session.stopwatch, self.__stopwatch_controller
        )
        self.__stopwatch_widget.setEnabled(False)

        self.__todays_totals_table = TodaysTotalsTable(
            self.__time_slice_repo, self.__tag_repo
        )

        self.__layout.addWidget(self.__new_slice_form)
        self.__layout.addWidget(self.__stopwatch_widget)
        self.__layout.addWidget(
            self.__todays_totals_table,
        )

        self.__make_toolbar()

        # self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)  # type: ignore
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

    @Slot()
    def __show_tag_dialog(self):
        if self.__tag_dialog is None:
            self.__tag_dialog = TagDialog(self.__tag_repo, self.__tag_controller)
        self.__tag_dialog.show()

    @Slot()
    def __show_task_dialog(self):
        if self.__tasks_dialog is None:
            self.__tasks_dialog = TasksDialog(self.__task_repo)
        self.__tasks_dialog.show()

    def __make_toolbar(self):
        self.__toolbar = self.addToolBar("Toolbar!")
        self.__toolbar.setMovable(False)  # moving this toolbar would just be silly.

        tag_action = QtGui.QAction("Tags", self.__toolbar)
        tag_action.triggered.connect(self.__show_tag_dialog)
        self.__toolbar.addAction(tag_action)

        task_action = QtGui.QAction("Tasks", self.__toolbar)
        task_action.triggered.connect(self.__show_task_dialog)
        self.__toolbar.addAction(task_action)

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
