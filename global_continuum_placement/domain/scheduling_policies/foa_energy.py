from typing import List, Union

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import (
    Cluster,
    Platform,
    site_has_enough_resources,
)
from global_continuum_placement.domain.scheduling_policies.exceptions import (
    NotEnoughResourcesException,
)
from global_continuum_placement.domain.workload.workload import (
    Flow,
    FunctionsMatrix,
    TaskDag,
)
from lp_pulp import *


#def apply(task: Union[TaskDag, Flow], valid_sites: List[Cluster]) -> Placement:
def apply(matrix: FunctionsMatrix, platform: Platform) -> List[Placement]:

    solver = 'CBC'
    verbosity = 0
    N = matrix.number_of_functions 
    K = matrix.number_of_containers
    p = matrix.functions_execution_time
    c = matrix.containers_execution_time
    p_tilde = matrix.functions_energy_consumption
    c_tilde = matrix.containers_energy_consumption
    env = matrix.containers_per_function

    # To build from the Platform
    H = list(range(len(platform.sites)))

    # To retrieve the number of resources per cluster
    mc: List[int] = [cluster.total_resources.nb_cpu for cluster in platform.sites]

    """
    Compute the max Cmax and Tmax allowed. Requirement: c and p, and b and d should have the same dimension, then:
    if we place all jobs and environments on one machine, 
    get the total cost on the worst machine, 
    and the total time on the worst machine.
    The worst cost and the worst time might not be on the same machine.
    """
    
    Tmax: int = 0
    for i in H:
        print("Cluster: ", i)
        curr_time = sum(p[i]) + sum(c[i])
        print(curr_time)
        if curr_time > Tmax:
            Tmax = curr_time
    print("Computed TMax: ", Tmax)
    
    allocation_x, allocation_y = lp_energy(N, H, K, c, p, c_tilde, p_tilde, mc, env, Tmax, solver, verbosity)
    
    print("Results of the X: \n\n", allocation_x)
    print("Results of the Y: \n\n", allocation_y)

    
    #Converting the LP solution into the Global Continuum Solution:
    #solutions: Dict = {}
    #solutions["flowID"] = "FlowID"

    solution_list: List[Placement] = []

    for function_id in range(len(allocation_x)): # to take cluster id

        #solution_entry: Dict = {}
        #solution_entry["cluster"] = "cluster" + str(cluster_id)

        for cluster_id in range(len(allocation_x[function_id])): # to take the function id
            print("Function ID: ", function_id)
            if (allocation_x[function_id][cluster_id] == 1):
                #solution_entry["resource_id"] = "function" + str(function_id)
                solution_list.append(Placement("cluster" + str(cluster_id), "function" + str(function_id)))
            
                #solution_list.append(solution_entry)
    
    #solutions["allocations"] = solution_list
    #print("\n\nSolutions list: ", solution_list)

    #print("Reverting Matrix dimensions")
    #return next_tasks[0]
    return solution_list
    
    """
    for site in valid_sites:
        if site_has_enough_resources(site, task.resource_request):
            site.allocate(task)
            return Placement(site.id, task.id)
    
    raise NotEnoughResourcesException(
        f"Not enough resources to schedule task {task.id}")
    """