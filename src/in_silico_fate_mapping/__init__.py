try:
    from in_silico_fate_mapping._version import version as __version__
except ImportError:
    __version__ = "unknown"

from in_silico_fate_mapping._widget import FateMappingWidget

__all__ = ("FateMappingWidget",)
