from enum import Enum
from typing import List


class TaskState(Enum):
    NONE = "None"
    SUBMITTED = "Submitted"
    RUNNING = "Running"
    DONE = "Done"


class Levels(Enum):
    LOW = 0.2
    MEDIUM = 0.5
    HIGH = 1

    @classmethod
    def list(cls) -> List[str]:
        return list(map(lambda c: c.name.lower(), cls))  # type: ignore


class Objectives(Enum):
    ENERGY = "Energy"
    PERFORMANCE = "Performance"
    AVAILABILITY = "Availability"

    @classmethod
    def list(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))  # type: ignore
