r"""
Usage:

    GMAP DEPICT
    GMAP DEPICT help
prints this help

    GMAP DEPICT calculate [name of input file] [optional parameters]
Calculates all datapoints for a potential vs estatic_range graph.

    GMAP DEPICT show [name of input file] [optional parameters]
Displays all data calculated previously using calculate.

    GMAP DEPICT calcshow [name of input file] [optional parameters]
Performs the functions of both 'calculate' and 'show'


Dependence of Electrostatic Properties on Individual Charges Taken

The purpose of DEPICT is to visualize how the calculated electrostatic
potential changes with estatic_range. This aids in determining what
value for estatic_range should be used, and what method for calculating
the electrostatic properties.

For more information, check the manual on N/A.
"""


# 3rd party lib imports
import numpy as np
import matplotlib.pyplot as plt

# local imports
import GMAP.src.tools.CLibLoader as GM_CL
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP
import GMAP.src.tools.SystemReader as GM_SR


def calc_data(Printer, RunPars, System):
    # GEM is now done - let maps initialize as well
    for mapname in System.oscillators_ordered.keys():
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_pre_run(Printer, map_, System)

    # And in case maps did anything weird...
    RunPars.manage_dtypes()
    Printer.add_time(3, "Starting on calculation", "ms")

    System.update_properties(Printer)
    Printer.add_time(4, "done system updates. next: osc updates", "ms")

    # only consider a single oscillator
    System.oscillators = [System.oscillators[0]]
    System.nosc = np.int32(1)
    for oscillator in System.oscillators:
        oscillator.frame_update(Printer, System)

    Printer.add_time(4, "updates done. next: initialize", "ms")

    VEGlib = GM_CL.VEG_CLib()
    # call pre-frame funcs of maps
    for mapname in System.oscillators_ordered.keys():
        map_ = RunPars.requested_mapdict[mapname]
        map_.code.GM_pre_frame(Printer, map_, System)

    Printer.add_time(4, "map init done. next: calculation", "ms")

    estatics = np.zeros((RunPars.number_frames, 4))
    startsize = RunPars.estatic_range
    for add_r_sphere in range(RunPars.number_frames):
        newsize = startsize + add_r_sphere
        RunPars.estatic_range = np.float32(newsize)
        VEGlib.calcPot_perres_mm(System, RunPars, oscillator)
        estatics[add_r_sphere, 0] = newsize
        estatics[add_r_sphere, 1:] = oscillator.VEGout[:3, 0]
    with open(RunPars.output_estatics_filename, "w") as fhand:
        np.savetxt(fhand, estatics)


def show_data(Printer, RunPars):
    with open(RunPars.output_estatics_filename, "r") as fhand:
        data = np.loadtxt(fhand)

    plt.plot(data[:, 0], data[:, 2] - data[:, 1])
    plt.show()
    plt.clf()


def DEPICT(callcommand, Files, Printer):
    alljobs = [
        "calculate",
        "show",
        "calcshow"
    ]

    job, in_parfile, argslist = GM_PP.parse_commandline(
        Files, Printer, callcommand, alljobs, "GMAP DEPICT", True, True
    )

    RunPars, mapdict, _, _, _, _ = GM_PP.get_parameters(
        Files, Printer, in_parfile, argslist
    )
    Printer.add_time(3, "Parsed GMAP parameters", "ms")

    # end of SU errors

    if job in ("calculate", "calcshow"):
        # do the thing
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
        calc_data(Printer, RunPars, System)

    if job in ("show", "calcshow"):
        # show the thing
        show_data(Printer, RunPars)
