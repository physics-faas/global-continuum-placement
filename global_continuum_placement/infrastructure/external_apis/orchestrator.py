import json
import logging
from dataclasses import asdict, dataclass
from typing import Dict, List, cast

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
        data = {
            "application": raw_application,
            "platform": {cluster.id: asdict(cluster) for cluster in platform.sites},
            "allocations": [asdict(placement) for placement in placements],
        }
        # Remove unwanted fields
        for cluster_id, cluster in cast(dict, data["platform"]).items():
            del cluster["free_resources"]
            del cluster["allocated_tasks"]

        json_data = json.dumps(data)
        logger.info("JSON formatted data to send: \n%s", json_data)
        try:
            url = self.orchestrator_base_api.rstrip("/") + "/deploy"
            logger.info("Get platform update from %s", url)
            async with aiohttp.client.ClientSession() as session:
                async with session.post(
                    url,
                    json=data
                    # headers={"authorization": authorization_token},
                ) as response:
                    logger.info("response for post %s", response)
                    response.raise_for_status()
        except Exception as err:
            logger.exception(
                f"When attempting to get updated platform from: {url}, got an error {err}"
            )
