r"""
Welcome to the G-MAP package. Currently, this is a work in progress. The
following options are available:

GMAP
GMAP help
    prints this help.

GMAP help [program]
    prints the help for the requested program

GMAP GEM
    This program will create the required files for calculating
    vibrational and electronic spectra.

GMAP Setup
    This program will copy the source code and maps to target folder.
"""


from importlib.metadata import version, PackageNotFoundError

from .src.programs import DEPICT
from .src.programs import GEM
from .src.programs import Setup


# Dynamic versioning from git tags.
try:
    __version__ = version("GMAP")
except PackageNotFoundError:
    # Fallback if package is not installed (e.g. local development)
    __version__ = "0.0.0-dev"


alltools = {
    "GEM": GEM,
    "Setup": Setup,
    "DEPICT": DEPICT
}
