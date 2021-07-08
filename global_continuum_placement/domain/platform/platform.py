from dataclasses import field, dataclass
from typing import List, Dict

from .platfom_values import SiteType
from ..events import InitializeCommand
from ..workload.workload import TaskDag, ResourceRequest


@dataclass
class Resources:
    nb_cpu: int = field(default=0)
    nb_gpu: int = field(default=0)
    memory_in_MB: int = field(default=0)

    def allocate(self, resources: ResourceRequest) -> None:
        self.nb_cpu = self.nb_cpu - resources.nb_cpu
        self.nb_gpu = self.nb_gpu - resources.nb_gpu
        self.memory_in_MB = self.memory_in_MB - resources.memory_in_MB


@dataclass
class Site:
    id: str
    type: SiteType
    total_resources: Resources
    free_resources: Resources
    allocated_tasks: List[TaskDag]

    @classmethod
    def create_site_from_dict(cls, site_dict: Dict) -> "Site":
        resources = site_dict["resources"]
        return Site(id=site_dict["id"],
                    type=SiteType[site_dict["type"].to_uppercase()],
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
    def create_site_from_init_command(cls, cmd: InitializeCommand) -> "Platform":
        sites: List[Site] = []
        for site in cmd.platform:
            sites.append(Site.create_site_from_dict(site))
        return Platform(sites)
