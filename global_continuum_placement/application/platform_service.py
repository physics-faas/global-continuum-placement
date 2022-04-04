import abc

from global_continuum_placement.domain.platform.platform import Platform


class IPlatformService(abc.ABC):
    @abc.abstractmethod
    async def update_platform(self) -> Platform:
        """ Method to get an updated platform """
        pass
