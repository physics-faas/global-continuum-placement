import importlib.metadata

try:
    __version__ = importlib.metadata.version(__package__)
except NameError:
    __version__ = "dev"
