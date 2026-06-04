from sqlite_setup import ConnectionFactory
from tag.repo import TagRepo
import sqlite_setup
import pytest


@pytest.fixture
def make_memory_connection():
    # Sqlite will kill the memory database if all connections to it are killed.
    stay_alive_connection = sqlite_setup.create_connection_factory(":memory:")()

    make_connection = sqlite_setup.create_connection_factory(":memory:")

    # this function closes the connection. Since we have stay_alive_connection,
    # the in memory database still exists, so we can reconnect to it.
    sqlite_setup.ensure_tables_created(make_connection)
    yield make_connection

    stay_alive_connection.close()


@pytest.fixture
def tag_repo(make_memory_connection: ConnectionFactory):
    return TagRepo(make_memory_connection)
