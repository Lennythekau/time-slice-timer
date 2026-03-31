from collections.abc import Callable
from datetime import date, datetime
import pathlib
import sqlite3 as sql


def __adapt_date_iso(val: date):
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


def register_adapters():
    sql.register_adapter(date, __adapt_date_iso)
    sql.register_adapter(datetime, __adapt_datetime_iso)
    sql.register_converter("date", __convert_date)
    sql.register_converter("datetime", __convert_datetime)


type ConnectionFactory = Callable[[], sql.Connection]


def create_connection_factory(path: pathlib.Path) -> ConnectionFactory:
    """Creates a function that gives sqlite3 connection to the database at `path`."""

    path.parent.mkdir(parents=True, exist_ok=True)

    def make_connection():
        return sql.connect(path, detect_types=sql.PARSE_DECLTYPES)

    return make_connection
