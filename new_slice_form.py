from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot

from db.repository import Repository
from time_slice import RunningTimeSlice
from user_session import UserSession


class NewSliceForm(QtWidgets.QWidget):
    submitted = Signal(RunningTimeSlice)

    def __init__(self, user_session: UserSession, repo: Repository):

        super().__init__()

        self.__user_session = user_session
        self.__repo = repo

        self.__make_ui()
        self.__setup_shortcuts()

        self.__user_session.stopwatch.started += lambda _: self.setEnabled(False)
        self.__user_session.stopwatch.finished += lambda _: self.setEnabled(True)
        self.__user_session.stopwatch.cancelled += lambda _: self.setEnabled(True)

    def __make_ui(self):
        self.__layout = QtWidgets.QVBoxLayout(self)
        self.__layout.setSpacing(0)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self.__description_input = QtWidgets.QLineEdit(
            placeholderText="Task description"
        )
        self.__tag_input = QtWidgets.QComboBox()
        self.__set_tag_input_items()

        self.__duration_input = QtWidgets.QSpinBox(
            suffix=" min", value=5, singleStep=5, minimum=1, maximum=60
        )

        self.__submit_button = QtWidgets.QPushButton("Start")
        self.__submit_button.clicked.connect(self.__on_submit_button_clicked)

        self.__layout.addWidget(self.__description_input)
        self.__layout.addWidget(self.__tag_input)
        self.__layout.addWidget(self.__duration_input)
        self.__layout.addWidget(self.__submit_button)

    def __set_tag_input_items(self):
        self.__tag_input.clear()
        for tag in self.__repo.get_tags():
            self.__tag_input.addItem(tag.name, tag)

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
