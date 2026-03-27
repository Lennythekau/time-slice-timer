from PySide6.QtCore import Slot
from stopwatch_controller import StopwatchController
from PySide6 import QtWidgets

from new_slice_form import NewSliceForm
from settings import Settings
import app_info
from stopwatch import Stopwatch


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, settings: Settings, stopwatch_controller: StopwatchController):
        super().__init__()

        self.setWindowTitle(app_info.APP_NAME)

        self.setCentralWidget(QtWidgets.QWidget())
        self.__layout = QtWidgets.QVBoxLayout(self.centralWidget())

        self.__new_slice_form = NewSliceForm(settings)
        self.__new_slice_form.submitted.connect(self.__on_new_slice_form_submitted)

        self.__stopwatch = Stopwatch(stopwatch_controller)
        self.__stopwatch.setEnabled(False)
        self.__stopwatch.started.connect(self.__on_stopwatch_started)
        self.__stopwatch.cancelled.connect(self.__on_stopwatch_cancelled)

        self.__layout.addWidget(self.__new_slice_form)
        self.__layout.addWidget(self.__stopwatch)

    def __on_new_slice_form_submitted(self, data: NewSliceForm.Data):
        self.__stopwatch.setEnabled(True)
        self.__stopwatch.start(data.duration)

    @Slot()
    def __on_stopwatch_started(self):
        self.__new_slice_form.setEnabled(False)

    @Slot()
    def __on_stopwatch_cancelled(self):
        self.__new_slice_form.setEnabled(True)
        self.__stopwatch.setEnabled(False)
