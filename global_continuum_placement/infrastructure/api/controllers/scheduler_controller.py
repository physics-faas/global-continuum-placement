import logging

from aiohttp.web import Request, json_response
from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema
from dependency_injector.wiring import Provide

from global_continuum_placement.application.scheduler import SchedulerService
from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.domain.platform.platform import Platform
from global_continuum_placement.domain.workload.workload import Workflow
from global_continuum_placement.infrastructure.api.schemas.error_schema import (
    ErrorSchema,
)
from global_continuum_placement.infrastructure.api.schemas.initialize_request_schema import (
    InitializeRequestSchema,
)
from global_continuum_placement.infrastructure.api.schemas.placement import (
    PlacementSchema,
)
from global_continuum_placement.infrastructure.api.schemas.sheduler_requests import (
    WorkflowScheduleRequestSchema,
)

logger = logging.getLogger(__name__)


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
) -> Response:
    try:
        platform = Platform.create_from_dict(request["data"]["platform"])
        scheduler.platform = platform
    except Exception as err:
        logger.exception(err)
        return json_response(ErrorSchema().dump({"error": str(err)}), status=400)

    return json_response("OK", status=201)


@docs(
    tags=["Scheduler"],
    summary="Schedule the workload",
    description="Run the scheduler on the given workload. Returns placement mapping for each allocatable tasks.",
    responses={
        201: {
            "description": "Scheduling done successfully",
            "schema": PlacementSchema(many=True),
        },
        400: {
            "description": "Scheduler initialization failed!",
            "schema": ErrorSchema(),
        },
    },
)
@request_schema(WorkflowScheduleRequestSchema)
async def schedule(
    request: Request,
    scheduler: SchedulerService = Provide[ApplicationContainer.scheduler_service],
) -> Response:
    try:
        workflow = Workflow.create_from_dict(request["data"])
        workflow_id = request["data"]["name"]
        scheduler.workload.workflows[workflow_id] = workflow
        placements = scheduler.schedule()
        result = [PlacementSchema().dump(placement) for placement in placements]
        return json_response(result, status=200)

    except Exception as err:
        logger.exception(err)
        return json_response(ErrorSchema().dump({"error": str(err)}), status=500)
