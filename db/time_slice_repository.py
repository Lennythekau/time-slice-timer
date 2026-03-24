import datetime
from dataclasses import dataclass
from typing import cast, TYPE_CHECKING

from time_slice import TimeSlice

if TYPE_CHECKING:
    from collections.abc import Callable
    import sqlite3 as sql


@dataclass
class TimeSliceRepository:
    make_connection: Callable[[], sql.Connection]

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

    def ensure_table_created(self):
        # PARSE_DECLTYPES so that the types given in the creating table syntax
        # are enough for the converter/adapter methods to be called.
        with self.make_connection() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS time_slice(
                        time_slice_id INTEGER PRIMARY KEY, 
                        created_at datetime, 
                        description TEXT, 
                        tag TEXT, 
                        duration INTEGER)"""
            )
        connection.close()

    def add(
        self,
        description: str,
        tag: str,
        duration_minutes: int,
        date: datetime.datetime | None = None,
    ):
        date = datetime.datetime.now() if date is None else date

        with self.make_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO time_slice(description, tag, duration, created_at) 
                    VALUES (?, ?, ?, ?)""",
                (description, tag, duration_minutes, date),
            )

        connection.close()

        time_slice_id = cast(int, cursor.lastrowid)
        return TimeSlice(time_slice_id, date, description, tag, duration_minutes)

    def get_by_date(self, date: datetime.date | None = None) -> list[TimeSlice]:
        date = self.__ensure_date_only(date)

        with self.make_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM time_slice WHERE DATE(created_at)=?", ((date),)
            ).fetchall()

        connection.close()

        return self.__convert_rows_to_time_slices(rows)

    def get_times_by_tag(
        self, date: datetime.date | None = None
    ) -> list[tuple[str, int]]:
        date = self.__ensure_date_only(date)

        with self.make_connection() as connection:
            rows = connection.execute(
                f"SELECT tag, SUM(duration) FROM time_slice WHERE DATE(created_at)=? GROUP BY tag",
                (date,),
            ).fetchall()

        connection.close()
        return rows
