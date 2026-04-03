from PySide6 import QtWidgets

from .adapter import TaskAdapter
from .repo import TaskRepo
from .view import TasksView


class TaskDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QMainWindow, task_repo: TaskRepo):
        super().__init__(parent=parent)
        self.__task_repo = task_repo
        self.__make_ui()

    def __make_ui(self):
        self.__layout = QtWidgets.QVBoxLayout(self)

        adapter = TaskAdapter(self.__task_repo)
        self.__task_view = TasksView(adapter)
        adapter.set_selection_model(self.__task_view.selectionModel())

        self.__layout.addWidget(self.__task_view)
