# 3rd party lib imports
from numba import njit
import numpy as np


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
    vect3 = np.copy(vect1)
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
