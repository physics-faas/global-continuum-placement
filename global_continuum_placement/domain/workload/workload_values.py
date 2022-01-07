from enum import Enum


class TaskState(Enum):
    NONE = "None"
    SUBMITTED = "Submitted"
    RUNNING = "Running"
    DONE = "Done"


class TaskProfileLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, TaskProfileLevel))
