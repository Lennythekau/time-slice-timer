from PySide6 import QtWidgets

from tag.service import TagService
from task.adapter import TaskAdapter
from task.view import TasksView
from user_session import UserSession


class TaskDialog(QtWidgets.QDialog):
    def __init__(
        self,
        user_session: UserSession,
        tag_service: TagService,
        task_adapter: TaskAdapter,
    ):
        super().__init__()

        self.__layout = QtWidgets.QVBoxLayout(self)

        self.__task_view = TasksView(user_session, tag_service, task_adapter)

        self.__layout.addWidget(self.__task_view)
        self.resize(650, 400)
