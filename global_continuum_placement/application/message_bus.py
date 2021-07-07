import logging
from typing import Any, Callable, Coroutine, Dict, List, Type, Union

from global_continuum_placement.domain.base_command import BaseCommand
from global_continuum_placement.domain.base_event import BaseEvent

logger = logging.getLogger(__name__)

Message = Union[BaseCommand, BaseEvent]

HANDLER_TYPE = Callable[..., Coroutine[Any, Any, Any]]


class MessageBus:
    event_handlers: Dict[Type[BaseEvent], List[HANDLER_TYPE]] = dict()
    command_handlers: Dict[Type[BaseCommand], HANDLER_TYPE] = dict()

    @staticmethod
    def register_event_handler(event: Type[BaseEvent], event_handler: HANDLER_TYPE):
        if event in MessageBus.event_handlers:
            MessageBus.event_handlers[event].append(event_handler)
        else:
            MessageBus.event_handlers[event] = [event_handler]

    @staticmethod
    def register_command_handler(
        command: Type[BaseCommand], command_handler: HANDLER_TYPE
    ):
        MessageBus.command_handlers[command] = command_handler

    async def handle(self, messages):
        """ Asynchronous event and command handling: create a task for each events and command"""
        while messages:
            message = messages.pop(0)
            if isinstance(message, BaseEvent):
                await self.handle_event(message)
            elif isinstance(message, BaseCommand):
                await self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

    async def handle_event(self, event: BaseEvent):
        for handler in self.event_handlers[type(event)]:
            try:
                logger.debug("Handling event %s with handler %s", event, handler)
                await handler(event)
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    async def handle_command(self, command: BaseCommand):
        logger.debug("Handling command %s", command)
        try:
            handler = self.command_handlers[type(command)]
            return await handler(command)
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
