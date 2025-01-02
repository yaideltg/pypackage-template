from importlib.metadata import version, PackageNotFoundError

__all__ = ["deps, armmodel"]

try:
    __version__ = version("pyarmm")
except PackageNotFoundError:
    # package is not installed
    pass
