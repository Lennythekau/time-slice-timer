from typing import Callable
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QShortcut
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QTreeView

from task.adapter import TasksViewAdapter


class TasksView(QTreeView):
    def __init__(self, adapter: TasksViewAdapter):
        super().__init__()
        self.setModel(adapter)
        self.adapter = adapter

        self.adapter.created_task.connect(self.__task_created)
        self.adapter.inserted_task.connect(self.__task_inserted)

        # Movement
        self.__add_shortcut("j", adapter.move_down)
        self.__add_shortcut("k", adapter.move_up)
        self.__add_shortcut("h", adapter.move_previous_process)
        self.__add_shortcut("l", adapter.move_next_process)

        self.__add_shortcut("Space", self.__toggle_expandedness)

        # CRUD
        self.__add_shortcut("Shift+a", adapter.create_task)
        self.__add_shortcut("i", adapter.insert_subtask)
        self.__add_shortcut("r", self.__start_edit)

        self.__add_shortcut("x", adapter.delete_task)

    def __add_shortcut(self, sequence: str, callback: Callable[[], None]):
        key_sequence = QKeySequence(sequence)
        QShortcut(key_sequence, self).activated.connect(callback)

    def __toggle_expandedness(self):
        indices = self.selectedIndexes()
        if not indices:
            return
        index = indices[0]
        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)

    def __start_edit(self):
        indices = self.selectedIndexes()
        if not indices:
            return

        index = indices[0]
        self.edit(index)

    def __task_created(self, index: QModelIndex):
        self.edit(index)
        self.setCurrentIndex(index)

    def __task_inserted(self, index: QModelIndex):
        self.expand(index.parent())
        self.edit(index)
