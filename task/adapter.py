from task.model import TaskDraft
from task.controller import TaskController
from typing import Any, cast, override

from PySide6.QtCore import (
    QAbstractItemModel,
    QItemSelectionModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
)

from .model import Task

type Index = QModelIndex | QPersistentModelIndex


class TaskAdapter(QAbstractItemModel):
    task_created = Signal(QModelIndex)
    task_inserted = Signal(QModelIndex)

    def __init__(self, task_controller: TaskController):
        super().__init__()
        self.__task_controller = task_controller

    def set_selection_model(self, selection_model: QItemSelectionModel):
        self.__selection_model = selection_model

    def __select(self, index: QModelIndex):
        self.__selection_model.setCurrentIndex(
            index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

    def __try_move_to_first(self):
        if self.__task_controller.processes:
            index = self.index(0, 0, QModelIndex())
            self.__select(index)
            return True
        return False

    def __try_move_into_subtree(self, current_index: QModelIndex):
        task: Task = current_index.internalPointer()
        if task.sub_tasks:
            new_index = self.index(0, 0, current_index)
            self.__select(new_index)
            return True

        return False

    def __try_move_to_preorder_successor(self, current_index):
        # If current index is invalid => no sibling at all.
        while current_index.isValid():
            parent_index = current_index.parent()
            candidate_row = current_index.row() + 1

            if candidate_row < self.rowCount(parent_index):
                new_index = self.index(candidate_row, 0, parent_index)
                self.__select(new_index)
                return True

            current_index = current_index.parent()
        return False

    def __try_move_out_of_subtree(self, current_index: QModelIndex):
        if current_index.row() != 0:
            return False
        parent_index = current_index.parent()

        if not parent_index.isValid():
            return False

        self.__select(parent_index)
        return True

    def __try_move_to_preorder_predecessor(self, current_index: QModelIndex):
        # If current index is invalid => no sibling at all.
        new_index = None
        while current_index.isValid():
            parent_index = current_index.parent()
            candidate_row = current_index.row() - 1

            # Current index isn't the first sibling, so we can go to previous one
            if candidate_row >= 0:
                new_index = self.index(candidate_row, 0, parent_index)
                break

            current_index = current_index.parent()

        if new_index is None:
            return False

        # Go as deep as possible, while the current index has child nodes
        while self.rowCount(new_index) > 0:
            new_index = self.index(self.rowCount(new_index) - 1, 0, new_index)

        self.__select(new_index)

    def move_down(self):
        indices = self.__selection_model.selectedIndexes()
        # No selection
        if not indices:
            # If there are any tasks then go to the first one
            self.__try_move_to_first()
            return

        current_index = indices[0]

        # try to move into the current subtree, if the current node is the parent of more nodes
        if self.__try_move_into_subtree(current_index):
            return

        # No subtree to go into, so find preorder successor
        # If there's a sibling, then it will go to that.
        # If not, it'll keep on asceending til it finds one or fails
        self.__try_move_to_preorder_successor(current_index)

    def move_up(self):
        indices = self.__selection_model.selectedIndexes()
        # No selection
        if not indices:
            # If there are tasks then go to the first one
            self.__try_move_to_first()
            return

        current_index = indices[0]

        # try to move out ofthe current subtree, if the current node is the first node of its siblings.
        if self.__try_move_out_of_subtree(current_index):
            return

        # No subtree to go out of, so find preorder predecessor
        # If there's a sibling, then it will go to that.
        # If not, it'll keep on asceending til it finds one (and then go as deep as possible) or fails
        self.__try_move_to_preorder_predecessor(current_index)

    def move_previous_process(self):
        indices = self.__selection_model.selectedIndexes()
        # No selection
        if not indices:
            self.__try_move_to_first()
            return

        current_index = indices[0]

        was_process = not current_index.parent().isValid()

        while current_index.parent().isValid():
            current_index = current_index.parent()

        # If we originally did not have a process, then go to the process it belongs to
        if not was_process:
            self.__select(current_index)
            return

        # Otherwise go to the previous process
        candidate_row = current_index.row() - 1

        if candidate_row >= 0:
            # Parent is going to be the root.
            new_index = self.index(candidate_row, 0, QModelIndex())
            self.__select(new_index)

    def move_next_process(self):
        indices = self.__selection_model.selectedIndexes()
        # No selection
        if not indices:
            self.__try_move_to_first()
            return

        current_index = indices[0]

        while current_index.parent().isValid():
            current_index = current_index.parent()

        # Otherwise go to the previous process
        candidate_row = current_index.row() + 1

        if candidate_row < self.rowCount(current_index.parent()):
            # Parent is going to be the root.
            new_index = self.index(candidate_row, 0, QModelIndex())
            self.__select(new_index)

    def create_task(self):
        indices = self.__selection_model.selectedIndexes()
        # No selection
        if not indices:
            # default preceding_index to be the index of the last process
            preceding_index = self.index(
                len(self.__task_controller.processes) - 1, 0, QModelIndex()
            )
        else:
            preceding_index = indices[0]

        new_row = preceding_index.row() + 1
        self.insertRow(new_row, preceding_index.parent())
        new_index = self.index(new_row, 0, preceding_index.parent())
        self.task_created.emit(new_index)

    def insert_subtask(self):
        indices = self.__selection_model.selectedIndexes()
        # No selection
        if not indices:
            self.create_task()
            return

        parent_index = indices[0]

        new_row = self.rowCount(parent_index)
        self.insertRow(new_row, parent_index)
        new_index = self.index(new_row, 0, parent_index)
        self.task_inserted.emit(new_index)

    def delete_task(self):
        indices = self.__selection_model.selectedIndexes()
        # No selection
        if not indices:
            return

        index = indices[0]
        self.removeRow(index.row(), index.parent())

    def shift_focus(self):
        indices = self.__selection_model.selectedIndexes()
        if not indices:
            return

        index = indices[0]
        column_count = self.columnCount(index.parent())

        if column_count != 2:
            return

        new_column = (index.column() + 1) % column_count
        self.__select(self.index(index.row(), new_column, index.parent()))

    def get_task_from_index(self, index: Index):
        if index.isValid():
            return cast(Task, index.internalPointer())
        return None

    @override
    def insertRows(self, row: int, count: int, parent: Index = QModelIndex()) -> bool:
        if count != 1:
            return False

        self.beginInsertRows(parent, row, row)

        parent_task = self.get_task_from_index(parent)
        self.__task_controller.create_task(TaskDraft(parent_task, index=row))

        self.endInsertRows()
        return True

    @override
    def removeRows(self, row: int, count: int, parent: Index = QModelIndex()) -> bool:
        """Deletes the subtasks of the `parent` at indices `row` to `row + count - 1`."""

        self.beginRemoveRows(parent, row, row + count - 1)
        parent_task = self.get_task_from_index(parent)
        self.__task_controller.remove_tasks(parent_task, row, count)
        self.endRemoveRows()
        return True

    @override
    def flags(self, index: Index) -> Qt.ItemFlag:
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    @override
    def parent(self, index: QModelIndex):  # type: ignore[override]
        child_task = self.get_task_from_index(index)
        if child_task is None:
            return QModelIndex()

        # We have a process as the child, so the 'parent' is the root
        # So return an invalid model index as expected.
        if child_task.parent is None:
            return QModelIndex()

        parent_item = child_task.parent
        parent_row = self.__task_controller.find_task_in_parent(parent_item)
        return self.createIndex(parent_row, 0, parent_item)

    @override
    def index(
        self, row: int, column: int, parent: Index = QModelIndex()
    ) -> QModelIndex:
        # This index doesn't exist
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_task = self.get_task_from_index(parent)
        child_tasks = self.__task_controller.get_children(parent_task)
        task = child_tasks[row]
        return self.createIndex(row, column, task)

    @override
    def columnCount(self, parent: Index = QModelIndex()) -> int:
        if parent.isValid():
            return 1
        return 2

    @override
    def rowCount(self, parent: Index = QModelIndex()) -> int:
        parent_task = self.get_task_from_index(parent)
        return len(self.__task_controller.get_children(parent_task))

    @override
    def data(self, index: Index, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        task = self.get_task_from_index(index)
        if task is None:
            return None

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if index.column() == 0:
                return task.description
            if index.column() == 1:
                return task.tag.name

    @override
    def setData(
        self, index: Index, value: Any, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:

        if role != Qt.ItemDataRole.EditRole:
            return False

        task = self.get_task_from_index(index)
        if task is None:
            return False

        update_funcs = [
            self.__task_controller.update_description,
            self.__task_controller.update_tag,
        ]

        column = index.column()
        assert 0 <= column < len(update_funcs)
        update_funcs[column](task, value)

        self.dataChanged.emit(index, index)
        return True

    @override
    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:

        if (
            role != Qt.ItemDataRole.DisplayRole
            or orientation != Qt.Orientation.Horizontal
        ):
            return

        if section == 0:
            return "Task"
        if section == 1:
            return "Tag"
