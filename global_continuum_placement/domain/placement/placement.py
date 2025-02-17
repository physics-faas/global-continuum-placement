from dataclasses import dataclass
from typing import Optional


@dataclass
class Placement:
    cluster: str
    resource_id: str
    fallback_cluster: Optional[str] = None


@dataclass
class Allocation:
    flowID: str
    allocations: list[Placement]
