
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


class GmapAttributeError(GMAPexception, AttributeError):
    """When GMAP catches (or prevents) an AttributeError"""


class OldFancyException(GMAPexception):
    """For when you want to be real fancy!"""
