from db.sqlite_setup import create_connection_factory
from db.time_slice_repository import TimeSliceRepository
from time_slice_controller import TimeSliceController
from timer_model import TimerModel
from stopwatch_controller import StopwatchController
import sys

from PySide6 import QtWidgets

import app_info
from main_window import MainWindow
from settings import get_settings_or_defaults
from user_session import UserSession


def make_time_slice_repo():
    make_connection = create_connection_factory(
        app_info.APP_ROOT / "data" / "time_slice.db"
    )
    time_slice_repo = TimeSliceRepository(make_connection)
    time_slice_repo.ensure_table_created()

    return time_slice_repo


def main() -> None:
    app = QtWidgets.QApplication([])
    app.setDesktopFileName(app_info.APP_ID)

    settings = get_settings_or_defaults(app_info.APP_ROOT / "data" / "settings.toml")
    timer_model = TimerModel()
    user_session = UserSession(timer_model, settings)
    time_slice_repo = make_time_slice_repo()

    time_slice_controller = TimeSliceController(user_session, time_slice_repo)
    stopwatch_controller = StopwatchController(timer_model)

    window = MainWindow(time_slice_controller, stopwatch_controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
