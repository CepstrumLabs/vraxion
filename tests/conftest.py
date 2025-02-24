import os
import pytest

from vraxion.orm import Table, Column, Database, ForeignKey
from vraxion.api import Api


TEST_DB_PATH = "./test.db"
@pytest.fixture
def api():
    return Api()

@pytest.fixture
def client(api):
    return api.test_session()


@pytest.fixture
def database():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = Database(TEST_DB_PATH)
    yield db
    os.remove(TEST_DB_PATH)


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author

@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)
    return Book