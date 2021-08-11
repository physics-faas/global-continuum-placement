from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from global_continuum_placement.application.scheduler import SchedulerService


class ApplicationContainer(containers.DeclarativeContainer):
    """ Application container for dependency injection """

    # Define configuration provider
    configuration = providers.Configuration()

    # TODO Inject scheduling policy here
    scheduler_service = Singleton(SchedulerService, policy=configuration.policy)
