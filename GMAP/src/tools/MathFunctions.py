# 3rd party lib imports
from numba import njit
import numpy as np


@njit
def crossprod(vect1: np.ndarray, vect2: np.ndarray) -> np.ndarray:
    """
    Calculates the cross product between two vectors of size 3. This is
    faster than the dedicated np method, as there are no checks for the
    correctness of the provided vectors.
    """
    vect3 = np.copy(vect1)
    vect3[0] = vect1[1]*vect2[2]-vect1[2]*vect2[1]
    vect3[1] = vect1[2]*vect2[0]-vect1[0]*vect2[2]
    vect3[2] = vect1[0]*vect2[1]-vect1[1]*vect2[0]

    return vect3


@njit
def dotprod(vect1: np.ndarray, vect2: np.ndarray) -> float:
    """
    Calculates the dot product between two vectors of size 3. This is faster
    than the dedicated np method, as there are no checks for the correctness
    of the provided vectors.
    """
    return vect1[0]*vect2[0] + vect1[1]*vect2[1] + vect1[2]*vect2[2]


@njit
def vec3_len(vect: np.ndarray) -> float:  # replacement for np.linalg.norm
    """
    Calculates the norm (length) of a vector of size 3. This is faster than the
    dedicated np method, as there are no checks for the correctness of the
    provided vectors.
    """
    return np.sqrt(vect[0]*vect[0] + vect[1]*vect[1] + vect[2]*vect[2])


@njit
def project(vect1: np.ndarray, vect2: np.ndarray) -> np.ndarray:
    """
    Calculates the part of vector vect2 that is orthogonal to the vector vect1
    (i.e. it subtracts from vect2 the part that is along vect1, and returns the
    result).
    Be aware that because of how numba works, both vect1 and vect2 should have
    float32 as the dtype.
    """
    inprod = dotprod(vect1, vect2)/dotprod(vect1, vect1)
    vectout = vect2 - inprod*vect1
    return vectout
