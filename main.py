from timer_model import TimerModel
from stopwatch_controller import StopwatchController
import random
import sys

from PySide6 import QtCore, QtGui, QtWidgets, __version__

import app_info
from main_window import MainWindow
from settings import get_settings_or_defaults


def main() -> None:
    app = QtWidgets.QApplication([])
    app.setDesktopFileName(app_info.APP_ID)

    settings = get_settings_or_defaults(app_info.APP_ROOT / "data" / "settings.toml")

    timer_model = TimerModel()
    stopwatch_controller = StopwatchController(timer_model)

    window = MainWindow(settings, stopwatch_controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
