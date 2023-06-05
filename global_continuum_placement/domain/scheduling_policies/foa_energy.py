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

    # To build from the Platform
    H = [0, 0, 1, 1, 1]

    #mc = [1, 2]
    mc = [4, 2, 1000] # number of machines per cluster

    #env = [0, 0, 1, 1, 0] # env i of task i

    Tmax = 200
    solver = 'CBC'
    verbosity = 0
    N = matrix.number_of_functions 
    K = matrix.number_of_containers
    p = matrix.functions_execution_time
    c = matrix.containers_execution_time
    p_tilde = matrix.functions_energy_consumption
    c_tilde = matrix.containers_energy_consumption
    env = matrix.containers_per_function
    
    allocation_x, allocation_y = lp_energy(N, H, K, c, p, c_tilde, p_tilde, mc, env, Tmax, solver, verbosity)
    
    print("Results of the LP: \n\n", allocation_x, allocation_y)

    
    #Converting the LP solution into the Global Continuum Solution:
    #solutions: Dict = {}
    #solutions["flowID"] = "FlowID"

    solution_list: List[Placement] = []

    for cluster_id in range(len(allocation_x)): # to take cluster id

        #solution_entry: Dict = {}
        #solution_entry["cluster"] = "cluster" + str(cluster_id)

        for function_id in range(len(allocation_x[cluster_id])): # to take the function id
            print("Function ID: ", function_id)
            if (allocation_x[cluster_id][function_id] == 1):
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