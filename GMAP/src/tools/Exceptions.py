
# standard library imports
import sys

# local imports
import GMAP.src.tools.PrintTools as GM_PT


class GMAPexception(Exception):
    def __init__(self, message, error_code="", cause=None):
        # super(GMAPexception, self).__init__(f"with code {error_code}")
        if GM_PT.Printer().verbose != 4:
            sys.tracebacklimit = 0
        self.message = message
        self.error_code = error_code
        self.cause = cause

    def __str__(self):
        # return f"\nError code {self.error_code}."
        if GM_PT.Printer().verbose == 4 and self.error_code is not None:
            cc = self.cause.__class__
            return (
                f"\n{cc.__module__}.{cc.__name__} "
                f"caused:{GM_PT.prettifier(self.message)}"
            )
        return f"{GM_PT.prettifier(self.message)}"


# ---------- Custom errors ---------------------------------------------

class GmapFileSyntaxError(GMAPexception, SyntaxError):
    """When GMAP parses a file with incorrect syntax"""


class GmapParameterError(GMAPexception):
    """When there is some issue with the input parameters

    | If the parameters are wrongly specified - GmapFileSyntaxError
    | If the parameters are of wrong type - GmapTypeError
    | If the parameters have unphysical value - GmapValueError

    This error is meant for more complex issues. For example, two
    parameters each have a choice specified. Each on their own is
    perfectly fine and wouldn't raise an error. The combination of the
    two however, has some issue.
    """


class GmapMDFileError(GMAPexception):
    """When there is some issue with the input MD file"""


# ---------- Python builtin-catchers -----------------------------------

class GmapAttributeError(GMAPexception, AttributeError):
    """When GMAP catches (or prevents) an AttributeError"""


class GmapFileNotFoundError(GMAPexception, FileNotFoundError):
    """When GMAP catches (or prevents) a FileNotFoundError"""


class GmapIndexError(GMAPexception, IndexError):
    """When GMAP catches (or prevents) an IndexError"""


class GmapIsADirectoryError(GMAPexception, IsADirectoryError):
    """When GMAP catches (or prevents) an IsADiretoryError"""


class GmapKeyError(GMAPexception, KeyError):
    """When GMAP catches (or prevents) a KeyError"""


class GmapNotADirectoryError(GMAPexception, NotADirectoryError):
    """When GMAP catches (or prevents) a NotADirectoryError"""


class GmapNotImplementedError(GMAPexception, NotImplementedError):
    """When the user wants something from GMAP that isn't implemented yet"""


class GmapOSError(GMAPexception, OSError):
    """When GMAP catches (or prevents) an OSError"""


class GmapTypeError(GMAPexception, TypeError):
    """When GMAP catches (or prevents) a TypeError"""


class GmapUnicodeDecodeError(GMAPexception, UnicodeDecodeError):
    """When GMAP catches (or prevents) a UnicodeDecodeError"""


class GmapValueError(GMAPexception, ValueError):
    """When GMAP catches (or prevents) a ValueError"""
