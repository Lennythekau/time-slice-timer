from typing import Any
from typing import override
from PySide6.QtCore import QAbstractListModel, QItemSelectionModel, QModelIndex
from PySide6.QtGui import Qt

from task.adapter import TaskAdapter
from task.model import Task


class FlattenedTaskAdapter(QAbstractListModel):
    def __init__(self, task_adapter: TaskAdapter) -> None:
        super().__init__()
        self.__task_tree = task_adapter
        self.__items = list[str]()
        self.__update()

    def __update(self):
        self.__items.clear()
        self.__dfs()

    def __dfs(self, index: QModelIndex = QModelIndex()):
        description = self.__task_tree.data(index)
        self.__items.append(description)

        for row in range(self.__task_tree.rowCount(index)):
            child_index = self.__task_tree.index(row, 0, index)
            self.__dfs(child_index)

    @override
    def rowCount(self, parent: Any = QModelIndex()):  # type: ignore[override]
        return len(self.__items)

    @override
    def data(self, index: QModelIndex, role):  # type: ignore[override]
        if role == Qt.ItemDataRole.DisplayRole:
            return self.__items[index.row()]
