import logging
from dataclasses import dataclass, field
from typing import Dict, List

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platfom_values import ArchitectureType
from global_continuum_placement.domain.platform.platform import Cluster, Platform
from global_continuum_placement.domain.scheduling_policies import first_fit
from global_continuum_placement.domain.workload.workload import (
    ClusterListPlacementConstraint,
    ClusterTypePlacementConstraint,
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
        list_constraints: ClusterListPlacementConstraint,
        type_constraint: ClusterTypePlacementConstraint,
        sites: List[Cluster],
    ) -> List[Cluster]:
        """
        Return a list of sites that fit the constraints

        All constraints are applied with a logical OR
        """
        cluster_that_fit: List[Cluster] = []

        if len(list_constraints.clusters) == 0 and type_constraint is None:
            return sites

        for constraint_cluster in list_constraints.clusters:
            for cluster in sites:
                if constraint_cluster == cluster.id and (
                    type_constraint is None
                    or type_constraint.cluster_type == cluster.type
                ):
                    cluster_that_fit.append(cluster)
                    logger.debug(
                        f"Found valid cluster constraint for cluster {cluster.id}"
                    )
            else:
                logger.debug("No valid constraints found")

        return cluster_that_fit

    @staticmethod
    def resolve_architecture_constraints(
        architecture_constraint: ArchitectureType, sites: List[Cluster]
    ) -> List[Cluster]:
        site_that_fit: List[Cluster] = []

        for site in sites:
            if site.architecture == architecture_constraint:
                site_that_fit.append(site)
        return site_that_fit

    @staticmethod
    def score_on_objectives(
        objectives: Dict[Objectives, Levels], valid_sites: List[Cluster]
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

        valid_sites: List[Cluster] = self.platform.sites

        # Apply filters
        # 1. Filter cluster that does not fit the constraints
        valid_sites = self.resolve_placement_constraints(
            function.cluster_list_placement_constraints,
            function.cluster_type_placement_constraints,
            valid_sites,
        )

        # 2. Filter on architecture constraint
        valid_sites = self.resolve_architecture_constraints(
            function.architecture_constraint, valid_sites
        )

        # 3. TODO Apply affinity constraints

        # Apply scoring functions
        # 1. Score on objectives
        # TODO also take into account function level objectives
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
