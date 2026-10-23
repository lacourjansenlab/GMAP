"""
Tests all the functions/classes/methods in the file:
src/tools/default_map_functions.py.

Missing tests:

(@ October 23rd '26):
  (0 missed statements)

"""

# 3rd party imports
import numpy as np
import pytest

# local imports
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.default_map_functions as GM_dmf
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.file_handler as GM_fh
import GMAP.src.tools.map_reader as GM_mr
import GMAP.src.tools.print_tools as GM_pt


def test_get_adjust_run_pars():
    newfunc = GM_dmf.get_adjust_run_pars()
    confirm_does_nothing(newfunc)


def test_get_adjust_map_core_raw():
    newfunc = GM_dmf.get_adjust_map_core_raw()
    confirm_does_nothing(newfunc)


def test_get_adjust_oscillators():
    newfunc = GM_dmf.get_adjust_oscillators()
    confirm_returns_last(newfunc)


def test_filter_single_line():
    map_ = GM_ct.CustomClass(**{
        "name": "mymap",
        "core": GM_ct.CustomClass(**{
            "allow_ranges": GM_mr.SingleCore.allow_ranges
        })})
    system = GM_ct.CustomClass(**{
        "nres": 100,
        "resnums": [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7],
        "resnames": list("AABBCCDDEEFFGGHH")
    })

    oscillators = []
    for i in range(8):
        oscillators.append(GM_ct.CustomClass(**{
            "used_atoms": [i * 2, i * 2 + 1]
        }))

    fullset = set(oscillators)
    first_half = set(oscillators[:4])

    assert GM_dmf.filter_single_line(
        [":All"], "white", first_half, fullset, map_, system) == (
            True, fullset)
    assert GM_dmf.filter_single_line(
        [":All"], "black", first_half, fullset, map_, system) == (
            True, set())
    assert GM_dmf.filter_single_line(
        [":None"], "white", first_half, fullset, map_, system) == (
            True, set())
    assert GM_dmf.filter_single_line(
        [":None"], "black", first_half, fullset, map_, system) == (
            True, first_half)

    assert GM_dmf.filter_single_line(
        ["resnums", "0-3"], "white", set(), fullset, map_, system) == (
            True, first_half)
    assert GM_dmf.filter_single_line(
        ["resnums", "4-7"], "black", fullset, fullset, map_, system) == (
            True, first_half)

    assert GM_dmf.filter_single_line(
        ["resnames", "A", "B", "C", "D"],
        "white", set(), fullset, map_, system) == (
            True, first_half)
    assert GM_dmf.filter_single_line(
        ["resnames", "E", "F", "G", "H"],
        "black", fullset, fullset, map_, system) == (
            True, first_half)

    assert GM_dmf.filter_single_line(
        ["unknown_filter"], "white", first_half, fullset, map_, system) == (
            False, first_half)


def test_get_post_init():
    newfunc = GM_dmf.get_post_init()
    confirm_does_nothing(newfunc)


def test_get_pre_run():
    newfunc = GM_dmf.get_pre_run()
    confirm_does_nothing(newfunc)


def test_get_pre_frame():
    newfunc = GM_dmf.get_pre_frame()
    confirm_does_nothing(newfunc)


def test_get_post_frame():
    newfunc = GM_dmf.get_post_frame()
    confirm_does_nothing(newfunc)


def test_get_post_run():
    newfunc = GM_dmf.get_post_run()
    confirm_does_nothing(newfunc)


def test_get_change_coup_type():
    for desout in [42, "hello", 3.141592]:
        newfunc = GM_dmf.get_change_coup_type(desout)
        confirm_returns_input(newfunc, desout)


def test_prep_coupling():
    newfunc = GM_dmf.get_prep_coupling()
    confirm_does_nothing(newfunc)


def test_get_str_osc():
    newfunc = GM_dmf.get_str_osc()
    osc1 = GM_ct.CustomClass(**{"used_atoms": [0, 1, 2]})
    osc2 = GM_ct.CustomClass(**{"used_atoms": [3, 4, 5]})
    system = GM_ct.CustomClass(**{"resnums": [0, 0, 0, 1, 1, 1]})
    assert newfunc(None, system, osc1) == "living on residue number 0"
    assert newfunc(None, system, osc2) == "living on residue number 1"


def test_report_system():
    newfunc = GM_dmf.get_report_system()
    map_ = GM_ct.CustomClass(**{"name": "A map for testing"})
    system = GM_ct.CustomClass(**{"oscillators_ordered": {
        "A map for testing": [3, 5, 1, 8, 9]}})
    assert newfunc(map_, system) == "A map for testing:       5"


def test_report_references():
    newfunc = GM_dmf.get_report_references()
    map_ = GM_ct.CustomClass(**{"references": "this is a reference"})
    system = GM_ct.CustomClass(**{})
    assert newfunc(map_, system) == "this is a reference"


def test_get_get_VEG_ref():
    VEGref_res = ["residues", "0", "2"]
    map_ = GM_ct.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_res
        }
    })

    mainfunc = GM_dmf.get_get_VEG_ref(map_)
    subfunc = GM_dmf.VEG_from_residues(VEGref_res[1:])
    confirm_funcs_equal(mainfunc, subfunc)

    VEGref_CoM = ["CoM", "0", "2"]
    map_.rawcore["VEG_reference"] = VEGref_CoM
    mainfunc = GM_dmf.get_get_VEG_ref(map_)
    subfunc = GM_dmf.VEG_from_CoM(VEGref_CoM[1:])
    confirm_funcs_equal(mainfunc, subfunc)

    VEGref_pos = ["position", "((((0+1)/2.0)+2)/2.0)"]
    map_.rawcore["VEG_reference"] = VEGref_pos
    mainfunc = GM_dmf.get_get_VEG_ref(map_)
    subfunc = GM_dmf.interpret_position(map_, VEGref_pos[1:], "VEG_reference")
    confirm_funcs_equal(mainfunc, subfunc)


def test_VEG_from_residues():
    VEGref_res = ["residues", "0", "2"]
    map_ = GM_ct.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_res
        }
    })
    subfunc = GM_dmf.VEG_from_residues(["0", "2"])

    system = get_system_VEGtests()
    osc = GM_ct.CustomClass(**{
        "used_atoms": [0, 1, 2, 3]
    })

    out = np.array([1.5, 10, 20])
    assert np.all(subfunc(map_, system, osc) == out)


def test_VEG_from_com():
    VEGref_CoM = ["CoM", "0", "2"]
    map_ = GM_ct.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_CoM
        }
    })

    subfunc = GM_dmf.VEG_from_CoM(["0", "2"])

    system = get_system_VEGtests()
    osc = GM_ct.CustomClass(**{
        "used_atoms": [0, 1, 2, 3]
    })

    out = np.array([1, 10, 20])
    assert np.all(subfunc(map_, system, osc) == out)


def test_interpret_position():
    VEGref_pos = ["position", "((((0+1)/2.0)+2)/2.0)"]
    map_ = GM_ct.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_pos
        }
    })
    subfunc = GM_dmf.interpret_position(map_, VEGref_pos[1:], "VEG_reference")

    system = get_system_VEGtests()
    osc = GM_ct.CustomClass(**{
        "used_atoms": [0, 1, 2, 3]
    })
    osc.positions_box = (
            system.positions[osc.used_atoms] @ system.boxvects_inv)

    out = np.array([1.25, 10, 20])
    assert np.all(subfunc(map_, system, osc) == out)


def test_MI_MC_9(capsys):
    # too few opening brackets (should be 4 instead of two)
    VEGref_pos = ["position", "((0+1)/2.0)+2)/2.0)"]

    map_ = GM_ct.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_pos
        },
        "directory": GM_fh.FileLocations.cwd
    })
    _ = GM_dmf.interpret_position(map_, VEGref_pos[1:], "VEG_reference")
    GM_pt.Printer.print_backlog()
    captured = capsys.readouterr()
    assert captured.out.endswith("MI_MC_9\n")


def test_SU_NP_8(capsys):
    map_ = GM_ct.CustomClass(**{
        "name": "mymap",
        "core": GM_ct.CustomClass(**{
            "allow_ranges": GM_mr.SingleCore.allow_ranges}),
        "run_pars": GM_ct.CustomClass(**{
            "main_run_pars": GM_ct.CustomClass(**{
                "singles_whitelist_dict": {"mymap": [[":All"]]},
                "singles_blacklist_dict": {"mymap": [[":None"]]}})})
    })
    system = GM_ct.CustomClass(**{
        "nres": 100})
    oscillators = []
    for i in range(8):
        oscillators.append(GM_ct.CustomClass(**{
            "used_atoms": [i * 2, i * 2 + 1]
        }))

    func = GM_dmf.get_filter_oscillators()

    map_.run_pars.main_run_pars.singles_whitelist_dict["mymap"] = [["unknown"]]
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_8$"):
        func(map_, system, oscillators)
    map_.run_pars.main_run_pars.singles_whitelist_dict["mymap"] = [[":All"]]

    map_.run_pars.main_run_pars.singles_blacklist_dict["mymap"] = [["unknown"]]
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_8$"):
        func(map_, system, oscillators)
    map_.run_pars.main_run_pars.singles_blacklist_dict["mymap"] = [[":None"]]

    # ----------------
    # errors in filter_single_line()

    # Trigger the first error (non-ints in input)
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_8$"):
        _ = GM_dmf.filter_single_line(
            ["resnums", "not", "a", "number"], "white", set(), set("hello"),
            map_, system)

    with pytest.raises(GM_ex.GmapIndexError, match="SU_NP_8$"):
        _ = GM_dmf.filter_single_line(
            ["resnums", "102"], "white", set(), set("hello"), map_, system)

    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_8$"):
        _ = GM_dmf.filter_single_line(
            ["resnums", "5-7-3"], "white", set(), set("hello"), map_, system)


# ==================================================


def confirm_does_nothing(func):
    strarg = "hello"
    intarg = 42
    floatarg = 3.141592
    boolarg = False
    listarg = [1, 2.3, "four"]
    dictarg = {"one": 1, "two": 2}

    out = func(strarg, boolarg, dictarg)
    assert out is None
    assert dictarg == {"one": 1, "two": 2}

    out = func(intarg)
    assert out is None

    out = func(floatarg, listarg)
    assert out is None
    assert listarg == [1, 2.3, "four"]

    out = func()
    assert out is None


def confirm_returns_last(func):
    strarg = "hello"
    intarg = 42
    floatarg = 3.141592
    boolarg = False
    listarg = [1, 2.3, "four"]
    dictarg = {"one": 1, "two": 2}

    out = func(boolarg, dictarg, strarg)
    assert out == "hello"
    assert dictarg == {"one": 1, "two": 2}

    out = func(intarg)
    assert out == 42

    out = func(listarg, floatarg)
    assert out == 3.141592
    assert listarg == [1, 2.3, "four"]


def confirm_returns_input(func, desout):
    strarg = "hello"
    intarg = 42
    floatarg = 3.141592
    boolarg = False
    listarg = [1, 2.3, "four"]
    dictarg = {"one": 1, "two": 2}

    out = func(boolarg, dictarg, strarg)
    assert out == desout
    assert dictarg == {"one": 1, "two": 2}

    out = func(intarg)
    assert out == desout

    out = func(listarg, floatarg)
    assert out == desout
    assert listarg == [1, 2.3, "four"]

    out = func()
    assert out == desout


def confirm_funcs_equal(funcA, funcB):
    # see if equal code
    # lambda x: x == lambda y: y  -> True
    # lambda x: x+1 == lambda x: x+2 -> True
    # lambda x: x+1 == lambda x: x-1 -> False
    assert funcA.__code__.co_code == funcB.__code__.co_code

    # see if equal constants
    # lambda x: x == lambda y: y  -> True
    # lambda x: x+1 == lambda x: x+2 -> False
    # lambda x: x+1 == lambda x: x-1 -> True
    assert funcA.__code__.co_consts == funcB.__code__.co_consts


def get_system_VEGtests():
    system = GM_ct.CustomClass(**{
        "residues": GM_ct.CustomClass(**{
            "first_ix": [0, 2, 4, 6],
            "last_ix": [1, 3, 5, 7]
        }),
        "resnums": np.array([0, 0, 1, 1, 2, 2, 3, 3]),
        "masses": np.array([1]*8),
        "boxvects": np.array([[100, 0, 0], [0, 100, 0], [0, 0, 100]]),
        "boxvects_inv": np.array([[0.01, 0, 0], [0, 0.01, 0], [0, 0, 0.01]]),
        "positions": np.array([
            [1, 10, 10],
            [2, 10, 10],
            [1, 10, 30],
            [2, 10, 30],
            [1, 30, 10],
            [2, 30, 10],
            [1, 30, 30],
            [2, 30, 30]
        ])
    })
    return system


# just for coverage....
def test_unused():
    assert GM_dmf.unused_user() is None
