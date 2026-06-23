from typing import Any, override

from PySide6.QtCore import QAbstractListModel, QModelIndex
from PySide6.QtGui import Qt

from task.adapter import TaskAdapter
from task.model import Task
from task.service import TaskService
from user_session import UserSession


class FlattenedTaskAdapter(QAbstractListModel):
    def __init__(
        self,
        user_session: UserSession,
        task_service: TaskService,
    ) -> None:
        super().__init__()

        self.__task_service = task_service

        self.__tasks = list[Task]()
        self.descriptions = list[str]()
        self.__update()

        self.__task_service.tasks_changed += self.__update

    def __update(self):
        self.descriptions.clear()
        self.__tasks.clear()
        self.__dfs()

    def get_description(self, index: QModelIndex):
        return self.descriptions[index.row()]

    def get_task(self, index: QModelIndex):
        return self.descriptions[index.row()]

    def get_tag_name(self, index: QModelIndex) -> str:
        task: Task = self.__tasks[index.row()]
        return self.__task_service.get_tag(task).name

    def __dfs(self, task: Task | None = None):
        for child in self.__task_service.get_children(task):
            self.descriptions.append(child.description)
            self.__tasks.append(child)
            self.__dfs(child)

    @override
    def rowCount(self, parent: Any = QModelIndex()):  # type: ignore[override]
        return len(self.descriptions)

    @override
    def data(self, index: QModelIndex, role):  # type: ignore[override]
        if role == Qt.ItemDataRole.DisplayRole:
            return self.descriptions[index.row()]
