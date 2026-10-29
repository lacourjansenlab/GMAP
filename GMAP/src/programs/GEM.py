r"""
Usage:

GMAP GEM
GMAP GEM help
    Prints this help.

GMAP GEM demo
    Launches GEM in demo-mode. Performs a basic calculation to
    demonstrate basic use and to verify the program is installed
    correctly.

GMAP GEM run [name of input file] [optional parameters]
    Performs a run of GEM using the parameters specified in the included
    file.


Groningen Electrostatic Maps

The purpose of GEM is to take an MD trajectory and compute the
time-dependent Hamiltonian to be used in electronic spectral calculations.
Instructions on how to deal with specific chromophores have to be included
in the corresponding .emap file.

For more information, check the manual on N/A.
"""


# standard lib imports
import concurrent.futures as cf
import cProfile
import datetime
import gc
import math
import subprocess
import sys

# 3rd party lib imports
# import numpy as np

# local imports
import GMAP.src.tools.clib_loader as GM_cl
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.file_handler as GM_fh
import GMAP.src.tools.map_reader as GM_mr
import GMAP.src.tools.parameter_parser as GM_pp
import GMAP.src.tools.physics_functions as GM_pf
import GMAP.src.tools.plotter as GM_Pl
import GMAP.src.tools.print_tools as GM_pt
from GMAP.src.tools.print_tools import devprint as dpr
import GMAP.src.tools.reference_handler as GM_rh
import GMAP.src.tools.system_reader as GM_sr


def manage_frame(frame, run_pars):
    """Performs all the checks involved with starting a new frame.

    Checks if the new frame should be treated (or is out of range).
    Prints the new frame number, along with an ETA (to know how much
    longer the calculation will take). Also confirms whether there is
    enough time to start on the next batch of frames before time runs
    out.

    Parameters
    ----------
    frame : `MDA.Timestep`
        The frame that will be treated next.
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.

    Returns
    -------
    break_after : bool
        Whether the per-frame loop should be broken after this frame.
    """

    framenum = frame.frame
    if framenum >= run_pars.stop_frame:
        return True

    # Do a frame number print here! (for ETA type prints)
    relframenum = framenum - run_pars.start_frame

    # If this is the 0th frame, or only first digit is non-zero.
    # We multiply relframenum (the n in nth frame treated) by 10 to make
    # sure that the resulting set is never empty (frames 1 through 9)
    if relframenum == 0 or set(str(relframenum * 10)[1:]) == set("0"):
        # if framenum has form 10^n with n=int
        if str(relframenum)[0] == "1":
            if relframenum != 1:
                GM_pt.Printer.print(2, "")
            verbose_level = 1
        else:
            verbose_level = 2
    else:  # lvl4 prints ETA for each frame.
        verbose_level = 4

    # Print the frame ETA header
    GM_pt.Printer.print(
        4,
        "Current time   | current frame | time elapsed | time to go   | "
        "end time  (est.)"
    )
    print_frame_ETA(
        verbose_level, framenum, run_pars.start_frame, run_pars.stop_frame)

    # Check if there is enough time to do another batch of frames
    return early_stop(framenum, run_pars)


def print_frame_ETA(verbose, framenum, startframe, endframe):
    """Prints some time information about this frame.

    Will report on the time at which the report takes place, the current
    frame, time elapsed, an estimate of the time remaining, and an
    estimate when the program will be done. The following format is
    used:

    Provided format:
    Current time | current frame | time elapsed | time to go   | end time
    Fri 13 HH:MM | xxxyyyzzz     | xxx-xx:xx:xx | xxx-xx:xx:xx | Fri 13 HH:MM

    .. important ::
        These estimates will improve when more frames have already been
        treated. For small systems (proteins, a speed of frames per
        second) any estimate below 10 frames is worthless, after 100
        frames they get usable. For large systems (assemblies, a speed
        of minutes per frame), this estimate will most likely converge
        much faster, but testing is required to know how fast.

        This difference is caused by the contribution of numba jitting.
        This usually takes a few seconds, which is a significant amount
        of time for small systems, but not for larger ones.

    .. note ::
        The weekdays will be reported in the installation(? System?)
        language of the user. As different languages have a shorthand
        for weekdays of a different amount of characters, the program
        has 14 characters reserved (so a few spaces are missing in the
        example above).

    .. note ::
        The estimated time to go (and end time) are based on how long
        earlier frames took. That means that during the first frame
        treated, no estimate can be provided, and wont. The last two
        columns will not be used/filled in on the first frame.

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

    timer = GM_pt.Printer.timer
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
    now_str = GM_pt.time_to_str(now_ns, "s")
    toprint.append(f"{now_str: >12}")  # To fit a max of 999 days.

    if not framenum == startframe:  # if not very first frame of calculation
        # Next: time to go
        start_heavy_ns = timer.get_time("StartLoop")
        ns_per_frame = int((now_ns - start_heavy_ns) / (framenum - startframe))
        ns_to_go = ns_per_frame * (endframe - framenum)
        to_go_str = GM_pt.time_to_str(ns_to_go, "s")
        toprint.append(f"{to_go_str: >12}")  # To fit a max of 999 days.

        # end time
        togo = datetime.timedelta(microseconds=ns_to_go // 1000)
        end_time = now + togo
        datestr = end_time.strftime("%a %d %H:%M")
        # English has len 12, german has len 11, make it 14 in case any other
        # language needs it... (can't find overview of supported languages)
        toprint.append(f"{datestr: <14}")

    GM_pt.Printer.print(verbose, " | ".join(toprint))


def early_stop(framenum, run_pars):
    """Determines whether to stop the calculation early, or to continue.

    This decision is based on the amount of remaining time, used time,
    and frame batch size. Basically, the program divides all frames to
    calculate in batches of a size determined by the user. Every first
    frame of a batch (except the very first batch), the program sees how
    long batches have taken until now, and whether there is enough time
    to finish another.
    If there is not enough time to finish two more, the next batch will
    not start. This is done to ensure that there is also enough time for
    the program to finish things off after the last batch.

    Parameters
    ----------
    framenum : int
        The frame number at which this function is called
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.

    Returns
    -------
    stop : bool
        Whether the calculation should stop early.
    """

    relframenum = framenum - run_pars.start_frame
    if relframenum == 0:  # don't quit on first frame
        return False

    # only consider quitting after completing a batch
    if relframenum % run_pars.batch_size != 0:
        return False

    # now, actually check whether the next batch will fit.
    timer = GM_pt.Printer.timer
    now_ns = timer.get_time("FrameUpdate")
    start_heavy_ns = timer.get_time("StartLoop")
    ns_per_frame = int((now_ns - start_heavy_ns) / (relframenum))
    avail_time_ns = run_pars.time_limit * 60 * 1000000000

    # if we could do another two batches, allow this batch to continue.
    # why two? because we also need time to finish up the calculation
    # after the last batch.
    if avail_time_ns - now_ns > 2 * ns_per_frame * run_pars.batch_size:
        return False
    else:
        run_pars.end_frame = framenum
        return True


def trj_loop(run_pars, system):
    """Performs the main per-frame loop for GEM.

    Does the last bit of initialization that needs to happen, and then
    treats each frame.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The class containing all the information on the system of the
        MD trajectory.
    """

    # first, do precalc
    GM_pt.Printer.add_time(
        3, "Preparing loop over frames", "PrepLoop", "ms")

    # create empty structures, initialize whats needed

    # compare runpar endframe to mda nframes - adjust endframe
    if run_pars.stop_frame >= len(system.universe.trajectory):
        run_pars.stop_frame = len(system.universe.trajectory)

    # Confirm start_frame is still smaller than stop, after the change
    if run_pars.start_frame > run_pars.stop_frame:
        GM_pt.Printer.warning(
            "Encountered an issue with the parameter start_frame. The frame "
            "doesn't exist, as the provided trajectory is too short. In the "
            "current way, there is nothing to do. Please either change the "
            "parameter start_frame to a smaller value, or use a different "
            "trajectory.",
            "SU_WP_17", True, GMAPerrclass=GM_ex.GmapParameterError
        )

    # let maps prepare for the calculation
    for mapname in system.oscillators_ordered.keys():  # singles
        map_ = run_pars.requested_mapdict[mapname]
        map_.code.GM_pre_run(map_, system)

    # pair maps only need to prepare if couplings are to be calculated.
    if "ham" in run_pars.output_data:
        for mapname in system.oscillators_ordered_coup.keys():  # pairs
            map_ = run_pars.requested_pairmapdict[mapname]
            map_.code.GM_pre_run(map_, system)

    # And in case maps did anything weird...
    run_pars.manage_dtypes()

    # Report on the system we're going to treat.
    GM_fh.write_legend(run_pars, system)

    trj = system.universe.trajectory
    GM_fh.clear_output(run_pars)

    # In case MDA needs a long time to start the loop.
    GM_pt.Printer.add_time(
        3, "Starting loop over frames", "StartLoop", "ms")

    cb = GM_pt.Printer.colors.green_lc
    ct = GM_pt.Printer.colors.clear
    line = f"{cb}════{ct}"
    GM_pt.Printer.print(
        1, f"\n{line} Processing frames {line}", detailed_instructions=[1])
    GM_pt.header(2, "Processing frames", "doublebox_bare")

    # print header for the ETA table (print lvl 4 has header per frame)
    GM_pt.Printer.print(
        1,
        "\nCurrent time   | current frame | time elapsed | time to go   | "
        "end time  (est.)", detailed_instructions=[1, 2, 3]
    )

    for frame in trj[run_pars.start_frame:]:
        GM_pt.Printer.add_time(
            4, "Starting on frame - starting updates", "FrameUpdate", "ms")
        # manage frame number (if not in range, skip, prints, ETA, etc)
        if manage_frame(frame, run_pars):
            break

        # rebuild the frame-specific data (positions, box, etc)
        system.update_properties(run_pars)
        GM_pt.Printer.add_time(
            4, "done system updates. next: osc updates", "OscUpdate", "ms")
        for oscillator in system.oscillators:
            oscillator.frame_update(system)

        GM_pt.Printer.add_time(
            4, "updates done. next: initialize", "StructInit", "ms")

        # initialize output structures (like Ham)
        outputs = GM_pf.generate_output_structures(run_pars, system)

        GM_pt.Printer.add_time(
            4, "initialize done. next: map init", "MapFInit", "ms")

        # call pre-frame funcs of maps
        for mapname in system.oscillators_ordered.keys():  # singles
            map_ = run_pars.requested_mapdict[mapname]
            map_.code.GM_pre_frame(map_, system)

        # pair maps only need to be called if couplings are to be calculated.
        if "ham" in run_pars.output_data:
            for mapname in system.oscillators_ordered_coup.keys():  # pairs
                map_ = run_pars.requested_pairmapdict[mapname]
                map_.code.GM_pre_frame(map_, system)

        GM_pt.Printer.add_time(
            4, "map init done. next: calculation", "Calc", "ms")

        # perform the actual calculations
        outputs = GM_pf.calc_frame(run_pars, system, outputs)

        GM_pt.Printer.add_time(
            4, "calculation done. next: map final", "MapFPost", "ms")

        # call post-frame functions of maps
        for mapname in system.oscillators_ordered.keys():  # singles
            map_ = run_pars.requested_mapdict[mapname]
            map_.code.GM_post_frame(map_, system)

        # pair maps only need to be called if couplings are to be calculated.
        if "ham" in run_pars.output_data:
            for mapname in system.oscillators_ordered_coup.keys():  # pairs
                map_ = run_pars.requested_pairmapdict[mapname]
                map_.code.GM_post_frame(map_, system)

        GM_pt.Printer.add_time(
            4, "map final done. next: write output", "FrameWrite", "ms")

        # write calculated data to files
        GM_fh.write_output(run_pars, frame.frame, outputs)

        GM_pt.Printer.add_time(
            4, "Frame completed. Loading next frame\n", "LoadFrame", "ms")

    cb = GM_pt.Printer.colors.green_lc
    ct = GM_pt.Printer.colors.clear
    GM_pt.Printer.print(
        2, f"\n{cb}====={ct} End of processing frames {cb}====={ct}\n")

    GM_pt.Printer.add_time(
        3, "Frames Completed. Finishing up.", "MapPost", "ms")

    # lastly, do postcalc:
    for mapname in system.oscillators_ordered.keys():  # singles
        map_ = run_pars.requested_mapdict[mapname]
        map_.code.GM_post_run(map_, system)

    # pair maps only need to do postcalc if couplings are to be calculated.
    if "ham" in run_pars.output_data:
        for mapname in system.oscillators_ordered_coup.keys():  # pairs
            map_ = run_pars.requested_pairmapdict[mapname]
            map_.code.GM_post_run(map_, system)


def print_calculation_summary(run_pars, system, parallel=False):
    """Reports how the calculation went, and some details users might
    want to know.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The class containing all the information on the system of the
        MD trajectory.
    parallel : bool, default=False
        Whether this function should report on a parallel run.
    """

    # making sure the last 'split' is saved in timer.totals()
    pr = GM_pt.Printer
    GM_pt.Printer.add_time(5, "", "end")

    GM_pt.header(
        1, "Calculation\nsummary", "doublebox_bare", detailed_instructions=[1])
    GM_pt.header(2, "\n  Calculation  \nsummary\n", "doublebox_bare")

    print_time_splits(run_pars, parallel=parallel)

    print_treated_avail_frames(run_pars, system)

    print_in_output_filenames(run_pars)

    if not parallel:
        print_relevant_references(run_pars, system)
    else:
        GM_pt.Printer.print(
            1, "\nFor references to cite, please look at the run above!"
        )

    end = " ██▓▓▒▒░░"
    start = end[::-1]
    msg = "That was all for today, folks. Thank you, and good night!"
    pr.print(1, f"\n  {start}{msg}{end}")


def print_time_splits(run_pars, parallel=False):
    """Report how much time was spent on what parts of the calculation

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    parallel : bool, default=False
        Whether this function should report on a parallel run.
    """

    def sumavg(*args):
        total_time = pr.timer.get_total_ns(*args)
        avg_time = total_time // nframes
        tot_str = GM_pt.time_to_str(total_time)
        avg_str = GM_pt.time_to_str(avg_time, "ms")
        return f"{tot_str: >12}  --> {avg_str[-12:]} / frame"

    pr = GM_pt.Printer
    sum_ = pr.timer.get_total_format
    nframes = run_pars.stop_frame - run_pars.start_frame

    GM_pt.header(2, "Time spent", "doublebox_bare", newlines=(1, 1))
    init_labels = [
        "ParParse", "AddMaps", "MDinit", "MapInit", "ClibLoad", "PrepLoop"]
    f_load = ["StartLoop", "LoadFrame"]
    f_upd = ["FrameUpdate", "PosBox", "COM"]
    f_init = f_upd + ["OscUpdate", "StructInit", "MapFInit"]
    f_calc = ["Calc", "VEGprop", "VEGcalc", "VEGuse"]
    if "ham" in run_pars.output_data:
        f_calc += ["PrepCoup", "CalcCoup"]
    f_post = ["MapFPost", "FrameWrite"]
    perframe = f_init + f_calc + f_post + f_load
    post_labels = ["MapPost"]
    all_labels = init_labels + perframe + post_labels

    if parallel:
        # for parallel jobs, there's far fewer labels available.

        init_labels = ["ParParse", "AddMaps"]
        all_labels = init_labels + ["ParJobs", "MergeFiles"]

        pr.print(1, f"Total time:                   {sum_(*all_labels): >12}")
        pr.print(2, f"  Initialization:             {sum_(*init_labels): >12}")
        pr.print(3, f"    Parsing parameters:       {sum_('ParParse'): >12}")
        pr.print(3, f"    Collecting maps:          {sum_('AddMaps'): >12}")
        pr.print(2, f"  Performing parallel runs:   {sum_('ParJobs'): >12}")
        pr.print(2, f"  Merging parallel files:     {sum_('MergeFiles'): >12}")

        return

    # The 'real', 'original' GEM print.

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
    if "ham" in run_pars.output_data:
        pr.print(4, f"      Coupling preparation:   {sumavg('PrepCoup')}")
        pr.print(4, f"      Coupling calculation:   {sumavg('CalcCoup')}")
    pr.print(3, f"    Frame finalization:       {sumavg(*f_post)}")
    pr.print(4, f"      Map finalization:       {sumavg('MapFPost')}")
    pr.print(4, f"      Writing frames:         {sumavg('FrameWrite')}")
    pr.print(2, f"  Calculation finalization:   {sum_(*post_labels): >12}")


def print_treated_avail_frames(run_pars, system):
    """Report what frames from MD are available, which were requested,
    and which actually calculated.

    For now, there is no difference between the requested and calculated
    frames. This will become relevant when the program can stop early
    due to time constraints.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The class containing all the information on the system of the
        MD trajectory.
    """

    pr = GM_pt.Printer

    GM_pt.header(2, "MD frames", "doublebox_bare")
    msg = "Frames treated:     " + " " * 12

    # if the calculation was stopped early, the attribute end_frame exists.
    last_frame = getattr(run_pars, "end_frame", run_pars.stop_frame)
    pr.print(1, f"{msg}{run_pars.start_frame}-{last_frame}")
    msg = "Frames requested:   " + " " * 12
    pr.print(2, f"{msg}{run_pars.start_frame}-{run_pars.stop_frame}")
    msg = "Frames available:   " + " " * 12
    pr.print(3, f"{msg}{0}-{len(system.universe.trajectory)}")
    msg = "Duration of frame:  " + " " * 12
    pr.print(1, f"{msg}{round(system.dt, 6) * 1000} fs")
    if round(system.dt, 6) == 1.0:
        pr.print(
            1,
            "Important: a timestep of 1.0 ps is the MDAnalyse default if this "
            "information is not present in the MD files. Please check "
            "manually yourself if needed as the actual timestep is likely "
            "different.")


def print_in_output_filenames(run_pars):
    """report which files were used during the calculation

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    """

    def report_files(run_pars, shorthand, printfname, txtverb, binverb):
        if shorthand in run_pars.output_data:
            fname = getattr(run_pars, f"output_{printfname.lower()}_filename")
            if "txt" in run_pars.output_format:
                temp = fname.parent / f"{fname.name}.txt"
                text = f"{printfname} text file:"
                wrapprint(txtverb, f"{text: <28}{temp}", ps)
            if "bin" in run_pars.output_format:
                temp = fname.parent / f"{fname.name}.bin"
                text = f"{printfname} binary file:"
                wrapprint(binverb, f"{text: <28}{temp}", ps)

    def wrapprint(verbose, message, wrap_preline):
        pr.print(verbose, message, wrap_preline=wrap_preline)

    pr = GM_pt.Printer

    GM_pt.header(2, "Files used", "doublebox_bare")
    cb = GM_pt.Printer.colors.green_lc
    ct = GM_pt.Printer.colors.clear
    line = f"{cb}════{ct}"
    GM_pt.Printer.print(
        1, f"\n{line} Files used {line}", detailed_instructions=[1])
    line = f"{cb}========{ct}"
    files = GM_fh.FileLocations
    ps = "  "  # The string to print as pre-wrap
    pr.print(3, f"{line}  Program files and information {line}")
    wrapprint(3, f"Python installation used:   {sys.executable}", ps)
    wrapprint(3, f"GMAP installation used:     {files.script_dir}", ps)
    wrapprint(3, f"Working directory:          {files.cwd}", ps)
    wrapprint(3, f"Program started at:         {files.now_str}", ps)

    pr.print(2, f"\n{line}  Input files {line}")
    wrapprint(1, f"Command issued:             {files.callcommand}", ps)
    wrapprint(2, f"Default parameter file:     {run_pars.defparfilename}", ps)
    wrapprint(2, f"Input parameter file:       {run_pars.inparfilename}", ps)
    wrapprint(1, f"Topology file analyzed:     {run_pars.topology_file}", ps)
    wrapprint(1, f"Trajectory file analyzed:   {run_pars.trajectory_file}", ps)
    mapdirs = ", ".join([str(direc) for direc in run_pars.map_directory])
    wrapprint(2, f"Map directories used:       {mapdirs}", ps)
    wrapprint(2, f"VEG-library file used:      {run_pars.VEG_clib_file}", ps)

    pr.print(2, f"\n{line}  Output files {line}")
    wrapprint(1, f"Logfile generated:          {run_pars.log_filename}", ps)
    fname = run_pars.output_legend_filename
    wrapprint(2, f"Legend file generated:      {fname}", ps)
    if "ham" in run_pars.output_data:
        fname = run_pars.output_couplingvis_filename
        wrapprint(2, f"Coupling visualization:     {fname}", ps)
    report_files(run_pars, "ham", "Hamiltonian", 2, 2)
    report_files(run_pars, "ene", "Energies", 2, 2)
    report_files(run_pars, "dip", "Dipole", 2, 2)
    report_files(run_pars, "ram", "Raman", 2, 2)
    report_files(run_pars, "pos", "Positions", 2, 2)
    report_files(run_pars, "dbp", "Doublepos", 2, 2)
    if run_pars.profiler:
        fname = run_pars.log_profiling_filename
        pr.print(2, f"profiler output:            {fname}")
    if run_pars.profiler_graph:
        fname = run_pars.log_profiling_graph_filename
        pr.print(2, f"profiler visualization:     {fname}")


def print_relevant_references(run_pars, system):
    """report which references should be cited for this calculation

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The class containing all the information on the system of the
        MD trajectory.
    """

    GM_pt.header(2, "References to cite", "doublebox_bare")
    cb = GM_pt.Printer.colors.green_lc
    ct = GM_pt.Printer.colors.clear
    line = f"{cb}════{ct}"
    GM_pt.Printer.print(
        1, f"\n{line} References to cite {line}", detailed_instructions=[1])

    all_references = []
    for singles_map in system.oscillators_ordered.keys():
        singles_map = run_pars.requested_mapdict[singles_map]
        all_references.append(
            singles_map.code.GM_report_references(singles_map, system))

    if "ham" in run_pars.output_data:
        for pairs_map in system.oscillators_ordered_coup.keys():
            pairs_map = run_pars.requested_pairmapdict[pairs_map]
            all_references.append(
                pairs_map.code.GM_report_references(pairs_map, system))

    GM_rh.report_references(run_pars, all_references)


def run(
    in_parfile, argslist, run_pars, singles_mapdict, pairs_mapdict,
    cmd_pars, in_pars, def_pars, ref_pars
):
    """Performs the 'run' command of GEM (GMAP GEM run)

    Initializes maps, C library, system_reader.System.
    Writes coupling file, parameter file.
    Performs trajectory loop (main calculation)
    Starts/ends profiling, and formats output.
    Reports calculation summary.

    Parameters
    ----------
    in_parfile : `pathlib.Path`
        The path to the requested input parameter file.
    argslist : list of str
        The slice of sys.argv containing all parameter choices given on
        the command line.
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    singles_mapdict : dict of str: \
        :class:`~GMAP.src.tools.map_reader.SingleMap` pairs
        Stores all the :class:`~GMAP.src.tools.map_reader.SingleMap`
        objects for each map supplied. The keys are the Map.name
        attributes corresponding to the maps stored as values.
    pairs_mapdict : dict of str: \
        :class:`~GMAP.src.tools.map_reader.PairMap` pairs
        Stores all the :class:`~GMAP.src.tools.map_reader.PairMap`
        objects for each map supplied. The keys are the Map.name
        attributes corresponding to the maps stored as values.
    cmd_pars : :class:`RawPars`
        Contains any parameter choices made on the command line
    in_pars : :class:`RawPars`
        Contains any parameter choices made in the input parameter file
    def_pars : :class:`RawPars` or :class:`RefPars`
        Contains all default parameter choices. Might be ref_pars, might
        be from a separate default parameters file.
    ref_pars : :class:`RefPars`
        Contains all available parameters from GMAP itself
        (not map-specific)
    """

    # If requested, profile the run.
    if run_pars.profiler:
        profile = cProfile.Profile()
        profile.enable()

    GM_pt.Printer.add_time(
        3, "Finished GMAP parameters, start adding maps", "AddMaps", "ms")

    # --- end of SU errors ---

    # Map initialization
    GM_mr.manage_maps_singles(run_pars, singles_mapdict)
    GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)
    GM_pt.Printer.add_time(
        2, "Added all maps, start loading C libraries", "ClibLoad", "ms")

    # initialize C library
    GM_cl.VEG_CLib(run_pars)

    GM_pt.Printer.add_time(
        3, "Libraries loaded, start initializing MD system", "MDinit",
        "ms"
    )

    # Looking at MD system - finding oscillators.
    system = GM_sr.System(run_pars)

    GM_pt.Printer.add_time(
        3, "Initialized MD system, start initializing maps", "MapInit", "ms")

    # GEM is now done - let maps initialize as well
    for mapname in system.oscillators_ordered.keys():  # singles
        map_ = run_pars.requested_mapdict[mapname]
        map_.code.GM_post_init(map_, system)

    # Report on what the system looks like (needs singles mapinit)
    system.print_system(run_pars)

    GM_pt.Printer.add_time(
        3, "Initialization complete, start considering pairs", "MDinit", "ms")

    if "ham" in run_pars.output_data:
        # prepare all pair lookup tables.
        system.order_oscillators_pairs(run_pars)

        # let all coupling maps initialize
        for mapname in system.oscillators_ordered_coup.keys():  # pairs
            map_ = run_pars.requested_pairmapdict[mapname]
            map_.code.GM_post_init(map_, system)

        # obtain all multiply factors of all coupling maps
        run_pars.final_resolve_coupling_scale()

        # Save overview of found coupling maps to file.
        GM_Pl.plot_coupling_choices(run_pars, system)

    # Write output parameter file
    GM_fh.write_parameter_file(
        ref_pars, run_pars, system, cmd_pars, in_pars, def_pars)

    # calculate all (requested) frames
    trj_loop(run_pars, system)

    # finalize profiler
    if run_pars.profiler:
        profile.create_stats()
        profile.dump_stats(run_pars.log_profiling_filename)

    if run_pars.profiler_graph:
        strcommand = [
            "gprof2dot", "-f", "pstats",
            run_pars.log_profiling_filename, "-o",
            run_pars.log_profiling_tempfile]
        subprocess.run(strcommand)

        dpr("running dot")
        strcommand = [
            "dot", "-Tpng", "-o", run_pars.log_profiling_graph_filename,
            run_pars.log_profiling_tempfile]
        subprocess.run(strcommand)

        # remove the tempfile again
        run_pars.log_profiling_tempfile.unlink()

    print_calculation_summary(run_pars, system)


def par_single_job(inputpar):
    """The executive unit for parallel jobs.

    concurrent.futures.ProcessPoolExecutor.map takes only a function
    to execute, and a single parameter to give to that function.
    This function is the one given to that executor. It needs to unpack
    the provided inputs, and contain the actual instruction for the
    calculation.

    The way this is done, is by using subprocess to call another
    GMAP instance to perform a single-core calculation. In/output file
    names, verbosity, number of cores, number of frames are all adjusted
    to work as a child-process.

    Parameters
    ----------
    inputpar : list of list of dict/int pairs
        The input needed for the call to work. The dict is the dict
        representation of runpars, while int is the number (id) of the
        core executing this job.
    """

    run_pars_dict, core_num = inputpar
    n_cores = run_pars_dict["number_cores"]

    # Just reusing the input file of the parallel run does not work - there
    # could be cmdline args used during the parallel run that would not be
    # conserved. But just putting the cmd line args here also doesn't
    # work - they might be the ones we'd like to use, too. So we need to
    # find an alternative way to store the cmdline args.
    # The found alternative? Have GMAP parse all parameters into runpars, and
    # write that to file (there's functionality for that anyways). Now, we
    # supply each of the single runs with that file as input. That leaves all
    # command line arguments free to overwrite the parts of the original that
    # don't make sense for each of the threads.
    cmd = ["GMAP", "GEM", "run", run_pars_dict["output_parameter_filename"]]

    # we want to spawn single-core processes now. Lets build up the required
    # process-specific parameters

    # verbose, cores
    if core_num != 0:
        cmd.extend(["--verbose", "0"])
    cmd.extend(["--number_cores", "1"])

    # frame numbers
    batch_size = math.ceil(run_pars_dict["number_frames"] / n_cores)
    cmd.extend([
        "--start_frame",
        str(run_pars_dict["start_frame"] + batch_size * core_num)])
    cmd.extend(["--number_frames", str(batch_size)])
    cmd.extend([
        "--stop_frame",
        str(run_pars_dict["start_frame"] + batch_size * (core_num + 1))])

    # file names
    cmd.extend([
        "--output_parameter_filename",
        GM_fh.fname_to_tempname("parfile", run_pars_dict, core_num)])
    cmd.extend([
        "-ohf", GM_fh.fname_to_tempname("ham", run_pars_dict, core_num)])
    cmd.extend([
        "-oef", GM_fh.fname_to_tempname("ene", run_pars_dict, core_num)])
    cmd.extend([
        "-odf", GM_fh.fname_to_tempname("dip", run_pars_dict, core_num)])
    cmd.extend([
        "-orf", GM_fh.fname_to_tempname("ram", run_pars_dict, core_num)])
    cmd.extend([
        "-opf", GM_fh.fname_to_tempname("pos", run_pars_dict, core_num)])
    cmd.extend([
        "--output_doublepos_filename",
        GM_fh.fname_to_tempname("dbp", run_pars_dict, core_num)])
    cmd.extend([
        "--log_filename",
        GM_fh.fname_to_tempname("logfile", run_pars_dict, core_num)])

    # lets go!
    subprocess.run(cmd)


def parallel(
    in_parfile, argslist, run_pars, singles_mapdict, pairs_mapdict,
    cmd_pars, in_pars, def_pars, ref_pars
):
    """Performs the 'parallel' command of GEM (GMAP GEM run)

    Initializes maps, system_reader.System.
    Writes parameter file.
    Removes system again (to save memory).
    Manages filelocations for parallel runs.
    Calls parallel runs.
    Merges output files to look like 'normal' outputs again.
    Reports calculation summary.

    Parameters
    ----------
    in_parfile : `pathlib.Path`
        The path to the requested input parameter file.
    argslist : list of str
        The slice of sys.argv containing all parameter choices given on
        the command line.
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    singles_mapdict : dict of str: \
        :class:`~GMAP.src.tools.map_reader.SingleMap` pairs
        Stores all the :class:`~GMAP.src.tools.map_reader.SingleMap`
        objects for each map supplied. The keys are the Map.name
        attributes corresponding to the maps stored as values.
    pairs_mapdict : dict of str: \
        :class:`~GMAP.src.tools.map_reader.PairMap` pairs
        Stores all the :class:`~GMAP.src.tools.map_reader.PairMap`
        objects for each map supplied. The keys are the Map.name
        attributes corresponding to the maps stored as values.
    cmd_pars : :class:`RawPars`
        Contains any parameter choices made on the command line
    in_pars : :class:`RawPars`
        Contains any parameter choices made in the input parameter file
    def_pars : :class:`RawPars` or :class:`RefPars`
        Contains all default parameter choices. Might be ref_pars, might
        be from a separate default parameters file.
    ref_pars : :class:`RefPars`
        Contains all available parameters from GMAP itself
        (not map-specific)
    """

    # first, some bookkeeping to figure out basics

    GM_pt.Printer.add_time(
        3, "Finished GMAP parameters, start adding maps", "AddMaps", "ms")

    # Map initialization (needed for correctly saving used parameters)
    GM_mr.manage_maps_singles(run_pars, singles_mapdict)
    GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)
    GM_pt.Printer.add_time(2, "Added all maps", "AddMaps", "ms")

    # Looking at MD system to figure out trajectory length.
    system = GM_sr.System(run_pars, read_only=True)
    # compare runpar endframe to mda nframes - adjust endframe
    if run_pars.stop_frame >= len(system.universe.trajectory):
        run_pars.stop_frame = len(system.universe.trajectory)
        run_pars.number_frames = run_pars.stop_frame - run_pars.start_frame

    GM_fh.write_parameter_file(
        ref_pars, run_pars, system, cmd_pars, in_pars, def_pars)

    # Creating a duck type for system, to use in printing the calculation
    # summary report.
    trajlength = len(system.universe.trajectory)
    system_dummy = GM_ct.CustomClass(**{
        "dt": system.dt,
        "universe": GM_ct.CustomClass(**{
            "trajectory": type(
                "CustomLenClass", (), {
                    "__len__": lambda self: trajlength}
            )()
        })
    })

    # free the memory (mainly from the MDA universe)
    del system
    gc.collect()

    # now, time for actually doing the parallel runs!
    n_cores = run_pars.number_cores

    # create temp dir
    files = GM_fh.FileLocations
    tempdir = files.cwd / ("tmp_" + files.now_str)
    counter = 0
    while tempdir.exists():
        tempdir = files.cwd / f"tmp_{files.now_str}_{counter}"
        counter += 1

    # now, tempdir stores name of a non-existent directory. create it!
    tempdir.mkdir()
    run_pars.parrun_directory = tempdir

    # we need access to (part of) runpars for setting up the parallel runs.
    # But, concurrent futures does not allow custom classes (easily?), so,
    # all required info is taken from run_pars, and put into a dictionary.
    runpardict = run_pars.parallel_dict()

    GM_pt.Printer.add_time(
        1,
        "Starting parallel jobs.",
        "ParJobs", "ms")
    GM_pt.Printer.print(
        1,
        "\nOnly job 0 will report output from here on out, all others are "
        "running silently in the background.",)

    # actually set up and run the parallel calculations
    with cf.ProcessPoolExecutor() as executor:
        jobs = list(zip([runpardict] * n_cores, list(range(n_cores))))
        _ = executor.map(par_single_job, jobs)

    GM_pt.Printer.add_time(
        1,
        "Done running jobs, merging output files.",
        "MergeFiles", "ms")

    # merge the files (= make sure data looks like that from standard run)
    GM_fh.merge_files(run_pars)

    print_calculation_summary(run_pars, system_dummy, parallel=True)


def GEM(callcommand):
    """The entry point of the module.

    Parses the command line, extracs parameters, and calls the
    required function for job execution.

    Parameters
    ----------
    callcommand : list of str
        This is the user input into the terminal.
    """

    GM_pt.Printer.add_time(
        3, "Start Parsing GMAP parameters", "ParParse", "ms")
    # step 1 (is GEM in demo mode? to become: What job do we need to do?)
    if callcommand[1] in ("demo"):
        exp_inpfile = False
    else:
        exp_inpfile = True
    # step 2 (very basic cmd line parse)
    job, in_parfile, argslist = GM_pp.parse_commandline(
        callcommand, alljobs, "GMAP GEM", exp_inpfile, True
    )

    # Parameter parsing
    (
        run_pars, singles_mapdict, pairs_mapdict, cmd_pars, in_pars, def_pars,
        ref_pars
    ) = GM_pp.get_parameters(in_parfile, argslist, "GEM")

    if run_pars.number_cores > 1:
        parallel(
            in_parfile, argslist, run_pars, singles_mapdict, pairs_mapdict,
            cmd_pars, in_pars, def_pars, ref_pars
        )
    else:
        run(
            in_parfile, argslist, run_pars, singles_mapdict, pairs_mapdict,
            cmd_pars, in_pars, def_pars, ref_pars
        )


# The jobs that GEM can currently execute.
alljobs = [
    "demo",
    "run"
]


def main(callcommand):
    """Fakes behaviour as if called from __main__.

    During normal operation (user types 'GMAP ...' in the command line),
    this function should never be called. Instead, the entrypoint is in
    the cmd_interface file, and it points directly to the GEM function
    above.
    
    This function replicates the 'normal' behaviour so partial tests are
    possible.

    Parameters
    ----------
    callcommand : list of str
        This is the user input into the terminal.
    """

    if len(callcommand) == 1:
        print(__doc__)
    else:
        GM_fh.FileLocations()
        GEM(callcommand)


if __name__ == "__main__":
    callcommand = sys.argv
    main(callcommand)
