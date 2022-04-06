import logging
from dataclasses import dataclass, field
from typing import Dict, List

from global_continuum_placement.application.platform_service import IPlatformService
from global_continuum_placement.application.schedule_result_publisher import (
    IResultPublisher,
)
from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platfom_values import ArchitectureType
from global_continuum_placement.domain.platform.platform import Cluster, Platform
from global_continuum_placement.domain.scheduling_policies import first_fit
from global_continuum_placement.domain.workload.workload import (
    Application,
    ClusterListPlacementConstraint,
    ClusterTypePlacementConstraint,
    TaskDag,
)
from global_continuum_placement.domain.workload.workload_values import (
    Levels,
    Objectives,
)

logger = logging.getLogger(__name__)


@dataclass
class SchedulerService:
    platform_service: IPlatformService
    result_publisher: IResultPublisher
    policy: str = "first_fit"

    @staticmethod
    def resolve_placement_constraints(
        list_constraints: ClusterListPlacementConstraint,
        type_constraint: ClusterTypePlacementConstraint,
        clusters: List[Cluster],
    ) -> List[Cluster]:
        """
        Return a list of clusters that fit the constraints

        All constraints are applied with a logical OR
        """
        cluster_that_fit: List[Cluster] = []

        if len(list_constraints.clusters) == 0:
            if type_constraint is None:
                return clusters
            else:
                for cluster in clusters:
                    if type_constraint.cluster_type == cluster.type:
                        cluster_that_fit.append(cluster)
                        logger.debug(
                            f"Found valid cluster type constraint for cluster {cluster.id}"
                        )

        for constraint_cluster in list_constraints.clusters:
            for cluster in clusters:
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
        self,
        platform: Platform,
        function: TaskDag,
        objectives: Dict[Objectives, Levels],
    ) -> List[Placement]:
        placements: List[Placement] = []

        valid_sites: List[Cluster] = platform.sites

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
            placements.extend(self.schedule_function(platform, function, objectives))

        return placements

    async def schedule_application(
        self,
        application: Application,
        raw_application: Dict = field(default_factory=dict),
    ) -> List[Placement]:
        placements: List[Placement] = []

        platform = await self.platform_service.get_platform()

        placements.extend(
            self.schedule_function(
                platform, application.functions_dag, application.objectives
            )
        )

        # FIXME: Reset resource availability fields because we do not access to the API that updates these values when the application is finished
        for cluster in platform.sites:
            cluster.reset_resource_availability()
        await self.result_publisher.publish(raw_application, platform, placements)

        return placements
