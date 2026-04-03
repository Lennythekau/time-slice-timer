from typing import Any
from typing import override
from PySide6.QtCore import QAbstractListModel, QModelIndex
from PySide6.QtGui import Qt

from task.adapter import TaskAdapter
from task.model import Task
from task.repo import TaskRepo


class FlattenedTaskAdapter(QAbstractListModel):
    def __init__(self, task_repo: TaskRepo, task_adapter: TaskAdapter) -> None:
        super().__init__()
        self.__task_tree = task_adapter
        self.__tasks = list[Task]()
        self.descriptions = list[str]()
        self.__update()

        task_repo.tasks_changed += lambda _: self.__update()

    def __update(self):
        self.descriptions.clear()
        self.__tasks.clear()
        self.__dfs()

    def get_tag_name(self, index: QModelIndex):
        task: Task = self.__tasks[index.row()]
        print(index.row(), index.column())
        while not task.is_process():
            assert task.parent is not None
            task = task.parent
        print(task.tag.name)
        return task.tag.name

    def __dfs(self, index: QModelIndex = QModelIndex()):
        for row in range(self.__task_tree.rowCount(index)):
            child_index = self.__task_tree.index(row, 0, index)

            task: Task = child_index.internalPointer()
            self.descriptions.append(task.description)
            self.__tasks.append(task)
            self.__dfs(child_index)

    @override
    def rowCount(self, parent: Any = QModelIndex()):  # type: ignore[override]
        return len(self.descriptions)

    @override
    def data(self, index: QModelIndex, role):  # type: ignore[override]
        if role == Qt.ItemDataRole.DisplayRole:
            return self.descriptions[index.row()]
