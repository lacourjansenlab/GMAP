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


Groningen Electrostatic Maps

The purpose of GEM is to take an MD trajectory and compute the time-dependent
Hamiltonian to be used in electronic spectral calculations. Instructions on how
to deal with specific chromophores have to be included in the corresponding
.emap file.

For more information, check the manual on N/A.
"""


# standard lib imports
import datetime
import sys

# 3rd party lib imports
# import numpy as np

# local imports
import GMAP.src.tools.CLibLoader as GM_CL
import GMAP.src.tools.FileHandler as GM_FH
# import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP
import GMAP.src.tools.PhysicsFunctions as GM_PF
import GMAP.src.tools.Plotter as GM_Pl
import GMAP.src.tools.PrintTools as GM_PT
import GMAP.src.tools.SystemReader as GM_SR


# TO DO inside!
def manage_frame(frame, RunPars):
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
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    """

    framenum = frame.frame
    if framenum >= RunPars.stop_frame:
        return True

    # Do a frame number print here! (for ETA type prints)
    relframenum = framenum - RunPars.start_frame

    # If this is the 0th frame, or only first digit is non-zero.
    # We multiply relframenum (the n in nth frame treated) by 10 to make
    # sure that the resulting set is never empty (frames 1 through 9)
    if relframenum == 0 or set(str(relframenum * 10)[1:]) == set("0"):
        # if framenum has form 10^n with n=int
        if str(relframenum)[0] == "1" and relframenum != 1:
            GM_PT.Printer().print(2, "")
            verbose_level = 1
        else:
            verbose_level = 2
    else:  # lvl4 prints ETA for each frame.
        verbose_level = 4

    GM_PT.Printer().print(
        4,
        "Current time   | current frame | time elapsed | time to go   | "
        "end time  (est.)"
    )
    print_frame_ETA(
        verbose_level, framenum, RunPars.start_frame, RunPars.stop_frame)

    # Check if there is enough time to do another batch of frames
    # (to avoid running longer than the max amount of time)


def print_frame_ETA(verbose, framenum, startframe, endframe):
    """Prints some time information about this frame.

    Will report on the time at which the report takes place, the current
    frame, time elapsed, an estimate of the time remaining, and an
    estimate when the program will be done. The following format is
    used:

    Provided format:
    Current time | current frame | time elapsed | time to go   | end time
    Fri 13 HH:MM | xxxyyyzzz     | xxx-xx:xx:xx | xxx-xx:xx:xx | Fri 13 HH:MM

    .. important :: These estimates will improve when more frames have
    already been treated. For small systems (proteins, a speed of frames
    per second) any estimate below 10 frames is worthless, after 100
    frames they get usable. For large systems (assemblies, a speed of
    minutes per frame), this estimate will most likely converge much
    faster, but testing is required to know how fast.

    This difference is caused by the contribution of numba jitting. This
    usually takes a few seconds, which is a significant amount of time
    for small systems, but not for larger ones.

    .. note :: The weekdays will be reported in the
    installation(? System?) language of the user. As different languages
    have a shorthand for weekdays of a different amount of characters,
    the program has 14 characters reserved (so a few spaces are missing
    in the example above).

    .. note :: The estimated time to go (and end time) are based on how
    long earlier frames took. That means that during the first frame
    treated, no estimate can be provided, and wont. The last two columns
    will not be used/filled in on the first frame.

    Parameters
    ----------
    verbose : int
        The verbose level at which the print of this function should be
        performed
    framenum : int
        The frame number at which this function is called
    startframe : int
        The first frame that is treated during the calculation, as
        specified by the user using the parameter start_frame.
    endframe : int
        The (excusive) end point of the calculation, so the first frame
        that won't be treated anymore. As specified by the user using
        the parameter end_frame.
    """

    timer = GM_PT.Printer().Timer
    toprint = []

    # first, add current time (e.g. Fri 13 HH:MM)
    now = datetime.datetime.now()
    datestr = now.strftime("%a %d %H:%M")
    # English has len 12, german has len 11, make it 14 in case any other
    # language needs it... (can't find overview of supported languages)
    toprint.append(f"{datestr: <14}")

    # Then, add current frame number
    toprint.append(f"{framenum: >13}")  # len("currrent frame") == 13

    # Next: time elapsed
    now_ns = timer.get_time("FrameUpdate")
    now_str = GM_PT.time_to_str(now_ns, "s")
    toprint.append(f"{now_str: >12}")  # To fit a max of 999 days.

    if not framenum == startframe:  # if not very first frame of calculation
        # Next: time to go
        start_heavy_ns = timer.get_time("StartLoop")
        ns_per_frame = int((now_ns - start_heavy_ns) / (framenum - startframe))
        ns_to_go = ns_per_frame * (endframe - framenum)
        to_go_str = GM_PT.time_to_str(ns_to_go, "s")
        toprint.append(f"{to_go_str: >12}")  # To fit a max of 999 days.

        # end time
        togo = datetime.timedelta(microseconds=ns_to_go // 1000)
        end_time = now + togo
        datestr = end_time.strftime("%a %d %H:%M")
        # English has len 12, german has len 11, make it 14 in case any other
        # language needs it... (can't find overview of supported languages)
        toprint.append(f"{datestr: <14}")

    GM_PT.Printer().print(verbose, " | ".join(toprint))


# TO DO inside!
def trj_loop(RunPars, System):
    """Performs the main per-frame loop for GEM.

    Does the last bit of initialization that needs to happen, and then
    treats each frame.

    Parameters
    ----------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    System : :class:`~GMAP.src.tools.SystemReader.System`
        The class containing all the information on the system of the
        MD trajectory.
    """

    # first, do precalc
    GM_PT.Printer().add_time(
        3, "Preparing loop over frames", "PrepLoop", "ms")

    # create empty structures, initialize whats needed

    # compare runpar endframe to mda nframes - adjust endframe
    if RunPars.stop_frame >= len(System.universe.trajectory):
        RunPars.stop_frame = len(System.universe.trajectory)

    # let maps prepare for the calculation
    for mapname in System.oscillators_ordered.keys():  # singles
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_pre_run(map_, System)
    for mapname in System.oscillators_ordered_coup.keys():  # pairs
        map_ = RunPars.requested_pairmapdict[mapname]
        map_.code.GM_pre_run(map_, System)

    # And in case maps did anything weird...
    RunPars.manage_dtypes()

    # Report on the system we're going to treat.
    GM_FH.write_legend(RunPars, System)

    trj = System.universe.trajectory
    GM_FH.clear_output(RunPars)

    # In case MDA needs a long time to start the loop.
    GM_PT.Printer().add_time(
        3, "Starting loop over frames", "StartLoop", "ms")

    # print header for the ETA table (print lvl 4 has header per frame)
    GM_PT.Printer().print(
        1,
        "\nCurrent time   | current frame | time elapsed | time to go   | "
        "end time  (est.)", detailed_instructions=[1, 2, 3]
    )

    for frame in trj[RunPars.start_frame:]:
        GM_PT.Printer().add_time(
            4, "Starting on frame - starting updates", "FrameUpdate", "ms")
        # manage frame number (if not in range, skip, prints, ETA, etc)
        if manage_frame(frame, RunPars):
            break

        # rebuild the frame-specific data (positions, box, etc)
        System.update_properties()
        GM_PT.Printer().add_time(
            4, "done system updates. next: osc updates", "OscUpdate", "ms")
        for oscillator in System.oscillators:
            oscillator.frame_update(System)

        GM_PT.Printer().add_time(
            4, "updates done. next: initialize", "StructInit", "ms")

        # (only if needed) recalc COM

        # initialize output structures (like Ham)
        outputs = GM_PF.generate_output_structures(RunPars, System)

        GM_PT.Printer().add_time(
            4, "initialize done. next: map init", "MapFInit", "ms")

        # call pre-frame funcs of maps
        for mapname in System.oscillators_ordered.keys():  # singles
            map_ = RunPars.requested_mapdict[mapname]
            map_.code.GM_pre_frame(map_, System)
        for mapname in System.oscillators_ordered_coup.keys():  # pairs
            map_ = RunPars.requested_pairmapdict[mapname]
            map_.code.GM_pre_frame(map_, System)

        GM_PT.Printer().add_time(
            4, "map init done. next: calculation", "Calc", "ms")

        # perform the actual calculations
        outputs = GM_PF.calc_frame(RunPars, System, outputs)

        GM_PT.Printer().add_time(
            4, "calculation done. next: map final", "MapFPost", "ms")

        # call post-frame functions of maps
        for mapname in System.oscillators_ordered.keys():  # singles
            map_ = RunPars.requested_mapdict[mapname]
            map_.code.GM_post_frame(map_, System)
        for mapname in System.oscillators_ordered_coup.keys():  # pairs
            map_ = RunPars.requested_pairmapdict[mapname]
            map_.code.GM_post_frame(map_, System)

        GM_PT.Printer().add_time(
            4, "map final done. next: write output", "FrameWrite", "ms")

        # write calculated data to files
        GM_FH.write_output(RunPars, frame.frame, outputs)

        GM_PT.Printer().add_time(
            4, "Frame completed. Loading next frame\n", "LoadFrame", "ms")

    GM_PT.Printer().add_time(
        3, "Frames Completed. Finishing up.", "MapPost", "ms")

    # lastly, do postcalc:
    for mapname in System.oscillators_ordered.keys():  # singles
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_post_run(map_, System)
    for mapname in System.oscillators_ordered_coup.keys():  # pairs
        map_ = RunPars.requested_pairmapdict[mapname]
        map_.code.GM_post_run(map_, System)

    # print all that the user does not yet know
    # (profiler?)


def print_calculation_summary(RunPars):

    def sumavg(*args):
        total_time = pr.Timer.get_total_ns(*args)
        avg_time = total_time // nframes
        tot_str = GM_PT.time_to_str(total_time)
        avg_str = GM_PT.time_to_str(avg_time, "ms")
        return f"{tot_str: >12}  --> {avg_str[-12:]} / frame"

    pr = GM_PT.Printer()
    sum_ = pr.Timer.get_total_format
    nframes = RunPars.stop_frame - RunPars.start_frame

    # making sure the last 'split' is saved in timer.totals()
    pr.add_time(5, "", "end")

    pr.print(1, "\n\nCalculation Finished. Summary:")

    # print all time splits
    init_labels = [
        "ParParse", "AddMaps", "MDinit", "MapInit", "ClibLoad", "PrepLoop"]
    f_load = ["StartLoop", "LoadFrame"]
    f_upd = ["FrameUpdate", "PosBox", "COM"]
    f_init = f_upd + ["OscUpdate", "StructInit", "MapFInit"]
    f_calc = ["Calc", "VEGprop", "VEGcalc", "VEGuse", "PrepCoup", "CalcCoup"]
    f_post = ["MapFPost", "FrameWrite"]
    perframe = f_init + f_calc + f_post + f_load
    post_labels = ["MapPost"]
    all_labels = init_labels + perframe + post_labels

    pr.print(1, f"Total time:                   {sum_(*all_labels): >12}")
    pr.print(2, f"  Initialization:             {sum_(*init_labels): >12}")
    pr.print(3, f"    Parsing parameters:       {sum_('ParParse'): >12}")
    pr.print(3, f"    Collecting maps:          {sum_('AddMaps'): >12}")
    pr.print(3, f"    Initializing MD system:   {sum_('MDinit'): >12}")
    pr.print(3, f"    Initializing maps:        {sum_('MapInit'): >12}")
    pr.print(3, f"    Loading C libraries:      {sum_('ClibLoad'): >12}")
    pr.print(2, f"  Treating frames:            {sumavg(*perframe)}")
    pr.print(3, f"    Reading frames:           {sumavg(*f_load)}")
    pr.print(3, f"    Per-frame initialization: {sumavg(*f_init)}")
    pr.print(4, f"      Position/box updates:   {sumavg('PosBox')}")
    pr.print(4, f"      Center of Mass:         {sumavg('COM')}")
    pr.print(4, f"      Oscillator updates:     {sumavg('OscUpdate')}")
    pr.print(4, f"      Structure init.:        {sumavg('PosBox')}")
    pr.print(4, f"      Map initialization:     {sumavg('MapFInit')}")
    pr.print(3, f"    Calculation:              {sumavg(*f_calc)}")
    pr.print(4, f"      Calculating estatics:   {sumavg('VEGcalc')}")
    pr.print(4, f"      SingleMap outputs:      {sumavg('VEGuse')}")
    pr.print(4, f"      Coupling preparation:   {sumavg('PrepCoup')}")
    pr.print(4, f"      Coupling calculation:   {sumavg('CalcCoup')}")
    pr.print(3, f"    Frame finalization:       {sumavg(*f_post)}")
    pr.print(4, f"      Map finalization:       {sumavg('MapFPost')}")
    pr.print(4, f"      Writing frames:         {sumavg('FrameWrite')}")
    pr.print(2, f"  Calculation finalization:   {sum_(*post_labels): >12}")
    pr.print(1, "x"*79)

    # treated + avail frames

    # (in/?)output filenames + sizes


# still a placeholder - this function still has to grow. Should in the
# end manage the different run modes, and probably do nothing else?
# This means, a big decision tree: match job, case x: call func_x,
# case y: call func_y, etc. Now, we're basically only doing 1 kind of job.
def GEM(callcommand, Files):
    GM_PT.Printer().add_time(
        3, "Start Parsing GMAP parameters", "ParParse", "ms")
    # step 1 (is GEM in demo mode? to become: What job do we need to do?)
    if callcommand[1] in ("demo"):
        exp_inpfile = False
    else:
        exp_inpfile = True
    # step 2 (very basic cmd line parse)
    job, in_parfile, argslist = GM_PP.parse_commandline(
        Files, callcommand, alljobs, "GMAP GEM", exp_inpfile, True
    )

    # Parameter parsing
    RunPars, singles_mapdict, pairs_mapdict, _, _, _, _ = GM_PP.get_parameters(
        Files, in_parfile, argslist
    )
    GM_PT.Printer().add_time(
        3, "Finished GMAP parameters, start adding maps", "AddMaps", "ms")

    # --- end of SU errors ---

    # Map initialization
    GM_MR.manage_maps_singles(Files, RunPars, singles_mapdict)
    GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)
    GM_PT.Printer().add_time(
        2, "Added all maps, start initializing MD system", "MDinit", "ms")

    # Looking at MD system - finding oscillators.
    System = GM_SR.System(Files, RunPars)

    # Save overview of found coupling maps to file.
    if "ham" in RunPars.output_data:
        GM_Pl.plot_coupling_choices(RunPars, System)

    GM_PT.Printer().add_time(
        3, "Initialized MD system, start initializing maps", "MapInit", "ms")

    # GEM is now done - let maps initialize as well
    for mapname in System.oscillators_ordered.keys():  # singles
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_post_init(Files, map_, System)
    for mapname in System.oscillators_ordered_coup.keys():  # pairs
        map_ = RunPars.requested_pairmapdict[mapname]
        map_.code.GM_post_init(Files, map_, System)
    GM_PT.Printer().add_time(
        3, "Initialization complete, start loading C libraries",
        "ClibLoad", "ms"
    )

    # Report on what the system looks like
    System.print_system(RunPars)

    # initialize C library
    GM_CL.VEG_CLib(RunPars)

    # calculate all (requested) frames
    trj_loop(RunPars, System)

    print_calculation_summary(RunPars)


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
        GEM(callcommand, Files)


if __name__ == "__main__":
    callcommand = sys.argv
    main(callcommand)
