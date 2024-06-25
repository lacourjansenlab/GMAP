"""Main code file for dipole-dipole map.

Also is the template/explanation for all that a map can hand directly to
GMAP. Of course, more functions are allowed, and these files can import
other custom python files stored in the same directory (or a directory
therein) as this file.
"""

from numba import njit
import numpy as np

from GMAP.src.tools import MathFunctions as GM_MF


# A function to adjust the parameters of the map. For some kinds of
# parameter (especially if theres multiple that are linked), the way
# RunPar is built might not be correct. In this function, the user can
# fix that.
def GM_adjust_RunPars(Files, Printer, Map):
    """Makes the necessary changes to Map.RunPar.

    Is expected to not return anything - return value is not caught.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass


# A function to adjust the choices made in core.txt. Perhaps, based on
# a detected parameter, a different choice is preferred. This function
# allows to make a different choice, **in the same format as the file**.
# if more complex behaviour is desired, a separate function is needed.
def GM_adjust_map_core_raw(Files, Printer, Map):
    """Makes the necessary changes to the 'raw' input read from core.txt.

    Is expected to not return anything - return value is not caught.

    The core.txt file is stored in Map.rawcore. It has not yet been
    parsed, just loaded into a dictionary. In this dictionary, each
    keyword is its own dictionary key. Most keywords can only occur once
    in the file - those have a list of the 'words' on the line as
    their value. The parameters that are allowed to occur more than once
    have a list as value, in which other lists appear - one for each
    line.

    The purpose of this function is to change this dictionary. Perhaps,
    a rule in core.txt is dependent on a parameter of the map. This
    function can make a decision based on those parameters (stored in
    Map.RunPars).

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass


# A function to change the coupling type of an oscillator pair. GMAP can
# only sort oscpairs into the correct couplingmaps based on the name of
# the map of each osc in a pair. However, some maps require different
# coupling maps for different circumstances. This function should return
# the name of the map that should be coupling this pair (instead of itself).
# IF this function does not exist, the map itself is returned by default.
def GM_change_coup_type(Map, Syst, oscix1, osc1, oscix2, osc2):
    return "DipDip"


# A place to actually do any prepwork. Any preparations should be done here
# (and not pre-frame, for example), as at the time this function is called,
# more information about the oscillator is available (dipole, VEG properties)
def GM_prep_coupling(Printer, Map, Syst, oscixlist, osclist):
    for oscix, osc in zip(oscixlist, osclist):
        # if the map has a function specifically for this map, use it!
        if hasattr(osc.Map.code, "CP_DipDip_calc_dipole"):
            (
                Map.dipole_vec_arr[oscix], dip_pos
            ) = osc.Map.code.CP_DipDip_calc_dipole(
                Printer, osc.Map, Syst, osc)
        else:
            Map.dipole_vec_arr[oscix] = osc.dipole_vec
            dip_pos = osc.dipole_pos

        # save positions in box coordinates
        Map.dipole_pos_arr[oscix] = dip_pos @ Syst.boxvects_inv


def GM_calc_coupling(Printer, Map, Syst, hamiltonian):
    for pair in Map.allpairs:
        oscix1, oscix2 = pair
        J = calc_coupling(
            oscix1, oscix2, Map.dipole_pos_arr, Map.dipole_vec_arr,
            Syst.boxvects
        )
        hamiltonian[oscix1, oscix2] = J
        hamiltonian[oscix2, oscix1] = J


# wrapper as not all these types are njit-friendly.
def GM_calc_coupling_old(Printer, Map, Syst, oscix1, osc1, oscix2, osc2):
    return calc_coupling(
        oscix1, oscix2, Map.dipole_pos_arr, Map.dipole_vec_arr, Syst.boxvects)


@njit
def calc_coupling(oscix1, oscix2, pos_arr, vec_arr, boxvects):
    # Used constants:
    # Cm = (1/3.33564) * 10^30 D  (Coulomb meter in Debye)
    # m = 10^10 ang (meter in angstrom)
    # J = 1/hc = (1/1.98644586) * 10^25 1/m
    # => J = 5.03411656 * 10^22 1/cm (joule in wavenumbers)
    # eps_0 = 8.8541878128 F/m = 8.8541878128 C^2/Jm (coulomb squared per
    # joule meter)

    # derived value:
    # 4piEinv = 1/(4 * pi * eps_0) Jm/C^2
    # Gives 5034.11656 cm^-1 * ang*3 Deb^-2

    fourPiEps_inv = np.float32(5034.11656)
    # the positions array is in box-coordinates -> easy subtraction, then
    # move back into cartesian
    d = GM_MF.PBC_back2box(pos_arr[oscix1, :] - pos_arr[oscix2, :], boxvects)
    ir2 = 1/GM_MF.dotprod(d, d)
    ir = np.sqrt(ir2)
    ir3 = ir*ir2
    ir5 = ir3*ir2

    return fourPiEps_inv * (
        GM_MF.dotprod(vec_arr[oscix1], vec_arr[oscix2]) * ir3
        - 3.0 * GM_MF.dotprod(vec_arr[oscix1], d)
        * GM_MF.dotprod(vec_arr[oscix2], d) * ir5)


# A place to do further initialization if a map requires it. Think of
# things like building further lookup tables, for instance.
# (for AmideBB - find neighbours!)
# (Or, for couplings that MUST get information from an oscillator,
# check if that specific function exists)
def GM_post_init(Files, Printer, Map, Syst):
    pass


# A place to do things before the main loop starts (create datastructures
# to be filled in, for example). GEM itself builds the coupling table at
# this point in time. Any preparation stuff that only requires constant
# properties (masses, charges, bonds, for example) should be done here.
def GM_pre_run(Printer, Map, Syst):
    setattr(Map, "dipole_vec_arr", np.zeros((Syst.nosc, 3), dtype="float32"))
    setattr(Map, "dipole_pos_arr", np.zeros((Syst.nosc, 3), dtype="float32"))

    # change dtype of allpair list to suit this map's needs.
    # setattr(Map, "allpairs", np.array(Map.allpairs, dtype='int32').T)
    # setattr(Map, "allpairs_c", np.ctypeslib.as_ctypes(
    #     np.ravel(Map.allpairs)))


# A place to do things before the properties for this frame are being
# calculated. Any preparation stuff that requires frame-dependent
# data should be done here. AIM calculated the CoMs here, GEM also
# builds hamiltonian (as its contents change per frame)
def GM_pre_frame(Printer, Map, Syst):
    pass


# A place to do things with the results from this frame. GEM itself
# writes information like the hamiltonian to files at this point in time.
def GM_post_frame(Printer, Map, Syst):
    pass


# A place to wrap up the entire calculation. GEM itself reports on
# calculation time and treated frames at this point in time.
def GM_post_run(Printer, Map, Syst):
    pass
