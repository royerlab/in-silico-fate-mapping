try:
    from in_silico_photo_manipulation._version import version as __version__
except ImportError:
    __version__ = "unknown"

from in_silico_photo_manipulation._widget import PhotoMWidget

__all__ = ("PhotoMWidget",)
