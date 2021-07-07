import pytest

from changeme.container import ApplicationContainer


@pytest.fixture(scope="function")
def app():
    container = ApplicationContainer()
    yield container
