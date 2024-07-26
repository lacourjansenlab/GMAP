
# local imports
from GMAP.src.tools import CmdInterface as GM_CI


# Now, we also test whether the program can actually run.
def test_if_runs():
    GM_CI.cmd_interface(["GMAP", "GEM", "run", "../test_inpar.txt"])
