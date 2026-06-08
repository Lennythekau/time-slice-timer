import datetime
from dataclasses import dataclass

import pytest

import sqlite_setup
from tag.repo import TagRepo
from tag.service import TagService
from task.repo import TaskRepo
from task.service import TaskService
from time_slice.repo import TimeSliceRepo
from time_slice.stopwatch.model import Stopwatch
from user_session import UserSession


@dataclass
class MockTimer:
    def __post_init__(self):
        self.time: float = 0

    def get_time(self):
        return self.time

    def tick(self, amount: float):
        self.time = self.time + amount


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
def timer():
    return MockTimer()


@pytest.fixture
def stopwatch(timer: MockTimer):
    return Stopwatch(timer.get_time)


@pytest.fixture
def user_session(stopwatch: Stopwatch):
    return UserSession(stopwatch)


@pytest.fixture
def tag_service(user_session: UserSession, tag_repo: TagRepo):
    return TagService(user_session, tag_repo)


@pytest.fixture
def task_service(user_session: UserSession, task_repo: TaskRepo):
    return TaskService(user_session, task_repo)
