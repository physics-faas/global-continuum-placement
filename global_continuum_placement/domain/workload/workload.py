import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..platform.platfom_values import ArchitectureType, SiteType
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
    site: Optional[str] = None
    site_type: Optional[SiteType] = None


@dataclass
class TaskDag:
    id: str
    architecture_constraint: ArchitectureType
    resource_request: ResourceRequest
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
                            site=constraint.get("site"),
                            site_type=SiteType[constraint["site_type"].upper()]
                            if constraint.get("site_type")
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
        # FIXME find root task, here we assume it is the first
        task_dict = list(workflow.keys())[0]
        # TODO call the recursive method on it
        return cls._create_task_from_dict([task_dict], workflow)[0]


@dataclass
class Workflow:
    id: str
    name: str
    objectives: Dict[Objectives, Levels]
    tasks_dag: TaskDag

    @classmethod
    def create_from_dict(cls, workflow_dict: Dict) -> "Workflow":
        return Workflow(
            id=str(uuid.uuid4()),
            name=workflow_dict.get("name"),
            objectives={
                Objectives[obj.upper()]: lvl
                for obj, lvl in workflow_dict.get("objectives", {}).items()
            },
            tasks_dag=TaskDag.create_dag_from_workflow(workflow_dict["tasks"]),
        )


@dataclass
class Workload:
    id: str
    workflows: Dict[str, Workflow] = field(default_factory=dict)

    @classmethod
    def create(cls):
        return Workload(id=str(uuid.uuid4()))
