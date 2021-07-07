from dataclasses import dataclass, field

from global_continuum_placement.domain.base_command import BaseCommand
from global_continuum_placement.domain.base_event import BaseEvent


@dataclass
class CreateCHANGEMECommand(BaseCommand):
    attibute1: str = field(default=None)


@dataclass
class CHANGEMEIsReadyEvent(BaseEvent):
    id: str = field(default=None)
