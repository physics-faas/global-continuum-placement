import pytest

from global_continuum_placement.container import ApplicationContainer


@pytest.fixture(scope="function")
def app():
    container = ApplicationContainer()
    yield container


@pytest.fixture
def platform_dict():
    return {
        "site1": {
            "type": "Edge",
            "resources": {"nb_cpu": 1, "nb_gpu": 0, "memory_in_MB": 1024},
        },
        "site2": {
            "type": "Edge",
            "resources": {"nb_cpu": 2, "nb_gpu": 1, "memory_in_MB": 4096},
            "architecture": "arm64",
        },
        "site3": {
            "type": "HPC",
            "resources": {"nb_cpu": 1000, "nb_gpu": 50, "memory_in_MB": 16e6},
        },
    }


@pytest.fixture
def workflow_dict():
    return {
        "task1": {"resources": {"nb_cpu": 1}, "next_tasks": ["task2"]},
        "task2": {"resources": {"nb_cpu": 2}, "next_tasks": ["task3", "task4"]},
        "task3": {
            "resources": {"nb_cpu": 2},
        },
        "task4": {"resources": {"nb_cpu": 2}, "next_tasks": ["task5"]},
        "task5": {
            "resources": {"nb_cpu": 2, "memory_in_MB": 1000},
        },
    }
