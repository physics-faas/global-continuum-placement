from enum import Enum


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
    def list(cls):
        return list(map(lambda c: c.name.lower(), cls))


class Objectives(Enum):
    ENERGY = "Energy"
    PERFORMANCE = "Performance"
    RESILIENCE = "Resilience"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
