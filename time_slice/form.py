from typing import cast

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import (
    QAbstractProxyModel,
    QModelIndex,
    Slot,
)

from tag.dropdown import TagDropDown
from tag.service import TagService
from task.flattened_adapter import FlattenedTaskAdapter
from time_slice.model import RunningTimeSlice
from time_slice.service import TimeSliceService
from user_session import UserSession


class NewSliceForm(QtWidgets.QWidget):

    def __init__(
        self,
        user_session: UserSession,
        time_slice_service: TimeSliceService,
        tag_service: TagService,
        task_adapter: FlattenedTaskAdapter,
    ):

        super().__init__()

        self.__session = user_session
        self.__time_slice_service = time_slice_service
        self.__tag_service = tag_service
        self.__task_adapter = task_adapter
        self.__make_ui()
        self.__setup_shortcuts()

        ts_svc = time_slice_service
        ts_svc.time_slice_started += lambda _: self.setEnabled(False)
        ts_svc.time_slice_finished += lambda _: self.setEnabled(True)
        ts_svc.time_slice_cancelled += lambda _: self.setEnabled(True)

    def __make_ui(self):
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

        self.__tag_input = TagDropDown(self.__session, self.__tag_service)

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

        self.__time_slice_service.start_slice(time_slice)
