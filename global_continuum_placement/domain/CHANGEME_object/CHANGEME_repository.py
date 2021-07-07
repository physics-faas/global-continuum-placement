import abc
from typing import List

from .CHANGEME_object import CHANGEME


class CHANGEMENotFoundError(Exception):
    pass


class ICHANGEMERepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: str) -> CHANGEME:
        pass

    @abc.abstractmethod
    def get_all(self) -> List[CHANGEME]:
        pass

    @abc.abstractmethod
    def add(self, module_dep: CHANGEME) -> None:
        pass

    @abc.abstractmethod
    def delete(self, module_deployment_id: str) -> None:
        pass
