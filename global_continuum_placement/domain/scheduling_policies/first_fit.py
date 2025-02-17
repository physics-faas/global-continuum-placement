from typing import List, Union

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import (
    Cluster,
    site_has_enough_resources,
)
from global_continuum_placement.domain.scheduling_policies.exceptions import (
    NotEnoughResourcesException,
)
from global_continuum_placement.domain.workload.workload import Flow, TaskDag


def apply(task: Union[TaskDag, Flow], valid_sites: List[Cluster]) -> Placement:
    placement: Placement = None
    for site in valid_sites:
        if site_has_enough_resources(site, task.resource_request):
            if placement is None:
                site.allocate(task)
                placement = Placement(site.id, task.id)
            else:
                placement.fallback_cluster = site.id
                return placement
    if placement is not None:
        return placement
    raise NotEnoughResourcesException(
        f"Not enough resources to schedule task {task.id}")
