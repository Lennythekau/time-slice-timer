import ctypes
from pprint import pformat
from typing import Any, Sequence, cast, override

from PySide6.QtCore import (
    QAbstractItemModel,
    QByteArray,
    QDataStream,
    QMimeData,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
)

from task.model import Task, TaskDraft
from task.service import TaskService
from user_session import UserSession

type Index = QModelIndex | QPersistentModelIndex

MIME_TYPE = "application/time-slice"

# TODO: unfold task if something is dragged into it, potentially focus on the newly dropped task.


class TaskAdapter(QAbstractItemModel):
    task_created = Signal(QModelIndex)
    task_inserted = Signal(QModelIndex)

    def __init__(self, user_session: UserSession, task_service: TaskService) -> None:
        super().__init__()
        self.__session = user_session
        self.__service = task_service
        self.__dragged_index: Index | None = None

    def __try_move_to_first_process(self):
        """Attempts to move to the first process in the list of processes."""

        if self.__session.processes:
            # No parent, as this is a process. So, parent is an invalid QModelIndex()
            return self.index(0, 0, QModelIndex())
        return None

    def __try_move_into_subtree(self, current_index: QModelIndex):
        """Attempts to move into the first subtask of the task at `current_index`."""
        task = current_index.internalPointer()
        assert isinstance(task, Task)

        if task.sub_tasks:
            # Go to the first subtask
            return self.index(0, 0, current_index)
        return None

    def __try_move_out_of_subtree(self, current_index: QModelIndex):
        if current_index.row() != 0:
            return False

        parent_index = current_index.parent()
        if not parent_index.isValid():
            return None

        return parent_index

    def move_to_previous_process(self, current_index: QModelIndex):
        if not current_index.isValid():
            return None

        is_process = not current_index.parent().isValid()

        while current_index.parent().isValid():
            current_index = current_index.parent()

        # If we originally did not have a process, then go to the process it belongs to
        if not is_process:
            return current_index

        # Otherwise, we are at a process, so go to the previous process
        candidate_row = current_index.row() - 1

        if candidate_row >= 0:
            # Parent is the root.
            return self.index(candidate_row, 0, QModelIndex())

        return None

    def move_to_next_process(self, current_index: QModelIndex):
        if not current_index.isValid():
            return None

        while current_index.parent().isValid():
            current_index = current_index.parent()

        candidate_row = current_index.row() + 1

        if candidate_row < self.rowCount(current_index.parent()):
            # Parent is going to be the root.
            return self.index(candidate_row, 0, QModelIndex())

        return None

    def move_to_parent(self, current_index: QModelIndex):
        if not current_index.isValid():
            return None

        parent_index = self.parent(current_index)
        if parent_index.isValid():
            return parent_index
        return None

    def create_task(self, current_index: QModelIndex):
        # Not selecting anything, so...
        if not current_index.isValid():
            # ...default preceding_index to be the index of the last process
            preceding_index = self.index(
                len(self.__session.processes) - 1, 0, QModelIndex()
            )
        else:
            preceding_index = current_index

        new_row = preceding_index.row() + 1
        self.insertRow(new_row, preceding_index.parent())
        new_index = self.index(new_row, 0, preceding_index.parent())
        self.task_created.emit(new_index)

    def insert_subtask(self, current_index: QModelIndex):
        # No selection
        if not current_index.isValid():
            self.create_task(current_index)
            return None

        parent_index = current_index
        new_row = self.rowCount(parent_index)
        self.insertRow(new_row, parent_index)

        new_index = self.index(new_row, 0, parent_index)
        self.task_inserted.emit(new_index)

    def delete_task(self, current_index: QModelIndex):
        if not current_index.isValid():
            return None

        self.removeRow(current_index.row(), current_index.parent())

    def shift_focus(self, current_index: QModelIndex):
        if not current_index.isValid():
            return None

        column_count = self.columnCount(current_index.parent())

        # If there's nothing to focus to. Only process tasks have a 2nd column.
        if column_count != 2:
            return

        new_column = (current_index.column() + 1) % column_count
        # Same row and parent, just shift to the column.
        return self.index(current_index.row(), new_column, current_index.parent())

    def get_task_from_index(self, index: Index):
        return cast(Task | None, index.internalPointer())

    @override
    def insertRows(self, row: int, count: int, parent: Index = QModelIndex()) -> bool:
        if count != 1:
            return False

        self.beginInsertRows(parent, row, row)

        parent_task = self.get_task_from_index(parent)
        self.__service.create_task(TaskDraft(parent_task, position=row))

        self.endInsertRows()
        return True

    @override
    def removeRows(self, row: int, count: int, parent: Index = QModelIndex()) -> bool:
        """Deletes the subtasks of the `parent` at indices `row` to `row + count - 1`."""

        self.beginRemoveRows(parent, row, row + count - 1)
        parent_task = self.get_task_from_index(parent)
        self.__service.remove_tasks(parent_task, row, count)
        self.endRemoveRows()
        return True

    @override
    def flags(self, index: Index) -> Qt.ItemFlag:
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
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
        parent_row = self.__service.find_task_in_parent(parent_item)
        return self.createIndex(parent_row, 0, parent_item)

    @override
    def index(
        self, row: int, column: int, parent: Index = QModelIndex()
    ) -> QModelIndex:
        # This index doesn't exist
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_task = self.get_task_from_index(parent)
        child_tasks = self.__service.get_children(parent_task)
        task = child_tasks[row]
        return self.createIndex(row, column, task)

    @override
    def columnCount(self, parent: Index = QModelIndex()) -> int:
        task = self.get_task_from_index(parent)
        if task is None:
            return 2
        return 1

    @override
    def rowCount(self, parent: Index = QModelIndex()) -> int:
        parent_task = self.get_task_from_index(parent)
        return len(self.__service.get_children(parent_task))

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
            self.__service.update_description,
            self.__service.update_tag,
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

    @override
    def mimeData(self, indexes: Sequence[QModelIndex]) -> QMimeData:
        # One index for column 1, one index for column 2 potentially
        index = indexes[0]
        self.__dragged_index = index
        print(f"DRAGGED INDEX: {index.row()}, {index.column()}")

        task = self.get_task_from_index(index)
        assert task is not None

        data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QDataStream.OpenModeFlag.WriteOnly)
        stream.writeInt64(id(task))
        data.setData(MIME_TYPE, encoded_data)
        return data

    @override
    def mimeTypes(self):
        return [MIME_TYPE]

    @override
    def dropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: Index,
    ):
        # see self.canDropMimeData for handling of no-op and invalid cases.

        assert self.__dragged_index is not None
        old_parent_index = self.__dragged_index.parent()

        # get the dragged task.
        encoded_data = data.data(MIME_TYPE)
        stream = QDataStream(encoded_data, QDataStream.OpenModeFlag.ReadOnly)
        task_addr = stream.readInt64()
        task = ctypes.cast(task_addr, ctypes.py_object).value
        assert isinstance(task, Task)

        print("🚀" * 10)
        print(
            f"START drop(\n- task={pformat(task)},\n- {row=}, {column=},\n- parent={pformat(parent.internalPointer())})"
        )

        if row < 0:
            row = self.rowCount(parent)
            print(f"- Dropped on parent => {row=}")

        new_parent_task = self.get_task_from_index(parent)
        print(f"- new_parent_task={pformat(new_parent_task)}")

        self.beginMoveRows(old_parent_index, task.position, task.position, parent, row)

        self.__service.move_task(task, new_parent_task, row)

        self.endMoveRows()
        self.__dragged_index = None

        print("END drop")
        print("🏁" * 10)

        return True

    @override
    def canDropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: Index,
    ):
        assert self.__dragged_index is not None
        task = self.get_task_from_index(self.__dragged_index)
        new_parent_task = self.get_task_from_index(parent)

        assert task is not None
        if row < 0:
            if parent == self.__dragged_index.parent():
                row = self.rowCount(parent)

        return self.__service.can_move(task, new_parent_task, row)

    @override
    def supportedDropActions(self):
        # Although we actually want to move tasks, just as in a move action,
        # Move action actually calls removeRows on the original location of the task,
        # which calls the service, which calls the repo to remove the task from the repo.
        # But we don't actually want the task removed; we just want to adjust its parent field
        # And the affected tasks' positions (also the implementation of our parent method)
        # means that when removeRows is called, the parent index passed in will be the new parent,
        # not the old one.
        return Qt.DropAction.CopyAction
