from PySide6 import QtWidgets
from PySide6.QtGui import Qt


class TimesUpDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent, modal=True)
        self.setWindowTitle("Time's up!")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)

        self.__layout = QtWidgets.QVBoxLayout(self)

        self.__layout.addWidget(
            QtWidgets.QLabel(
                """If you weren't able to finish in time, think about why.
If you underestimated how much time you needed, consider breaking the task up into smaller pieces."""
            )
        )

        confirm_button = QtWidgets.QPushButton("Okay")
        confirm_button.clicked.connect(self.accept)
        self.__layout.addWidget(confirm_button)
