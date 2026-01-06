from datetime import date, datetime
import pathlib
import sqlite3 as sql

from time_slice import TimeSlice

__DATA_DIRECTORY = "data"
__DB_NAME = "time_slice.db"
__TIME_SLICE_TABLE = "time_slice"
__CURRENT_DIRECTORY = pathlib.Path(__file__).resolve().parent


def __adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def __adapt_datetime_iso(val: datetime):
    """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
    return val.replace(tzinfo=None).isoformat()


def __convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return date.fromisoformat(val.decode())


def __convert_datetime(val: bytes):
    """Convert ISO 8601 datetime to datetime.datetime object."""
    return datetime.fromisoformat(val.decode())


sql.register_adapter(date, __adapt_date_iso)
sql.register_adapter(datetime, __adapt_datetime_iso)
sql.register_converter("date", __convert_date)
sql.register_converter("datetime", __convert_datetime)


def __create_connection():
    path = __CURRENT_DIRECTORY / __DATA_DIRECTORY / __DB_NAME
    return sql.connect(path, detect_types=sql.PARSE_DECLTYPES)


def __convert_rows_to_time_slices(rows: list[tuple]):
    return [TimeSlice(*row) for row in rows]


def ensure_table_created():
    # PARSE_DECLTYPES so that the types given in the creating table syntax are enough for the converter/adapter methods to be called.
    with __create_connection() as connection:
        connection.execute(
            f"CREATE TABLE IF NOT EXISTS {__TIME_SLICE_TABLE}(time_slice_id INTEGER PRIMARY KEY, created_at datetime, description TEXT, tag TEXT, duration INTEGER)"
        )


def add_time_slice(description: str, tag: str, duration_minutes: int):
    with __create_connection() as connection:
        connection.execute(
            f"INSERT INTO {__TIME_SLICE_TABLE} (description, tag, duration, created_at) VALUES (?, ?, ?, ?)",
            (description, tag, duration_minutes, datetime.now()),
        )


def get_time_slices(date: date | None = None) -> list[TimeSlice]:
    with __create_connection() as connection:
        date = date or datetime.now().date()

        # prevent silly mistakes, ensuring we only have the date part of what could be a datetime object (since datetime inherits from date)
        if isinstance(date, datetime):
            date = date.date()

        return __convert_rows_to_time_slices(
            connection.execute(
                f"SELECT * FROM {__TIME_SLICE_TABLE} WHERE DATE(created_at)=?",
                ((date),),
            ).fetchall()
        )


def get_times_by_tag(date: date | None = None) -> list[tuple[str, int]]:
    with __create_connection() as connection:
        date = date or datetime.now().date()

        if isinstance(date, datetime):
            date = date.date()

        return connection.execute(
            f"SELECT tag, SUM(duration) FROM {__TIME_SLICE_TABLE} WHERE DATE(created_at)=? GROUP BY tag",
            (date,),
        ).fetchall()


def get_all_time_slices():
    with __create_connection() as connection:
        return __convert_rows_to_time_slices(
            connection.execute(f"SELECT * FROM {__TIME_SLICE_TABLE}").fetchall()
        )
