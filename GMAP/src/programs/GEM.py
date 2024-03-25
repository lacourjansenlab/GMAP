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

# local imports
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP
import GMAP.src.tools.PrintTools as GM_PT
from GMAP.src.tools.PrintTools import devprint as dpr


def get_parameters(Files, Printer, in_parfile, argslist):
    """Collect all provided parameters, and store them.

    Parameters are defined (along with default choices) in the reference
    parameter file. Users can have a different set of defaults defined
    in the default parameter file, and specific choices for this (set of)
    runs in the input parameter file and the command line. This function
    uses the functionality in src/tools/ParameterParser.py to collect
    all choices, and construct a final set of choices from them. All
    generated options are then returned.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    in_parfile : `pathlib.Path`
        The path to the requested input parameter file.
    argslist : list of str
        The slice of sys.argv containing all parameter choices given on
        the command line.

    Returns
    -------
    CmdPars : :class:`RawPars`
        Contains any parameter choices made on the command line
    InPars : :class:`RawPars`
        Contains any parameter choices made in the input parameter file
    DefPars : :class:`RawPars` or :class:`RefPars`
        Contains all default parameter choices. Might be RefPars, might be
        from a separate default parameters file.
    RefPars : :class:`RefPars`
        Contains all available parameters from GMAP itself (not map-specific)
    mapdict : dict of str: :class:`~GMAP.src.tools.MapReader.Map` pairs
        Stores all the :class:`~GMAP.src.tools.MapReader.Map` objects for
        each map supplied. The keys are the Map.name attributes corresponding
        to the maps stored as values.
    """

    # very basic parsing of cmd

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
    # reference parameter file (regardless of program flow), no need to do
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
            "SU_GEM_1", True
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
    for map_ in mapdict.values():
        map_.find_refpars(Printer)
        if map_.RefPars:
            dpr(map_.RefPars.choices)

    # step 12 (finish parsing cmdline, inparfile, defparfile)

    # cmdline
    CmdPars = GM_PP.RawPars.from_cmdline(
        Printer, argslist, RefPars,
        {name: map_.RefPars for name, map_ in mapdict.items()},
        False
    )

    for map_ in mapdict.values():
        map_.find_rawpars(Printer, CmdPars, InPars, DefPars)

    CmdPars.finalize_map_pars(Printer)
    InPars.finalize_map_pars(Printer)
    if def_parfile != ref_parfile:
        DefPars.finalize_map_pars(Printer)

    RunPars = GM_PP.RunPars(
        Files, Printer, CmdPars, InPars, DefPars, RefPars, True
    )

    for map_ in mapdict.values():
        map_.find_runpars(Files, Printer, RunPars)

    return CmdPars, InPars, DefPars, RefPars, mapdict


# still a placeholder - this function still has to grow. Should in the
# end manage the different run modes, and probably do nothing else?
def GEM(callcommand, Files, Printer):
    # step 1 (is GEM in demo mode?)
    if callcommand[1] in ("demo"):
        exp_inpfile = False
    else:
        exp_inpfile = True
    # step 2 (very basic cmd line parse)
    job, in_parfile, argslist = GM_PP.parse_commandline(
        Files, Printer, callcommand, alljobs, "GMAP GEM", exp_inpfile, True
    )

    CmdPars, InPars, DefPars, RefPars, mapdict = get_parameters(
        Files, Printer, in_parfile, argslist
    )
    GM_PT.devprint("entered main of GEM - yet to be constructed")


# The jobs that GEM can currently execute.
alljobs = [
    "demo",
    "run"
]


def main(callcommand):
    """Fakes behaviour as if called from __main__.

    During normal operation (user types 'GMAP ...' in the command line),
    this function should never be called. This function replicates the
    'normal' behaviour so partial tests are possible.
    """

    if len(callcommand) == 1:
        print(__doc__)
    else:
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        GEM(callcommand, Files, Printer)


if __name__ == "__main__":
    callcommand = sys.argv
    main(callcommand)
