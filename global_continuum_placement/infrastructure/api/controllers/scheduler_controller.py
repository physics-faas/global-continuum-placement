import logging

from aiohttp.web import Request, json_response
from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema
from dependency_injector.wiring import Provide

from global_continuum_placement.application.platform_service import IPlatformService
from global_continuum_placement.application.scheduler import SchedulerService
from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.domain.platform.platform import Platform
from global_continuum_placement.domain.workload.workload import Application
from global_continuum_placement.infrastructure.api.schemas.application_schema import (
    ApplicationSchema,
)
from global_continuum_placement.infrastructure.api.schemas.error_schema import (
    ErrorSchema,
)
from global_continuum_placement.infrastructure.api.schemas.placement import (
    PlacementSchema,
)
from global_continuum_placement.infrastructure.api.schemas.platform_schema import (
    PlatformSchema,
)

logger = logging.getLogger(__name__)


@docs(
    tags=["Platform"],
    summary="Initialize platform",
    responses={
        201: {"description": "Platform initialized"},
        400: {"description": "Platform initialization failed!", "schema": ErrorSchema},
    },
)
@request_schema(PlatformSchema)
async def create_platform(
    request: Request,
    platform_service: IPlatformService = Provide[ApplicationContainer.platform_service],
) -> Response:
    try:
        platform = Platform.create_from_dict(request["data"]["platform"])
        platform_service.platform = platform
    except Exception as err:
        logger.exception(err)
        return json_response(ErrorSchema().dump({"error": str(err)}), status=400)

    return json_response("OK", status=201)


@docs(
    tags=["Application"],
    summary="Schedule the application",
    description="Run the scheduler on the given application. Returns placement mapping for each allocatable functions.",
    responses={
        200: {
            "description": "Application allocation done successfully",
            "schema": PlacementSchema(many=True),
        },
        400: {
            "description": "Scheduler initialization failed!",
            "schema": ErrorSchema(),
        },
    },
)
@request_schema(ApplicationSchema)
async def schedule_application(
    request: Request,
    scheduler: SchedulerService = Provide[ApplicationContainer.scheduler_service],
) -> Response:
    application = Application.create_from_application(request["data"])
    placements = await scheduler.schedule_application(
        application, raw_application=request["data"]
    )
    result = [PlacementSchema().dump(placement) for placement in placements]
    return json_response(result, status=200)
