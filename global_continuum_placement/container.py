from dependency_injector import containers, providers

from .application.message_bus import MessageBus
from .domain.CHANGEME_object.CHANGEME_repository import ICHANGEMERepository
from .infrastructure.database.engine import DatabaseEngine
from .infrastructure.database.repositories.CHANGEME_repository import DatabaseCHANGEMERepository
from .infrastructure.database.unit_of_work import DatabaseUnitOfWork


class ApplicationContainer(containers.DeclarativeContainer):
    """ Application container for dependency injection """

    # Define configuration provider
    configuration = providers.Configuration()

    db_engine: providers.Singleton[DatabaseEngine] = providers.Singleton(
        DatabaseEngine, connection_url=configuration.ryax_datastore
    )

    CHANGEME_repository: providers.Factory[ICHANGEMERepository] = providers.Factory(
        DatabaseCHANGEMERepository
    )

    unit_of_work: DatabaseUnitOfWork = providers.Factory(
        DatabaseUnitOfWork,
        engine=db_engine,
        CHANGEME_repository_factory=CHANGEME_repository.provider,
    )

    message_bus = providers.Factory(MessageBus)
