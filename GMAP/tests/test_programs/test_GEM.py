
# local imports
from GMAP.src.tools import CmdInterface as GM_CLI


# Now, we also test whether the program can actually run.
def test_if_runs():
    GM_CLI.cmd_interface(["GMAP", "GEM", "run", "../test_inpar.txt"])
