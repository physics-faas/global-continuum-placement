import abc
from dataclasses import dataclass

from global_continuum_placement.domain.CHANGEME_object.CHANGEME_repository import ICHANGEMERepository


@dataclass
class IUnitOfWork(abc.ABC):
    CHANGEME_repository: ICHANGEMERepository

    def __enter__(self) -> "IUnitOfWork":
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
