from dataclasses import dataclass
from typing import cast

from lib.event import Event
from sqlite_setup import ConnectionFactory

from .model import EMPTY_TAG, Tag


@dataclass
class TagRepo:
    make_connection: ConnectionFactory

    def __post_init__(self):
        self.tags_changed = Event[None]()

    def add_tag(self, name: str):
        with self.make_connection() as connection:
            cursor = connection.execute("""INSERT INTO tag(name) VALUES (?)""", (name,))
        connection.close()

        tag_id = cast(int, cursor.lastrowid)
        tag = Tag(tag_id=tag_id, name=name)
        self.tags_changed.invoke(None)
        return tag

    def edit_tag(self, old_name: str, new_name: str):
        with self.make_connection() as connection:
            cursor = connection.execute(
                """UPDATE tag SET name=? WHERE name=?""", (new_name, old_name)
            )
        connection.close()

        tag_id = cast(int, cursor.lastrowid)
        tag = Tag(tag_id=tag_id, name=new_name)
        self.tags_changed.invoke(None)
        return tag

    def delete_tag(self, name: str):
        with self.make_connection() as connection:
            connection.execute("DELETE FROM tag WHERE name=?", (name,))
        connection.close()
        self.tags_changed.invoke(None)

    def get_tags(self) -> list[Tag]:
        with self.make_connection() as connection:
            tag_rows = connection.execute("SELECT tag_id, name FROM tag").fetchall()
        connection.close()
        return [EMPTY_TAG] + [Tag(*row) for row in tag_rows]
