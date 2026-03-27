from db.sqlite_setup import create_connection_factory
from db.time_slice_repository import TimeSliceRepository
from timer_model import TimerModel
from stopwatch_controller import StopwatchController
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

    sqlite_connection = create_connection_factory(
        app_info.APP_ROOT / "data" / "time_slice.db"
    )
    time_slice_repo = TimeSliceRepository(sqlite_connection)

    window = MainWindow(settings, stopwatch_controller, time_slice_repo)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
