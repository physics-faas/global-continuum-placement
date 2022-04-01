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
class TaskDag:
    id: str
    architecture_constraint: ArchitectureType
    resource_request: ResourceRequest
    # WARNING: a list of cluster placement constraints defined are resolved with a logical OR.
    cluster_list_placement_constraints: ClusterListPlacementConstraint
    cluster_type_placement_constraints: Optional[ClusterTypePlacementConstraint] = None
    objective: Optional[Tuple[Objectives, Levels]] = None
    state: TaskState = field(default=TaskState.NONE)
    next_tasks: List["TaskDag"] = field(default_factory=list)

    @classmethod
    def create_dag_from_functions_sequence(cls, functions: List[Dict]) -> "TaskDag":
        # Be sure that the functions are sorted in reverse order
        if len(functions) > 1:
            functions = sorted(functions, key=lambda elem: elem.get("sequence"), reverse=True)
        next_tasks: List[TaskDag] = []
        for function in functions:
            annotations = function.get("annotations", {})
            architecture_raw = annotations.get("architecture")
            try:
                architecture = (ArchitectureType[architecture_raw.upper()]
                if architecture_raw
                else ArchitectureType.X86_64)
            except (KeyError, ValueError):
                raise UnknownArchitectureError
            next_tasks = [
                TaskDag(
                    id=function["id"],
                    next_tasks=next_tasks,
                    architecture_constraint=architecture,
                    resource_request=ResourceRequest(
                        nb_cpu=int(annotations.get("sizingCores", 0)),
                        memory_in_MB=int(annotations.get("sizingMB", 0)),
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
class Application:
    id: str
    objectives: Dict[Objectives, Levels]
    functions_dag: TaskDag

    @classmethod
    def create_from_application(cls, app_dict: Dict) -> "Application":
        return Application(
            id=str(uuid.uuid4()),
            objectives={
                Objectives[obj.upper()]: Levels[lvl.upper()]
                for obj, lvl in app_dict.get("objectives", {}).items()
            },
            functions_dag=TaskDag.create_dag_from_functions_sequence(
                app_dict["functions"]
            ),
        )


@dataclass
class Workload:
    id: str
    applications: Dict[str, Application] = field(default_factory=dict)

    @classmethod
    def create(cls) -> "Workload":
        return Workload(id=str(uuid.uuid4()))
