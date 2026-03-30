import sys

from PySide6 import QtWidgets

import app_info
from db.repository import Repository
from db.sqlite_setup import create_connection_factory, register_adapters
from main_window import MainWindow
from stopwatch.model import StopwatchModel
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

    timer_model = StopwatchModel()
    user_session = UserSession(timer_model)
    repo = make_repo()

    window = MainWindow(user_session, repo)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
