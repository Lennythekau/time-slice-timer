import sys

from PySide6 import QtWidgets

import app_info
from sqlite_setup import (
    create_connection_factory,
    ensure_tables_created,
    register_adapters,
)
from stopwatch.controller import StopwatchController
from stopwatch.model import StopwatchModel
from tag.controller import TagController
from tag.repo import TagRepo
from task.repo import TaskRepo
from time_slice.controller import TimeSliceController
from time_slice.main_window import TimeSliceWindow
from time_slice.repo import TimeSliceRepo
from user_session import UserSession


def make_repos():
    make_connection = create_connection_factory(
        app_info.APP_ROOT / "data" / "time_slice.db"
    )

    ensure_tables_created(make_connection)
    time_slice_repo = TimeSliceRepo(make_connection)
    tag_repo = TagRepo(make_connection)
    task_repo = TaskRepo(make_connection)

    return time_slice_repo, tag_repo, task_repo


def main() -> None:
    app = QtWidgets.QApplication([])
    app.setDesktopFileName(app_info.APP_ID)

    # Models
    stopwatch_model = StopwatchModel()
    user_session = UserSession(stopwatch_model)

    # Data
    register_adapters()
    time_slice_repo, tag_repo, task_repo = make_repos()

    # Controllers
    stopwatch_controller = StopwatchController(stopwatch_model)
    time_slice_controller = TimeSliceController(user_session, time_slice_repo)
    tag_view_controller = TagController(tag_repo)

    window = TimeSliceWindow(
        user_session,
        time_slice_repo,
        tag_repo,
        task_repo,
        stopwatch_controller,
        time_slice_controller,
        tag_view_controller,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
