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
                if annotations.get("locality")
                else None,
            ),
            architecture_constraint=get_architecture(annotations.get("architecture")),
            resource_request=ResourceRequest(
                nb_cpu=int(annotations.get("cores", 0)),
                memory_in_MB=int(annotations.get("memory", 0)),
            ),
        )
