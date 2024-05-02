
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
    requested). In the future, frequency, dipole, etc will also be
    calculated here.
    Next, in a separate loop, the couplings will be computed.
    """

    VEGlib = GM_CL.VEG_CLib()

    for oscix, oscillator in enumerate(System.oscillators):
        # we also need dipoles for the (full) hamiiltonian.
        if any(data in RunPars.output_data for data in ("ham", "dip")):
            if oscillator.Map.Core.electrostatic_choice in ("V", "E", "G"):
                # calculate VEG
                VEGlib.calcPot_perres_mm(System, RunPars, oscillator)

                # ROTATE VEG!

            r_vec, r_pos = calc_dipole(Printer, System, oscillator)
            outputs["dipoles"][oscix] = r_vec

            if any(data in RunPars.output_data for data in ("ham")):
                outputs["dipole_pos"][oscix] = r_pos

        if "ham" in RunPars.output_data:
            outputs["hamiltonian"][oscix, oscix] = calc_frequency()
            prep_coupling()

    # for every oscillator pair (that should be covered) - calc_coupling

    return outputs


def calc_dipole(Printer, System, oscillator):
    # every map should have a calc dipole function
    map_ = oscillator.Map
    r_vec, r_pos = map_.code.GM_get_dipole(Printer, map_, System, oscillator)
    return r_vec, r_pos


def calc_frequency():
    return


def prep_coupling():
    return


def calc_coupling():
    return


def generate_output_structures(RunPars, System):
    outputs = {}
    if any(data in RunPars.output_data for data in ("ham")):
        outputs["hamiltonian"] = np.zeros(
            (System.nosc, System.nosc), dtype="float32")
        outputs["dipole_pos"] = np.zeros((System.nosc, 3), dtype="float32")
    elif any(data in RunPars.output_data for data in ("ham", "dip")):
        outputs["dipoles"] = np.zeros((System.nosc, 3), dtype="float32")

    return outputs
