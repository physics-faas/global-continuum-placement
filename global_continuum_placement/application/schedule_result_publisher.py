from typing import Dict

from global_continuum_placement.domain.placement.placement import Allocation
from global_continuum_placement.domain.platform.platform import Platform


class IResultPublisher:
    async def publish(
        self, raw_application: Dict, platform: Platform, allocations: list[Allocation]
    ) -> None:
        ...
