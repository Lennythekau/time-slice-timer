from dataclasses import dataclass
from typing import cast

from sqlite_setup import ConnectionFactory
from tag.model import EMPTY_TAG, Tag


@dataclass
class TagRepo:
    make_connection: ConnectionFactory

    def add_tag(self, name: str) -> Tag:
        conn = self.make_connection()
        try:
            with conn:
                cursor = conn.execute("""INSERT INTO tag(name) VALUES (?)""", (name,))
        finally:
            conn.close()

        tag_id = cast(int, cursor.lastrowid)
        tag = Tag(tag_id=tag_id, name=name)
        return tag

    def edit_tag(self, tag_id: int, new_name: str):
        with self.make_connection() as connection:
            cursor = connection.execute(
                """UPDATE tag SET name=? WHERE tag_id=?""", (new_name, tag_id)
            )
        connection.close()

        tag_id = cast(int, cursor.lastrowid)
        tag = Tag(tag_id=tag_id, name=new_name)
        return tag

    def delete_tag(self, tag_id: int):
        conn = self.make_connection()
        with conn:
            conn.execute("DELETE from tag WHERE tag_id=?", (tag_id,))
        conn.close()

    def get_tags(self) -> list[Tag]:
        """Get the tags from the database. This will not include `EMPTY_TAG` as that is never stored in the database."""
        with self.make_connection() as connection:
            tag_rows = connection.execute("SELECT tag_id, name FROM tag").fetchall()
        connection.close()
        return [Tag(*row) for row in tag_rows]
