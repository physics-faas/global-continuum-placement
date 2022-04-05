import abc

from global_continuum_placement.domain.platform.platform import Platform


class IPlatformService(abc.ABC):
    @abc.abstractmethod
    async def get_platform(self) -> Platform:
        """ Method to get the platform in cache without updates"""
        pass

    @abc.abstractmethod
    async def update_platform(self) -> Platform:
        """ Method to get an updated platform """
        pass

    @abc.abstractmethod
    async def set_platform(self, platform: Platform) -> None:
        pass
