from typing import cast
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import (
    QAbstractProxyModel,
    QModelIndex,
    QStringListModel,
    Signal,
    Slot,
)

from tag.dropdown import TagDropDown
from tag.repo import TagRepo
from task.adapter import TaskAdapter
from task.flattened_adapter import FlattenedTaskAdapter
from task.repo import TaskRepo
from user_session import UserSession

from .model import RunningTimeSlice


class NewSliceForm(QtWidgets.QWidget):
    submitted = Signal(RunningTimeSlice)

    def __init__(
        self,
        user_session: UserSession,
        tag_repo: TagRepo,
        task_repo: TaskRepo,
        task_adapter: TaskAdapter,
    ):

        super().__init__()

        self.__user_session = user_session
        self.__task_adapter = FlattenedTaskAdapter(task_repo, task_adapter)

        self.__make_ui(tag_repo)
        self.__setup_shortcuts()

        self.__user_session.stopwatch.started += lambda _: self.setEnabled(False)
        self.__user_session.stopwatch.finished += lambda _: self.setEnabled(True)
        self.__user_session.stopwatch.cancelled += lambda _: self.setEnabled(True)

    def __make_ui(self, tag_repo: TagRepo):
        self.__layout = QtWidgets.QVBoxLayout(self)
        self.__layout.setSpacing(0)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self.__description_input = QtWidgets.QLineEdit(
            placeholderText="Task description"
        )

        self.__completer = QtWidgets.QCompleter()
        self.__completer.setModel(self.__task_adapter)
        self.__completer.setCaseSensitivity(QtGui.Qt.CaseSensitivity.CaseInsensitive)
        self.__completer.setCompletionRole(QtGui.Qt.ItemDataRole.DisplayRole)
        self.__completer.setCompletionMode(
            QtWidgets.QCompleter.CompletionMode.PopupCompletion
        )
        self.__completer.setCompletionColumn(0)
        self.__completer.setFilterMode(QtGui.Qt.MatchFlag.MatchContains)

        self.__completer.activated[QModelIndex].connect(self.__completion_chosen)  # type: ignore

        self.__description_input.setCompleter(self.__completer)

        self.__tag_input = TagDropDown(tag_repo)

        self.__duration_input = QtWidgets.QSpinBox(
            suffix=" min", value=5, singleStep=5, minimum=1, maximum=60
        )

        self.__submit_button = QtWidgets.QPushButton("Start")
        self.__submit_button.clicked.connect(self.__on_submit_button_clicked)

        self.__layout.addWidget(self.__description_input)
        self.__layout.addWidget(self.__tag_input)
        self.__layout.addWidget(self.__duration_input)
        self.__layout.addWidget(self.__submit_button)

    @Slot()
    def __completion_chosen(self, index: QModelIndex):
        completion_model = cast(QAbstractProxyModel, self.__completer.completionModel())
        adapter_index = completion_model.mapToSource(index)
        tag_name = self.__task_adapter.get_tag_name(adapter_index)
        self.__tag_input.setCurrentText(tag_name)

    def __setup_focus_shortcuts(self):
        form_widgets = (
            self.__description_input,
            self.__tag_input,
            self.__duration_input,
        )

        # Start counting from 1, so that the 1st form widget can be focused with
        # Alt+1, the second item with Alt+2 etc.
        for number_key, widget in enumerate(form_widgets, 1):
            key_sequence = QtGui.QKeySequence(f"Alt+{number_key}")

            @Slot()
            def callback(widget: QtWidgets.QWidget = widget):
                widget.setFocus()

            QtGui.QShortcut(key_sequence, self).activated.connect(callback)

    def __setup_submit_shortcut(self):
        @Slot()
        def callback():
            self.__submit_button.clicked.emit()

        QtGui.QShortcut("Alt+Return", self).activated.connect(callback)

    def __setup_shortcuts(self):
        self.__setup_focus_shortcuts()
        self.__setup_submit_shortcut()

    @Slot()
    def __on_submit_button_clicked(self):
        time_slice = RunningTimeSlice(
            description=self.__description_input.text(),
            tag=self.__tag_input.currentData(),
            duration=self.__duration_input.value(),
        )

        self.submitted.emit(time_slice)
