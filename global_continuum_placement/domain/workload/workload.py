import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from lp_pulp import *

from ..platform import platform
from ..platform.platfom_values import ArchitectureType, ClusterType
from .workload_values import Levels, Objectives, TaskState


class UnknownArchitectureError(BaseException):
    pass


@dataclass
class ResourceRequest:
    nb_cpu: int = field(default=0)
    nb_gpu: int = field(default=0)
    memory_in_MB: int = field(default=0)


@dataclass
class ClusterListPlacementConstraint:
    clusters: List[str] = field(default_factory=list)


@dataclass
class ClusterTypePlacementConstraint:
    cluster_type: Optional[ClusterType] = None


@dataclass
class PerformanceKnown:
    archictecture_used: List[str] = field(default="None")
    cpu_speed: List[float] = field(default=0)
    memory_in_MB: List[float] = field(default=0)
    function_execution_time: List[float] = field(default=0)
    function_energy_consumed: List[float] = field(default=0)
    container_execution_time: List[float] = field(default=0)
    container_energy_consumed: List[float] = field(default=0)
    container_required: str = field(default="None")


def get_architecture(architecture_raw: str) -> ArchitectureType:
    try:
        return (
            ArchitectureType[architecture_raw.upper()]
            if architecture_raw
            else ArchitectureType.X86_64
        )
    except (KeyError, ValueError):
        raise UnknownArchitectureError


@dataclass
class TaskDag:
    id: str
    architecture_constraint: ArchitectureType
    resource_request: ResourceRequest
    # WARNING: a list of cluster placement constraints defined are resolved with a logical OR.
    cluster_list_placement_constraints: ClusterListPlacementConstraint
    cluster_type_placement_constraints: ClusterTypePlacementConstraint
    objective: Optional[Tuple[Objectives, Levels]] = None
    state: TaskState = field(default=TaskState.NONE)
    next_tasks: List["TaskDag"] = field(default_factory=list)
    performance_known: Optional[PerformanceKnown] = None

    @staticmethod
    def create_dag_from_functions_sequence(functions: List[Dict]) -> "TaskDag":

        print("\n #####  Reading and building the dag")

        # Be sure that the functions are sorted in reverse order
        if len(functions) > 1:
            functions = sorted(
                functions, key=lambda elem: elem.get("sequence"), reverse=True
            )

        """
        next_tasks: List[float] = []
        p: List[float] = []
        c: List[float] = []
        p_tilde: List[float] = []
        c_tilde: List[float] = []
        env: List[float] = []
        container_image_ids = {}
        
        for function in functions:
            print("Function here: ", function)
            annotations = function.get("annotations", {})
            performance = annotations.get("performance_known", {})
            print("Annotations: ", annotations)
            p.append(performance.get("function_execution_time", 0))
            c.append(performance.get("function_energy_consumed", 0))
            p_tilde.append(performance.get("container_execution_time", 0))
            c_tilde.append(performance.get("container_energy_consumed", 0))
            container_required = performance.get("container_required", None)

            # Computing the list env: env i of task i
            if (container_required not in container_image_ids):
                new_container_id = len(container_image_ids)
                container_image_ids[container_required] = new_container_id
            env.append(container_image_ids.get(container_required))

        p = [[p[j][i] for j in range(len(p))] for i in range(len(p[0]))]
        c = [[c[j][i] for j in range(len(c))] for i in range(len(c[0]))]
        p_tilde = [[p_tilde[j][i] for j in range(len(p_tilde))] for i in range(len(p_tilde[0]))]
        c_tilde = [[c_tilde[j][i] for j in range(len(c_tilde))] for i in range(len(c_tilde[0]))]
        print("p: ", p)
        print("c: ", c)
        print("p_tilde: ", p_tilde)
        print("c_tilde: ", c_tilde)
        print("env: ", env)

        N = list(range(len(functions)))
        #H = list(range(len(set(env))))
        K = list(range(len(set(env))))

        print("N: ", N)
        print("K: ", K)

        H = [0, 0, 1, 1, 1]

        #mc = [1, 2]
        mc = [4, 2, 1000] # number of machines per cluster

        #env = [0, 0, 1, 1, 0] # env i of task i

        Tmax = 200
        solver = 'CBC'
        verbosity = 0
        allocation_x, allocation_y = lp_energy(N, H, K, c, p, c_tilde, p_tilde, mc, env, Tmax, solver, verbosity)
        print("Results of the LP: \n\n", allocation_x, allocation_y)

        
        #Converting the LP solution into the Global Continuum Solution:
        solutions: Dict = {}
        solutions["flowID"] = "FlowID"

        solution_list: List[Dict] = []

        for cluster_id in range(len(allocation_x)): # to take cluster id

            solution_entry: Dict = {}
            solution_entry["cluster"] = "cluster" + str(cluster_id)

            for function_id in range(len(allocation_x[cluster_id])): # to take the function id
                print("Function ID: ", function_id)
                if (allocation_x[cluster_id][function_id] == 1):
                    solution_entry["resource_id"] = "function" + str(function_id)
                
                    solution_list.append(solution_entry)
        
        solutions["allocations"] = solution_list
        print("\n\nSolutions: ", solutions)
        
        #print("Reverting Matrix dimensions")
        #return next_tasks[0]
        """
        next_tasks: List[TaskDag] = []
        for function in functions:
            print("Function here: ", function)
            annotations = function.get("annotations", {})
            performance = annotations.get("performance_known", {})
            print("Annotations: ", annotations)
            next_tasks = [
                TaskDag(
                    id=function["id"],
                    next_tasks=next_tasks,
                    architecture_constraint=get_architecture(
                        annotations.get("architecture")
                    ),
                    resource_request=ResourceRequest(
                        nb_cpu=int(annotations.get("cores", 0)),
                        memory_in_MB=int(annotations.get("memory", 0)),
                    ),
                    cluster_list_placement_constraints=ClusterListPlacementConstraint(
                        clusters=function.get("allocations", [])
                    ),
                    performance_known=PerformanceKnown(
                        archictecture_used=performance.get("archictecture_used", None),
                        cpu_speed=performance.get("cpu_speed", 0),
                        memory_in_MB=performance.get("memory_in_MB", 0),
                        function_execution_time=performance.get(
                            "function_execution_time", 0
                        ),
                        function_energy_consumed=performance.get(
                            "function_energy_consumed", 0
                        ),
                        container_execution_time=performance.get(
                            "container_execution_time", 0
                        ),
                        container_energy_consumed=performance.get(
                            "container_energy_consumed", 0
                        ),
                        container_required=performance.get("container_required", None),
                    ),
                    cluster_type_placement_constraints=ClusterTypePlacementConstraint(
                        cluster_type=ClusterType[annotations["locality"].upper()]
                    )
                    if annotations.get("locality")
                    else None,
                    objective=(
                        Objectives[annotations["optimizationGoal"].upper()],
                        Levels[annotations.get("importance").upper()],
                    )
                    if annotations.get("optimizationGoal")
                    else None,
                )
            ]

        return next_tasks[0]


@dataclass
class Flow:
    id: str
    objectives: Dict[Objectives, Levels]
    functions_dag: TaskDag
    executor_mode: str
    architecture_constraint: ArchitectureType
    resource_request: ResourceRequest
    cluster_list_placement_constraints: ClusterListPlacementConstraint
    cluster_type_placement_constraints: Optional[ClusterTypePlacementConstraint] = None
    performance_known: Optional[PerformanceKnown] = None

    @classmethod
    def create_from_dict(cls, app_dict: Dict) -> "Flow":
        annotations = app_dict.get("annotations", {})
        performance = annotations.get("performance_known", {})
        return Flow(
            id=app_dict.get("flowID", str(uuid.uuid4())),
            objectives={
                Objectives[obj.upper()]: Levels[lvl.upper()]
                for obj, lvl in app_dict.get("objectives", {}).items()
            },
            functions_dag=TaskDag.create_dag_from_functions_sequence(
                app_dict["functions"]
            ),
            executor_mode=app_dict.get("executorMode", "NativeSequence"),
            cluster_list_placement_constraints=ClusterListPlacementConstraint(
                clusters=app_dict.get("allocations", [])
            ),
            cluster_type_placement_constraints=ClusterTypePlacementConstraint(
                cluster_type=ClusterType[annotations["locality"].upper()]
                if annotations.get("locality") in [elem.value for elem in ClusterType]
                else None,
            ),
            performance_known=PerformanceKnown(
                archictecture_used=performance.get("archictecture_used", None),
                cpu_speed=performance.get("cpu_speed", 0),
                memory_in_MB=performance.get("memory_in_MB", 0),
                function_execution_time=performance.get("function_execution_time", 0),
                function_energy_consumed=performance.get("function_energy_consumed", 0),
                container_execution_time=performance.get("container_execution_time", 0),
                container_energy_consumed=performance.get(
                    "container_energy_consumed", 0
                ),
                container_required=performance.get("container_required", None),
            ),
            architecture_constraint=get_architecture(annotations.get("architecture")),
            resource_request=ResourceRequest(
                nb_cpu=int(annotations.get("cores", 0)),
                memory_in_MB=int(annotations.get("memory", 0)),
            ),
        )


"""
    print("Test 11")
    
    N = list(range(3))
    H = list(range(2))
    K = list(range(3))

    c = [[1, 1, 1],
        [1, 1, 1]]

    p = [[1, 1, 1],
        [1, 1, 1]]

    c_tilde = [[1, 10, 1],
            [1, 1, 1]]

    p_tilde = [[1, 1, 1],
            [1, 1, 1]]

    env = [1, 2, 0]

    mc = [1, 1] #number of machines per class

    Tmax = 12

    return N, H, K, c, p, c_tilde, p_tilde, mc, env, Tmax 
"""


@dataclass
class FunctionsMatrix:
    id: str
    functions_execution_time: List[float]
    containers_execution_time: List[float]
    functions_energy_consumption: List[float]
    containers_energy_consumption: List[float]
    containers_per_function: List[float]
    number_of_functions: List[int]
    number_of_containers: List[int]

    @classmethod
    # def create_matrix_from_functions_sequence(cls, app_dict: Dict) -> "FunctionsMatrix":
    def create_matrix_from_functions_sequence(
        cls, functions: List[Dict]
    ) -> "FunctionsMatrix":

        print("\n #####  Reading and building the dag", functions)

        # next_tasks: List[float] = []
        p: List[float] = []
        c: List[float] = []
        p_tilde: List[float] = []
        c_tilde: List[float] = []
        env: List[float] = []
        container_image_ids = {}
        list_of_functions = functions.get("functions", [])

        for function in list_of_functions:
            print("Function here: ", function)
            annotations = function.get("annotations", {})
            performance = annotations.get("performance_known", {})
            print("Annotations: ", annotations)
            p.append(performance.get("function_execution_time", 0))
            c.append(performance.get("function_energy_consumed", 0))
            p_tilde.append(performance.get("container_execution_time", 0))
            c_tilde.append(performance.get("container_energy_consumed", 0))
            container_required = performance.get("container_required", None)

            # Computing the list env: env i of task i
            if container_required not in container_image_ids:
                new_container_id = len(container_image_ids)
                container_image_ids[container_required] = new_container_id
            env.append(container_image_ids.get(container_required))

        p = [[p[j][i] for j in range(len(p))] for i in range(len(p[0]))]
        c = [[c[j][i] for j in range(len(c))] for i in range(len(c[0]))]
        p_tilde = [
            [p_tilde[j][i] for j in range(len(p_tilde))] for i in range(len(p_tilde[0]))
        ]
        c_tilde = [
            [c_tilde[j][i] for j in range(len(c_tilde))] for i in range(len(c_tilde[0]))
        ]
        print("p: ", p)
        print("c: ", c)
        print("p_tilde: ", p_tilde)
        print("c_tilde: ", c_tilde)
        print("env: ", env)

        N = list(range(len(functions)))
        # H = list(range(len(set(env))))
        K = list(range(len(set(env))))

        print("N: ", N)
        print("K: ", K)

        # print("\n\n Matrix Created: ", next_tasks)

        return FunctionsMatrix(
            id=str(uuid.uuid4()),
            functions_execution_time=p,
            containers_execution_time=c,
            functions_energy_consumption=p_tilde,
            containers_energy_consumption=c_tilde,
            containers_per_function=env,
            number_of_functions=N,
            number_of_containers=K,
        )
