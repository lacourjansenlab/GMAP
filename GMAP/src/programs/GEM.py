r"""
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
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP
import GMAP.src.tools.PrintTools as GM_PT
from GMAP.src.tools.PrintTools import devprint as dpr


def get_parameters(callcommand, Files, Printer):
    # very basic parsing of cmd

    # step 1 (is GEM in demo mode?)
    if callcommand[1] in ("demo"):
        exp_inpfile = False
    else:
        exp_inpfile = True
    # step 2 (very basic cmd line parse)
    job, in_parfile, argslist = GM_PP.parse_commandline(
        Files, Printer, callcommand, alljobs, "GMAP GEM", exp_inpfile, True
    )

    # before we can parse the command line, or the input parameter file,
    # we have to know what parameter names to expect. However, to know
    # this, we need to open the default parameter file, but we don't
    # know where it is, before parsing command line and input parameter
    # file.

    # solution: only look for sourcedir and defparfilename in command
    # line and input parameter file, do further parsing later.

    # step 3 (See if the arg from cmdline have anything on srcdir or defpar)
    temp_cmd_pardict = GM_PP.find_defparfile_in_cmd(Printer, argslist)

    if in_parfile:
        # step 4 (very basic inpar file parser)

        # check if file is UTF8
        GM_FH.check_file_readability(Printer, in_parfile)
        with open(in_parfile) as file:
            in_pardict = GM_PP.get_pardict(file)
        # step 5 (find which defpar to use)
        def_parfile = GM_FH.get_def_parfile(
            Files, Printer, temp_cmd_pardict, in_parfile, in_pardict
        )
    else:
        # step 5 (find which defpar to use)
        def_parfile = GM_FH.get_def_parfile(Files, Printer, temp_cmd_pardict)

    # as get_def_parfile also checks for the presence of the hard-coded
    # default parameter file (regardless of program flow), no need to do
    # it again.
    # step 6 (find refparfile)
    ref_parfile = Files.sourcedir_hc / Files.refparfilename_hc
    # step 7 (parse refparfile)
    GM_FH.check_file_readability(Printer, ref_parfile)  # check if file is UTF8
    RefPars = GM_PP.RefPars(Printer, ref_parfile)

    # step 8 (parse defparfile)
    if def_parfile.suffix == ".txt":
        # check if file is UTF8
        GM_FH.check_file_readability(Printer, def_parfile)
        DefPars = GM_PP.RawPars.from_file(
            Printer, def_parfile, RefPars, True
        )
    elif def_parfile == ref_parfile:
        DefPars = RefPars
        setattr(DefPars, "not_found", {})
    elif def_parfile.suffix == ".ref":
        DefPars = GM_PP.RefPars.add_reffile(Printer, def_parfile, RefPars)
    else:
        Printer.warning(
            f"The requested default parameter file {def_parfile} is of the "
            "wrong file format. "
            "Please refer to the manual to see what file types are supported.",
            True
        )

    # step 9 (parse inparfile, not map part)
    if in_parfile:
        InPars = GM_PP.RawPars.from_dict(
            Printer, in_parfile, in_pardict, RefPars, False)
    else:
        InPars = GM_PP.RawPars.create_empty()

    # step 10 (find mapdir in cmdline > inparfile > defparfile)
    mapdirs = GM_PP.find_mapdir(Files, Printer, argslist, InPars, DefPars)

    # step 11 (for each map, parse parameters.ref, if present)
    mapdict = GM_MR.scan_mapdirs(mapdirs)
    for _map in mapdict.values():
        _map.find_refpars(Printer)
        dpr(_map.RefPars.choices)

    # step 12 (finish parsing cmdline, inparfile, defparfile)

    # cmdline
    CmdPars = GM_PP.RawPars.from_cmdline(
        Printer, argslist, RefPars,
        {name: _map.RefPars for name, _map in mapdict.items()},
        False
    )

    # inparfile
    if InPars:
        for name, _map in mapdict.items():
            InPars.extract_choices_map(Printer, name, _map.RefPars)
        InPars.finalize_map_pars(Printer)

    # defparfile - _if_ it contains anything from a certain map, it must
    # contain all from that map
    if def_parfile != ref_parfile:
        for name, _map in mapdict.items():
            present = DefPars.extract_choices_map(Printer, name, _map.RefPars)
            if present and DefPars.is_default:
                DefPars.check_completeness(Printer, _map.RefPars)
        DefPars.finalize_map_pars(Printer)

    # --------
    # TO DO
    # --------

    # step 4 (combine cmdline, inparfile, defparfile, base refparfile
    #         into runpar)
    #       take into account possible conflicts
    #       Check whether requested files exist, (are of correct format?), etc.
    # step 5 (step 4, but for maps)

    RunPars = GM_PP.RunPars(Files, Printer, CmdPars, InPars, DefPars, RefPars)

    GM_PT.devprint(def_parfile)
    GM_PT.devprint(RefPars)
    GM_PT.devprint(RefPars.fname)
    GM_PT.devprint(RefPars.options)
    GM_PT.devprint(RefPars.choices)
    GM_PT.devprint(type(RefPars.fname))
    GM_PT.devprint(DefPars.choices)
    GM_PT.devprint(DefPars.not_found)
    GM_PT.devprint(InPars.choices)
    GM_PT.devprint(InPars.not_found)
    GM_PT.devprint(RunPars)


def GEM(callcommand, Files, Printer):
    get_parameters(callcommand, Files, Printer)
    GM_PT.devprint("entered main of GEM - yet to be constructed")


alljobs = [
    "demo",
    "run"
]


def main():
    callcommand = sys.argv
    if len(callcommand) == 1:
        print(__doc__)
    else:
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        GEM(callcommand, Files, Printer)


if __name__ == "__main__":
    main()
