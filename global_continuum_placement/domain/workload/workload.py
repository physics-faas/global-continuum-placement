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
class PlacementConstraint:
    cluster: Optional[str] = None
    cluster_type: Optional[ClusterType] = None


@dataclass
class TaskDag:
    id: str
    architecture_constraint: ArchitectureType
    resource_request: ResourceRequest
    objective: Optional[Tuple[Objectives, Levels]] = None
    # WARNING: Multiple placement constraints defined are resolved with a logical OR.
    placement_constraints: List[PlacementConstraint] = field(default_factory=list)
    state: TaskState = field(default=TaskState.NONE)
    next_tasks: List["TaskDag"] = field(default_factory=list)

    @classmethod
    def _create_task_from_dict(
        cls, task_ids: List[str], workflow: Dict
    ) -> List["TaskDag"]:
        new_tasks = []
        for task_id in task_ids:
            current_task = workflow[task_id]
            architecture = current_task.get("architecture")
            try:
                architecture_constraint = (
                    ArchitectureType[architecture.upper()]
                    if architecture
                    else ArchitectureType.X86_64
                )
            except KeyError:
                raise UnknownArchitectureError(
                    f"Architecture {architecture} is not recognised. Available architectures are {', '.join(ArchitectureType.list())}."
                )
            new_tasks.append(
                TaskDag(
                    id=task_id,
                    resource_request=ResourceRequest(
                        **current_task.get("resources", {})
                    ),
                    placement_constraints=[
                        PlacementConstraint(
                            cluster=constraint.get("cluster"),
                            cluster_type=ClusterType[constraint["cluster_type"].upper()]
                            if constraint.get("cluster_type")
                            else None,
                        )
                        for constraint in current_task.get("constraints", [])
                    ],
                    architecture_constraint=architecture_constraint,
                    next_tasks=cls._create_task_from_dict(
                        current_task.get("next_tasks", []), workflow
                    ),
                )
            )
        return new_tasks

    @classmethod
    def create_dag_from_workflow(cls, workflow: Dict) -> "TaskDag":
        """
        FIXME Define a workflow definition schema and create this function after!
        """
        # FIXME find root function, here we assume it is the first
        task_dict = list(workflow.keys())[0]
        # TODO call the recursive method on it
        return cls._create_task_from_dict([task_dict], workflow)[0]

    @classmethod
    def create_dag_from_functions_sequence(cls, functions: List[Dict]) -> "TaskDag":
        # Be sure that the functions are sorted in reverse order
        functions = sorted(functions, key=lambda elem: elem["sequence"], reverse=True)
        next_tasks: List[TaskDag] = []
        for function in functions:
            annotations = function["annotations"]
            architecture = annotations.get("architecture")
            next_tasks = [
                TaskDag(
                    id=function["id"],
                    next_tasks=next_tasks,
                    architecture_constraint=(
                        ArchitectureType[architecture.upper()]
                        if architecture
                        else ArchitectureType.X86_64
                    ),
                    resource_request=ResourceRequest(
                        nb_cpu=annotations.get("sizingCores", 0),
                        memory_in_MB=annotations.get("sizingMB", 0),
                    ),
                    placement_constraints=[
                        PlacementConstraint(
                            cluster=constraint,
                        )
                        for constraint in function.get("allocations", [])
                    ]
                    + (
                        [
                            PlacementConstraint(
                                cluster_type=ClusterType[
                                    annotations["locality"].upper()
                                ]
                            )
                        ]
                        if annotations.get("locality")
                        else []
                    ),
                    objective=(
                        Objectives[annotations["optimizationGoal"].upper()],
                        Levels[annotations.get("importance").upper()],
                    ) if annotations.get("optimizationGoal") else None,
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
