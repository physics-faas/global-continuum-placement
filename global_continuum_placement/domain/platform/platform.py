from dataclasses import dataclass, field
from typing import Dict, List, Union

from ..workload.workload import ResourceRequest, TaskDag
from .platfom_values import SiteType


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
class Site:
    id: str
    type: SiteType
    total_resources: Resources
    free_resources: Resources
    allocated_tasks: List[TaskDag]

    @classmethod
    def create_site_from_dict(
        cls, site_id: str, site_dict: Dict[str, Union[str, Dict[str, int]]]
    ) -> "Site":
        try:
            resources = site_dict["resources"]
            type = site_dict["type"]
        except KeyError as err:
            raise InvalidSiteDefinition(
                f"Missing element in the Site definition: {err}"
            )
        return Site(
            id=site_id,
            type=SiteType[type.upper()],
            total_resources=Resources(**resources),
            free_resources=Resources(**resources),
            allocated_tasks=[],
        )

    def allocate(self, task: TaskDag):
        self.allocated_tasks.append(task)
        self.free_resources.allocate(task.resource_request)


@dataclass
class Platform:
    sites: List[Site] = field(default_factory=list)

    @classmethod
    def create_from_dict(cls, platform_dict: Dict) -> "Platform":
        sites: List[Site] = []
        for site_id, site in platform_dict.items():
            sites.append(Site.create_site_from_dict(site_id, site))
        return Platform(sites)


def site_has_enough_resources(site: Site, resource_request: ResourceRequest):
    """
    Return True if the given site has enough resource to allocate the given resource request.
    """
    return (
        resource_request.memory_in_MB <= site.free_resources.memory_in_MB
        and resource_request.nb_gpu <= site.free_resources.nb_gpu
        and resource_request.nb_cpu <= site.free_resources.nb_cpu
    )
