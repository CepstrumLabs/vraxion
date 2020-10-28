import pytest

from api import Api


@pytest.fixture
def test_api():
    return Api()