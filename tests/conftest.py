import pytest
from global_continuum_placement.container import ApplicationContainer


@pytest.fixture(scope="function")
def app():
    container = ApplicationContainer()
    yield container
