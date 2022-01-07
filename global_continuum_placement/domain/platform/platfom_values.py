from enum import Enum


class SiteType(Enum):
    HPC = "HPC"
    EDGE = "Edge"
    CLOUD = "Cloud"
    ON_PREMISE = "On-premise"


class ArchitectureType(Enum):
    """
    Values are linux defined arch like returned by uname -a
    """

    X86_64 = "x86_64"
    ARM64 = "arm64"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, ArchitectureType))
