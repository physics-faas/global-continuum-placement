import platform

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

try:
    module_name = ".".join(__name__.split(".")[:-1])
    __version__ = importlib_metadata.version(module_name)
except Exception:
    __version__ = "dev"

python_version = platform.python_version()
