import logging
from dataclasses import dataclass, field
from typing import List

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import Platform, Site
from global_continuum_placement.domain.scheduling_policies import first_fit
from global_continuum_placement.domain.workload.workload import (
    PlacementConstraint,
    TaskDag,
    Workload,
)

logger = logging.getLogger(__name__)


@dataclass
class SchedulerService:
    # TODO  move them to a DB
    policy: str
    platform: Platform = field(default=None)
    workload: Workload = field(default_factory=Workload.create)

    def resolve_constraints(self, constraints: List[PlacementConstraint]) -> List[Site]:
        """
        Return a list of sites that fit the constraints

        All constraints are applied with a logical OR
        """
        site_that_fit: List[Site] = []
        platform = self.platform

        if len(constraints) == 0:
            return platform.sites

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
                    if site.type.name == constraint.site_type.upper():
                        site_that_fit.append(site)
                        logger.debug(
                            f"Found valid site type constraint for site {site.id}"
                        )
            else:
                logger.debug("No valid constraints found")

        return site_that_fit

    def schedule_task(self, task: TaskDag) -> List[Placement]:
        placements: List[Placement] = []

        # Filter site that does not fi the constraints
        valid_sites: List[Site] = self.resolve_constraints(task.placement_constraints)

        # Apply scheduling policy
        # TODO Implement smarter scheduling policy!
        if self.policy == "first_fit":
            placement = first_fit.apply(task, valid_sites)
        else:
            raise Exception(f"Unimplemented policy {self.policy}")
        # Here we always schedule the task to the first site with enough available Resources
        placements.append(placement)

        # Recursion
        for task in task.next_tasks:
            placements.extend(self.schedule_task(task))

        return placements

    def schedule(self):
        placements: List[Placement] = []

        for workflow in self.workload.workflows.values():
            placements.extend(self.schedule_task(workflow.tasks_dag))

        return placements
