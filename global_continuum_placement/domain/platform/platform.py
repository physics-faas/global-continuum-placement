from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, cast

from ..workload.workload import ResourceRequest, TaskDag
from ..workload.workload_values import Objectives
from .platfom_values import ArchitectureType, ClusterType


@dataclass
class Resources:
    nb_cpu: int = field(default=0)
    nb_gpu: int = field(default=0)
    memory_in_MB: int = field(default=0)

    def allocate(self, resources: ResourceRequest) -> None:
        self.nb_cpu = self.nb_cpu - resources.nb_cpu
        self.nb_gpu = self.nb_gpu - resources.nb_gpu
        self.memory_in_MB = self.memory_in_MB - resources.memory_in_MB


class InvalidSiteDefinition(Exception):
    pass


@dataclass
class Cluster:
    id: str
    type: ClusterType
    total_resources: Resources
    free_resources: Resources
    allocated_tasks: List[TaskDag]
    # Each set of resource is considered homogeneous: Only one architecture per set of resources
    architecture: ArchitectureType
    # A score for each objectives
    objective_scores: Dict[Objectives, int]

    @classmethod
    def create_site_from_dict(
        cls, site_id: str, site_dict: Dict[str, Union[str, Dict[str, int]]]
    ) -> "Cluster":
        try:
            resources = cast(Dict[str, int], site_dict["resources"])
            type = cast(str, site_dict["type"])
            architecture_raw = cast(Optional[str], site_dict.get("architecture"))
            architecture = (
                ArchitectureType[architecture_raw.upper()]
                if architecture_raw
                else ArchitectureType.X86_64
            )
            scores = {objective: 1 for objective in Objectives}
            objectives_raw = (
                cast(Dict[str, int], site_dict["objective_scores"])
                if "objective_scores" in site_dict
                else {}
            )
            for objective, score in objectives_raw.items():
                scores[Objectives[objective.upper()]] = score

        except KeyError as err:
            raise InvalidSiteDefinition(
                f"Missing element in the Cluster definition: {err}"
            )
        return Cluster(
            id=site_id,
            type=ClusterType[type.upper()],
            total_resources=Resources(**resources),
            free_resources=Resources(**resources),
            allocated_tasks=[],
            architecture=architecture,
            objective_scores=scores,
        )

    def allocate(self, task: TaskDag) -> None:
        self.allocated_tasks.append(task)
        self.free_resources.allocate(task.resource_request)


@dataclass
class Platform:
    sites: List[Cluster] = field(default_factory=list)

    @classmethod
    def create_from_dict(cls, platform_dict: Dict) -> "Platform":
        sites: List[Cluster] = []
        for site_id, site in platform_dict.items():
            sites.append(Cluster.create_site_from_dict(site_id, site))
        return Platform(sites)


def site_has_enough_resources(site: Cluster, resource_request: ResourceRequest) -> bool:
    """
    Return True if the given cluster has enough resource to allocate the given resource request.
    """
    return (
        resource_request.memory_in_MB <= site.free_resources.memory_in_MB
        and resource_request.nb_gpu <= site.free_resources.nb_gpu
        and resource_request.nb_cpu <= site.free_resources.nb_cpu
    )
