"""
Defines all custom exceptions used by GMAP

There is one central GMAPexception subclassing Exception. All other
exceptions here subclass GMAPexception. The purpose of this is so any
program directly calling GMAP (not through subprocess) can catch
GMAPexceptions to find any problems raised by GMAP explicitly.

Where applicable, these errors also subclass the relevant python
exception to also allow catching the type they actually represent.

Classes
-------
GMAPexception
    The base exception parent to all errors raised by GMAP
GmapFileSyntaxError
    A SyntaxError raised by GMAP, specifically for an input file
GmapParameterError
    Raised upon problems with input parameters
GmapMDFileError
    Raised upon problems with input MD file
GmapAttributeError
    An AttributeError raised by GMAP
GmapFileNotFoundError
    A FileNotFoundError raised by GMAP
GmapIndexError
    An IndexError raised by GMAP
GmapIsADirectoryError
    An IsADirectoryError raised by GMAP
GmapKeyError
    A KeyError raised by GMAP
GmapNotADirectoryError
    A NotADirectoryError raised by GMAP
GmapNotImplementedError
    A NotImplementedError raised by GMAP
GmapOSError
    An OSError raised by GMAP
GmapTypeError
    A TypeError raised by GMAP
GmapUnicodeDecodeError
    A UnicodeDecodeError raised by GMAP
GmapValueError
    A ValueError raised by GMAP
"""


# standard library imports
import sys

# local imports
import GMAP.src.tools.print_tools as GM_pt


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
        if GM_pt.Printer.verbose != 4:
            sys.tracebacklimit = 0
        self.message = message
        self.error_code = error_code
        self.cause = cause

    def __str__(self):
        if GM_pt.Printer.verbose == 4 and self.cause is not None:
            cc = self.cause.__class__
            return (
                f"\n{cc.__module__}.{cc.__name__} "
                f"caused:{GM_pt.word_wrap(self.message)}"
            )
        return f"{GM_pt.word_wrap(self.message)}"


# ---------- Custom errors ---------------------------------------------

class GmapFileSyntaxError(GMAPexception, SyntaxError):
    """Raised when GMAP parses a file with incorrect syntax."""


class GmapParameterError(GMAPexception):
    """Raised when there is some issue with the input parameters.

    | If the parameters are wrongly specified - GmapFileSyntaxError
    | If the parameters are of wrong type - GmapTypeError
    | If the parameters have unphysical value - GmapValueError

    This error is meant for more complex issues. For example, two
    parameters each have a choice specified. Each on their own is
    perfectly fine and wouldn't raise an error. The combination of the
    two however, has some issue.
    """


class GmapMDFileError(GMAPexception):
    """Raised when there is some issue with the input MD file."""


# ---------- Python builtin-catchers -----------------------------------

class GmapAttributeError(GMAPexception, AttributeError):
    """Raised when GMAP catches (or prevents) an AttributeError."""


class GmapFileNotFoundError(GMAPexception, FileNotFoundError):
    """Raised when GMAP catches (or prevents) a FileNotFoundError."""


class GmapIndexError(GMAPexception, IndexError):
    """Raised when GMAP catches (or prevents) an IndexError."""


class GmapIsADirectoryError(GMAPexception, IsADirectoryError):
    """Raised when GMAP catches (or prevents) an IsADiretoryError."""


class GmapKeyError(GMAPexception, KeyError):
    """Raised when GMAP catches (or prevents) a KeyError."""


class GmapNotADirectoryError(GMAPexception, NotADirectoryError):
    """Raised when GMAP catches (or prevents) a NotADirectoryError."""


class GmapNotImplementedError(GMAPexception, NotImplementedError):
    """Raised when the user wants something from GMAP that isn't
    implemented yet.
    """


class GmapOSError(GMAPexception, OSError):
    """Raised when GMAP catches (or prevents) an OSError."""


class GmapTypeError(GMAPexception, TypeError):
    """Raised when GMAP catches (or prevents) a TypeError."""


class GmapUnicodeDecodeError(GMAPexception, UnicodeDecodeError):
    """Raised when GMAP catches (or prevents) a UnicodeDecodeError."""


class GmapValueError(GMAPexception, ValueError):
    """Raised when GMAP catches (or prevents) a ValueError."""
