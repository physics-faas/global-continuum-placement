from typing import List

import pytest

from global_continuum_placement.application.scheduler import SchedulerService
from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import Platform
from global_continuum_placement.domain.scheduling_policies.exceptions import (
    NotEnoughResourcesException,
)
from global_continuum_placement.domain.workload.workload import (
    Application,
    UnknownArchitectureError,
)


def test_scheduler_schedule_without_constraints(platform_dict, workflow_dict):
    workflow = Application.create_from_application(workflow_dict)
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.applications[workflow.id] = workflow
    placements: List[Placement] = scheduler.schedule()
    assert len(placements) == len(workflow_dict["functions"])


@pytest.mark.parametrize(
    "workflow_dict",
    [
        pytest.param(
            {"id": "task1", "annotations": {"sizingCores": 2000}},
            id="not enough CPU resources",
        ),
        pytest.param(
            {"id": "task1", "annotations": {"sizingCores": 1, "sizingMB": 100e6}},
            id="not enough Memory resources",
        ),
    ],
)
def test_scheduler_schedule_not_enough_resources(
        platform_dict,
        workflow_dict,
):
    workflow = Application.create_from_application({"functions": [workflow_dict]})
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.applications[workflow.id] = workflow
    with pytest.raises(NotEnoughResourcesException):
        scheduler.schedule()


@pytest.mark.parametrize(
    "workflow_dict,expected_placements",
    [
        pytest.param(
            {
                "id": "task1", "resources": {"nb_cpu": 1}, "allocations": ["site1"],
            },
            [Placement("site1", "task1")],
            id="cluster constraints",
        ),
        pytest.param(
            {
                "id": "task1",
                "resources": {"nb_cpu": 1},
                "annotations": {"locality": "HPC"},
            },
            [Placement("site3", "task1")],
            id="cluster type constraints",
        ),
    ],
)
def test_scheduler_schedule_site_constraints(
        platform_dict, workflow_dict, expected_placements
):
    workflow = Application.create_from_application({"functions": [workflow_dict]})
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.applications[workflow.id] = workflow
    placements: List[Placement] = scheduler.schedule()
    assert placements == expected_placements


def test_scheduler_architecture_invalid_constraint():
    workflow_dict = {
        "functions": [{"id": "task1", "resources": {"nb_cpu": 1}, "annotations": {"architecture": "NOTEXITS"}}]
    }
    with pytest.raises(UnknownArchitectureError):
        Application.create_from_application(workflow_dict)


@pytest.mark.parametrize(
    "workflow_dict,expected_placements",
    [
        pytest.param(
            {"id": "taskARM", "resources": {"nb_cpu": 1}, "annotations": {"architecture": "arm64"}},
            [Placement("site2", "taskARM")],
            id="arm64 constraint",
        ),
        pytest.param(
            {"id": "taskX86", "resources": {"nb_cpu": 1}, "annotations": {"architecture": "x86_64"}},
            [Placement("site1", "taskX86")],
            id="x86_64 constraint",
        ),
    ],
)
def test_scheduler_architecture_constraints(
        platform_dict, workflow_dict, expected_placements
):
    workflow = Application.create_from_application({"functions": [workflow_dict]})
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.applications[workflow.id] = workflow
    placements: List[Placement] = scheduler.schedule()
    assert placements == expected_placements


@pytest.mark.parametrize(
    "platform_dict,workflow_dict,expected_placements",
    [
        pytest.param(
            {
                "site1": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 1,
                        "Resilience": 5,
                        "Performance": 25,
                    },
                },
                "site2": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 30,
                        "Performance": 50,
                    },
                },
            },
            {
                "functions": [{"id": "task1", "resources": {"nb_cpu": 1}}],
                "objectives": {"Energy": "High"},
            },
            [Placement("site2", "task1")],
            id="mono objective",
        ),
        pytest.param(
            {
                "site1": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 5,
                        "Performance": 25,
                    },
                },
                "site2": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 30,
                        "Performance": 50,
                    },
                },
            },
            {
                "functions": [{"id": "task1", "resources": {"nb_cpu": 1}}],
                "objectives": {"Energy": "Medium"},
            },
            [Placement("site1", "task1")],
            id="mono objective equals",
        ),
        pytest.param(
            {
                "site1": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 30,
                        "Performance": 25,
                    },
                },
                "site2": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 100,
                        "Performance": 50,
                    },
                },
            },
            {
                "functions": [{"id": "task1", "resources": {"nb_cpu": 1}}],
                "objectives": {"Energy": "High", "Resilience": "High"},
            },
            [Placement("site2", "task1")],
            id="two objectives same level",
        ),
        pytest.param(
            {
                "site1": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 30,
                        "Performance": 25,
                    },
                },
                "site2": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 100,
                        "Performance": 50,
                    },
                },
            },
            {
                "functions": [{"id": "task1", "resources": {"nb_cpu": 1}}],
                "objectives": {"Energy": "High", "Resilience": "Low"},
            },
            [Placement("site2", "task1")],
            id="two objectives different level",
        ),
        pytest.param(
            {
                "site1": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 30,
                        "Performance": 25,
                    },
                },
                "site2": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 100,
                        "Performance": 50,
                    },
                },
                "site3": {
                    "type": "Edge",
                    "resources": {"nb_cpu": 1},
                    "objective_scores": {
                        "Energy": 100,
                        "Resilience": 10,
                        "Performance": 90,
                    },
                },
            },
            {
                "functions": [{"id": "task1", "resources": {"nb_cpu": 1}}],
                "objectives": {
                    "Energy": "High",
                    "Resilience": "Low",
                    "Performance": "Medium",
                },
            },
            [Placement("site3", "task1")],
            id="three objectives different level",
        ),
    ],
)
def test_objective_scoring(platform_dict, workflow_dict, expected_placements):
    workflow = Application.create_from_application(workflow_dict)
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.applications[workflow.id] = workflow
    placements: List[Placement] = scheduler.schedule()
    assert placements == expected_placements
