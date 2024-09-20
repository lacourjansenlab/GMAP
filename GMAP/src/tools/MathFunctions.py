
# standard library imports
import math

# 3rd party lib imports
from numba import njit
import numpy as np

# local imports
import GMAP.src.tools.constants as GM_con


# (as I keep searching here for this, I'm putting this here)
# rotating vectors and tensors in numpy:

# assuming R is the rotation matrix that rotates base (or global, or default)
# coordinates in changed/local ones. (so R rotates cartesian to box, or
# MD to molecule). R must then look like this:
# R[0] = local x vector defined in global coordinates (same for 1=y and 2=z)
# Ri = R^-1, such that R @ Ri = np.diag([1, 1, 1])

# v = some vector in global coords, v' is that same vector in local coords:
# v = v' @ R   (and v' = v @ Ri)
# This makes sense, as we take v'[0] amounts of R[0], etc, giving the 'total'
# amount of global that v' represents.
# This can be seen in how we convert cartesian to box and back.
# also, how we convert the global field to local field (local = global @ invRM)

# Tensors (like the electric field gradient and raman tensor) are seen as
# operators (although they aren't used much as such) - a tensor T operates on
# a vector v to do:  v -> vT
# Then, analogously, T' does v' -> v'T'
# so, how to find T' if we have T (or vice versa?)
# v' = v @ Ri
# v' @ T' = v @ Ri @ T'
# v @ T = v @ Ri @ T' @ R
# T = Ri @ T' @ R
# and the other way around:
# R @ T @ Ri = R @ Ri @ T' @ R @ Ri = T'
# So, T = Ri @ T' @ R,    and T' = R @ T @ Ri
# (the latter can be seen in rotating the global VEG)

# But, when rotating global to local (and vice versa), we use R.T instead of
# Ri, why? R.T is cheaper, and the two are equal if the matrix consists of
# real-valued orthonormal vectors (which is the case for the global-local
# matrix, but not for the cartesian-box matrix)

# numpy matrix multiplication:
# A = np.array([[a11, a12, a13], [a21, a22, a23], [a31, a32, a33]])
# Then, this holds true: A @ B == np.array([
#     [a11*b11 + a12*b21 + a13*b31, a11*b12 + a12*b22 + a13*b32, ...],
#     [a21*b11 + a22*b21 + a23*b31, a21*b12 + a22*b22 + a23*b32, ...],
#     [a31*b11 + a32*b21 + a33*b31, a31*b12 + a32*b22 + a33*b32, ...],
# ])
# Trick for memorization:
# if C = A @ B, then C[i, j] = sum{k=1 -> k=3}(A[i, k] * B[k, j])
# (hence, why A's second dimension must equal B's first)


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

    unit_vec = vect @ boxvects_inv
    return (unit_vec - np.floor(unit_vec + 0.5)) @ boxvects


@njit
def PBC_back2box(vect, boxvects):
    """Takes a vector in box coordinates, moves it to lie within the
    main box, and translate back to global/system/MD coordinates.
    """

    half = np.float32(0.5)
    return (vect - np.floor(vect + half)) @ boxvects


# # currently unused - missing docstring
# def PBC_diff_triclinic(vect1, vect2, boxvects, boxvects_inv):
#     diff = vect1 - vect2
#     unit_diff = diff @ boxvects_inv
#     unit_diff_fract = unit_diff - np.floor(unit_diff + 0.5)
#     # unit_diff_fract = unit_diff - np.floor(unit_diff)
#     # unit_diff_fract[unit_diff_fract >= 0.5] -= 1
#     shortdiff = unit_diff_fract @ boxvects
#     return shortdiff


# # currently unused - missing docstring
# @njit
# def PBC_diff_orthorhombic(vect1, vect2, halfbox, boxdims):
#     """
#     Calculates the distance vector between vect1 and vect2, taking into
#     account the periodic nature of the system. diff = vect1 - vect2
#     (diff = the vector pointing from vect2 to vect1).
#     """
#     diff = vect1 - vect2
#     PBC_orthorhombic(diff, halfbox, boxdims)
#     return diff


# # from AIM, currently unused - missing docstring
# @njit
# def PBC_orthorhombic(vect, halfbox, boxdims):
#     for i in range(3):
#         if vect[i] > halfbox[i]:
#             vect[i] -= boxdims[i]
#         elif vect[i] < -halfbox[i]:
#             vect[i] += boxdims[i]
#     return vect


@njit
def crossprod(vect1: np.ndarray, vect2: np.ndarray) -> np.ndarray:
    """Calculates the cross product between two vectors of size 3.

    This is faster than the dedicated np method, as there are no checks
    for the correctness of the provided vectors. The method is njitted
    for added speed.

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

    This is faster than the dedicated np method, as there are no checks
    for the correctness of the provided vectors. The method is njitted
    for added speed.

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
    This is faster than the dedicated np method, as there are no checks
    for the correctness of the provided vectors. The method is njitted
    for added speed.

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

    Calculates the part of vector `vect2` that is orthogonal to the
    vector `vect1` (i.e. it subtracts from `vect2` the part that is
    along `vect1`, and returns the result).
    Be aware that because of how numba works, both `vect1` and `vect2`
    should have float32 as the dtype.

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


def calc_color_dist(r1, g1, b1, r2, g2, b2):
    """Calculates the distance between the two provided colors.

    The distance is calculated using the
    `redmean method <https://en.wikipedia.org/wiki/Color_difference>`__

    Parameters
    ----------
    r1, g1, b1 : int
        The rgb values of the first color, ints in the interval [0, 255]
    r1, g1, b1 : int
        The rgb values of the second color, ints in the interval
        [0, 255]

    Returns
    -------
    delC : float
        The distance between the two colors. A smaller number means they
        are more similar. Does not depend on the order of the two
        colors.
    """

    # redmean method: https://en.wikipedia.org/wiki/Color_difference
    r_bar = 0.5 * (r1 + r2)
    delC = math.sqrt(
        (2 + r_bar/255) * abs(r1 - r2)**2
        + 4 * abs(g1 - g2)**2
        + (2 + (255 - r_bar)/255) * abs(b1 - b2)**2
    )
    return delC


def convert_color_24_4(r, g, b, lookup={}):
    """Converts a given 24bit color to the closest 4bit one.

    Calculates the distance of the provided color to each of the 4bit
    colors, and returns the closest one.

    If a specific 24bit color has been converted, it is saved in the
    lookup dict for quick reuse.

    Parameters
    ----------
    r, g, b : int
        The rgb values of the color to convert, ints in the interval
        [0, 255]

    Returns
    -------
    outcolor : tuple
        A tuple of two items, an int and a bool. The integer represents
        the color (values 0-7), the bool whether it should be bright.
    """

    rgb = (int(r), int(g), int(b))

    if rgb in lookup:
        return lookup[rgb]

    maxdist = 765
    outcolor = (255, 255, 255)
    for ix, (col, output) in enumerate(GM_con.printed_colors.items()):
        delC = calc_color_dist(*rgb, *col)
        if 0 < ix < 4:
            delC *= 2
        if delC < maxdist:
            maxdist = delC
            outcolor = output

    lookup[rgb] = outcolor
    return outcolor
