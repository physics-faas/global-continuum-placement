import uuid
from dataclasses import dataclass, field
from typing import Dict, List

from ..platform.platfom_values import SiteType
from .workload_values import TaskState


@dataclass
class ResourceRequest:
    nb_cpu: int = field(default=0)
    nb_gpu: int = field(default=0)
    memory_in_MB: int = field(default=0)


@dataclass
class PlacementConstraint:
    site: str = field(default=None)
    site_type: SiteType = field(default=None)


@dataclass
class TaskDag:
    id: str = field(default=None)
    resource_request: ResourceRequest = field(default_factory=None)
    # WARNING: Multiple constraints defined are resolved with a logical OR.
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
            new_tasks.append(
                TaskDag(
                    id=task_id,
                    resource_request=ResourceRequest(
                        **current_task.get("resources", {})
                    ),
                    placement_constraints=[
                        PlacementConstraint(**constraint)
                        for constraint in current_task.get("constraints", [])
                    ],
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
    id: str = field(default=None)
    tasks_dag: TaskDag = field(default=None)

    @classmethod
    def create_from_dict(cls, workflow_dict: Dict) -> "Workflow":
        return Workflow(
            id=str(uuid.uuid4()),
            tasks_dag=TaskDag.create_dag_from_workflow(workflow_dict),
        )


@dataclass
class Workload:
    id: str = field(default=None)
    workflows: Dict[str, Workflow] = field(default_factory=dict)

    @classmethod
    def create(cls):
        return Workload(id=str(uuid.uuid4()))
