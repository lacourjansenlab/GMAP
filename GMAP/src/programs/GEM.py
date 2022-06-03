"""
Usage:

    GMAP GEM
    GMAP GEM help
prints this help

    GMAP GEM demo
Launches GEM in demo-mode. Performs a basic calculation to demonstrate basic
use and to verify the program is installed correctly.

    GMAP GEM run [name of input file]
Performs a run of GEM using the parameters specified in the included file.


The purpose of GEM is to take an MD trajectory and compute the time-dependent
Hamiltonian to be used in electronic spectral calculations. Instructions on how
to deal with specific chromophores have to be included in the corresponding
.emap file.

For more information, check the manual on N/A.
"""


# standard lib imports
import sys

import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.ParameterParser as GM_PP


def get_parameters(callcommand, FILES):
    job, in_parfile, argslist = GM_PP.parse_commandline(
        FILES, callcommand, alljobs, "GMAP GEM"
    )

    cmd_pardict = GM_PP.get_pardict(argslist)
    if in_parfile:
        with open(in_parfile) as file:
            in_pardict = GM_PP.get_pardict(file)
        def_parfile = GM_FH.get_def_parfile(
            FILES, cmd_pardict, in_parfile, in_pardict
        )
    else:
        def_parfile = GM_FH.get_def_parfile(FILES, cmd_pardict)

    ref_parfile = FILES.sourcedir_hc / FILES.refparfilename_hc
    ref_pars = GM_PP.RefPars(ref_parfile)

    # if def_parfile is of .ref format, update the ref_pars class to change the
    # allowed options (should only be more limiting??) ?
    # Also, add chosen parameter defaults to def_pars object (dict or class?)

    # if def_parfile is of .txt format, only do the latter.

    print(def_parfile)


def main(callcommand, FILES):
    get_parameters(callcommand, FILES)
    print("entered main of GEM - yet to be constructed")


alljobs = [
    "demo",
    "run"
]


if __name__ == "__main__":
    callcommand = sys.argv
    if len(callcommand) == 1:
        print(__doc__)
    else:
        FILES = GM_FH.FileLocations()
        main(callcommand, FILES)
