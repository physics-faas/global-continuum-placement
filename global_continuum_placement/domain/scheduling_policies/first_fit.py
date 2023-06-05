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
from lp_pulp import *


def apply(task: Union[TaskDag, Flow], valid_sites: List[Cluster]) -> Placement:
    """
    # build mc for the lp: a list with the number of machines per cluster

    mc: List[float] = []
    for site in valid_sites:
        mc.append(site.total_resources)
    H = list(range(len(mc)))

    print("\n @@## mc: ", mc)
    print("\n @@## H: ", H)
    
    Tmax = 200
    solver = 'CBC'
    verbosity = 0
    lp_energy(N, H, K, c, p, c_tilde, p_tilde, mc, env, Tmax, solver, verbosity)
    """

    for site in valid_sites:
        if site_has_enough_resources(site, task.resource_request):
            site.allocate(task)
            return Placement(site.id, task.id)
    raise NotEnoughResourcesException(
        f"Not enough resources to schedule task {task.id}")
