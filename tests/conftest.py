import datetime

import pytest

import sqlite_setup
from tag.repo import TagRepo
from task.controller import TaskController
from task.repo import TaskRepo
from time_slice.repo import TimeSliceRepo


@pytest.fixture
def make_memory_connection():
    # Sqlite will kill the memory database if all connections to it are killed.
    stay_alive_connection = sqlite_setup.create_connection_factory(":memory:")()
    sqlite_setup.register_adapters()

    make_connection = sqlite_setup.create_connection_factory(":memory:")

    # this function closes the connection. Since we have stay_alive_connection,
    # the in memory database still exists, so we can reconnect to it.
    sqlite_setup.ensure_tables_created(make_connection)
    yield make_connection

    stay_alive_connection.close()


@pytest.fixture
def today():
    return datetime.datetime.today()


@pytest.fixture
def time_slice_repo(make_memory_connection: sqlite_setup.ConnectionFactory):
    return TimeSliceRepo(make_memory_connection)


@pytest.fixture
def tag_repo(make_memory_connection: sqlite_setup.ConnectionFactory):
    return TagRepo(make_memory_connection)


@pytest.fixture
def task_repo(make_memory_connection: sqlite_setup.ConnectionFactory):
    return TaskRepo(make_memory_connection)


@pytest.fixture
def task_controller(task_repo: TaskRepo):
    return TaskController(task_repo)
