"""
Tests all the functions/classes/methods in the file:
src/tools/PhysicsFunctions.py.

Missing tests:

(@ apr 29th '24):
93-122, 126, 130, 134, 138 (23 missed statements)

- [WIP] calc_frame not yet tested  (93-122)
- [WIP] calc_dipole not yet populated/used  (126)
- [WIP] calc_frequency not yet populated/used  (130)
- [WIP] prep_coupling not yet populated/used  (134)
- [WIP] calc_coupling not yet populated/used  (138)
"""

# 3rd party imports
import numpy as np

# local imports
from GMAP.src.tools import PhysicsFunctions as GM_PF


class EmptyClass:
    def __init__(self, **kwargs):
        for parname, val in kwargs.items():
            setattr(self, parname, val)
        return


def test_calc_CoM():
    System = EmptyClass(**{
        "positions": np.array([
            [40, 10, 30],
            [42, 8, 29],
            [35, 14, 27],
            [38, 12, 28]
        ], dtype="float32"),
        "masses": np.array([8, 9, 10, 11], dtype="float32"),  # sum = 38
        "boxvects": np.array([
            [100, 0, 0],
            [0, 100, 0],
            [0, 0, 100]
        ], dtype="float32")
    })

    setattr(
        System, "boxvects_inv",
        np.linalg.inv(System.boxvects).astype("float32")
    )

    atlist = [0, 1, 2, 3]

    ans = np.array(
        [38.5789473, 11.1578947, 28.3947368], dtype="float32").round(4)

    assert np.all(GM_PF.calc_CoM(System, atlist).round(4) == ans)


def test_system_CoM():
    positions = np.array([
        [8, 28, 68],
        [11, 31, 71],
        [28, 68, 8],
        [31, 71, 11],
        [68, 8, 28],
        [71, 11, 31]
    ], dtype="float32")
    masses = np.array([1, 2, 1, 2, 1, 2], dtype="float32")
    boxvects = np.array([
            [100, 0, 0],
            [0, 100, 0],
            [0, 0, 100]
    ], dtype="float32")
    boxvects_inv = np.linalg.inv(boxvects).astype("float32")
    res_first_ix = np.array([0, 2, 4], dtype="int32")
    res_last_ix = np.array([1, 3, 5], dtype="int32")
    nres = np.int32(3)

    ans = np.array([
        [10, 30, -30],
        [30, -30, 10],
        [-30, 10, 30]
    ], dtype="float32")

    assert np.all(GM_PF.system_CoM(
        positions, masses, boxvects_inv, boxvects,
        res_first_ix, res_last_ix, nres
    ).round(4) == ans)
    assert np.all(GM_PF.system_CoM.py_func(
        positions, masses, boxvects_inv, boxvects,
        res_first_ix, res_last_ix, nres
    ).round(4) == ans)
