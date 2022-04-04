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
            "architecture": "x86_64",
            "objective_scores": {"Energy": 60, "Availability": 5, "Performance": 25},
        },
        "site2": {
            "type": "Edge",
            "resources": {"nb_cpu": 2, "nb_gpu": 1, "memory_in_MB": 4096},
            "architecture": "arm64",
            "objective_scores": {"Energy": 100, "Availability": 30, "Performance": 50},
        },
        "site3": {
            "type": "HPC",
            "resources": {"nb_cpu": 1000, "nb_gpu": 50, "memory_in_MB": 16e6},
            "objective_scores": {"Energy": 10, "Availability": 80, "Performance": 100},
        },
    }


@pytest.fixture
def workflow_dict():
    return {
        "functions": [
            {"id": "task1", "resources": {"nb_cpu": 1}, "sequence": 1},
            {"id": "task2", "resources": {"nb_cpu": 2}, "sequence": 2},
            {"id": "task3", "resources": {"nb_cpu": 2}, "sequence": 3},
            {"id": "task4", "resources": {"nb_cpu": 2}, "sequence": 4},
            {
                "id": "task5",
                "resources": {"nb_cpu": 2, "memory_in_MB": 1000},
                "sequence": 5,
            },
        ]
    }
