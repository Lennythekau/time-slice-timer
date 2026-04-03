from PySide6.QtWidgets import QComboBox

from tag.repo import TagRepo


class TagDropDown(QComboBox):
    def __init__(self, tag_repo: TagRepo, parent=None):
        super().__init__(parent)
        self.__tag_repo = tag_repo
        self.__tag_repo.tags_changed += lambda _: self.__update_tag_input_items()
        self.__tag_names = list[str]()

        self.__update_tag_input_items()

    def get_tag_names(self):
        return self.__tag_names

    def __update_tag_input_items(self):
        self.clear()
        self.__tag_names.clear()
        for tag in self.__tag_repo.get_tags():
            self.addItem(tag.name, tag)
            self.__tag_names.append(tag.name)
