from typing import List

from foa_energy_lib import compute_max_cmax_and_tmax, minimize_cmax_and_tmax
from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import Platform
from global_continuum_placement.domain.workload.workload import FunctionsMatrix


def apply(matrix: FunctionsMatrix, platform: Platform) -> List[Placement]:
    print("---------- Calling the scheduler !!!!!!")
    N = matrix.number_of_functions
    K = matrix.number_of_containers
    p = matrix.functions_execution_time
    c = matrix.containers_execution_time
    p_tilde = matrix.functions_energy_consumption
    c_tilde = matrix.containers_energy_consumption
    env = matrix.containers_per_function

    # To build from the Platform
    H = len(platform.sites)

    # To retrieve the number of resources per cluster
    mc: List[int] = [cluster.total_resources.nb_cpu for cluster in platform.sites]

    # Compute the Tmax allowed: the total time on the worst machine.
    Tmax: float = 0
    for i in range(0, H):
        curr_time = sum(p[i]) + sum(c[i])
        if curr_time > Tmax:
            Tmax = curr_time

    Cmax, Tmax = compute_max_cmax_and_tmax(p, c, p_tilde, c_tilde, H, N, K)
    status_new, allocation_x, allocation_y = minimize_cmax_and_tmax(Cmax, Tmax, H, N, K, c, p, c_tilde, p_tilde, env, mc)
    solution_list: List[Placement] = []

    # Create the placement to be returned using the cluster_id and function_id
    for function_id in range(len(allocation_x)):
        for cluster_id in range(len(allocation_x[function_id])):
            if (allocation_x[function_id][cluster_id] == 1):
                solution_list.append(Placement("cluster" + str(cluster_id), "function" + str(function_id)))

    return solution_list
