from dependency_injector.wiring import Provide, inject
from logfmt_logger import getLogger

from global_continuum_placement.application.message_bus import MessageBus
from global_continuum_placement.application.unit_of_work import IUnitOfWork
from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.domain.base_event import ApplicationStartupEvent
from global_continuum_placement.domain.CHANGEME_object.CHANGEME_events import (
    CHANGEMEIsReadyEvent,
    CreateCHANGEMECommand,
)
from global_continuum_placement.domain.CHANGEME_object.CHANGEME_object import CHANGEME

logger = getLogger(__name__)


@inject
async def create(
    cmd: CreateCHANGEMECommand,
    message_bus: MessageBus = Provide[ApplicationContainer.message_bus],
    uow: IUnitOfWork = Provide[ApplicationContainer.unit_of_work],
):
    with uow:
        obj: CHANGEME = CHANGEME.create_from_run_CHANGEME_command(cmd)
        obj.set_ready()
        uow.CHANGEME_repository.add(obj)
        uow.commit()
    # Send events
    await message_bus.handle(obj.events)
    return obj.id


@inject
async def on_is_ready(
    event: CHANGEMEIsReadyEvent,
    message_bus: MessageBus = Provide[ApplicationContainer.message_bus],
    uow: IUnitOfWork = Provide[ApplicationContainer.unit_of_work],
):
    with uow:
        obj = uow.CHANGEME_repository.get_by_id(event.id)
        # TODO: do some treatment on obj
        logger.debug(obj)
        uow.commit()
    # Send events
    await message_bus.handle(obj.events)


async def on_startup(cmd: ApplicationStartupEvent):
    # Do initialization
    logger.debug(cmd)
    pass
