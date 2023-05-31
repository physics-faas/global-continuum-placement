import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

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
    archictecture_used: List[str] = field(default='None')
    cpu_speed: List[float] = field(default=0)
    memory_in_MB: List[float] = field(default=0)
    execution_time: List[float] = field(default=0)
    energy_consumed: List[float] = field(default=0)

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
                        execution_time=performance.get("execution_time", 0),
                        energy_consumed=performance.get("energy_consumed", 0)
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
                archictecture_used=str(annotations.get("archictecture_used", None)),
                cpu_speed=float(annotations.get("cpu_speed", 0)),
                memory_in_MB=float(annotations.get("memory_in_MB", 0)),
                execution_time=float(annotations.get("execution_time", 0)),
                energy_consumed=float(annotations.get("energy_consumed", 0))
            ),
            architecture_constraint=get_architecture(annotations.get("architecture")),
            resource_request=ResourceRequest(
                nb_cpu=int(annotations.get("cores", 0)),
                memory_in_MB=int(annotations.get("memory", 0)),
            )
        )
    
    @classmethod
    def create_matrix_from_functions_sequence(cls, app_dict: Dict) -> "FunctionsMatrix":

        print("\n #####  Reading and building the Matrix")

        # Be sure that the functions are sorted in reverse order
        if len(functions) > 1:
            functions = sorted(
                functions, key=lambda elem: elem.get("sequence"), reverse=True
            )
        next_tasks: List[float] = []
        p: List[float] = []
        c: List[float] = []
        p_tilde: List[float] = []
        c_tilde: List[float] = []
        
        for function in functions:
            print("Function here: ", function)
            annotations = function.get("annotations", {})
            performance = annotations.get("performance_known", {})
            print("Annotations: ", annotations)
            next_tasks = [
                FunctionsMatrix(
                    performance_known=PerformanceKnown(
                        #archictecture_used=performance.get("archictecture_used", None),
                        cpu_speed=performance.get("cpu_speed", 0),
                        #memory_in_MB=performance.get("memory_in_MB", 0),
                        #execution_time=performance.get("execution_time", 0),
                        #energy_consumed=performance.get("energy_consumed", 0)
                    )
                )
            ]
        print("\n\n Matrix Created: ", next_tasks)

        return next_tasks[0]

@dataclass
class FunctionsMatrix:
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

    @classmethod
    def create_matrix_from_functions_sequence(cls, app_dict: Dict) -> "FunctionsMatrix":

        print("\n #####  Reading and building the Matrix")

        # Be sure that the functions are sorted in reverse order
        if len(functions) > 1:
            functions = sorted(
                functions, key=lambda elem: elem.get("sequence"), reverse=True
            )
        next_tasks: List[float] = []
        p: List[float] = []
        c: List[float] = []
        p_tilde: List[float] = []
        c_tilde: List[float] = []
        
        for function in functions:
            print("Function here: ", function)
            annotations = function.get("annotations", {})
            performance = annotations.get("performance_known", {})
            print("Annotations: ", annotations)
            next_tasks = [
                FunctionsMatrix(
                    performance_known=PerformanceKnown(
                        #archictecture_used=performance.get("archictecture_used", None),
                        cpu_speed=performance.get("cpu_speed", 0),
                        #memory_in_MB=performance.get("memory_in_MB", 0),
                        #execution_time=performance.get("execution_time", 0),
                        #energy_consumed=performance.get("energy_consumed", 0)
                    )
                )
            ]
        print("\n\n Matrix Created: ", next_tasks)

        return next_tasks[0]