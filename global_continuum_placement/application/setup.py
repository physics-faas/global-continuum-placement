from global_continuum_placement.application.handlers import CHANGEME_handlers
from global_continuum_placement.application.message_bus import MessageBus
from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.domain.base_event import ApplicationStartupEvent
from global_continuum_placement.domain.CHANGEME_object.CHANGEME_events import (
    CreateCHANGEMECommand,
)


def setup(container: ApplicationContainer):
    """ Method to setup messaging mapper (event type/messages mapping)"""
    container.wire(modules=[CHANGEME_handlers])

    # Register command handlers
    MessageBus.register_command_handler(CreateCHANGEMECommand, CHANGEME_handlers.create)

    # Register event handlers
    MessageBus.register_event_handler(
        ApplicationStartupEvent, CHANGEME_handlers.on_startup
    )
