from dependency_injector import containers
from dependency_injector.providers import Configuration, Factory, Singleton

from global_continuum_placement.application.scheduler import SchedulerService
from global_continuum_placement.infrastructure.external_apis.inference_engine import (
    InferenceEngineAPIPlatformService,
)
from global_continuum_placement.infrastructure.external_apis.orchestrator import (
    OrchestratorPublishScheduleResultService,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """Application container for dependency injection"""

    # Define configuration provider
    configuration: Configuration = Configuration()

    # Platform service get updates on the platform state from the outside
    platform_service = Singleton(
        InferenceEngineAPIPlatformService, configuration.inference_engine_base_api
    )
    # Service to push results of the schedule to
    result_publisher = Factory(
        OrchestratorPublishScheduleResultService, configuration.orchestrator_base_api
    )

    # Inject scheduling policy here
    scheduler_service = Singleton(
        SchedulerService,
        platform_service=platform_service,
        result_publisher=result_publisher,
        policy=configuration.policy,
    )
