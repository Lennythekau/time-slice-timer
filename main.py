import sys

from PySide6 import QtWidgets

import app_info
from db.repository import Repository
from db.sqlite_setup import create_connection_factory, register_adapters
from main_window import MainWindow
from stopwatch.controller import StopwatchController
from stopwatch.model import StopwatchModel
from time_slice_controller import TimeSliceController
from user_session import UserSession


def make_repo():
    register_adapters()

    make_connection = create_connection_factory(
        app_info.APP_ROOT / "data" / "time_slice.db"
    )
    repo = Repository(make_connection)
    repo.ensure_tables_created()

    return repo


def main() -> None:
    app = QtWidgets.QApplication([])
    app.setDesktopFileName(app_info.APP_ID)

    # Models
    stopwatch_model = StopwatchModel()
    user_session = UserSession(stopwatch_model)
    repo = make_repo()

    # Controllers
    stopwatch_controller = StopwatchController(stopwatch_model)
    time_slice_controller = TimeSliceController(user_session, repo)

    window = MainWindow(user_session, repo, stopwatch_controller, time_slice_controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
