import sqlite3

from lib.event import Event
from tag.model import EMPTY_TAG, Tag
from tag.repo import TagRepo
from user_session import UserSession

# TODO: make this a Result[T], probably with constructors fail(str) and success(T)
type TagResult = tuple[Tag | None, str]


def fail(reason: str) -> TagResult:
    return None, reason


def succeed(tag: Tag) -> TagResult:
    return tag, ""


class TagService:

    def __init__(self, user_session: UserSession, repo: TagRepo):
        self.__session = user_session
        self.__repo = repo

        self.__session.tags = self.get_tags()

        self.tags_changed = Event[None]()

        self.__NAME_EMPTY_ERROR = "Name must not be empty 🦆!"
        self.__NAME_NOT_UNIQUE_ERROR = "Tag name must be unique 🦆!"
        self.__UNEXPECTED_ERROR = "Something unexpected went wrong 😔."

    def get_tags(self):
        tags = self.__repo.get_tags()
        tags_by_id: dict[int, Tag] = {}
        tags_by_id[EMPTY_TAG.tag_id] = EMPTY_TAG

        for tag in tags:
            tags_by_id[tag.tag_id] = tag

        return tags_by_id

    def add_tag(self, name: str) -> TagResult:
        """Returns the tag, and an error, if there was any."""

        if not name:
            return fail(self.__NAME_EMPTY_ERROR)
        try:
            tag = self.__repo.add_tag(name)
            self.__session.tags[tag.tag_id] = tag
            self.tags_changed.invoke(None)
            return succeed(tag)

        except sqlite3.IntegrityError as e:
            if e.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                return fail(self.__NAME_NOT_UNIQUE_ERROR)

            return fail(self.__UNEXPECTED_ERROR)

    def edit_tag(self, tag_id: int, new_name: str) -> TagResult:
        if not new_name:
            return fail(self.__NAME_EMPTY_ERROR)
        try:
            tag = self.__repo.edit_tag(tag_id, new_name)
            self.__session.tags[tag_id] = tag
            self.tags_changed.invoke(None)
            return succeed(tag)

        except sqlite3.IntegrityError as e:
            if e.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                return None, ""
            return fail(self.__UNEXPECTED_ERROR)

    def delete_tag(self, tag_id: int) -> str:
        try:
            self.__repo.delete_tag(tag_id)

            if tag_id in self.__session.tags:
                self.__session.tags.pop(tag_id)

            self.tags_changed.invoke(None)
            return ""
        except:
            return self.__UNEXPECTED_ERROR
