from enum import Enum


class SiteType(Enum):
    HPC = "HPC",
    EDGE = "Edge",
    CLOUD = "Cloud",
    ON_PREMISE = "On-premise"
