from typing import List

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import (
    Site,
    site_has_enough_resources,
)
from global_continuum_placement.domain.scheduling_policies.exceptions import (
    NotEnoughResourcesException,
)


def apply(task, valid_sites: List[Site]):
    for site in valid_sites:
        if site_has_enough_resources(site, task.resource_request):
            site.allocate(task)
            return Placement(site.id, task.id)
    raise NotEnoughResourcesException(
        f"Not enough resources to schedule task {task.id}")
