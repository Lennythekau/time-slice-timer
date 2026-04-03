from PySide6 import QtWidgets

from tag.repo import TagRepo

from .adapter import TaskAdapter
from .repo import TaskRepo
from .view import TasksView


class TaskDialog(QtWidgets.QDialog):
    def __init__(
        self,
        tag_repo: TagRepo,
        task_adapter: TaskAdapter,
    ):
        super().__init__()

        self.__layout = QtWidgets.QVBoxLayout(self)

        self.__task_view = TasksView(task_adapter, tag_repo)
        task_adapter.set_selection_model(self.__task_view.selectionModel())

        self.__layout.addWidget(self.__task_view)
        self.resize(650, 400)
