from collections.abc import Callable

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon
from PySide6.QtGui import Qt

import rc_icons

from .controller import StopwatchController
from .model import StopwatchModel


class StopwatchWidget(QtWidgets.QWidget):

    def __init__(
        self, stopwatch_model: StopwatchModel, stopwatch_controller: StopwatchController
    ):
        self.__TIMEOUT_INTERVAL = 250
        self.__INITIAL_TEXT = "unset"
        super().__init__()

        self.__make_ui()
        self.__poll_timer = QtCore.QTimer(timerType=Qt.TimerType.CoarseTimer)
        self.__poll_timer_connection: QtCore.QMetaObject.Connection | None = None

        self.__stopwatch_controller = stopwatch_controller
        self.__model = stopwatch_model

        self.__model.started += self.__on_start
        self.__model.paused += self.__on_pause
        self.__model.resumed += self.__on_resume
        self.__model.cancelled += self.__on_cancel
        self.__model.finished += self.__on_finish

    def __make_ui(self):
        self.__layout = QtWidgets.QVBoxLayout(self)

        self.__time_text = QtWidgets.QLabel(self.__INITIAL_TEXT)
        self.__time_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__controls_box = QtWidgets.QGroupBox()
        self.__controls_box_layout = QtWidgets.QHBoxLayout(self.__controls_box)
        # self.__controls_box_layout.setContentsMargins(0, 0, 0, 0)

        self.__play_icon = self.__create_control_icon("play")
        self.__pause_icon = self.__create_control_icon("pause")
        self.__cancel_icon = self.__create_control_icon("end")

        self.__play_pause_button = self.__control_button(
            self.__play_icon, self.__play_pause_button_clicked
        )
        self.__cancel_button = self.__control_button(
            self.__cancel_icon, self.__cancel_button_clicked
        )

        self.__layout.addWidget(self.__time_text)
        self.__layout.addWidget(self.__controls_box)

    def __create_control_icon(self, name: str):
        return QIcon(f":/assets/{name}.svg")

    def __control_button(self, icon: QIcon, slot: Callable):
        ICON_SIZE = 32
        button = QtWidgets.QPushButton()

        button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        button.clicked.connect(slot)
        button.setIcon(icon)
        self.__controls_box_layout.addWidget(button)
        return button

    def __on_start(self, seconds: int):
        self.__time_text.setText(self.__format_time(seconds))

        self.__poll_timer_connection = self.__poll_timer.timeout.connect(
            self.__on_poll_timer_timeout
        )
        self.__poll_timer.start(self.__TIMEOUT_INTERVAL)

        # Wait for next tick otherwise focus will still be stolen by the form.
        QtCore.QTimer().singleShot(0, self.__play_pause_button.setFocus)

    @QtCore.Slot()
    def __play_pause_button_clicked(self):
        self.__stopwatch_controller.toggle()

    @QtCore.Slot()
    def __on_resume(self, _):
        # show pause icon
        self.__play_pause_button.setIcon(self.__pause_icon)

        self.__poll_timer_connection = self.__poll_timer.timeout.connect(
            self.__on_poll_timer_timeout
        )
        self.__poll_timer.start(self.__TIMEOUT_INTERVAL)

    @QtCore.Slot()
    def __on_pause(self, _):
        # show play icon
        self.__play_pause_button.setIcon(self.__play_icon)

        self.__poll_timer.stop()

        assert self.__poll_timer_connection is not None
        self.__poll_timer.timeout.disconnect(self.__poll_timer_connection)
        self.__poll_timer_connection = None

    @QtCore.Slot()
    def __cancel_button_clicked(self, _):
        self.__stopwatch_controller.cancel()

    def __on_cancel(self, _):
        self.__poll_timer.stop()

        # Connection might be None, since we can cancel, while paused,
        # And when we pause, we set the connection to None (see above).
        if self.__poll_timer_connection is not None:
            self.__poll_timer.timeout.disconnect(self.__poll_timer_connection)
            self.__poll_timer_connection = None

    def __on_finish(self, _):
        self.__poll_timer.stop()
        if self.__poll_timer.isActive():
            self.__poll_timer.stop()
            assert self.__poll_timer_connection is not None
            self.__poll_timer.disconnect(self.__poll_timer_connection)
        self.__time_text.setText(self.__INITIAL_TEXT)

    @QtCore.Slot()
    def __on_poll_timer_timeout(self):
        seconds_left = round(self.__model.update_time())
        self.__time_text.setText(self.__format_time(seconds_left))

    def __format_time(self, seconds: int):
        return f"{seconds//60:02}:{seconds%60:02}"
