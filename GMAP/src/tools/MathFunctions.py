# 3rd party lib imports
from numba import njit
import numpy as np

from GMAP.src.tools.PrintTools import devprint as dpr
dpr("", end="")  # to disable error of dpr unused


def PBC_triclinic(vect, boxvects, boxvects_inv):
    """Translates the vector to within the box centred around the origin

    If vect is a 2D array, the oneth dimension must be of the same size
    as the boxvects array.

    If boxvects is the identity matrix, each value in vect will be
    -0.5 <= value < 0.5.

    Parameters
    ----------
    vect : np.ndarray
        The vector that should be treated following the PBC. The method
        is tested for shapes (3,) and (M, 3), but it should work for
        the general case (N,) and (M, N), where N is the size of
        boxvects, and M is arbitrary.
    boxvects : np.ndarray
        The vectors uniquely defining the box.
        Must be a square array. Size (3,3) has been tested, but in
        theory, any shape (N, N) should work.
    boxvects_inv : np.ndarray
        The inverse matrix of boxvects.
        Must be a square array. Size (3,3) has been tested, but in
        theory, any shape (N, N) should work.

    Returns
    -------
    new_vect : np.ndarray
        The vector that has been corrected for PBC
    """

    # dpr("triclin")
    unit_vec = vect @ boxvects_inv
    return (unit_vec - np.floor(unit_vec + 0.5)) @ boxvects


# currently unused - missing docstring
def PBC_diff_triclinic(vect1, vect2, boxvects, boxvects_inv):
    diff = vect1 - vect2
    unit_diff = diff @ boxvects_inv
    unit_diff_fract = unit_diff - np.floor(unit_diff + 0.5)
    # unit_diff_fract = unit_diff - np.floor(unit_diff)
    # unit_diff_fract[unit_diff_fract >= 0.5] -= 1
    shortdiff = unit_diff_fract @ boxvects
    return shortdiff


# currently unused - missing docstring
@njit
def PBC_diff_orthorhombic(vect1, vect2, halfbox, boxdims):
    """
    Calculates the distance vector between vect1 and vect2, taking into account
    the periodic nature of the system. diff = vect1 - vect2 (diff = the vector
    pointing from vect2 to vect1).
    """
    diff = vect1 - vect2
    PBC_orthorhombic(diff, halfbox, boxdims)
    return diff


# from AIM, currently unused - missing docstring
@njit
def PBC_orthorhombic(vect, halfbox, boxdims):
    for i in range(3):
        if vect[i] > halfbox[i]:
            vect[i] -= boxdims[i]
        elif vect[i] < -halfbox[i]:
            vect[i] += boxdims[i]
    return vect


@njit
def crossprod(vect1: np.ndarray, vect2: np.ndarray) -> np.ndarray:
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
    vect3 = np.empty((3,))
    vect3[0] = vect1[1]*vect2[2]-vect1[2]*vect2[1]
    vect3[1] = vect1[2]*vect2[0]-vect1[0]*vect2[2]
    vect3[2] = vect1[0]*vect2[1]-vect1[1]*vect2[0]

    return vect3


@njit
def dotprod(vect1: np.ndarray, vect2: np.ndarray) -> float:
    """Calculates the dot product between two vectors of size 3.

    This is faster than the dedicated np method, as there are no checks for the
    correctness of the provided vectors. The method is njitted for added speed.

    Parameters
    ----------
    vect1, vect2 : `np.ndarray`
        The length-3 vectors of which to take the dot product.

    Returns
    -------
    vect3 : `np.ndarray`
        The dot product of `vect1` and `vect2`.
    """
    return vect1[0]*vect2[0] + vect1[1]*vect2[1] + vect1[2]*vect2[2]


@njit
def vec3_len(vect: np.ndarray) -> float:  # replacement for np.linalg.norm
    """Calculates the norm (length) of a vector of size 3.

    This is a replacement for the function `np.linalg.norm`.
    This is faster than the dedicated np method, as there are no checks for the
    correctness of the provided vectors. The method is njitted for added speed.

    Parameters
    ----------
    vect1 : `np.ndarray`
        The length-3 vector of which to find the length.

    Returns
    -------
    length : float
        The length of the provided vector.
    """
    return np.sqrt(vect[0]*vect[0] + vect[1]*vect[1] + vect[2]*vect[2])


@njit
def project(vect1: np.ndarray, vect2: np.ndarray) -> np.ndarray:
    """ Calculates the orthogonal part of `vect2` to `vect1`.

    Calculates the part of vector `vect2` that is orthogonal to the vector
    `vect1` (i.e. it subtracts from `vect2` the part that is along `vect1`,
    and returns the result).
    Be aware that because of how numba works, both `vect1` and `vect2` should
    have float32 as the dtype.

    Parameters
    ----------
    vect1 : `np.ndarray`
        The vector to compare against
    vect2 : `np.ndarray`
        The vector of which the orthogonal part is extracted

    Returns
    -------
    vectout : `np.ndarray`
        The part of `vect2` that is orthogonal to `vect1`.
    """
    inprod = dotprod(vect1, vect2)/dotprod(vect1, vect1)
    vectout = vect2 - inprod*vect1
    return vectout
