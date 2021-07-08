import logging
from typing import List

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import Platform, Site
from global_continuum_placement.domain.workload.workload import TaskDag, Workload, ResourceRequest, PlacementConstraint

logger = logging.getLogger(__name__)


def site_has_enough_resources(site: Site, resource_request: ResourceRequest):
    """
    Return True if the given site has enough resource to allocate the given resource request.
    """
    return (resource_request.memory_in_MB <= site.free_resources.memory_in_MB
            and resource_request.nb_gpu <= site.free_resources.nb_gpu
            and resource_request.nb_cpu <= site.free_resources.nb_cpu)


def resolve_constraints(constraints: List[PlacementConstraint], platform: Platform) -> List[Site]:
    """
    Return a list of sites that fit the constraints
    """
    site_that_fit: List[Site] = []

    for constraint in constraints:
        if constraint.site is not None:
            for site in platform.sites:
                if constraint.site == site.id:
                    site_that_fit.append(site)
                    logger.debug(f"Found valid site constraint for site {site.id}")
        elif constraint.site_type is not None:
            for site in platform.sites:
                # TODO Implement smarter scheduling policy!
                # Here we always schedule the task to the first site in the list
                if site.type is constraint.site_type:
                    site_that_fit.append(site)
                    logger.debug(f"Found valid site type constraint for site {site.id}")
        else:
            logger.debug(f"No valid constraints found")

    return site_that_fit


def schedule_task(task: TaskDag, platform: Platform) -> List[Placement]:
    placements: List[Placement] = []

    # Filter site that does not fi the constraints
    valid_sites: List[Site] = resolve_constraints(task.placement_constraints, platform)

    # Apply scheduling policy
    # TODO Make the scheduling policy configurable
    # FIST FIT
    # TODO Implement smarter scheduling policy!
    # Here we always schedule the task to the first site with enough available Resources
    for site in valid_sites:
        if site_has_enough_resources(site, task.resource_request):
            site.allocate(task)
            placements.append(Placement(site.id, task.id))

    # Recursion
    for task in task.next_task:
        placements.extend(schedule_task(task, platform))

    return placements


def schedule(workload: Workload, platform: Platform):
    placements: List[Placement] = []

    for workflow in workload.workflows.values():
        for task in workflow.tasks_dag.next_task():
            placements.extend(schedule_task(task, platform))

    return placements
