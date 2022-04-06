from global_continuum_placement.domain.platform.platform import Platform
from global_continuum_placement.domain.workload.workload_values import Objectives


def test_create_platform_from_dict():
    platform_dict = {
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
    platform = Platform.create_from_dict(platform_dict)
    assert len(platform.sites) == 3
    assert platform.sites[0].type is not None
    assert platform.sites[0].architecture is not None
    assert platform.sites[0].total_resources.nb_cpu >= 1
    assert platform.sites[0].objective_scores[Objectives.ENERGY] > 1
