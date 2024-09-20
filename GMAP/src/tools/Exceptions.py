
# standard library imports
import sys

# local imports
import GMAP.src.tools.PrintTools as GM_PT


class GMAPexception(Exception):
    """The base exception to all errors raised by GMAP.

    Because all errors raised by the program inherit from this one, it
    is easier for any code calling this program to identify any errors
    raised.

    If it is appropriate to, for example, raise an IndexError somewhere,
    instead, GMAP raises the GmapIndexError - a class that inherits from
    this GMAPexception, and from IndexError (to aid callers). If an
    error is not easily traceable back to python errors, it does not
    inherit from any of those, just this one.

    Parameters
    ----------
    message : str
        The message to display when the error triggers.
    error_code : str, default=""
        The code of the triggered error. These error codes also exist
        in the manual. There is more information there, and clickable
        links to the relevant manual pages for solving the issues that
        arose.
    cause : , default=None
    """

    def __init__(self, message=" ", error_code="", cause=None):
        if GM_PT.Printer().verbose != 4:
            sys.tracebacklimit = 0
        self.message = message
        self.error_code = error_code
        self.cause = cause

    def __str__(self):
        if GM_PT.Printer().verbose == 4 and self.cause is not None:
            cc = self.cause.__class__
            return (
                f"\n{cc.__module__}.{cc.__name__} "
                f"caused:{GM_PT.word_wrap(self.message)}"
            )
        return f"{GM_PT.word_wrap(self.message)}"


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
    """When the user wants something from GMAP that isn't implemented
    yet"""


class GmapOSError(GMAPexception, OSError):
    """When GMAP catches (or prevents) an OSError"""


class GmapTypeError(GMAPexception, TypeError):
    """When GMAP catches (or prevents) a TypeError"""


class GmapUnicodeDecodeError(GMAPexception, UnicodeDecodeError):
    """When GMAP catches (or prevents) a UnicodeDecodeError"""


class GmapValueError(GMAPexception, ValueError):
    """When GMAP catches (or prevents) a ValueError"""
