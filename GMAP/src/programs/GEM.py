"""
Usage:

    GMAP GEM
    GMAP GEM help
prints this help

    GMAP GEM demo
Launches GEM in demo-mode. Performs a basic calculation to demonstrate basic
use and to verify the program is installed correctly.

    GMAP GEM run [name of input file] [optional parameters]
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
import GMAP.src.tools.WarnSys as GM_WS


def get_parameters(callcommand, FILES):
    # very basic parsing of cmd
    if callcommand[1] in ("demo"):
        exp_inpfile = False
    else:
        exp_inpfile = True
    job, in_parfile, argslist = GM_PP.parse_commandline(
        FILES, callcommand, alljobs, "GMAP GEM", exp_inpfile, True
    )

    # before we can parse the command line, or the input parameter file,
    # we have to know what parameter names to expect. However, to know
    # this, we need to open the default parameter file, but we don't
    # know where it is, before parsing command line and input parameter
    # file.

    # solution: only look for sourcedir and defparfilename in command
    # line and input parameter file, do further parsing later.

    temp_cmd_pardict = GM_PP.find_defparfile_in_cmd(argslist)

    if in_parfile:
        with open(in_parfile) as file:
            in_pardict = GM_PP.get_pardict(file)
        def_parfile = GM_FH.get_def_parfile(
            FILES, temp_cmd_pardict, in_parfile, in_pardict
        )
    else:
        def_parfile = GM_FH.get_def_parfile(FILES, temp_cmd_pardict)

    # as get_def_parfile also checks for the presence of the hard-coded
    # default parameter file (regardless of program flow), no need to do
    # it again.
    ref_parfile = FILES.sourcedir_hc / FILES.refparfilename_hc
    ref_pars = GM_PP.RefPars(ref_parfile)

    # now, we know what the parameters look like. Use this information
    # to properly parse commandline

    # ADD THAT CODE!!!!!!!!!!!!!!

    if def_parfile.suffix == ".txt":
        def_pars = GM_PP.RawPars.from_file(def_parfile, ref_pars, True)
    elif def_parfile == ref_parfile:
        def_pars = ref_pars
    elif def_parfile.suffix == ".ref":
        def_pars = GM_PP.RefPars.add_reffile(def_parfile, ref_pars)
    else:
        GM_WS.Warning(
            "The requested default parameter file " + str(def_parfile) +
            " is of the wrong file format. Please refer to the manual to see "
            "what file types are supported."
        )

    if in_parfile:
        in_pars = GM_PP.RawPars.from_dict(
            in_parfile, in_pardict, ref_pars, False)
    else:
        in_pars = {}

    run_pars = GM_PP.RunPars(FILES, ref_pars, def_pars, in_pars)

    print(def_parfile)
    print(ref_pars)
    print(ref_pars.fname)
    print(ref_pars.options)
    print(ref_pars.choices)
    print(type(ref_pars.fname))
    print(def_pars)
    print(in_pars)
    print(run_pars)


def GEM(callcommand, FILES):
    get_parameters(callcommand, FILES)
    print("entered main of GEM - yet to be constructed")


alljobs = [
    "demo",
    "run"
]


def main():
    callcommand = sys.argv
    if len(callcommand) == 1:
        print(__doc__)
    else:
        FILES = GM_FH.FileLocations()
        GEM(callcommand, FILES)


if __name__ == "__main__":
    main()
