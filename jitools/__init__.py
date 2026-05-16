from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("jitools")
except PackageNotFoundError:
    __version__ = "unknown"

from .constants import SABAT_SCHWEINITZ_TUNEABLE_INTERVALS
from .pitch import Pitch
from .pitch_collection import PitchCollection
from .lookup_table_generator import generate_enharmonic_lookup_table