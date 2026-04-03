from typing import Literal

from PySide6 import QtWidgets
from PySide6.QtCore import Slot

from tag.model import EMPTY_TAG

from .controller import TagController
from .repo import TagRepo


class TagDialog(QtWidgets.QDialog):
    def __init__(
        self,
        tag_repo: TagRepo,
        tag_view_controller: TagController,
    ):
        super().__init__()
        self.__tag_repo = tag_repo
        self.__tag_view_controller = tag_view_controller
        self.__mode: Literal["Add"] | Literal["Edit"] = "Add"

        self.__BUTTON_ADD_TEXT = "Add"
        self.__BUTTON_EDIT_TEXT = "Edit"
        self.__selected_item: QtWidgets.QListWidgetItem | None = None
        self.__make_ui()

    def __make_ui(self):
        self.__layout = QtWidgets.QVBoxLayout(self)
        self.__tags_list = QtWidgets.QListWidget()

        # Although we only allow for selecting 0/1 items, this means that
        # We get item toggling for free, and keyboard navigation doesn't automatically
        # Select the item, which is important.
        self.__tags_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )
        self.__tags_list.addItems([tag.name for tag in self.__tag_repo.get_tags()])
        self.__tags_list.itemSelectionChanged.connect(self.__selection_changed)

        self.__error_message = QtWidgets.QLabel()
        self.__error_message.hide()

        self.__form = QtWidgets.QWidget()
        self.__form_layout = QtWidgets.QHBoxLayout(self.__form)

        self.__text_field = QtWidgets.QLineEdit()
        self.__form_button = QtWidgets.QPushButton()
        self.__form_button.clicked.connect(self.__form_button_clicked)

        self.__delete_button = QtWidgets.QPushButton("Delete")
        self.__delete_button.setDisabled(False)
        self.__delete_button.clicked.connect(self.__on_delete_button_clicked)

        self.__form_layout.addWidget(self.__text_field)
        self.__form_layout.addWidget(self.__form_button)
        self.__form_layout.addWidget(self.__delete_button)
        self.__start_add_mode()

        self.__layout.addWidget(self.__tags_list)
        self.__layout.addWidget(self.__error_message)
        self.__layout.addWidget(self.__form)

    @Slot()
    def __selection_changed(self):
        self.__discard_error()
        selected_items = self.__tags_list.selectedItems()

        # No items selected, so go back to add mode
        if not selected_items:
            self.__start_add_mode()
            return

        # Deselect everything except last item.
        for selected_item in selected_items[:-1]:
            selected_item.setSelected(False)

        # Select last item
        selected_item = selected_items[-1]
        if selected_item.text() == EMPTY_TAG.name:
            self.__form_button.setEnabled(False)
        else:
            self.__form_button.setEnabled(True)

        self.__start_edit_mode(selected_item)

    @Slot()
    def __on_delete_button_clicked(self):

        @Slot()
        def confirmed_deletion():
            assert self.__selected_item is not None
            error = self.__tag_view_controller.delete_tag(self.__selected_item.text())
            if error is None:
                self.__update_tags_list()
            else:
                self.__display_error(error)

        assert self.__selected_item is not None
        confirmation_box = QtWidgets.QMessageBox(
            self,
            text=f"Are you sure you want to delete tag: {self.__selected_item.text()}?",
        )

        confirmation_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Cancel
            | QtWidgets.QMessageBox.StandardButton.Yes
        )
        QtWidgets.QDialogButtonBox.StandardButton.Yes
        confirmation_box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Cancel)
        confirmation_box.open()

        confirmation_box.accepted.connect(confirmed_deletion)

    def __add_tag(self):
        error = self.__tag_view_controller.add_tag(self.__text_field.text())
        if error is None:
            self.__text_field.clear()
            self.__update_tags_list()
        else:
            self.__display_error(error)

    def __edit_tag(self):
        assert self.__selected_item is not None
        error = self.__tag_view_controller.edit_tag(
            old_name=self.__selected_item.text(), new_name=self.__text_field.text()
        )
        if error is None:
            self.__update_tags_list()
        else:
            self.__display_error(error)

    @Slot()
    def __form_button_clicked(self):
        if self.__mode == "Add":
            self.__add_tag()
        else:
            self.__edit_tag()

    def __display_error(self, error: str):
        self.__error_message.setText(error)
        self.__error_message.show()

    def __discard_error(self):
        self.__error_message.setText("")
        self.__error_message.hide()

    def __update_tags_list(self):
        # Clear any error message
        self.__discard_error()

        names = [tag.name for tag in self.__tag_repo.get_tags()]
        self.__tags_list.clear()
        self.__tags_list.addItems(names)

    def __start_add_mode(self):
        self.__mode = "Add"
        self.__selected_item = None
        self.__form_button.setText(self.__BUTTON_ADD_TEXT)
        self.__text_field.setText("")

        # Deletion only enabled during edit mode
        self.__delete_button.setEnabled(False)

    def __start_edit_mode(self, selected_item: QtWidgets.QListWidgetItem):
        self.__mode = "Edit"
        self.__selected_item = selected_item
        self.__form_button.setText(self.__BUTTON_EDIT_TEXT)
        self.__text_field.setText(selected_item.text())

        # Deletion only enabled during edit mode
        self.__delete_button.setEnabled(True)
