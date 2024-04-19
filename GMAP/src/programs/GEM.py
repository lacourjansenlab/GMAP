r"""
Usage:

    GMAP GEM
    GMAP GEM help
Prints this help.

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

# 3rd party lib imports
import numpy as np

# local imports
import GMAP.src.tools.CLibLoader as GM_CL
import GMAP.src.tools.FileHandler as GM_FH
# import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP
import GMAP.src.tools.PhysicsFunctions as GM_PF
import GMAP.src.tools.PrintTools as GM_PT
from GMAP.src.tools.PrintTools import devprint as dpr
import GMAP.src.tools.SystemReader as GM_SR


# TO DO inside!
def manage_frame(frame, Printer, RunPars):
    """Performs all the checks involved with starting a new frame.

    Future/TODO:
    Checks if the new frame should be treated (or is out of range).
    Prints the new frame number, along with an ETA (to know how much
    longer the calculation will take). Also confirms whether there is
    enough time to start on the next batch of frames before time runs
    out.

    Parameters
    ----------
    frame : `MDA.Timestep`
        The frame that will be treated next.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    """

    framenum = frame.frame
    if framenum >= RunPars.stop_frame:
        return True

    # Do a frame number print here! (for ETA type prints)
    # Check if there is enough time to do another batch of frames
    # (to avoid running longer than the max amount of time)


# TO DO inside!
def trj_loop(Printer, RunPars, System):
    """Performs the main per-frame loop for GEM.

    Does the last bit of initialization that needs to happen, and then
    treats each frame.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    System : :class:`~GMAP.src.tools.SystemReader.System`
        The class containing all the information on the system of the
        MD trajectory.
    """

    # first, do precalc

    # create empty structures, initialize whats needed

    # compare runpar endframe to mda nframes - adjust endframe
    if RunPars.stop_frame >= len(System.universe.trajectory):
        RunPars.stop_frame = len(System.universe.trajectory)

    # GEM is now done - let maps initialize as well
    for mapname in System.oscillators_ordered.keys():
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_pre_run(Printer, map_, System)

    # And in case maps did anything weird...
    RunPars.manage_dtypes()

    Printer.add_time(3, "Starting on frames", "ms")

    trj = System.universe.trajectory
    for frame in trj[RunPars.start_frame:]:
        Printer.add_time(4, "Starting on frame - starting updates", "ms")
        # manage frame number (if not in range, skip, prints, ETA, etc)
        if manage_frame(frame, Printer, RunPars):
            break

        # rebuild the frame-specific data (positions, box, etc)
        System.update_properties(Printer)
        Printer.add_time(4, "done system updates. next: osc updates", "ms")
        for oscillator in System.oscillators:
            oscillator.frame_update(Printer, System)

        Printer.add_time(4, "updates done. next: initialize", "ms")

        # (only if needed) recalc COM

        # initialize output structures (like Ham)
        hamiltonian = np.zeros((System.nosc, System.nosc), dtype="float32")
        dipoles = np.zeros((System.nosc, 3), dtype="float32")

        Printer.add_time(4, "initialize done. next: map init", "ms")

        # call pre-frame funcs of maps
        for mapname in System.oscillators_ordered.keys():
            map_ = RunPars.requested_mapdict[mapname]
            map_.code.GM_pre_frame(Printer, map_, System)

        Printer.add_time(4, "map init done. next: calculation", "ms")

        # perform the actual calculations
        hamiltonian, dipoles = GM_PF.calc_frame(
            Printer, RunPars, System, dipoles, hamiltonian)

        Printer.add_time(4, "calculation done. next: map final", "ms")

        # call post-frame functions of maps
        for mapname in System.oscillators_ordered.keys():
            map_ = RunPars.requested_mapdict[mapname]
            map_.code.GM_post_frame(Printer, map_, System)

        Printer.add_time(4, "map final done. next: write output", "ms")

        # write calculated data to files
        GM_FH.write_output(RunPars, frame.frame, hamiltonian, dipoles)

    # lastly, do postcalc:
    for mapname in System.oscillators_ordered.keys():
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_post_run(Printer, map_, System)

    # print all that the user does not yet know
    # (profiler?)


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

    RunPars, mapdict, _, _, _, _ = GM_PP.get_parameters(
        Files, Printer, in_parfile, argslist
    )
    Printer.add_time(3, "Parsed GMAP parameters", "ms")

    # end of SU errors

    GM_MR.manage_maps(Files, Printer, RunPars, mapdict)
    Printer.add_time(3, "Added all maps", "ms")

    # next - MD system!
    System = GM_SR.System(Files, Printer, RunPars)
    Printer.add_time(3, "Initialized MD system", "ms")

    # GEM is now done - let maps initialize as well
    for mapname in System.oscillators_ordered.keys():
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_post_init(Files, Printer, map_, System)
    Printer.add_time(2, "Initialization complete", "ms")

    # initialize C library
    GM_CL.VEG_CLib(Printer, RunPars)

    trj_loop(Printer, RunPars, System)

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
