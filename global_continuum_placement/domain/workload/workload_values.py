from enum import Enum


class TaskState(Enum):
    NONE = "None"
    SUBMITTED = "Submitted"
    RUNNING = "Running"
    DONE = "Done"
