from aiohttp.web import Request, json_response
from aiohttp_apispec import docs, request_schema
from dependency_injector.wiring import Provide

from global_continuum_placement.application.scheduler import SchedulerService
from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.domain.platform.platform import Platform
from global_continuum_placement.infrastructure.api.schemas.error_schema import (
    ErrorSchema,
)
from global_continuum_placement.infrastructure.api.schemas.initialize_request_schema import (
    InitializeRequestSchema,
)


@docs(
    tags=["Scheduler"],
    summary="Initialize scheduler",
    description="Provide platform and workload to the scheduler",
    responses={
        201: {"description": "Scheduler initialized"},
        400: {"description": "Scheduler initialization failed!", "schema": ErrorSchema},
    },
)
@request_schema(InitializeRequestSchema)
async def initialize(
    request: Request,
    scheduler: SchedulerService = Provide[ApplicationContainer.scheduler_service],
):
    try:
        platform = Platform.create_site_from_dict(request["data"]["platform"])
        scheduler.platform = platform
    except Exception as err:
        return json_response(ErrorSchema().dump({"name": str(err)}), status=400)

    return json_response("OK", status=201)
