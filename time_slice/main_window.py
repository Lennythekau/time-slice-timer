from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Slot

import app_info
from stats.dialog import StatsDialog
from tag.dialog import TagDialog
from tag.service import TagService
from task.adapter import TaskAdapter
from task.dialog import TaskDialog
from time_slice.form import NewSliceForm
from time_slice.service import TimeSliceService
from time_slice.stopwatch.widget import StopwatchWidget
from time_slice.times_up_dialog import TimesUpDialog
from user_session import UserSession


class TimeSliceWindow(QtWidgets.QMainWindow):

    def __init__(
        self,
        user_session: UserSession,
        time_slice_service: TimeSliceService,
        tag_service: TagService,
        task_adapter: TaskAdapter,
        new_slice_form: NewSliceForm,
        stopwatch_widget: StopwatchWidget,
    ):
        super().__init__()

        self.__session = user_session
        self.__time_slice_service = time_slice_service
        self.__tag_service = tag_service
        self.__task_adapter = task_adapter
        self.__new_slice_form = new_slice_form
        self.__stopwatch_widget = stopwatch_widget

        self.__make_ui()

        QtGui.QShortcut(QtGui.QKeySequence("Alt+s"), self).activated.connect(
            self.__show_stats_dialog
        )
        QtGui.QShortcut(QtGui.QKeySequence("Alt+t"), self).activated.connect(
            self.__show_tag_dialog
        )
        QtGui.QShortcut(QtGui.QKeySequence("Alt+k"), self).activated.connect(
            self.__show_task_dialog
        )

        self.__time_slice_service.slice_finished += self.__on_time_slice_finished

    def __make_ui(self):
        self.setWindowTitle(app_info.APP_NAME)

        # Maybe should be refactored?
        self.__tag_dialog: TagDialog | None = None
        self.__task_dialog: TaskDialog | None = None
        self.__stats_dialog: StatsDialog | None = None

        self.setCentralWidget(QtWidgets.QWidget())
        self.__layout = QtWidgets.QVBoxLayout(self.centralWidget())
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.__layout.setSpacing(0)

        self.__stopwatch_widget.setEnabled(
            self.__session.current_time_slice is not None
        )

        self.__layout.addWidget(self.__new_slice_form)
        self.__layout.addWidget(self.__stopwatch_widget)

        self.__make_toolbar()

        # self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)  # type: ignore
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

    @Slot()
    def __show_tag_dialog(self):
        if self.__tag_dialog is None:
            self.__tag_dialog = TagDialog(self.__session, self.__tag_service)
        self.__tag_dialog.open()

    @Slot()
    def __show_task_dialog(self):
        if self.__task_dialog is None:
            self.__task_dialog = TaskDialog(
                self.__session, self.__tag_service, self.__task_adapter
            )
        self.__task_dialog.open()

    @Slot()
    def __show_stats_dialog(self):
        if self.__stats_dialog is None:
            self.__stats_dialog = StatsDialog(
                self.__session, self.__tag_service, self.__time_slice_service
            )
        self.__stats_dialog.open()

    def __make_toolbar(self):
        self.__toolbar = self.addToolBar("Toolbar!")
        self.__toolbar.setMovable(False)  # moving this toolbar would just be silly.

        tag_action = QtGui.QAction("Tags", self.__toolbar)
        tag_action.triggered.connect(self.__show_tag_dialog)
        self.__toolbar.addAction(tag_action)

        task_action = QtGui.QAction("Tasks", self.__toolbar)
        task_action.triggered.connect(self.__show_task_dialog)
        self.__toolbar.addAction(task_action)

        stats_action = QtGui.QAction("Stats", self.__toolbar)
        stats_action.triggered.connect(self.__show_stats_dialog)
        self.__toolbar.addAction(stats_action)

    def __on_time_slice_finished(self):
        TimesUpDialog(self).open()
