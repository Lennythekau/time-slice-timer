import datetime
import sqlite3 as sql
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from tag.model import EMPTY_TAG, Tag
from time_slice.model import RunningTimeSlice, TimeSlice


@dataclass
class TimeSliceRepo:
    make_connection: Callable[[], sql.Connection]

    def add_slice(
        self,
        time_slice: RunningTimeSlice,
        date: datetime.datetime | None = None,
    ):
        date = date or datetime.datetime.today()

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

        return created_time_slice

    def get_slices_by_date(self, date: datetime.date):
        if isinstance(date, datetime.datetime):
            date = date.date()

        with self.make_connection() as connection:
            rows = connection.execute(
                """SELECT ts.time_slice_id, ts.created_at, ts.description, ts.tag_id, tag.name, ts.duration
                   FROM time_slice AS ts 
                   LEFT JOIN tag ON tag.tag_id = ts.tag_id
                   WHERE date(ts.created_at)=?
                """,
                (date,),
            ).fetchall()
        connection.close()

        result: list[TimeSlice] = []
        for ts_id, created_at, description, tag_id, tag_name, duration in rows:
            if tag_id == EMPTY_TAG.tag_id:
                tag = EMPTY_TAG
            else:
                tag = Tag(tag_id, tag_name)
            ts = TimeSlice(ts_id, created_at, description, tag, duration)
            result.append(ts)

        return result

    def get_times_by_tag(self, date: datetime.date) -> dict[Tag, int]:
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

            (empty_tag_duration,) = connection.execute(
                """SELECT SUM(duration) FROM time_slice WHERE tag_id=? AND date(created_at)=?""",
                (EMPTY_TAG.tag_id, date),
            ).fetchone()

            empty_tag_duration = empty_tag_duration or 0

        connection.close()

        rows = cast(list[tuple[int, str, int]], rows)

        times = {}

        for tag_id, name, total in rows:
            times[Tag(tag_id, name)] = total

        times[EMPTY_TAG] = empty_tag_duration

        return times

    def get_total_time(self, date: datetime.date) -> int:
        if isinstance(date, datetime.datetime):
            date = date.date()

        with self.make_connection() as connection:
            (total,) = connection.execute(
                "SELECT SUM(duration) FROM time_slice WHERE date(created_at)=?", (date,)
            ).fetchone()

        connection.close()

        return total or 0
