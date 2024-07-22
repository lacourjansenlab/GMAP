"""
Tests all the functions/classes/methods in the file:
src/tools/PhysicsFunctions.py.

Missing tests:

(@ July 22nd '24):
110-146, 287-299  (29 missed statements)

- [WIP] calc_frame not yet tested  (110-146)
- generate_output_structures not yet tested (287-299)
"""

# standard lib imports
from pathlib import Path

# 3rd party imports
import numpy as np

# local imports
from .test_SystemReader import parameter_getter
from . import test_MapReader as tMR
# import GMAP.src.tools.CLibLoader as GM_CL
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.PhysicsFunctions as GM_PF


def test_calc_CoM():
    System = GM_CT.CustomClass(**{
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
    cmdline = ["--verbose", "4"]
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict, pairs_mapdict
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
            oscillator.Map, System, oscillator))

    r_vec, r_pos = GM_PF.calc_dipole(System, oscillator)

    # r_vec base = 0.3, 0.2, 0.1
    # r_vec add: 0.06+0.16+0.3, 0.08+0.2+0.36, 0.1+0.24+0.42
    # r_vec becomes:  0.82, 0.84, 0.86

    r_vec_ans = np.array([0.82, 0.84, 0.86], dtype="float32")
    r_vec_ans = np.dot(r_vec_ans, oscillator.rotation_matrix).round(6)
    # GM_PT.Printer().print(0, r_vec_ans)
    # GM_PT.Printer().print(0, r_vec)
    # GM_PT.Printer().print(0, r_pos)

    assert np.all(r_vec.round(6) == r_vec_ans)
    assert np.all(r_pos.round(4) == np.array([8, 28, -32], dtype="float32"))


def test_calc_dipole_magnitude():
    cmdline = []
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict, pairs_mapdict
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
            oscillator.Map, System, oscillator))

    r_vec, r_pos = GM_PF.calc_dipole(System, oscillator)

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


def test_calc_frequency():
    cmdline = []
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict, pairs_mapdict
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
            oscillator.Map, System, oscillator))

    freq = GM_PF.calc_frequency(System, oscillator)

    # freq_gas = 1200
    # VEGout = 0, 0.01, 0.02 ... 0.09, for each atom
    # freq += 0*0 + 0.01*1 + 0.02*2 + 0.03*3 + 0*4 + 0.01*5 + 0.02*6 + 0.03*7
    #       = 1200 + 0 + 0.01 + 0.04 + 0.09 + 0 + 0.05 + 0.12 + 0.21
    #       = 1200 + 0.14 + 0.38  = 1200.52

    assert freq == np.float32(1200.52)

    # -----------------------------------------------------------------
    # quad

    cmdline = []
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_freq_quad", cmdline)

    System = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "Map", mapdict["test_calc_freq_quad"])
    setattr(
        oscillator, "positions_box",
        System.positions[[0, 1]] @ System.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.Map.code.GM_get_rotation_matrix(
            oscillator.Map, System, oscillator))

    freq = GM_PF.calc_frequency(System, oscillator)

    # freq_gas = 1200
    # VEGout = 0, 0.01, 0.02 ... 0.09, for each atom
    # VEGout^2 = 0, 0.0001, 0.0004, 0.0009, etc
    # freq = 1200 + 0*0 + 0.0001*1 + 0.0004*2 + 0.0009*3
    #        + 0*4 + 0.0001*5 + 0.0004*6 + 0.0009*7
    #      = 1200 + 0 + 0.0001 + 0.0008 + 0.0027
    #        + 0 + 0.0005 + 0.0024 + 0.0063
    #      = 1200 + 0.0036 + 0.0092
    #      = 1200.0128

    assert freq == np.float32(1200.0128)

    # -----------------------------------------------------------------
    # lin and quad

    cmdline = []
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_freq_linquad", cmdline)

    System = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "Map", mapdict["test_calc_freq_linquad"])
    setattr(
        oscillator, "positions_box",
        System.positions[[0, 1]] @ System.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.Map.code.GM_get_rotation_matrix(
            oscillator.Map, System, oscillator))

    freq = GM_PF.calc_frequency(System, oscillator)
    # freq += 0*0 + 0.01*1 + 0.02*2 + 0.03*3 + 0*4 + 0.01*5 + 0.02*6 + 0.03*7
    #       = 1200 + 0 + 0.01 + 0.04 + 0.09 + 0 + 0.05 + 0.12 + 0.21
    #       = 1200 + 0.14 + 0.38  = 1200.52

    # freq_gas = 1200
    # VEGout = 0, 0.01, 0.02 ... 0.09, for each atom
    # VEGout^2 = 0, 0.0001, 0.0004, 0.0009, etc
    # freq = 1200
    #        + 0*0 + 0.01*1 + 0.02*2 + 0.03*3 + 0*4 + 0.01*5 + 0.02*6 + 0.03*7
    #        + 0*0 + 0.0001*1 + 0.0004*2 + 0.0009*3
    #        + 0*4 + 0.0001*5 + 0.0004*6 + 0.0009*7
    #      = 1200
    #        + 0 + 0.01 + 0.04 + 0.09 + 0 + 0.05 + 0.12 + 0.21
    #        + 0 + 0.0001 + 0.0008 + 0.0027
    #        + 0 + 0.0005 + 0.0024 + 0.0063
    #      = 1200 + 0.14 + 0.38 + 0.0036 + 0.0092
    #      = 1200.5328

    assert freq == np.float32(1200.5328)


def test_prep_coupling():
    RunPars, System, coupmap = prep_coupling_tests()
    GM_PF.prep_coupling(RunPars, System)

    # the prepared r_vec should be the same as the one calculated by
    # (test)_calc_dipole(_magnitude)
    r_vec_ans = np.array(
        [0.473427220735493126, 0.473427220735493126, 0.473427220735493126],
        dtype="float32").round(6)
    assert np.all(coupmap.dipole_vec_arr[0].round(6) == r_vec_ans)
    assert np.all(coupmap.dipole_vec_arr[1].round(6) == r_vec_ans)

    # The position should be the same, too, but now in box coords
    assert np.all(coupmap.dipole_pos_arr[0].round(4) == np.array(
        [0.08, 0.28, -0.32], dtype="float32"))
    assert np.all(coupmap.dipole_pos_arr[1].round(4) == np.array(
        [0.28, -0.32, 0.08], dtype="float32"))


def test_calc_coupling():
    RunPars, System, coupmap = prep_coupling_tests()
    GM_PF.prep_coupling(RunPars, System)

    # osclist = System.oscillators_ordered_coup["DipDip"]
    oscixlist = System.oscillators_ordered_coup_ix["DipDip"]
    coupmap.allpairs = [(oscixlist[0], oscixlist[1])]
    outputs = {"hamiltonian": np.zeros((2, 2), dtype="float32")}
    GM_PF.calc_coupling(RunPars, System, outputs)
    J = outputs["hamiltonian"][1, 0]

    # d = r(1) - r(2) = (8,28,68) - (28,68,8) = (-20, -40, -40) (PBC!)
    # ir = 1/dot(d,d) = sqrt(1/3600) = 60
    # fourPiEps_inv = 5034.11656
    # J = 4PiEpsinv * dot(v1, v2)*ir3 - 3*dot(v1,d))*dot(v2,d)*ir5
    # J = 4PiEpsinv * 3*0.4734...^2/60^3 - 3*100*0.4734...*100*0.4734.../60^5
    # J = 4PiEpsinv * 3.1129629629629629511601e-6 - 8.6471193415637859754448e-6
    # J = 4PiEpsinv * -5.534156378600825e-6
    # J = 5034.11656 * -0.000005534156378600825
    # J = -0.0278595882711440427
    assert round(J, 6) == round(outputs["hamiltonian"][0, 1], 6)
    assert round(J, 6) == round(np.float32(-0.0278595882711440427), 6)


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

    return GM_CT.CustomClass(**{
        "positions": positions,
        "positions_c": np.ctypeslib.as_ctypes(np.ravel(positions)),
        "charges_c": np.ctypeslib.as_ctypes(charges),
        "residues": GM_CT.CustomClass(**{
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
    return GM_CT.CustomClass(**{
        "electrostatic_atoms": estat_ats,
        "electrostatic_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_estatic_atoms": np.int32(2),
        "VEG_refpos_c": np.ctypeslib.as_ctypes(VEG_refpos),
        "local_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_local_atoms": np.int32(2),
        "VEGout": VEGout,
        "VEGout_c": np.ctypeslib.as_ctypes(VEGout),
    })


def get_oscillator_2():
    estat_ats = np.array([2, 3], dtype="int32")
    VEG_refpos = np.array([30, 70, 10], dtype="float32")
    VEGout = np.array([[*range(10)]] * 2, dtype="float32")
    VEGout /= 100
    return GM_CT.CustomClass(**{
        "electrostatic_atoms": estat_ats,
        "electrostatic_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_estatic_atoms": np.int32(2),
        "VEG_refpos_c": np.ctypeslib.as_ctypes(VEG_refpos),
        "local_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_local_atoms": np.int32(2),
        "VEGout": VEGout,
        "VEGout_c": np.ctypeslib.as_ctypes(VEGout),
    })


def prep_coupling_tests():
    cmdline = []
    inpardict = {
        "map_directory": [
            Path("../../maps"),
            Path("Data/maps_for_test_MapReader_1")
        ],
        "maps_to_use": ["test_calc_dipoles_magnitude"],  # in data/testMR maps
        "couplings_to_use": [["DipDip", ":All"]]  # in 'main' maps
    }
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, singles_mapdict, pairs_mapdict
    ) = tMR.basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_MR.manage_maps_singles(Files, RunPars, singles_mapdict)
    oscillators = [get_oscillator_1(), get_oscillator_2()]
    for oscillator in oscillators:
        # assign map to the oscillators
        setattr(
            oscillator, "Map", singles_mapdict["test_calc_dipoles_magnitude"])

    GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)

    System = get_System_1()

    for oscillator in oscillators:
        # assign the positions to the oscillator
        setattr(
            oscillator, "positions_box",
            System.positions[
                oscillator.electrostatic_atoms] @ System.boxvects_inv)

        # assign the correct rotation matrix to the oscillator
        setattr(
            oscillator, "rotation_matrix",
            oscillator.Map.code.GM_get_rotation_matrix(
                oscillator.Map, System, oscillator))

        GM_PF.calc_dipole(System, oscillator)

    setattr(System, "oscillators_ordered_coup", {
        "DipDip": oscillators})
    setattr(System, "oscillators_ordered_coup_ix", {
        "DipDip": [0, 1]})
    setattr(System, "nosc", len(oscillators))

    coupmap = RunPars.requested_pairmapdict["DipDip"]
    coupmap.code.GM_pre_run(coupmap, System)

    return RunPars, System, coupmap
