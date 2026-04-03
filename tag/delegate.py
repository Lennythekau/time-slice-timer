from PySide6 import QtCore
from PySide6.QtCore import QAbstractItemModel
from typing import cast, override

from PySide6.QtGui import Qt
from tag.repo import TagRepo
from PySide6 import QtWidgets
from PySide6.QtCore import QPersistentModelIndex
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QStyledItemDelegate

from tag.dropdown import TagDropDown


class TagDelegate(QStyledItemDelegate):
    def __init__(self, tag_repo: TagRepo):
        super().__init__()
        self.__tag_repo = tag_repo

    @override
    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
        /,
    ) -> QtWidgets.QWidget:
        drop_down = TagDropDown(self.__tag_repo, parent)
        QtCore.QTimer.singleShot(0, drop_down.showPopup)

        return drop_down

    @override
    def setEditorData(
        self, editor: QtWidgets.QWidget, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        editor = cast(TagDropDown, editor)
        value = index.data(Qt.ItemDataRole.EditRole)
        if value in editor.get_tag_names():
            editor.setCurrentText(value)

    @override
    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        editor = cast(TagDropDown, editor)
        model.setData(index, editor.currentData(), Qt.ItemDataRole.EditRole)

    @override
    def updateEditorGeometry(
        self,
        editor: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ):
        editor.setGeometry(option.rect)  # type: ignore
