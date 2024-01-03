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
    archictecture_used: List[str] = field(default_factory=list)
    cpu_speed: List[float] = field(default_factory=list)
    memory_in_MB: List[float] = field(default_factory=list)
    function_execution_time: List[float] = field(default_factory=list)
    function_energy_consumed: List[float] = field(default_factory=list)
    container_execution_time: List[float] = field(default_factory=list)
    container_energy_consumed: List[float] = field(default_factory=list)
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
        # Be sure that the functions are sorted in reverse order
        if len(functions) > 1:
            functions = sorted(
                functions, key=lambda elem: elem.get("sequence"), reverse=True
            )

        next_tasks: List[TaskDag] = []
        for function in functions:
            annotations = function.get("annotations", {})
            print(annotations)

            containerRequired = annotations.get("containerRequired", {})
            loadGenData = annotations.get("loadGenData", {})
            print(loadGenData)

            durationAverages = []
            energyAverages = []
            containerDurationAverages = []
            containerEnergyAverages = []
            
            for measure in loadGenData:
                durationAverages.append([measure.get("averageDuration", 0)])
                energyAverages.append([measure.get("averageEnergy", 0)])
                containerDurationAverages.append([measure.get("averageDurationContainer", 0)])
                containerEnergyAverages.append([measure.get("averageEnergyContainer", 0)])
            print(durationAverages)

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
                        memory_in_MB=annotations.get("memory", 0),
                        function_execution_time=durationAverages,
                        function_energy_consumed=energyAverages,
                        container_execution_time=containerDurationAverages,
                        container_energy_consumed=containerEnergyAverages,
                        container_required=containerRequired,
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
    print("Here Flow")
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


@dataclass
class FunctionsMatrix:
    print("Here FunctionsMatrix")
    id: str
    functions_execution_time: List[List[float]]
    containers_execution_time: List[List[float]]
    functions_energy_consumption: List[List[float]]
    containers_energy_consumption: List[List[float]]
    containers_per_function: List[float]
    number_of_functions: List[int]
    number_of_containers: List[int]

    @classmethod
    # def create_matrix_from_functions_sequence(cls, app_dict: Dict) -> "FunctionsMatrix":
    def create_matrix_from_functions_sequence(
        cls, functions: Dict
    ) -> "FunctionsMatrix":

        p: List[List[float]] = []
        c: List[List[float]] = []
        p_tilde: List[List[float]] = []
        c_tilde: List[List[float]] = []
        env: List[float] = []
        container_image_ids: Dict = {}
        list_of_functions = functions.get("functions", [])

        for function in list_of_functions:
            annotations = function.get("annotations", {})
            print(annotations)
            
            loadGenData = annotations.get("loadGenData", {})
            print(loadGenData)
            
            for measure in loadGenData:
                p.append([measure.get("averageDuration", 0)])
                c.append([measure.get("averageEnergy", 0)])
                p_tilde.append([measure.get("averageDurationContainer", 0)])
                c_tilde.append([measure.get("averageEnergyContainer", 0)])

            container_required = annotations.get("containerRequired", None)
            # Computing the list env: env i of task i
            if container_required not in container_image_ids:
                new_container_id = len(container_image_ids)
                container_image_ids[container_required] = new_container_id
            env.append(container_image_ids.get(container_required))

        print(p)
        print(c)
        print(p_tilde)
        print(c_tilde)
        
        """
        p = [[p[j][i] for j in range(len(p))] for i in range(len(p[0]))]
        print(p)
        c = [[c[j][i] for j in range(len(c))] for i in range(len(c[0]))]
        p_tilde = [
            [p_tilde[j][i] for j in range(len(p_tilde))] for i in range(len(p_tilde[0]))
        ]
        c_tilde = [
            [c_tilde[j][i] for j in range(len(c_tilde))] for i in range(len(c_tilde[0]))
        ]
        """

        #print("!!!Computing N, k", len(list_of_functions), len(set(env)))
        #N = list(range(len(list_of_functions)))
        #K = list(range(len(set(env))))

        N = len(list_of_functions)
        K = len(set(env))

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
