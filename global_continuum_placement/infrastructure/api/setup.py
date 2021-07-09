from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.infrastructure.api.controllers import (
    scheduler_controller,
    util_controller,
)
from global_continuum_placement.version import __version__


def setup(app: web.Application, container: ApplicationContainer):
    """ Method to setup api """
    # Configure application container for wiring
    container.wire(
        modules=[
            util_controller,
            scheduler_controller,
        ]
    )

    # Setup server middlewares
    app.middlewares.extend(
        [
            validation_middleware,
        ]
    )

    # Configure api routing
    app.add_routes(
        [
            web.get("/healthz", util_controller.health_check, allow_head=False),
            web.post("/init", scheduler_controller.initialize),
        ]
    )

    # Configure api documentation
    setup_aiohttp_apispec(
        app,
        title="global_continuum_placement",
        version=__version__,
        url="/docs/swagger.json",
        swagger_path="/docs",
        static_path="/static/swagger",
        # securityDefinitions={
        #    "bearer": {
        #        "type": "apiKey",
        #        "name": "Authorization",
        #        "in": "header",
        #        "description": "Ryax token",
        #    }
        # },
        # security=[{"bearer": []}],
    )
