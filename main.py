import sys

from PySide6 import QtWidgets

import app_info
from sqlite_setup import (
    create_connection_factory,
    ensure_tables_created,
    register_adapters,
)
from tag.repo import TagRepo
from tag.service import TagService
from task.adapter import TaskAdapter
from task.flattened_adapter import FlattenedTaskAdapter
from task.repo import TaskRepo
from task.service import TaskService
from time_slice.form import NewSliceForm
from time_slice.main_window import TimeSliceWindow
from time_slice.repo import TimeSliceRepo
from time_slice.service import TimeSliceService
from time_slice.stopwatch.model import Stopwatch
from time_slice.stopwatch.widget import StopwatchWidget
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
    stopwatch_model = Stopwatch()
    user_session = UserSession(stopwatch_model)

    # Data
    register_adapters()
    time_slice_repo, tag_repo, task_repo = make_repos()

    # services
    time_slice_service = TimeSliceService(user_session, time_slice_repo)
    tag_service = TagService(user_session, tag_repo)
    task_service = TaskService(user_session, task_repo)
    task_adapter = TaskAdapter(user_session, task_service)
    flattened_adapter = FlattenedTaskAdapter(user_session, task_service, task_adapter)

    # Views
    new_slice_form = NewSliceForm(
        user_session, time_slice_service, tag_service, flattened_adapter
    )
    stopwatch_widget = StopwatchWidget(user_session)

    window = TimeSliceWindow(
        user_session,
        time_slice_service,
        tag_service,
        task_adapter,
        new_slice_form,
        stopwatch_widget,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
