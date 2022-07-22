from dataclasses import dataclass


@dataclass
class Placement:
    cluster: str
    resource_id: str


@dataclass
class Allocation:
    flowID: str
    allocations: list[Placement]
