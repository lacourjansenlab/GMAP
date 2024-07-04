
# 3rd party imports
from numba import njit
import numpy as np

# local imports
import GMAP.src.tools.CLibLoader as GM_CL


def calc_CoM(System, atomlist):
    """Calculate the centre of mass of a given set of atoms.

    Parameters
    ----------
    System : :class:`~GMAP.src.tools.SystemReader.System
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

    allpos_box = System.positions[atomlist] @ System.boxvects_inv
    masses = System.masses[atomlist]

    CoM_box = np.sum(allpos_box * masses[:, None], axis=0) / np.sum(masses)
    CoM = (CoM_box - np.floor(CoM_box + 0.5)) @ System.boxvects
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
        allpos_box = positions[
            res_first_ix[resix]: res_last_ix[resix]+1
        ] @ boxvects_inv
        masses_res = masses[res_first_ix[resix]: res_last_ix[resix]+1]

        CoM_box = np.sum(
            allpos_box * masses_res[:, None], axis=0
        ) / np.sum(masses_res)
        CoM_array[resix] = (
            CoM_box - np.floor(CoM_box + half)) @ boxvects

    return CoM_array


def calc_frame(Printer, RunPars, System, outputs):
    """The heart of the per-frame loop. Does the actual calculations.

    Currently, for each oscillator, the potential is calculated (if
    requested), along with frequency and dipole
    Next, in a separate loop, the couplings are computed.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    System : :class:`~GMAP.src.tools.SystemReader.System`
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

    VEGlib = GM_CL.VEG_CLib()

    for oscix, oscillator in enumerate(System.oscillators):
        # Do we need the estatics?
        if any(data in RunPars.output_data for data in ("ham", "dip", "ene")):
            if oscillator.Map.Core.electrostatic_choice in ("V", "E", "G"):
                # calculate VEG
                VEGlib.calcVEG_perres_mm(System, RunPars, oscillator)

            # ROTATE VEG
            if oscillator.Map.Core.electrostatic_choice in ("E", "G"):
                oscillator.rotate_VEG()

        # do we need dipoles?
        # we also need dipoles for the (full) hamiiltonian.
        if any(data in RunPars.output_data for data in ("ham", "dip")):
            r_vec, r_pos = calc_dipole(Printer, System, oscillator)
            outputs["dipoles"][oscix] = r_vec

            if any(data in RunPars.output_data for data in ("ham")):
                outputs["dipole_pos"][oscix] = r_pos

        if "ene" in RunPars.output_data:
            outputs["energies"][oscix] = calc_frequency(
                Printer, System, oscillator)

        if "ham" in RunPars.output_data:
            outputs["hamiltonian"][oscix, oscix] = calc_frequency(
                Printer, System, oscillator)

    # calculate the couplings for the hamiltonian
    if "ham" in RunPars.output_data:
        prep_coupling(Printer, RunPars, System)

        calc_coupling(Printer, RunPars, System, outputs)

    return outputs


def calc_dipole(Printer, System, oscillator):
    """Calculate the dipole moment for a given oscillator

    The oscillator 'knows' how this should be done - invoke that method.
    The results are returned, but also saved as attributes to the
    oscillator.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    System : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.SystemReader.Oscillator`
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
    map_ = oscillator.Map
    r_vec, r_pos = map_.code.GM_calculate_dipole(
        Printer, map_, System, oscillator)
    setattr(oscillator, "dipole_vec", r_vec)
    setattr(oscillator, "dipole_pos", r_pos)
    return r_vec, r_pos


def calc_frequency(Printer, System, oscillator):
    """Calculate the frequency for a given oscillator

    The oscillator 'knows' how this should be done - invoke that method.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    System : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.SystemReader.Oscillator`
        The specific oscillator for which the calculation is requested.

    Returns
    -------
    frequency : float
        The frequency found for this oscillator
    """

    map_ = oscillator.Map
    return map_.code.GM_calculate_frequency(Printer, map_, System, oscillator)


def prep_coupling(Printer, RunPars, System):
    """Calculate some oscillator-dependent properties for couplings

    Although the actual coupling value depends on the precise
    combination of two oscillators, the calculations often require some
    information about each that doesn't depend on it's partner. These
    calculations can become relatively extensive, so by doing them once
    for each oscillator (instead of per pair), we can save a lot of
    time!

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    System : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    """

    for coupmapname, osclist in System.oscillators_ordered_coup.items():
        oscixlist = System.oscillators_ordered_coup_ix[coupmapname]
        coupmap = RunPars.requested_pairmapdict[coupmapname]
        coupmap.code.GM_prep_coupling(
            Printer, coupmap, System, oscixlist, osclist)


def calc_coupling(Printer, RunPars, System, outputs):
    """Calculate the couplings of the system.

    This function loops through the requested maps, and lets each
    calculate the couplings for its assigned pairs.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    System : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    outputs : dict of str: `np.ndarray` pairs
        The outputs the program is requested to generate. Currently
        contains hamiltonian and dipole arrays.
    """

    for coupmapname in System.oscillators_ordered_coup.keys():
        coupmap = RunPars.requested_pairmapdict[coupmapname]
        coupmap.code.GM_calc_coupling(
            Printer, coupmap, System, outputs["hamiltonian"])


def generate_output_structures(RunPars, System):
    """The heart of the per-frame loop. Does the actual calculations.

    Currently, for each oscillator, the potential is calculated (if
    requested), along with frequency and dipole
    Next, in a separate loop, the couplings are computed.

    Parameters
    ----------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    System : :class:`~GMAP.src.tools.SystemReader.System`
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
    if any(data in RunPars.output_data for data in ("ham",)):
        outputs["hamiltonian"] = np.zeros(
            (System.nosc, System.nosc), dtype="float32")
        outputs["dipole_pos"] = np.zeros((System.nosc, 3), dtype="float32")

    if any(data in RunPars.output_data for data in ("ene",)):
        outputs["energies"] = np.zeros((System.nosc,), dtype="float32")

    if any(data in RunPars.output_data for data in ("ham", "dip")):
        outputs["dipoles"] = np.zeros((System.nosc, 3), dtype="float32")

    return outputs
