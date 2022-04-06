from enum import Enum
from typing import List


class ClusterType(str, Enum):
    HPC = "HPC"
    EDGE = "Edge"
    CLOUD = "Cloud"
    ON_PREMISE = "On-premise"


class ArchitectureType(str, Enum):
    """
    Values are linux defined arch like returned by uname -a
    """

    X86_64 = "x86_64"
    ARM64 = "arm64"

    @classmethod
    def list(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))  # type: ignore
