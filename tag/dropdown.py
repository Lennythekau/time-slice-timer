from PySide6.QtWidgets import QComboBox

from tag.service import TagService
from user_session import UserSession


class TagDropDown(QComboBox):
    def __init__(self, user_session: UserSession, tag_service: TagService, parent=None):
        super().__init__(parent)

        self.__session = user_session
        tag_service.tags_changed += lambda _: self.__update_tag_input_items()

        self.__update_tag_input_items()

    def __update_tag_input_items(self):
        self.clear()
        for tag in self.__session.tags.values():
            self.addItem(tag.name, tag)
