from typing import List

import pytest

from global_continuum_placement.application.scheduler import SchedulerService
from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import Platform
from global_continuum_placement.domain.scheduling_policies.exceptions import (
    NotEnoughResourcesException,
)
from global_continuum_placement.domain.workload.workload import Workflow


def test_scheduler_schedule_without_constraints(platform_dict, workflow_dict):
    workflow = Workflow.create_from_dict(workflow_dict)
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.workflows[workflow.id] = workflow
    placements: List[Placement] = scheduler.schedule()
    assert len(placements) == len(workflow_dict)


@pytest.mark.parametrize(
    "workflow_dict",
    [
        pytest.param(
            {"task1": {"resources": {"nb_cpu": 2000}}},
            id="not enough CPU resources",
        ),
        pytest.param(
            {"task1": {"resources": {"nb_cpu": 1, "nb_gpu": 2000}}},
            id="not enough GPU resources",
        ),
        pytest.param(
            {"task1": {"resources": {"nb_cpu": 1, "nb_gpu": 1, "memory_in_MB": 100e6}}},
            id="not enough Memory resources",
        ),
    ],
)
def test_scheduler_schedule_not_enough_resources(
    platform_dict,
    workflow_dict,
):
    workflow = Workflow.create_from_dict(workflow_dict)
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.workflows[workflow.id] = workflow
    with pytest.raises(NotEnoughResourcesException):
        scheduler.schedule()


@pytest.mark.parametrize(
    "workflow_dict,expected_placements",
    [
        pytest.param(
            {"task1": {"resources": {"nb_cpu": 1}, "constraints": [{"site": "site1"}]}},
            [Placement("site1", "task1")],
            id="site constraints",
        ),
        pytest.param(
            {
                "task1": {
                    "resources": {"nb_cpu": 1},
                    "constraints": [{"site_type": "HPC"}],
                }
            },
            [Placement("site3", "task1")],
            id="site type constraints",
        ),
        pytest.param(
            {
                "task1": {
                    "resources": {"nb_cpu": 1},
                    "constraints": [{"site_type": "Cloud"}, {"site_type": "HPC"}],
                }
            },
            [Placement("site3", "task1")],
            id="multi site type constraints",
        ),
    ],
)
def test_scheduler_schedule_site_constraints(
    platform_dict, workflow_dict, expected_placements
):
    workflow = Workflow.create_from_dict(workflow_dict)
    platform = Platform.create_from_dict(platform_dict)
    scheduler = SchedulerService(platform)
    scheduler.workload.workflows[workflow.id] = workflow
    placements: List[Placement] = scheduler.schedule()
    assert placements == expected_placements
