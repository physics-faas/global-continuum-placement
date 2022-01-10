from global_continuum_placement.domain.workload.workload import Workflow


def test_create_workload_from_dict():
    workflow_dict = {
        "name": "test",
        "objectives": {
            "Energy": "High",
            "Resilience": "Low",
        },
        "tasks": {
            "task1": {
                "resources": {"nb_cpu": 1},
                "next_tasks": ["task2"],
                "constraints": [{"site": "site3"}],
                "architecture": "X86_64",
            },
            "task2": {"resources": {"nb_cpu": 2}, "next_tasks": ["task3", "task4"]},
            "task3": {
                "resources": {"nb_cpu": 2},
            },
            "task4": {"resources": {"nb_cpu": 2}, "next_tasks": ["task5"]},
            "task5": {
                "resources": {"nb_cpu": 2, "memory_in_MB": 1000},
            },
        },
    }
    Workflow.create_from_dict(workflow_dict)
