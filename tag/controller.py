import sqlite3

from db.repository import Repository


class TagController:

    def __init__(self, repo: Repository):
        self.__repo = repo
        self.current_text: str | None = None

        self.__NAME_EMPTY_ERROR = "Name must not be empty 🦆!"
        self.__NAME_NOT_UNIQUE_ERROR = "Tag name must be unique 🦆!"
        self.__UNEXPECTED_ERROR = "Something unexpected went wrong 😔."

    def add_tag(self, name: str) -> str | None:
        """Returns an error, if there was any."""
        if not name:
            return self.__NAME_EMPTY_ERROR
        try:
            self.__repo.add_tag(name)
            return None
        except sqlite3.IntegrityError as e:
            if e.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                return self.__NAME_NOT_UNIQUE_ERROR

            return self.__UNEXPECTED_ERROR

    def edit_tag(self, old_name: str, new_name: str) -> str | None:
        if not new_name:
            return self.__NAME_EMPTY_ERROR
        try:
            self.__repo.edit_tag(old_name, new_name)
            return None
        except sqlite3.IntegrityError as e:
            if e.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                return
            return self.__UNEXPECTED_ERROR

    def delete_tag(self, name: str):
        try:
            self.__repo.delete_tag(name)
        except:
            return self.__UNEXPECTED_ERROR
