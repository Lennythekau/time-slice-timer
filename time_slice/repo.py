from dataclasses import dataclass
import datetime
from typing import cast

from lib.event import Event
from time_slice.model import RunningTimeSlice, TimeSlice
from tag.model import Tag

from collections.abc import Callable
import sqlite3 as sql


@dataclass
class TimeSliceRepo:
    make_connection: Callable[[], sql.Connection]

    def __post_init__(self):
        self.time_slice_added = Event[TimeSlice]()

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

    def get_by_date(self, date: datetime.date) -> list[TimeSlice]:
        if isinstance(date, datetime.datetime):
            date = date.date()

        with self.make_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM time_slice WHERE DATE(created_at)=?", ((date),)
            ).fetchall()

        connection.close()

        return [TimeSlice(*row) for row in rows]

    def get_times_by_tag(self, date: datetime.date):
        if isinstance(date, datetime.datetime):
            date = date.date()

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
