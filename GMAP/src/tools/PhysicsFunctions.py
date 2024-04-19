
# 3rd party imports
from numba import njit
import numpy as np

# local imports
import GMAP.src.tools.CLibLoader as GM_CL
from GMAP.src.tools.PrintTools import devprint as dpr


def calc_CoM(System, atomlist):
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
    """Calculates the cross product between two vectors of size 3.

    This is faster than the dedicated np method, as there are no checks for the
    correctness of the provided vectors. The method is njitted for added speed.

    Parameters
    ----------
    vect1, vect2 : `np.ndarray`
        The length-3 vectors of which to take the cross product.

    Returns
    -------
    vect3 : `np.ndarray`
        The cross product of `vect1` and `vect2`.
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


def calc_frame(Printer, RunPars, System, dipoles, hamiltonian):

    VEGlib = GM_CL.VEG_CLib()

    for oscix, oscillator in enumerate(System.oscillators):
        if any(data in RunPars.output_data for data in ("ham", "dip")):
            if oscillator.Map.Core.electrostatic_choice in ("V", "E", "G"):
                # calculate VEG
                VEGlib.calcPot_perres_mm(System, RunPars, oscillator)
                V = oscillator.VEGout[:, 0]
            else:
                V = None
            if oscillator.Map.Core.electrostatic_choice in ("E", "G"):
                E = oscillator.VEGout[:, 1:4]
            else:
                E = None
            if oscillator.Map.Core.electrostatic_choice == "G":
                G = oscillator.VEGout[:, 4:]
            else:
                G = None

            dpr(V, E, G)

            dipoles[oscix] = calc_dipole()

        if "ham" in RunPars.output_data:
            hamiltonian[oscix, oscix] = calc_frequency()
            prep_coupling()

    # for every oscillator pair (that should be covered) - calc_coupling

    return hamiltonian, dipoles


def calc_dipole():
    return


def calc_frequency():
    return


def prep_coupling():
    return


def calc_coupling():
    return
