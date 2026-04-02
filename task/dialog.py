from PySide6 import QtWidgets

from .adapter import TasksViewAdapter
from .repo import TaskRepo
from .view import TasksView


class TasksDialog(QtWidgets.QDialog):
    def __init__(self, task_repo: TaskRepo):
        super().__init__()
        self.__task_repo = task_repo
        self.__make_ui()

    def __make_ui(self):
        self.__layout = QtWidgets.QVBoxLayout(self)

        adapter = TasksViewAdapter(self.__task_repo)
        self.__task_view = TasksView(adapter)
        adapter.set_selection_model(self.__task_view.selectionModel())

        self.__layout.addWidget(self.__task_view)
