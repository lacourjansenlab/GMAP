"""
Tests all the functions/classes/methods in the file:
src/tools/MathFunctions.py.

Missing tests:
    None?
"""

# 3rd party imports
import numpy as np
import pytest

# local imports
import GMAP.src.tools.MathFunctions as GM_MF


def test_PBC_back2box():
    boxvects = np.array([[10, 0, 0], [0, 10, 0], [0, 0, 10]], dtype="float32")
    movevect = np.array([0.8, 0.4, 0.26], dtype="float32")
    ans = np.array([-2, 4, 2.6], dtype="float32")

    assert np.all(GM_MF.PBC_back2box(movevect, boxvects).round(6) == ans)
    assert np.all(
        GM_MF.PBC_back2box.py_func(movevect, boxvects).round(6) == ans)


@pytest.mark.parametrize(("vect", "expt", "boxvects"), [
    ([3, 7, 2], [3, -3, 2], [[10, 0, 0], [0, 10, 0], [0, 0, 10]]),
    ([33, 77, 22], [3, -3, 2], [[10, 0, 0], [0, 10, 0], [0, 0, 10]]),
    ([33, 22, 11], [3, 2, 1], [[10, 0, 0], [10, 10, 0], [10, 10, 10]]),
])
def test_PBC_triclinic(vect, expt, boxvects):
    """
    See that vectors (points) are moved back into the box.
    """

    vect = np.array(vect)
    expt = np.array(expt)
    boxvects = np.array(boxvects)
    boxvects_inv = np.linalg.inv(boxvects)
    translated_point = GM_MF.PBC_triclinic(vect, boxvects, boxvects_inv)
    assert np.all(
        np.round(translated_point, 3) == expt
    )


@pytest.mark.parametrize(("vector1", "vector2"), [
    ([1, 5, 7], [1, 5, 7]),
    ([1, 5, 7], [-3, 0, 4]),
    ([-3, 0, 4], [0, 0, 0])
])
def test_crossprod(vector1, vector2):
    """
    Test that the local version of the cross product gives the same results as
    the numpy one.
    """
    vector1 = np.array(vector1, dtype='float32')
    vector2 = np.array(vector2, dtype='float32')
    assert np.all(
        GM_MF.crossprod(vector1, vector2) == np.cross(vector1, vector2)
    )
    assert np.all(
        GM_MF.crossprod.py_func(vector1, vector2) == np.cross(vector1, vector2)
    )


@pytest.mark.parametrize(("vector1", "vector2"), [
    ([1, 5, 7], [1, 5, 7]),
    ([1, 5, 7], [-3, 0, 4]),
    ([-3, 0, 4], [0, 0, 0])
])
def test_dotprod(vector1, vector2):
    """
    Test that the local version of the dot product gives the same results as
    the numpy one.
    """
    vector1 = np.array(vector1, dtype='float32')
    vector2 = np.array(vector2, dtype='float32')
    assert np.all(GM_MF.dotprod(vector1, vector2) == np.dot(vector1, vector2))
    assert np.all(
        GM_MF.dotprod.py_func(vector1, vector2) == np.dot(vector1, vector2)
    )


@pytest.mark.parametrize("vector", [
    [1, 5, 7],
    [-3, 0, 4],
    [0, 0, 0]
])
def test_vec3len(vector):
    """
    Test that the local version of calculating vector norm gives the same
    results as the numpy one.
    """
    inpvec = np.array(vector)
    assert GM_MF.vec3_len(inpvec) == np.linalg.norm(inpvec)
    assert GM_MF.vec3_len.py_func(inpvec) == np.linalg.norm(inpvec)


@pytest.mark.parametrize(("vector1", "vector2"), [
    ([1, 5, 7], [1, 5, 7]),
    ([1, 5, 7], [-3, 0, 4])
])
def test_project(vector1, vector2):
    """
    The vector returned by project should be the component of vect2 that is
    perpendicular to vect1. Therefore, the projection and vect1 should be
    orthogonal -> dot product should equal zero.
    As vect1 has infinitely many orthogonal vectors, we also need tocheck if
    the one found is the one corresponding to vect2. This is done by taking the
    cross product of the projection and vect2. Only if the two correspond, this
    cross product is also orthogonal to vect1.
    """
    vector1 = np.array(vector1, dtype='float32')
    vector2 = np.array(vector2, dtype='float32')
    prj = GM_MF.project(vector1, vector2)
    assert all((
        abs(np.dot(vector1, prj)) <= 1e-5,
        abs(np.dot(vector1, np.cross(vector2, prj))) <= 1e-5
    ))

    prj = GM_MF.project.py_func(vector1, vector2)
    assert all((
        abs(np.dot(vector1, prj)) <= 1e-5,
        abs(np.dot(vector1, np.cross(vector2, prj))) <= 1e-5
    ))
