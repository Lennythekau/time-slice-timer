from db.time_slice_repository import TimeSliceRepository
from PySide6.QtCore import Slot
from PySide6 import QtCore, QtGui
from stopwatch_controller import StopwatchController
from PySide6 import QtWidgets

from new_slice_form import NewSliceForm
from settings import Settings
import app_info
from stopwatch import Stopwatch


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        settings: Settings,
        stopwatch_controller: StopwatchController,
        time_slice_repo: TimeSliceRepository,
    ):
        super().__init__()

        self.repo = time_slice_repo

        self.setWindowTitle(app_info.APP_NAME)

        self.setCentralWidget(QtWidgets.QWidget())
        self.__layout = QtWidgets.QVBoxLayout(self.centralWidget())

        self.__new_slice_form = NewSliceForm(settings)
        self.__new_slice_form.submitted.connect(self.__on_new_slice_form_submitted)

        self.__stopwatch = Stopwatch(stopwatch_controller)
        self.__stopwatch.setEnabled(False)

        self.__stopwatch.started.connect(self.__on_stopwatch_started)
        self.__stopwatch.cancelled.connect(self.__on_stopwatch_cancelled)
        self.__stopwatch.finished.connect(self.__on_stopwatch_finished)

        self.__layout.addWidget(self.__new_slice_form)
        self.__layout.addWidget(self.__stopwatch)

        self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)  # type: ignore

    def __on_new_slice_form_submitted(self, data: NewSliceForm.Data):
        self.__stopwatch.setEnabled(True)
        self.form_data = data
        self.__stopwatch.start(data.duration)

    @Slot()
    def __on_stopwatch_started(self):
        self.__new_slice_form.setEnabled(False)

    @Slot()
    def __on_stopwatch_cancelled(self):
        self.__new_slice_form.setEnabled(True)
        self.__stopwatch.setEnabled(False)

    @Slot()
    def __on_stopwatch_finished(self):
        self.__new_slice_form.setEnabled(True)
        self.__stopwatch.setEnabled(False)
        self.repo.add(*self.form_data)
