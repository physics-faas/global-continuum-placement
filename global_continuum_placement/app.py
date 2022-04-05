import logging
from logging import getLogger

from aiohttp import web

from .container import ApplicationContainer
from .infrastructure.api.setup import setup as api_setup
from .version import __version__


def init() -> web.Application:
    """Init application"""
    # Init application container
    container = ApplicationContainer()

    # Override with env variables
    container.configuration.log_level.from_env("LOG_LEVEL", "INFO")
    container.configuration.orchestrator_base_api.from_env("ORCHESTRATOR_BASE_API")
    container.configuration.inference_engine_base_api.from_env(
        "INFERENCE_ENGINE_BASE_API"
    )
    container.configuration.policy.from_env("POLICY", "first_fit")

    # Setup logging
    str_level = container.configuration.log_level()
    numeric_level = getattr(logging, str_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % str_level)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s.%(msecs)03d %(levelname)-7s %(name)-22s %(message)s",
        datefmt="%Y-%m-%d,%H:%M:%S",
    )
    logger = getLogger(__name__)
    logger.info("Logging level is set to %s" % str_level.upper())
    logger.info("PHYSICS Global Continuum Placement version: %s", __version__)

    # Init web app
    app: web.Application = web.Application()
    api_setup(app, container)
    app["container"] = container

    return app


async def on_startup(app: web.Application) -> None:
    """Hooks for application startup"""
    container: ApplicationContainer = app["container"]
    logger = getLogger(__name__)
    try:
        platform_service = container.platform_service()
        await platform_service.update_platform()
    except Exception as err:
        logger.exception(
            "Unable to initialized the platform at startup. Error: %s", err
        )


async def on_cleanup(app: web.Application) -> None:
    """Define hook when application stop"""
    # container: ApplicationContainer = app["container"]
    # FIXME: add cleaning hooks here
    pass


def start() -> None:
    """Start application"""
    app: web.Application = init()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    web.run_app(app)
