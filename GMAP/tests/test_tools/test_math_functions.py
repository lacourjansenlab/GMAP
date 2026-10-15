"""
Tests all the functions/classes/methods in the file:
src/tools/math_functions.py.

Missing tests:

- None?

"""

# 3rd party imports
import numpy as np
import pytest

# local imports
import GMAP.src.tools.constants as GM_con
import GMAP.src.tools.math_functions as GM_mf


def test_PBC_back2box():
    boxvects = np.array([[10, 0, 0], [0, 10, 0], [0, 0, 10]], dtype="float32")
    movevect = np.array([0.8, 0.4, 0.26], dtype="float32")
    ans = np.array([-2, 4, 2.6], dtype="float32")

    assert np.all(GM_mf.PBC_back2box(movevect, boxvects).round(6) == ans)
    assert np.all(
        GM_mf.PBC_back2box.py_func(movevect, boxvects).round(6) == ans)


@pytest.mark.parametrize(("vect", "expt", "boxvects"), [
    ([3, 7, 2], [3, -3, 2], [[10, 0, 0], [0, 10, 0], [0, 0, 10]]),
    ([33, 77, 22], [3, -3, 2], [[10, 0, 0], [0, 10, 0], [0, 0, 10]]),
    ([33, 22, 11], [3, 2, 1], [[10, 0, 0], [10, 10, 0], [10, 10, 10]]),
])
def test_PBC_triclinic(vect, expt, boxvects):
    """
    See that vectors (points) are moved back into the box.
    """

    vect = np.array(vect, dtype="float32")
    expt = np.array(expt, dtype="float32")
    boxvects = np.array(boxvects, dtype="float32")
    boxvects_inv = np.linalg.inv(boxvects)
    translated_point = GM_mf.PBC_triclinic(vect, boxvects, boxvects_inv)
    assert np.all(np.round(translated_point, 3) == expt)
    translated_point = GM_mf.PBC_triclinic.py_func(
        vect, boxvects, boxvects_inv)
    assert np.all(np.round(translated_point, 3) == expt)


@pytest.mark.parametrize(("boxvect1", "boxvect2", "boxvects", "expt"), [
    (
        [0.5, 0.9, 0.5], [0.2, 0.2, 0.3], [[10, 0, 0], [0, 10, 0], [0, 0, 10]],
        [3, -3, 2]),
    (
        [9.9, 9.9, 9.9], [6.6, 2.2, 7.7], [[10, 0, 0], [0, 10, 0], [0, 0, 10]],
        [3, -3, 2]),
    (
        [4.4, 4.4, 4.4], [3.3, 3.3, 3.3],
        [[10, 0, 0], [10, 10, 0], [10, 10, 10]], [3, 2, 1]),
])
def test_PBC_boxdiff_triclin(boxvect1, boxvect2, boxvects, expt):
    boxvect1 = np.array(boxvect1, dtype="float32")
    boxvect2 = np.array(boxvect2, dtype="float32")
    boxvects = np.array(boxvects, dtype="float32")
    expt = np.array(expt, dtype="float32")
    newdiff = GM_mf.PBC_boxdiff_triclin(boxvect1, boxvect2, boxvects)
    assert np.all(np.round(newdiff, 3) == expt)
    newdiff = GM_mf.PBC_boxdiff_triclin.py_func(boxvect1, boxvect2, boxvects)
    assert np.all(np.round(newdiff, 3) == expt)


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
        GM_mf.crossprod(vector1, vector2) == np.cross(vector1, vector2)
    )
    assert np.all(
        GM_mf.crossprod.py_func(vector1, vector2) == np.cross(vector1, vector2)
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
    assert np.all(GM_mf.dotprod(vector1, vector2) == np.dot(vector1, vector2))
    assert np.all(
        GM_mf.dotprod.py_func(vector1, vector2) == np.dot(vector1, vector2)
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
    assert GM_mf.vec3_len(inpvec) == np.linalg.norm(inpvec)
    assert GM_mf.vec3_len.py_func(inpvec) == np.linalg.norm(inpvec)


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
    prj = GM_mf.project(vector1, vector2)
    assert all((
        abs(np.dot(vector1, prj)) <= 1e-5,
        abs(np.dot(vector1, np.cross(vector2, prj))) <= 1e-5
    ))

    prj = GM_mf.project.py_func(vector1, vector2)
    assert all((
        abs(np.dot(vector1, prj)) <= 1e-5,
        abs(np.dot(vector1, np.cross(vector2, prj))) <= 1e-5
    ))


@pytest.mark.parametrize(("b0", "b1", "b2", "expt"), [
    # rotation around Z axis, one fixed at x axiss
    ([1, 0, 0], [0, 0, 1], [1, 1, 0], 45),
    ([1, 0, 0], [0, 0, 1], [0, 1, 0], 90),
    ([1, 0, 0], [0, 0, 1], [-1, 1, 0], 135),
    ([1, 0, 0], [0, 0, 1], [-1, 0, 0], 180),
    ([1, 0, 0], [0, 0, 1], [-1, -1, 0], -135),
    ([1, 0, 0], [0, 0, 1], [0, -1, 0], -90),
    ([1, 0, 0], [0, 0, 1], [1, -1, 0], -45),
    ([1, 0, 0], [0, 0, 1], [1, 0, 0], 0),

    # rotation around (1, 1, 1), one fixed at z axis
    ([0, 0, 1], [1, 1, 1], [0, -1, 0], 60),
    ([0, 0, 1], [1, 1, 1], [1, 0, 0], 120),
    ([0, 0, 1], [1, 1, 1], [0, 0, -1], 180),
    ([0, 0, 1], [1, 1, 1], [0, 1, 0], -120),
    ([0, 0, 1], [1, 1, 1], [-1, 0, 0], -60),
    ([0, 0, 1], [1, 1, 1], [0, 0, 1], 0),
])
def test_dihedral_base(b0, b1, b2, expt):
    b0 = np.array(b0, dtype='float32')
    b1 = np.array(b1, dtype='float32')
    b2 = np.array(b2, dtype='float32')
    assert round(GM_mf.dihedral_base(b0, b1, b2) * GM_con.rad2deg, 4) == expt
    assert round(
        GM_mf.dihedral_base.py_func(b0, b1, b2) * GM_con.rad2deg, 4) == expt


@pytest.mark.parametrize(("p0", "p1", "p2", "p3", "boxvects", "expt"), [
    # rotation around (1, 1, 1), one fixed at z axis
    (
        [0, 0, 1], [0, 0, 0], [1, 1, 1], [1, 0, 1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 60),
    (
        [0, 0, 1], [0, 0, 0], [1, 1, 1], [2, 1, 1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 120),
    (
        [0, 0, 1], [0, 0, 0], [1, 1, 1], [1, 1, 0],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 180),
    (
        [0, 0, 1], [0, 0, 0], [1, 1, 1], [1, 2, 1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], -120),
    (
        [0, 0, 1], [0, 0, 0], [1, 1, 1], [0, 1, 1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], -60),
    (
        [0, 0, 1], [0, 0, 0], [1, 1, 1], [1, 1, 2],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 0),

    # over box edge
    (
        [0, 0, 1], [0, 0, 0], [-8, -8, -8], [-6, -7, -7],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 120),
    # slanted box
    (
        [0, 0, 1], [0, 0, 0], [-8, -8, -8], [-6, -7, -7],
        [[10, 0, 0], [10, 10, 0], [10, 10, 10]], 120),
])
def test_dihedral(p0, p1, p2, p3, boxvects, expt):
    p0 = np.array(p0, dtype='float32')
    p1 = np.array(p1, dtype='float32')
    p2 = np.array(p2, dtype='float32')
    p3 = np.array(p3, dtype='float32')
    boxvects = np.array(boxvects, dtype='float32')
    boxvects_inv = np.linalg.inv(boxvects)
    assert round(GM_mf.dihedral(
        p0, p1, p2, p3, boxvects, boxvects_inv) * GM_con.rad2deg, 4) == expt
    assert round(GM_mf.dihedral.py_func(
        p0, p1, p2, p3, boxvects, boxvects_inv) * GM_con.rad2deg, 4) == expt


@pytest.mark.parametrize(("p0", "p1", "p2", "p3", "boxvects", "expt"), [
    # rotation around (1, 1, 1), one fixed at z axis
    (
        [0, 0, 0.1], [0, 0, 0], [0.1, 0.1, 0.1], [0.1, 0, 0.1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 60),
    (
        [0, 0, 0.1], [0, 0, 0], [0.1, 0.1, 0.1], [0.2, 0.1, 0.1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 120),
    (
        [0, 0, 0.1], [0, 0, 0], [0.1, 0.1, 0.1], [0.1, 0.1, 0],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 180),
    (
        [0, 0, 0.1], [0, 0, 0], [0.1, 0.1, 0.1], [0.1, 0.2, 0.1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], -120),
    (
        [0, 0, 0.1], [0, 0, 0], [0.1, 0.1, 0.1], [0, 0.1, 0.1],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], -60),
    (
        [0, 0, 0.1], [0, 0, 0], [0.1, 0.1, 0.1], [0.1, 0.1, 0.2],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 0),

    # over box edge
    (
        [0, 0, 0.1], [0, 0, 0], [-0.8, -0.8, -0.8], [-0.6, -0.7, -0.7],
        [[10, 0, 0], [0, 10, 0], [0, 0, 10]], 120),
    # slanted box
    (
        [0, -0.1, 0.1], [0, 0, 0], [0, 0, -0.8], [0.1, 0, -0.7],
        [[10, 0, 0], [10, 10, 0], [10, 10, 10]], 120),
])
def test_dihedral_boxcoords(p0, p1, p2, p3, boxvects, expt):
    p0 = np.array(p0, dtype='float32')
    p1 = np.array(p1, dtype='float32')
    p2 = np.array(p2, dtype='float32')
    p3 = np.array(p3, dtype='float32')
    boxvects = np.array(boxvects, dtype='float32')
    assert round(GM_mf.dihedral_boxcoords(
        p0, p1, p2, p3, boxvects) * GM_con.rad2deg, 4) == expt
    assert round(GM_mf.dihedral_boxcoords.py_func(
        p0, p1, p2, p3, boxvects) * GM_con.rad2deg, 4) == expt
