import uuid
from dataclasses import dataclass, field
from typing import List, Dict

from .workload_values import TaskState
from ..platform.platfom_values import SiteType
from ..events import InitializeCommand


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
    placement_constraints: List[PlacementConstraint] = field(default=list)
    state: TaskState = field(default=TaskState.NONE)
    next_task: List["TaskDag"] = field(default_factory=list)

    @classmethod
    def _create_task_from_dict(cls, task_ids: List[str], workflow: Dict) -> List["TaskDag"]:
        new_tasks = []
        for task_id in task_ids:
            current_task = workflow[task_id]
            new_tasks.append(TaskDag(**current_task, next_task=cls._create_task_from_dict(current_task.next_tasks, workflow)))
        return new_tasks

    @classmethod
    def create_dag_from_workflow(cls, workflow: Dict) -> "TaskDag":
        """
        FIXME Define a workflow definition schema and create this function after!
        """
        # FIXME find root task, here we assume it is the first
        task_dict = list(workflow.keys())[0]
        # TODO call the recursive method on it
        return cls._create_task_from_dict([task_dict.id], workflow)[0]


@dataclass
class Workflow:
    id: str = field(default=None)
    tasks_dag: TaskDag = field(default=None)

    @classmethod
    def create_from_new_workflow_command(cls, cmd: InitializeCommand):
        return Workflow(id=str(uuid.uuid4()), tasks_dag=TaskDag.create_dag_from_workflow(cmd.workflow))


@dataclass
class Workload:
    id: str = field(default=None)
    workflows: Dict[Workflow] = field(default_factory=dict)

    @classmethod
    def create(cls):
        return Workload(id=str(uuid.uuid4()))
