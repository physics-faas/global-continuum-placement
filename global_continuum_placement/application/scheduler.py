import logging
from dataclasses import dataclass, field
from typing import Dict, List

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platfom_values import ArchitectureType
from global_continuum_placement.domain.platform.platform import Platform, Site
from global_continuum_placement.domain.scheduling_policies import first_fit
from global_continuum_placement.domain.workload.workload import (
    PlacementConstraint,
    TaskDag,
    Workload,
)
from global_continuum_placement.domain.workload.workload_values import (
    Levels,
    Objectives,
)

logger = logging.getLogger(__name__)


@dataclass
class SchedulerService:
    # TODO  move them to a DB
    platform: Platform = None
    workload: Workload = field(default_factory=Workload.create)
    policy: str = "first_fit"

    @staticmethod
    def resolve_placement_constraints(
        constraints: List[PlacementConstraint], sites: List[Site]
    ) -> List[Site]:
        """
        Return a list of sites that fit the constraints

        All constraints are applied with a logical OR
        """
        site_that_fit: List[Site] = []

        if len(constraints) == 0:
            return sites

        for constraint in constraints:
            if constraint.cluster is not None:
                for site in sites:
                    if constraint.cluster == site.id:
                        site_that_fit.append(site)
                        logger.debug(
                            f"Found valid cluster constraint for cluster {site.id}"
                        )
            elif constraint.cluster_type is not None:
                for site in sites:
                    # TODO Implement smarter scheduling policy!
                    # Here we always schedule the function to the first cluster in the list
                    if site.type.name == constraint.cluster_type.name:
                        site_that_fit.append(site)
                        logger.debug(
                            f"Found valid cluster type constraint for cluster {site.id}"
                        )
            else:
                logger.debug("No valid constraints found")

        return site_that_fit

    @staticmethod
    def resolve_architecture_constraints(
        architecture_constraint: ArchitectureType, sites: List[Site]
    ) -> List[Site]:
        site_that_fit: List[Site] = []

        for site in sites:
            if site.architecture == architecture_constraint:
                site_that_fit.append(site)
        return site_that_fit

    @staticmethod
    def score_on_objectives(
        objectives: Dict[Objectives, Levels], valid_sites: List[Site]
    ) -> Dict[str, float]:
        scores: Dict[str, float] = {site.id: 0 for site in valid_sites}
        for objective, level in objectives.items():
            for site in valid_sites:
                scores[site.id] = scores[site.id] + (
                    site.objective_scores[objective] * level.value
                )
        return scores

    def schedule_function(
        self, function: TaskDag, objectives: Dict[Objectives, Levels]
    ) -> List[Placement]:
        placements: List[Placement] = []

        valid_sites: List[Site] = self.platform.sites

        # Apply filters
        # 1. Filter cluster that does not fit the constraints
        valid_sites = self.resolve_placement_constraints(
            function.placement_constraints, valid_sites
        )

        # 2. Filter on architecture constraint
        valid_sites = self.resolve_architecture_constraints(
            function.architecture_constraint, valid_sites
        )

        # 3. TODO Apply affinity constraints

        # Apply scoring functions
        # 1. Score on objectives
        scores = self.score_on_objectives(objectives, valid_sites)

        # Sort with the highest score first
        valid_sites.sort(key=lambda cluster: scores[cluster.id], reverse=True)
        for site in valid_sites:
            logger.info(
                "Score: function=%s cluster=%s score=%s",
                function.id,
                site.id,
                scores[site.id],
            )

        # Apply scheduling policy
        # TODO Implement smarter scheduling policy!
        if self.policy == "first_fit":
            placement = first_fit.apply(function, valid_sites)
        else:
            raise Exception(f"Unimplemented policy {self.policy}")
        # Here we always schedule the function to the first cluster with enough available Resources
        placements.append(placement)

        # Recursion
        for function in function.next_tasks:
            placements.extend(self.schedule_function(function, objectives))

        return placements

    def schedule(self) -> List[Placement]:
        placements: List[Placement] = []

        for workflow in self.workload.applications.values():
            placements.extend(
                self.schedule_function(workflow.functions_dag, workflow.objectives)
            )

        return placements
