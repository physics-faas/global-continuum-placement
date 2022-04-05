from enum import Enum
from typing import List


class TaskState(str, Enum):
    NONE = "None"
    SUBMITTED = "Submitted"
    RUNNING = "Running"
    DONE = "Done"


class Levels(int, Enum):
    LOW = 0.2
    MEDIUM = 0.5
    HIGH = 1

    @classmethod
    def list(cls) -> List[str]:
        return list(map(lambda c: c.name.lower(), cls))  # type: ignore


class Objectives(str, Enum):
    ENERGY = "Energy"
    PERFORMANCE = "Performance"
    AVAILABILITY = "Availability"

    @classmethod
    def list(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))  # type: ignore
