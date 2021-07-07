from aiohttp import web
from aiohttp_apispec import docs
from dependency_injector.wiring import Provide

from global_continuum_placement.application.util_service import UtilService
from global_continuum_placement.container import ApplicationContainer


@docs(
    tags=["Monitoring"],
    summary="Check service status",
    description="Help to know service status",
    responses={
        200: {"description": "Service healthy"},
        400: {"description": "Service unhealthy"},
    },
    security=[],
)
async def health_check(
    _: web.Request,
    service: UtilService = Provide[ApplicationContainer.util_service],
):
    if service.is_healthy():
        return web.json_response("Service healthy", status=200)
    else:
        return web.json_response("Service unhealthy", status=400)
