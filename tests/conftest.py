"""Test fixtures for the Vraxion framework.

This module contains pytest fixtures that are used across the test suite to set up
common test scenarios and dependencies.
"""

import os
import pytest

from vraxion.orm import Table, Column, Database, ForeignKey
from vraxion.api import Api


TEST_DB_PATH = "./test.db"
@pytest.fixture
def api():
    """Create a new API instance for testing.

    Returns:
        Api: A fresh instance of the Vraxion API.
    """
    return Api()

@pytest.fixture
def client(api):
    """Create a test client for making requests to the API.

    Args:
        api (Api): The API fixture instance.

    Returns:
        TestClient: A configured test client for making HTTP requests.
    """
    return api.test_session()


@pytest.fixture
def database():
    """Create a temporary test database.

    Creates a fresh database for each test and cleans it up afterwards.

    Yields:
        Database: A configured database instance.
    """
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = Database(TEST_DB_PATH)
    yield db
    os.remove(TEST_DB_PATH)


@pytest.fixture
def Author():
    """Create a sample Author model for testing.

    Returns:
        Table: An Author model class with name and age columns.
    """
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author

@pytest.fixture
def Book(Author):
    """Create a sample Book model for testing.

    Args:
        Author (Table): The Author model class to link as a foreign key.

    Returns:
        Table: A Book model class with title, published status, and author reference.
    """
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)
    return Book