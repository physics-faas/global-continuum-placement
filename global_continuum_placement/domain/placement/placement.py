from dataclasses import dataclass


@dataclass
class Placement:
    cluster: str
    resource_id: str
