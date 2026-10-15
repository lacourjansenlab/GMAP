"""
Tests all the functions/classes/methods in the file:
src/tools/physics_functions.py.

Missing tests:

(@ September 20th '24):
111-168, 250-251  (37 missed statements)

- [WIP] calc_frame not yet tested  (111-165)
- calc_raman not yet tested (as so custom) (250-251)

"""

# standard lib imports
from pathlib import Path

# 3rd party imports
import numpy as np
import pytest

# local imports
from .test_system_reader import parameter_getter
from . import test_map_reader as tmr
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.map_reader as GM_mr
import GMAP.src.tools.physics_functions as GM_pf


def test_calc_CoM():
    system = GM_ct.CustomClass(**{
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
        system, "boxvects_inv",
        np.linalg.inv(system.boxvects).astype("float32")
    )

    atlist = [0, 1, 2, 3]

    ans = np.array(
        [38.5789473, 11.1578947, 28.3947368], dtype="float32").round(4)

    assert np.all(GM_pf.calc_CoM(system, atlist).round(4) == ans)

    # ------------------------------------------------------------------

    system = GM_ct.CustomClass(**{
        "positions": np.array([
            [80, 92, 76],
            [12, 16, 4],
            [96, 96, 96],
            [10, 10, 10]
        ], dtype="float32"),
        "masses": np.array([1, 2, 1, 1], dtype="float32"),  # sum = 38
        "boxvects": np.array([
            [100, 0, 0],
            [0, 100, 0],
            [0, 0, 100]
        ], dtype="float32")
    })

    setattr(
        system, "boxvects_inv",
        np.linalg.inv(system.boxvects).astype("float32")
    )

    atlist = [0, 1, 2, 3]

    ans = np.array(
        [2, 6, -2], dtype="float32").round(4)

    assert np.all(GM_pf.calc_CoM(system, atlist).round(4) == ans)

    # ------------------------------------------------------------------

    system = GM_ct.CustomClass(**{
        # before moving all into (1, 1, 1) box
        # 55, 110, 95 (close to Y edge on 'top' (max Z) surface)
        # 55, 110, 105 (still within in Y dir, outside in Z dir)
        # 45, 110, 95 (Over Y edge (too small x coord to be in box))
        # 45, 110, 105 (too small x, too large z)
        # avg (weights 1,2,3,4) -> 48, 110, 101

        # moving it into box (all in 0-1 boxcoord range):
        # 55, 110, 95 -> 0.064, 0.53, 0.95 -> no translation
        # 55, 110, 105 -> 0.036, 0.47, 1.05 -> 15 50 5
        # 45, 110, 95 -> -0.036, 0.53, 0.95 -> 145, 110, 95
        # 45, 110, 105 -> -0.064, 0.47, 1.05 -> 105 50 5
        # avg: 48, 110, 101 -> -0.0228, 0.494, 1.01 -> 8 50 1
        # (avg is shifted to -0.5, 0.5, as answer will be, too)
        "positions": np.array([
            [55, 110, 95],
            [15, 50, 5],
            [145, 110, 95],
            [105, 50, 5]
        ], dtype="float32"),
        "masses": np.array([1, 2, 3, 4], dtype="float32"),
        # top view:
        #               20    ____________
        #               |    /(top layer)/
        #   100   _     ____/_______    /
        #    60   _    /   /_______/___/
        #             /  (bottom) /
        #     0   _  /___________/
        #             |  |  |     |
        #             0  20  40   100
        "boxvects": np.array([
            [100, 0, 0],
            [20, 100, 0],
            [40, 60, 100]
        ], dtype="float32")
    })

    setattr(
        system, "boxvects_inv",
        np.linalg.inv(system.boxvects).astype("float32")
    )

    atlist = [0, 1, 2, 3]

    ans = np.array(
        [8, 50, 1], dtype="float32").round(4)

    assert np.all(GM_pf.calc_CoM(system, atlist).round(4) == ans)


# numba 0.61.2 errors on WIN11, but only when running ALL tests.
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

    assert np.all(GM_pf.system_CoM(
        positions, masses, boxvects_inv, boxvects,
        res_first_ix, res_last_ix, nres
    ).round(4) == ans)
    assert np.all(GM_pf.system_CoM.py_func(
        positions, masses, boxvects_inv, boxvects,
        res_first_ix, res_last_ix, nres
    ).round(4) == ans)


@pytest.mark.parametrize("center,pos,dbp", [
    ([0, 0, 0], [28, -32, 8], [[31, -29, 11], [11, 31, -29]]),
    ([0.5, 0.5, 0.5], [28, 68, 8], [[31, 71, 11], [11, 31, 71]]),
    ([0.2, 0.2, 0.2], [28, 68, 8], [[31, -29, 11], [11, 31, -29]])])
def test_get_positions(center, pos, dbp):
    # position = [28, 68, 8]
    # dbp = [31, 71, 11], [11, 31, 71]
    # boxsize = [100, 100, 100]

    psstring = " ".join([str(item) for item in center])
    cmdline = [
        "--verbose", "4", "--positions_center", f"{psstring}\\;"]
    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_dipoles_xyz", cmdline)
    # position - 2,  db0 - 3, db1 - 1

    system = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "map", mapdict["test_calc_dipoles_xyz"])
    setattr(
        oscillator, "positions_box",
        system.positions[0:4] @ system.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.map.code.GM_get_rotation_matrix(
            oscillator.map, system, oscillator))

    pos = GM_pf.get_positions(system, oscillator)
    assert np.all(pos.round(4) == np.array(pos, dtype="float32").round(4))
    dbp = GM_pf.get_doublepos(system, oscillator)
    assert np.all(np.array(dbp).round(4) == np.array(
        dbp, dtype="float32").round(4))

    # positions = np.array([
    #     [8, 28, 68],
    #     [11, 31, 71],
    #     [28, 68, 8],
    #     [31, 71, 11],
    #     [68, 8, 28],
    #     [71, 11, 31]
    # ]


def test_calc_dipole_xyz():
    cmdline = ["--verbose", "4"]
    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_dipoles_xyz", cmdline)

    system = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "map", mapdict["test_calc_dipoles_xyz"])
    setattr(
        oscillator, "positions_box",
        system.positions[[0, 1]] @ system.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.map.code.GM_get_rotation_matrix(
            oscillator.map, system, oscillator))

    r_vec, r_pos = GM_pf.calc_dipole(system, oscillator)

    # r_vec base = 0.3, 0.2, 0.1
    # r_vec add: 0.06+0.16+0.3, 0.08+0.2+0.36, 0.1+0.24+0.42
    # r_vec becomes:  0.82, 0.84, 0.86

    r_vec_ans = np.array([0.82, 0.84, 0.86], dtype="float32")
    r_vec_ans = np.dot(r_vec_ans, oscillator.rotation_matrix).round(6)
    # GM_pt.Printer.print(0, r_vec_ans)
    # GM_pt.Printer.print(0, r_vec)
    # GM_pt.Printer.print(0, r_pos)

    assert np.all(r_vec.round(6) == r_vec_ans)
    assert np.all(r_pos.round(4) == np.array([8, 28, -32], dtype="float32"))


def test_calc_dipole_magnitude():
    cmdline = []
    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_dipoles_magnitude", cmdline)

    system = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "map", mapdict["test_calc_dipoles_magnitude"])
    setattr(
        oscillator, "positions_box",
        system.positions[[0, 1]] @ system.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.map.code.GM_get_rotation_matrix(
            oscillator.map, system, oscillator))

    r_vec, r_pos = GM_pf.calc_dipole(system, oscillator)

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
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_dipoles_magnitude", cmdline)

    system = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "map", mapdict["test_calc_dipoles_magnitude"])
    setattr(
        oscillator, "positions_box",
        system.positions[[0, 1]] @ system.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.map.code.GM_get_rotation_matrix(
            oscillator.map, system, oscillator))

    freq = GM_pf.calc_frequency(system, oscillator)

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
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_freq_quad", cmdline)

    system = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "map", mapdict["test_calc_freq_quad"])
    setattr(
        oscillator, "positions_box",
        system.positions[[0, 1]] @ system.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.map.code.GM_get_rotation_matrix(
            oscillator.map, system, oscillator))

    freq = GM_pf.calc_frequency(system, oscillator)

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
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter("test_calc_freq_linquad", cmdline)

    system = get_System_1()
    oscillator = get_oscillator_1()
    setattr(oscillator, "map", mapdict["test_calc_freq_linquad"])
    setattr(
        oscillator, "positions_box",
        system.positions[[0, 1]] @ system.boxvects_inv)

    setattr(
        oscillator, "rotation_matrix",
        oscillator.map.code.GM_get_rotation_matrix(
            oscillator.map, system, oscillator))

    freq = GM_pf.calc_frequency(system, oscillator)
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
    run_pars, system, coupmap = prep_coupling_tests()
    GM_pf.prep_coupling(run_pars, system)

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
    run_pars, system, coupmap = prep_coupling_tests()
    GM_pf.prep_coupling(run_pars, system)

    # osclist = system.oscillators_ordered_coup["DipDip"]
    oscixlist = system.oscillators_ordered_coup_ix["DipDip"]
    coupmap.allpairs = np.array([(oscixlist[0], oscixlist[1])], dtype="int32")
    outputs = {"hamiltonian": np.zeros((2, 2), dtype="float32")}
    GM_pf.calc_coupling(run_pars, system, outputs)
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


def test_generate_output_structures():
    system = GM_ct.CustomClass(**{"nosc": 5})

    runpars = GM_ct.CustomClass(**{"output_data": ["ham"]})
    out = GM_pf.generate_output_structures(runpars, system)
    assert [*out.keys()] == ["hamiltonian", "dipole_pos", "dipoles"]

    runpars = GM_ct.CustomClass(**{"output_data": ["ene"]})
    out = GM_pf.generate_output_structures(runpars, system)
    assert [*out.keys()] == ["energies"]

    runpars = GM_ct.CustomClass(**{"output_data": ["dip"]})
    out = GM_pf.generate_output_structures(runpars, system)
    assert [*out.keys()] == ["dipoles"]

    runpars = GM_ct.CustomClass(**{"output_data": ["ram"]})
    out = GM_pf.generate_output_structures(runpars, system)
    assert [*out.keys()] == ["raman"]

    runpars = GM_ct.CustomClass(**{"output_data": ["pos"]})
    out = GM_pf.generate_output_structures(runpars, system)
    assert [*out.keys()] == ["positions"]

    runpars = GM_ct.CustomClass(**{"output_data": ["dbp"]})
    out = GM_pf.generate_output_structures(runpars, system)
    assert [*out.keys()] == ["doublepos"]

    runpars = GM_ct.CustomClass(**{"output_data": [
        "ham", "ene", "dip", "ram", "pos", "dbp"]})
    out = GM_pf.generate_output_structures(runpars, system)

    assert out["hamiltonian"].shape == (5, 5)
    assert out["hamiltonian"].dtype == np.float32
    assert out["energies"].shape == (5,)
    assert out["energies"].dtype == np.float32
    assert out["dipole_pos"].shape == (5, 3)
    assert out["dipole_pos"].dtype == np.float32
    assert out["dipoles"].shape == (5, 3)
    assert out["dipoles"].dtype == np.float32
    assert out["raman"].shape == (5, 6)
    assert out["raman"].dtype == np.float32
    assert out["positions"].shape == (5, 3)
    assert out["positions"].dtype == np.float32
    assert out["doublepos"].shape == (10, 3)
    assert out["doublepos"].dtype == np.float32


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
    residues_CoM = GM_pf.system_CoM(
        positions, masses, boxvects_inv, boxvects,
        res_first_ix, res_last_ix, nres
    )
    boxdims = np.array([100, 100, 100], dtype="float32")
    halfbox = np.array([50, 50, 50], dtype="float32")

    return GM_ct.CustomClass(**{
        "positions": positions,
        "positions_c": np.ctypeslib.as_ctypes(np.ravel(positions)),
        "charges_c": np.ctypeslib.as_ctypes(charges),
        "residues": GM_ct.CustomClass(**{
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
    return GM_ct.CustomClass(**{
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
    return GM_ct.CustomClass(**{
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
            Path("Data/maps_for_test_map_reader_1")
        ],
        "maps_to_use": ["test_calc_dipoles_magnitude"],  # in data/testMR maps
        "couplings_to_use": [["DipDip", ":All"]]  # in 'main' maps
    }
    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, singles_mapdict, pairs_mapdict
    ) = tmr.basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_mr.manage_maps_singles(run_pars, singles_mapdict)
    oscillators = [get_oscillator_1(), get_oscillator_2()]
    for oscillator in oscillators:
        # assign map to the oscillators
        setattr(
            oscillator, "map", singles_mapdict["test_calc_dipoles_magnitude"])

    GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)
    run_pars.final_resolve_coupling_scale()

    system = get_System_1()

    for oscillator in oscillators:
        # assign the positions to the oscillator
        setattr(
            oscillator, "positions_box",
            system.positions[
                oscillator.electrostatic_atoms] @ system.boxvects_inv)

        # assign the correct rotation matrix to the oscillator
        setattr(
            oscillator, "rotation_matrix",
            oscillator.map.code.GM_get_rotation_matrix(
                oscillator.map, system, oscillator))

        GM_pf.calc_dipole(system, oscillator)

    setattr(system, "oscillators_ordered_coup", {
        "DipDip": oscillators})
    setattr(system, "oscillators_ordered_coup_ix", {
        "DipDip": [0, 1]})
    setattr(system, "nosc", len(oscillators))

    coupmap = run_pars.requested_pairmapdict["DipDip"]
    coupmap.code.GM_pre_run(coupmap, system)

    return run_pars, system, coupmap
