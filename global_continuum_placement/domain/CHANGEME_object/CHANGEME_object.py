import uuid
from dataclasses import dataclass, field
from typing import List, Union

from global_continuum_placement.domain.base_command import BaseCommand
from global_continuum_placement.domain.base_event import BaseEvent
from global_continuum_placement.domain.CHANGEME_object.CHANGEME_events import (
    CHANGEMEIsReadyEvent,
)


@dataclass
class CHANGEME:
    id: str = field(default=None)
    attibute_1: str = field(default=None)
    attibute_list: str = field(default_factory=list)
    attibute_dict: str = field(default_factory=dict)
    # Generated events
    events: List[Union[BaseEvent, BaseCommand]] = field(default_factory=list, init=True)

    @classmethod
    def create_from_run_CHANGEME_command(cls, cmd):
        return CHANGEME(id=str(uuid.uuid4()), attibute_1=cmd.attribute1)

    def set_ready(self):
        self.events.append(CHANGEMEIsReadyEvent(self.id))
