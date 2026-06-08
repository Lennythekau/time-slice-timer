from typing import cast, override

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QStyledItemDelegate

from tag.dropdown import TagDropDown
from tag.model import Tag
from tag.service import TagService
from user_session import UserSession


class TagDelegate(QStyledItemDelegate):
    def __init__(self, user_session: UserSession, tag_service: TagService):
        super().__init__()

        self.__session = user_session
        self.__tag_service = tag_service

    @override
    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
        /,
    ) -> QtWidgets.QWidget:
        drop_down = TagDropDown(self.__session, self.__tag_service, parent)
        QtCore.QTimer.singleShot(0, drop_down.showPopup)

        return drop_down

    @override
    def setEditorData(
        self, editor: QtWidgets.QWidget, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        editor = cast(TagDropDown, editor)
        value: str = index.data(Qt.ItemDataRole.EditRole)

        if editor.findText(value) != -1:
            editor.setCurrentText(value)

    @override
    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        editor = cast(TagDropDown, editor)

        tag = editor.currentData()
        assert isinstance(tag, Tag)

        model.setData(index, tag, Qt.ItemDataRole.EditRole)

    @override
    def updateEditorGeometry(
        self,
        editor: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ):
        editor.setGeometry(option.rect)  # type: ignore
