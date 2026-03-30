from db.sqlite_setup import create_connection_factory, register_adapters
from db.time_slice_repository import TimeSliceRepository
from timer_model import TimerModel
import sys

from PySide6 import QtWidgets

import app_info
from main_window import MainWindow
from user_session import UserSession


def make_time_slice_repo():
    register_adapters()

    make_connection = create_connection_factory(
        app_info.APP_ROOT / "data" / "time_slice.db"
    )
    time_slice_repo = TimeSliceRepository(make_connection)
    time_slice_repo.ensure_tables_created()

    return time_slice_repo


def main() -> None:
    app = QtWidgets.QApplication([])
    app.setDesktopFileName(app_info.APP_ID)

    timer_model = TimerModel()
    user_session = UserSession(timer_model)
    time_slice_repo = make_time_slice_repo()

    window = MainWindow(user_session, time_slice_repo)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
