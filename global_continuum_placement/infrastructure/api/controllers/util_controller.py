from aiohttp import web
from aiohttp_apispec import docs


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
):
    return web.json_response("Service healthy", status=200)
