from collections.abc import Callable
from PySide6.QtGui import QIcon
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import Qt

import rc_icons
from stopwatch.controller import StopwatchController
from stopwatch.model import StopwatchModel


class StopwatchWidget(QtWidgets.QWidget):

    def __init__(
        self, stopwatch_model: StopwatchModel, stopwatch_controller: StopwatchController
    ):
        self.__TIMEOUT_INTERVAL = 250
        self.__INITIAL_TEXT = "unset"
        super().__init__()

        self.__make_ui()
        self.__poll_timer = QtCore.QTimer(timerType=Qt.TimerType.VeryCoarseTimer)
        self.__poll_timer_connection: QtCore.QMetaObject.Connection | None = None

        self.__stopwatch_controller = stopwatch_controller
        self.__model = stopwatch_model
        self.__model.started += self.__on_timer_start
        self.__model.finished += self.__on_timer_finish

    def __make_ui(self):
        self.__layout = QtWidgets.QVBoxLayout(self)

        self.__time_text = QtWidgets.QLabel(self.__INITIAL_TEXT)
        self.__time_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__controls_box = QtWidgets.QGroupBox()
        self.__controls_box_layout = QtWidgets.QHBoxLayout(self.__controls_box)
        # self.__controls_box_layout.setContentsMargins(0, 0, 0, 0)

        self.__play_button = self.__control_button("play", self.__resume)
        self.__pause_button = self.__control_button("pause", self.__pause)
        self.__cancel_button = self.__control_button("end", self.__cancel)

        self.__layout.addWidget(self.__time_text)
        self.__layout.addWidget(self.__controls_box)

    def __control_button(self, name: str, slot: Callable):
        icon = QIcon(f":/assets/{name}.svg")
        ICON_SIZE = 32
        button = QtWidgets.QPushButton()

        button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        button.clicked.connect(slot)
        button.setIcon(icon)
        self.__controls_box_layout.addWidget(button)
        return button

    def __on_timer_start(self, seconds: int):
        self.__time_text.setText(self.__format_time(seconds))

        self.__play_button.setEnabled(False)
        self.__pause_button.setEnabled(True)
        self.__cancel_button.setEnabled(True)

        self.__poll_timer_connection = self.__poll_timer.timeout.connect(
            self.__on_poll_timer_timeout
        )
        self.__poll_timer.start(self.__TIMEOUT_INTERVAL)

    @QtCore.Slot()
    def __resume(self):
        self.__play_button.setEnabled(False)
        self.__pause_button.setEnabled(True)
        self.__cancel_button.setEnabled(True)

        self.__poll_timer_connection = self.__poll_timer.timeout.connect(
            self.__on_poll_timer_timeout
        )
        self.__poll_timer.start(self.__TIMEOUT_INTERVAL)
        self.__stopwatch_controller.resume()

    @QtCore.Slot()
    def __pause(self):
        self.__play_button.setEnabled(True)
        self.__pause_button.setEnabled(False)
        self.__cancel_button.setEnabled(True)

        self.__poll_timer.stop()

        assert self.__poll_timer_connection is not None
        self.__poll_timer.timeout.disconnect(self.__poll_timer_connection)
        self.__poll_timer_connection = None

        self.__stopwatch_controller.pause()

    @QtCore.Slot()
    def __cancel(self, _):
        self.__poll_timer.stop()

        # Connection might be None, since we can cancel, while paused,
        # And when we pause, we set the connection to None (see above).
        if self.__poll_timer_connection is not None:
            self.__poll_timer.timeout.disconnect(self.__poll_timer_connection)
            self.__poll_timer_connection = None

        self.__stopwatch_controller.cancel()

    def __on_timer_finish(self, _):
        if self.__poll_timer.isActive():
            self.__poll_timer.stop()
        self.__time_text.setText(self.__INITIAL_TEXT)

    @QtCore.Slot()
    def __on_poll_timer_timeout(self):
        seconds_left = round(self.__model.update_time())
        self.__time_text.setText(self.__format_time(seconds_left))

    def __format_time(self, seconds: int):
        return f"{seconds//60:02}:{seconds%60:02}"
