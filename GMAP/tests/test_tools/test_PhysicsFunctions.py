"""
Tests all the functions/classes/methods in the file:
src/tools/PhysicsFunctions.py.

Missing tests:

(@ apr 29th '24):
92-115, 120-122, 126, 130, 134, 138-146 (26 missed statements)

- [WIP] calc_frame not yet tested  (92-115)
- calc_dipole not yet tested  (120-122)
- [WIP] calc_frequency not yet populated/used  (130)
- [WIP] prep_coupling not yet populated/used  (134)
- [WIP] calc_coupling not yet populated/used  (138)
- generate_output_structures not yet tested (138-146)
"""

# 3rd party imports
import numpy as np

# local imports
from .test_SystemReader import parameter_getter
# import GMAP.src.tools.CLibLoader as GM_CL
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


def test_calc_dipole_xyz():
    cmdline = []
    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter("test_calc_dipoles_xyz", cmdline)

    System = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "Map", mapdict["test_calc_dipoles_xyz"])
    setattr(
        oscillator, "positions_box",
        System.positions[[0, 1]] @ System.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.Map.code.GM_get_rotation_matrix(
            Printer, oscillator.Map, System, oscillator))

    r_vec, r_pos = GM_PF.calc_dipole(Printer, System, oscillator)

    # r_vec base = 0.3, 0.2, 0.1
    # r_vec add: 0.06+0.16+0.3, 0.08+0.2+0.36, 0.1+0.24+0.42
    # r_vec becomes:  0.82, 0.84, 0.86

    r_vec_ans = np.array([0.82, 0.84, 0.86], dtype="float32")
    r_vec_ans = np.dot(r_vec_ans, oscillator.rotation_matrix).round(6)
    print(r_pos)

    assert np.all(r_vec.round(6) == r_vec_ans)
    assert np.all(r_pos.round(4) == np.array([8, 28, -32], dtype="float32"))


def test_calc_dipole_magnitude():
    cmdline = []
    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter("test_calc_dipoles_magnitude", cmdline)

    System = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "Map", mapdict["test_calc_dipoles_magnitude"])
    setattr(
        oscillator, "positions_box",
        System.positions[[0, 1]] @ System.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.Map.code.GM_get_rotation_matrix(
            Printer, oscillator.Map, System, oscillator))

    r_vec, r_pos = GM_PF.calc_dipole(Printer, System, oscillator)

    # r_vec base = 0.3
    # r_vec add: 0.06+0.16+0.3
    # r_vec becomes:  0.82 (this is magnitude)
    # r_vec was 3,3,3, normalizing -> / 5.1961524227066318805823390245176
    # (sqrt 27)
    # 3 / 5.19.... * 0.82 = 0.47...

    r_vec_ans = np.array(
        [0.473427220735493126, 0.473427220735493126, 0.473427220735493126],
        dtype="float32").round(6)

    assert np.all(r_vec.round(6) == r_vec_ans)
    assert np.all(r_pos.round(4) == np.array([8, 28, -32], dtype="float32"))


def get_System_1():
    positions = np.array([
        [8, 28, 68],
        [11, 31, 71],
        [28, 68, 8],
        [31, 71, 11],
        [68, 8, 28],
        [71, 11, 31]
    ], dtype="float32")
    masses = np.array([1, 2, 1, 2, 1, 2], dtype="float32")
    # charges = np.array([1, -1, 0, 1, 0, 0], dtype="float32")
    charges = np.array([1, -1, 1, -1, 1, -1], dtype="float32")
    boxvects = np.array([
            [100, 0, 0],
            [0, 100, 0],
            [0, 0, 100]
    ], dtype="float32")
    boxvects_inv = np.linalg.inv(boxvects).astype("float32")
    res_first_ix = np.array([0, 2, 4], dtype="int32")
    res_last_ix = np.array([1, 3, 5], dtype="int32")
    nres = np.int32(3)
    residues_CoM = GM_PF.system_CoM(
        positions, masses, boxvects_inv, boxvects,
        res_first_ix, res_last_ix, nres
    )
    boxdims = np.array([100, 100, 100], dtype="float32")
    halfbox = np.array([50, 50, 50], dtype="float32")

    return EmptyClass(**{
        "positions": positions,
        "positions_c": np.ctypeslib.as_ctypes(np.ravel(positions)),
        "charges_c": np.ctypeslib.as_ctypes(charges),
        "residues": EmptyClass(**{
            "CoM_c": np.ctypeslib.as_ctypes(np.ravel(residues_CoM)),
            "first_ix_c": np.ctypeslib.as_ctypes(res_first_ix),
            "last_ix_c": np.ctypeslib.as_ctypes(res_last_ix)
        }),
        "nres": nres,
        "halfbox_c": np.ctypeslib.as_ctypes(halfbox),
        "boxdims_c": np.ctypeslib.as_ctypes(boxdims),
        "boxvects": boxvects,
        "boxvects_inv": boxvects_inv
    })


def get_oscillator_1():
    estat_ats = np.array([0, 1], dtype="int32")
    VEG_refpos = np.array([10, 30, 70], dtype="float32")
    VEGout = np.array([[*range(10)]] * 2, dtype="float32")
    VEGout /= 100
    return EmptyClass(**{
        "electrostatic_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_estatic_atoms": np.int32(2),
        "VEG_refpos_c": np.ctypeslib.as_ctypes(VEG_refpos),
        "local_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_local_atoms": np.int32(2),
        "VEGout": VEGout,
        "VEGout_c": np.ctypeslib.as_ctypes(VEGout),
    })
