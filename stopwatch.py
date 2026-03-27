from collections.abc import Callable
from PySide6.QtGui import QIcon
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import Qt

from stopwatch_controller import StopwatchController
import rc_icons


class Stopwatch(QtWidgets.QWidget):
    started = QtCore.Signal()
    cancelled = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self, stopwatch_controller: StopwatchController):
        super().__init__()
        self.__controller = stopwatch_controller

        self.__layout = QtWidgets.QVBoxLayout(self)

        self.__time_text = QtWidgets.QLabel("unset")
        self.__time_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__time_text.setEnabled(False)

        self.__controls_box = QtWidgets.QGroupBox()
        self.__controls_box_layout = QtWidgets.QHBoxLayout(self.__controls_box)

        self.__play_button = self.__control_button("play", self.__resume)
        self.__pause_button = self.__control_button("pause", self.__pause)
        self.__cancel_button = self.__control_button("end", self.__cancel)

        self.__layout.addWidget(self.__time_text)
        self.__layout.addWidget(self.__controls_box)

        self.__timer = QtCore.QTimer(timerType=Qt.TimerType.VeryCoarseTimer)

    def __control_button(self, name: str, slot: Callable):
        icon = QIcon(f":/assets/{name}.svg")
        ICON_SIZE = 32
        button = QtWidgets.QPushButton()

        button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        button.clicked.connect(slot)
        button.setIcon(icon)
        self.__controls_box_layout.addWidget(button)
        return button

    def start(self, duration_minutes: int):
        self.started.emit()

        seconds = duration_minutes * 60
        self.__controller.start(seconds)

        self.__time_text.setEnabled(True)
        self.__time_text.setText(self.__format_time(seconds))

        self.__play_button.setEnabled(False)
        self.__pause_button.setEnabled(True)
        self.__cancel_button.setEnabled(True)

        self.__timer.timeout.connect(self.__on_timer_timeout)
        self.__timer.start(250)

    @QtCore.Slot()
    def __resume(self):
        self.__controller.unpause()

        self.__play_button.setEnabled(False)
        self.__pause_button.setEnabled(True)
        self.__cancel_button.setEnabled(True)

        self.__timer.timeout.connect(self.__on_timer_timeout)
        self.__timer.start(250)

    @QtCore.Slot()
    def __pause(self):
        self.__controller.pause()

        self.__play_button.setEnabled(True)
        self.__pause_button.setEnabled(False)
        self.__cancel_button.setEnabled(True)

        self.__timer.stop()

    @QtCore.Slot()
    def __cancel(self):
        self.cancelled.emit()
        self.__controller.cancel()
        self.__timer.stop()

    @QtCore.Slot()
    def __on_timer_timeout(self):
        seconds_left = round(self.__controller.get_remaining_time())
        self.__time_text.setText(self.__format_time(seconds_left))

    def __format_time(self, seconds: int):
        return f"{seconds//60:02}:{seconds%60:02}"
