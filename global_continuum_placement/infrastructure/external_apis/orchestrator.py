import logging
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import urljoin

import aiohttp

from global_continuum_placement.application.schedule_result_publisher import (
    IResultPublisher,
)
from global_continuum_placement.domain.placement.placement import Placement
from global_continuum_placement.domain.platform.platform import Platform

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorPublishScheduleResultService(IResultPublisher):
    orchestrator_base_api: str

    async def publish(
        self, raw_application: Dict, platform: Platform, placements: List[Placement]
    ) -> None:
        url = urljoin(self.orchestrator_base_api, "/applications")
        data = {
            "application": raw_application,
            "platform": platform.sites,
            "allocations": placements,
        }
        try:
            logger.info("Get platform update from %s", url)
            async with aiohttp.client.ClientSession() as session:
                async with session.post(
                    url,
                    data=data
                    # headers={"authorization": authorization_token},
                ) as response:
                    logger.info("response for post %s", response)
                    response.raise_for_status()
        except Exception as err:
            logger.exception(
                f"When attempting to get updated platform from: {url}, got an error {err}"
            )
