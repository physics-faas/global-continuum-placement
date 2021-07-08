from aiohttp.web import Request, json_response
from aiohttp_apispec import docs
from dependency_injector.wiring import Provide

from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.domain.services.scheduler import ISchedulerService


@docs(
    tags=["Scheduler"],
    summary="Initialize scheduler",
    description="Provide platform and workload to the scheduler",
    responses={
        200: {"description": "Scheduler initialized"},
        400: {"description": "Scheduler initialization failed!"},
    },
)
async def initialize(
    request: Request,
):

    return json_response(, status=200)