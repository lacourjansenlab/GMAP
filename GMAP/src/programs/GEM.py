"""

Usage:

    GMAP GEM
    GMAP GEM help
prints this help

    GMAP GEM demo
Launches GEM in demo-mode. Performs a basic calculation to demonstrate basic
use and to verify the program is installed correctly.

    GMAP GEM [name of input file]
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


def get_parameters(callcommand):
    FILES = GM_FH.FileLocations()
    job, in_parfile, argslist = GM_PP.parse_commandline(FILES, callcommand)
    
    cmd_pardict = GM_PP.get_pardict(argslist)
    if in_parfile:
        with open(in_parfile) as file:
            in_pardict = GM_PP.get_pardict(file)
        def_parfile = get_def_parfile(
            FILES, cmd_pardict, in_parfile, in_pardict
        )
    else:
        def_parfile = get_def_parfile(FILES, cmd_pardict)
    
    print(def_parfile)
    

def get_def_parfile(FILES, cmd_pardict, in_parfile=None, in_pardict={}):
    for pardict in [cmd_pardict, in_pardict]:
        if "defparfilename" in pardict:
            try:
                defname = pardict["defparfilename"][0]
            except Exception:
                continue
            defpath = get_def_parfile_core(
                defname, FILES, cmd_pardict, in_parfile, in_pardict
            )
            if defpath:
                return defpath

    defname = "default_parameters.txt"
    defpath = get_def_parfile_core(
        defname, FILES, cmd_pardict, in_parfile, in_pardict
    )
    if defpath:
        return defpath
    
    return None


def get_def_parfile_core(
    defname, FILES, cmd_pardict, in_parfile=None, in_pardict={}
):
    if "sourcedir" in cmd_pardict and len(cmd_pardict["sourcedir"]) > 0:
        defpath = FILES.cwd / cmd_pardict["sourcedir"][0] / defname
        if defpath.is_file():
            return defpath.resolve()
    if "sourcedir" in in_pardict:
        defpath = in_parfile.parent / defname
        if defpath.is_file():
            return defpath.resolve()
    defpath = FILES.sourcedir_hc / defname
    if defpath.is_file():
        return defpath.resolve()
    return None


def main(callcommand):
    get_parameters(callcommand)
    print("entered main of GEM - yet to be constructed")


if __name__ == "__main__":
    callcommand = sys.argv
    if len(callcommand) == 1:
        print(__doc__)
    else:
        main(callcommand)
