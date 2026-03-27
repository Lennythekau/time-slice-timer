from typing import NamedTuple
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot

from settings import Settings


class NewSliceForm(QtWidgets.QWidget):
    class Data(NamedTuple):
        description: str
        tag: str
        duration: int

    submitted = Signal(Data)

    def __init__(self, settings: Settings):

        super().__init__()
        self.__layout = QtWidgets.QVBoxLayout(self)

        self.__description_input = QtWidgets.QLineEdit(
            placeholderText="Task description"
        )
        self.__tag_input = QtWidgets.QComboBox()
        self.__tag_input.addItems(settings["tag_names"])

        self.__duration_input = QtWidgets.QSpinBox(
            suffix=" min", value=5, singleStep=5, minimum=1, maximum=60
        )

        self.__submit_button = QtWidgets.QPushButton("Start")
        self.__submit_button.clicked.connect(self.__on_submit_button_clicked)

        self.__layout.addWidget(self.__description_input)
        self.__layout.addWidget(self.__tag_input)
        self.__layout.addWidget(self.__duration_input)
        self.__layout.addWidget(self.__submit_button)

    def get_form_data(self):
        return NewSliceForm.Data(
            description=self.__description_input.text(),
            tag=self.__tag_input.currentText(),
            duration=self.__duration_input.value(),
        )

    @Slot()
    def __on_submit_button_clicked(self):
        self.submitted.emit(self.get_form_data())
