import pathlib
import sqlite3 as sql
from collections.abc import Callable
from datetime import date, datetime
from sqlite3 import Connection
from typing import Literal


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


def create_connection_factory(
    path: pathlib.Path | Literal[":memory:"],
) -> ConnectionFactory:
    """Creates a function that gives sqlite3 connection to the database at `path`."""

    if path == ":memory:":
        uri = "file:testdb?mode=memory&cache=shared"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        uri = path

    def make_connection():
        connection = sql.connect(uri, detect_types=sql.PARSE_DECLTYPES, uri=True)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    return make_connection


def ensure_tables_created(make_connection: ConnectionFactory):
    with make_connection() as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS time_slice (
                    time_slice_id INTEGER PRIMARY KEY, 
                    created_at datetime, 
                    description TEXT, 
                    tag_id INTEGER, 
                    duration INTEGER)""")

        connection.execute("""CREATE TABLE IF NOT EXISTS tag (
                    tag_id INTEGER PRIMARY KEY, 
                    name TEXT UNIQUE NOT NULL)""")

        connection.execute("""CREATE TABLE IF NOT EXISTS task (
                    task_id INTEGER PRIMARY KEY, 
                    parent_id INTEGER NULL REFERENCES task(task_id) ON DELETE CASCADE, 
                    description TEXT NOT NULL, 
                    tag_id INTEGER NULL,
                    position INTEGER
                    )""")
        __ensure_task_table_has_position_column(connection)

    connection.close()


def __ensure_task_table_has_position_column(connection: Connection):

    # Count how many times the column 'position' appears
    (count,) = connection.execute(
        "SELECT COUNT(*) FROM pragma_table_info('task') WHERE name='position'"
    ).fetchone()

    # the position column exists, so no need to do anything
    if count > 0:
        return

    # the position column doesn't exist, so create it.
    connection.execute("ALTER TABLE task ADD COLUMN position INTEGER")

    parent_ids: list[tuple[int | None]] = connection.execute(
        "SELECT DISTINCT parent_id FROM task"
    ).fetchall()

    # The parent id might be none
    parent_ids.append((None,))

    for (parent_id,) in parent_ids:
        # get the child task ids with that parent.
        child_ids: list[tuple[int]] = connection.execute(
            "SELECT task_id FROM task WHERE (parent_id=? OR (? IS NULL AND parent_id is NULL)) ORDER BY task_id",
            (parent_id, parent_id),
        ).fetchall()

        # set the position to be the relative order of their task ids
        for position, (child_id,) in enumerate(child_ids):
            connection.execute(
                "UPDATE task SET position=? WHERE task_id=?",
                (position, child_id),
            )
