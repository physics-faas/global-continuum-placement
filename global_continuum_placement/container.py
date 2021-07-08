from dependency_injector import containers, providers
from dependency_injector.providers import Singleton


class ApplicationContainer(containers.DeclarativeContainer):
    """ Application container for dependency injection """

    # Define configuration provider
    configuration = providers.Configuration()

    scheduler_service = Singleton(Scheduler, platform=platform, )
