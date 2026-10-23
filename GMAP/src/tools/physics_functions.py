
# 3rd party imports
from numba import njit
import numpy as np

# local imports
import GMAP.src.tools.clib_loader as GM_cl
import GMAP.src.tools.print_tools as GM_pt


def calc_CoM(system, atomlist):
    """Calculate the centre of mass of a given set of atoms.

    How to?

    - Convert a list of positions to box coordinates
    - Translate by the first atom position (center the first atom)
    - Shift all atoms so they are in the 'middle' box (between -0.5 and
      0.5 box vectors), i.e. closest position to the first atom
    - Undo the translation by the first atom position
    - Do the actual calculation (center of mass)
    - Shift the result to the middle box and then convert back to
      cartesian coordinates.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    atomlist : list of int
        The indices of all the atoms of which the (combined) centre of
        mass should be calculated.

    Returns
    -------
    CoM : `np.ndarray`
        A numpy array of length 3 containing the position of the
        centre of mass.
    """

    # converting positions into box coordinates
    allpos_box = system.positions[atomlist] @ system.boxvects_inv
    # Translating by position of first atom
    shift = allpos_box[0].copy()
    allpos_box -= shift

    # shift to 'middle' box, undo first-atom-translation
    allpos_box -= np.floor(allpos_box + 0.5) - shift

    # do the calculation
    masses = system.masses[atomlist]
    CoM_box = np.sum(allpos_box * masses[:, None], axis=0) / np.sum(masses)

    # This current CoM_box can be saved/used as is!
    # (as long as in-C implementation does the shift after diff calc)

    # convert back to cartesian
    CoM = (CoM_box - np.floor(CoM_box + 0.5)) @ system.boxvects
    return CoM


@njit
def system_CoM(
    positions: np.ndarray, masses: np.ndarray, boxvects_inv: np.ndarray,
    boxvects: np.ndarray, res_first_ix: np.ndarray, res_last_ix: np.ndarray,
    nres: int
) -> np.ndarray:
    """Calculate the centre of mass of each residue in the system.

    Parameters
    ----------
    positions : `np.ndarray`
        The positions of all atoms in the system.
    masses : `np.ndarray`
        The masses of all atoms in the system.
    boxvects_inv : `np.ndarray`
        The inverse of the boxvects array.
    boxvects : `np.ndarray`
        The array storing the vectors defining the MD simulation box.
    res_first_ix : `np.ndarray`
        Stores the system index of the first atom in each residue.
    res_last_ix : `np.ndarray`
        Stores the system index of the last atom in each residue.
    nres : int
        The amount of residues in the system.
    """

    CoM_array = np.empty((res_first_ix.shape[0], 3), dtype="float32")
    half = np.float32(0.5)

    # for each residue, rewrite of calc_CoM for numba
    for resix in range(nres):
        # converting positions into box coordinates
        allpos_box = positions[
            res_first_ix[resix]: res_last_ix[resix]+1
        ] @ boxvects_inv

        # Translating by position of first atom
        shift = allpos_box[0].copy()
        allpos_box -= shift

        # shift to 'middle' box, undo first-atom-translation
        allpos_box -= np.floor(allpos_box + half) - shift

        # do the calculation
        masses_res = masses[res_first_ix[resix]: res_last_ix[resix]+1]
        CoM_box = np.sum(
            allpos_box * masses_res[:, None], axis=0
        ) / np.sum(masses_res)

        # convert back to cartesian
        CoM_array[resix] = (CoM_box - np.floor(CoM_box + half)) @ boxvects

    return CoM_array


def calc_frame(run_pars, system, outputs):
    """The heart of the per-frame loop. Does the actual calculations.

    Currently, for each oscillator, the potential is calculated (if
    requested), along with frequency and dipole
    Next, in a separate loop, the couplings are computed.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    outputs : dict of str: `np.ndarray` pairs
        The outputs the program is requested to generate. Currently
        contains hamiltonian and dipole arrays.

    Returns
    -------
    outputs : dict of str: `np.ndarray` pairs
        The outputs the program is requested to generate. Currently
        contains hamiltonian and dipole arrays.
    """

    VEGlib = GM_cl.VEG_CLib()
    printer = GM_pt.Printer

    printer.add_time(4, "VEG-related properties:", "VEGprop", "ms")
    for oscix, oscillator in enumerate(system.oscillators):
        # Do we need the estatics?
        printer.add_time(5, "", "VEGcalc")
        if any(data in run_pars.output_data for data in ("ham", "dip", "ene")):
            if oscillator.map.core.electrostatic_choice in ("V", "E", "G"):
                # calculate VEG
                VEGlib.calcVEG_perres_main(system, run_pars, oscillator)

            # ROTATE VEG
            if oscillator.map.core.electrostatic_choice in ("E", "G"):
                oscillator.rotate_VEG()

            # scale VEG with dielectric_constant
            oscillator.apply_dielectric_constant(run_pars.dielectric_constant)

        printer.add_time(5, "", "VEGuse")

        if "ene" in run_pars.output_data and oscillator.map.core.ham_first:
            outputs["energies"][oscix] = calc_frequency(
                system, oscillator)

        if "ham" in run_pars.output_data and oscillator.map.core.ham_first:
            outputs["hamiltonian"][oscix, oscix] = calc_frequency(
                system, oscillator)

        # do we need dipoles?
        # we also need dipoles for the (full) hamiiltonian.
        if any(data in run_pars.output_data for data in ("ham", "dip")):
            r_vec, r_pos = calc_dipole(system, oscillator)
            outputs["dipoles"][oscix] = r_vec  # needed for both ham and dip

            if any(data in run_pars.output_data for data in ("ham",)):
                outputs["dipole_pos"][oscix] = r_pos  # only ham!

        if "ram" in run_pars.output_data:
            outputs["raman"][oscix] = calc_raman(system, oscillator)

        if (
            "ene" in run_pars.output_data
            and not oscillator.map.core.ham_first
        ):
            outputs["energies"][oscix] = calc_frequency(
                system, oscillator)

        if (
            "ham" in run_pars.output_data
            and not oscillator.map.core.ham_first
        ):
            outputs["hamiltonian"][oscix, oscix] = calc_frequency(
                system, oscillator)

        if "pos" in run_pars.output_data:
            outputs["positions"][oscix] = get_positions(system, oscillator)

        if "dbp" in run_pars.output_data:
            # very similar to positions, but doublepos returns two positions
            # simultaneously, so we catch both into the doublepos array.
            outputs["doublepos"][oscix*2:(oscix+1)*2] = get_doublepos(
                system, oscillator)

    # calculate the couplings for the hamiltonian
    if "ham" in run_pars.output_data:
        printer.add_time(4, "Preparing coupling:", "PrepCoup", "ms")
        prep_coupling(run_pars, system)

        printer.add_time(4, "Calculating coupling:", "CalcCoup", "ms")
        calc_coupling(run_pars, system, outputs)

    return outputs


def calc_dipole(system, oscillator):
    """Calculate the dipole moment for a given oscillator

    The oscillator 'knows' how this should be done - invoke that method.
    The results are returned, but also saved as attributes to the
    oscillator.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the calculation is requested.

    Returns
    -------
    r_vec : `np.ndarray`
        A length-3 vector containing the direction of the dipole moment.
        Datatype of this array must be float32!
    r_pos : `np.ndarray`
        A length-3 vector containing the position of the dipole moment.
        The vector must lie within the simulation box.
        Datatype of this array must be float32!
    """

    # every map should have a calc dipole function
    map_ = oscillator.map
    r_vec, r_pos = map_.code.GM_calculate_dipole(
        map_, system, oscillator)
    setattr(oscillator, "dipole_vec", r_vec)
    setattr(oscillator, "dipole_pos", r_pos)
    return r_vec, r_pos


def calc_frequency(system, oscillator):
    """Calculate the frequency for a given oscillator

    The oscillator 'knows' how this should be done - invoke that method.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the calculation is requested.

    Returns
    -------
    frequency : float
        The frequency found for this oscillator
    """

    map_ = oscillator.map
    return map_.code.GM_calculate_frequency(map_, system, oscillator)


def calc_raman(system, oscillator):
    """Calculate the raman tensor for a given oscillator

    The oscillator 'knows' how this should be done - invoke that method.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the calculation is requested.

    Returns
    -------
    tensvect : `np.ndarray`
        A length-6 vector representing the upper triangular part of the
        raman tensor.
        Datatype of this array must be float32!
    """

    map_ = oscillator.map
    return map_.code.GM_calculate_raman(map_, system, oscillator)


def get_positions(system, oscillator):
    """Determine the position for a given oscillator.

    The oscillator 'knows' how this should be done - invoke that method.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the calculation is requested.

    Returns
    -------
    pos : `np.ndarray`
        A length-3 vector representing the position of the oscillator.
        Datatype of this array must be float32!
    """

    map_ = oscillator.map
    return map_.code.GM_get_position(map_, system, oscillator)


def get_doublepos(system, oscillator):
    """Determine the positions for a given oscillator.

    The oscillator 'knows' how this should be done - invoke that method.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the calculation is requested.

    Returns
    -------
    doublepos : `np.ndarray`
        Two length-3 vectors representing the positions of the
        oscillator. Datatype of these arrays must be float32!
    """

    map_ = oscillator.map
    return map_.code.GM_get_doublepos(map_, system, oscillator)


def prep_coupling(run_pars, system):
    """Calculate some oscillator-dependent properties for couplings

    Although the actual coupling value depends on the precise
    combination of two oscillators, the calculations often require some
    information about each that doesn't depend on it's partner. These
    calculations can become relatively extensive, so by doing them once
    for each oscillator (instead of per pair), we can save a lot of
    time!

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    """

    for coupmapname, osclist in system.oscillators_ordered_coup.items():
        oscixlist = system.oscillators_ordered_coup_ix[coupmapname]
        coupmap = run_pars.requested_pairmapdict[coupmapname]
        coupmap.code.GM_prep_coupling(
            coupmap, system, oscixlist, osclist)


def calc_coupling(run_pars, system, outputs):
    """Calculate the couplings of the system.

    This function loops through the requested maps, and lets each
    calculate the couplings for its assigned pairs.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    outputs : dict of str: `np.ndarray` pairs
        The outputs the program is requested to generate. Currently
        contains hamiltonian and dipole arrays.
    """

    for coupmapname in system.oscillators_ordered_coup.keys():
        coupmap = run_pars.requested_pairmapdict[coupmapname]
        coupmap.code.GM_calc_coupling(
            coupmap, system, outputs["hamiltonian"])

        # scale all couplings with the parameter from the input parameters
        arr = coupmap.allpairs
        outputs["hamiltonian"][arr[:, 0], arr[:, 1]] *= (
            run_pars.coupling_scale_factors_dict[coupmapname]
            / run_pars.dielectric_constant)


def generate_output_structures(run_pars, system):
    """The heart of the per-frame loop. Does the actual calculations.

    Currently, for each oscillator, the potential is calculated (if
    requested), along with frequency and dipole
    Next, in a separate loop, the couplings are computed.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)

    Returns
    -------
    outputs : dict of str: `np.ndarray` pairs
        The outputs the program is requested to generate. Currently
        contains hamiltonian and dipole arrays.
    """

    outputs = {}
    nosc = system.nosc
    if any(data in run_pars.output_data for data in ("ham",)):
        outputs["hamiltonian"] = np.zeros((nosc, nosc), dtype="float32")
        outputs["dipole_pos"] = np.zeros((nosc, 3), dtype="float32")

    if any(data in run_pars.output_data for data in ("ene",)):
        outputs["energies"] = np.zeros((nosc,), dtype="float32")

    if any(data in run_pars.output_data for data in ("ham", "dip")):
        outputs["dipoles"] = np.zeros((nosc, 3), dtype="float32")

    if any(data in run_pars.output_data for data in ("ram",)):
        outputs["raman"] = np.zeros((nosc, 6), dtype="float32")

    if any(data in run_pars.output_data for data in ("pos",)):
        outputs["positions"] = np.zeros((nosc, 3), dtype="float32")

    if any(data in run_pars.output_data for data in ("dbp",)):
        outputs["doublepos"] = np.zeros((nosc*2, 3), dtype="float32")

    return outputs
