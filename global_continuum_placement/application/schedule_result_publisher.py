from typing import Dict, List

from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import Platform


class IResultPublisher:
    async def publish(
        self, raw_application: Dict, platform: Platform, placements: List[Placement]
    ) -> None:
        ...
