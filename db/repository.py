from dataclasses import dataclass
import datetime
from typing import TYPE_CHECKING, cast

from lib.event import Event
from time_slice import RunningTimeSlice, Tag, TimeSlice

if TYPE_CHECKING:
    from collections.abc import Callable
    import sqlite3 as sql


@dataclass
class Repository:
    make_connection: Callable[[], sql.Connection]

    def __post_init__(self):
        self.time_slice_added = Event[TimeSlice]()

        # TODO: Decide if we should change this to a more granular system (tag_added, tag_removed etc)
        self.tags_changed = Event[None]()

    def __convert_rows_to_time_slices(self, rows: list[tuple]):
        return [TimeSlice(*row) for row in rows]

    def __ensure_date_only(self, date: datetime.date | None):
        """Given `date`, return the date only component. If date is `None`, then just give today's date (no time component)."""
        if date is None:
            return datetime.date.today()

        # Unfortunately, `datetime.datetime` inherits from `datetime.date`, so we might accidentally have some time info.
        if isinstance(date, datetime.datetime):
            date = date.now()

        return date

    def ensure_tables_created(self):
        # PARSE_DECLTYPES so that the types given in the creating table syntax
        # are enough for the converter/adapter methods to be called.
        with self.make_connection() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS time_slice(
                        time_slice_id INTEGER PRIMARY KEY, 
                        created_at datetime, 
                        description TEXT, 
                        tag_id INTEGER, 
                        duration INTEGER)"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS tag(
                        tag_id INTEGER PRIMARY KEY, 
                        name TEXT UNIQUE NOT NULL)"""
            )
        connection.close()

    def add_slice(
        self,
        time_slice: RunningTimeSlice,
        date: datetime.datetime | None = None,
    ):
        date = datetime.datetime.now() if date is None else date

        with self.make_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO time_slice(description, tag_id, duration, created_at) 
                    VALUES (?, ?, ?, ?)""",
                (
                    time_slice.description,
                    time_slice.tag.tag_id,
                    time_slice.duration,
                    date,
                ),
            )

        connection.close()

        time_slice_id = cast(int, cursor.lastrowid)
        created_time_slice = TimeSlice(time_slice_id, date, *time_slice)

        self.time_slice_added.invoke(created_time_slice)
        return created_time_slice

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
        return [Tag(*row) for row in tag_rows]

    def get_by_date(self, date: datetime.date | None = None) -> list[TimeSlice]:
        date = self.__ensure_date_only(date)

        with self.make_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM time_slice WHERE DATE(created_at)=?", ((date),)
            ).fetchall()

        connection.close()

        return self.__convert_rows_to_time_slices(rows)

    def get_times_by_tag(self, date: datetime.date | None = None):
        date = self.__ensure_date_only(date)

        with self.make_connection() as connection:
            rows = connection.execute(
                """SELECT tag.tag_id, tag.name, COALESCE(s.total, 0) 
                   FROM (SELECT ts.tag_id, SUM(ts.duration) AS total 
                        FROM time_slice ts 
                        WHERE date(ts.created_at) = ?
                        GROUP BY ts.tag_id)
                   AS s RIGHT JOIN tag 
                   ON tag.tag_id = s.tag_id""",
                (date,),
            ).fetchall()

        connection.close()

        rows = cast(list[tuple[int, str, int]], rows)

        times = []
        for tag_id, name, total in rows:
            times.append((Tag(tag_id, name), total))

        return times
