from typing import Callable, override

from PySide6 import QtGui
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QClipboard, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import QTreeView

from tag.delegate import TagDelegate
from tag.service import TagService
from task.adapter import TaskAdapter
from user_session import UserSession


class TasksView(QTreeView):
    def __init__(
        self,
        user_session: UserSession,
        tag_service: TagService,
        adapter: TaskAdapter,
    ):
        super().__init__()
        self.setAlternatingRowColors(True)

        self.__session = user_session

        self.setModel(adapter)
        self.__adapter = adapter

        self.__adapter.task_created.connect(self.__task_created)
        self.__adapter.task_inserted.connect(self.__task_inserted)

        self.setItemDelegateForColumn(1, TagDelegate(user_session, tag_service))

        # TODO: copying, undo/redo, find.

        # Movement
        sc = self.__add_shortcut
        scwi = self.__add_shortcut_with_index

        sc("j", self.__move_down)
        sc("k", self.__move_up)
        scwi("h", adapter.move_to_previous_process)
        scwi("l", adapter.move_to_next_process)
        scwi(";", adapter.move_to_parent)

        sc("y", self.__copy)
        scwi("w", adapter.shift_focus)

        sc("Space", self.__toggle_expandedness)

        # CRUD
        scwi("Shift+a", adapter.create_task)
        scwi("i", adapter.insert_subtask)
        sc("r", self.__start_edit)
        scwi("x", adapter.delete_task)

    @override
    def resizeEvent(self, event: QtGui.QResizeEvent, /) -> None:
        first_column_width = int(self.width() * 0.8)
        self.setColumnWidth(0, first_column_width)
        self.setColumnWidth(1, self.width() - first_column_width - 2)
        return super().resizeEvent(event)

    def select(self, index: QModelIndex):
        if index.isValid():
            self.setCurrentIndex(index)

    def __move_down(self):
        index = self.indexBelow(self.currentIndex())
        self.select(index)

    def __move_up(self):
        index = self.indexAbove(self.currentIndex())
        self.select(index)

    def __copy(self):
        index = self.currentIndex()
        task = self.__adapter.get_task_from_index(index)
        if task is not None:
            QGuiApplication.clipboard().setText(task.description)

    def __add_shortcut(self, sequence: str, callback: Callable[[], None]):
        key_sequence = QKeySequence(sequence)
        QShortcut(key_sequence, self).activated.connect(callback)

    def __add_shortcut_with_index(
        self, sequence: str, callback: Callable[[QModelIndex], QModelIndex | None]
    ):
        def curried():
            index = callback(self.currentIndex())
            if index and index.isValid():
                self.setCurrentIndex(index)

        self.__add_shortcut(sequence, curried)

    def __toggle_expandedness(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)

    def __start_edit(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        self.edit(index)

    def __task_created(self, index: QModelIndex):
        self.edit(index)

        self.setCurrentIndex(index)

    def __task_inserted(self, index: QModelIndex):
        self.expand(index.parent())
        self.edit(index)
