"""
Tests all the functions/classes/methods in the file:
src/tools/DefaultMapFunctions.py.

Missing tests:

(@ August 2nd '24):
  (0 missed statements)

"""

# 3rd party imports
import numpy as np

# local imports
import GMAP.src.tools.DefaultMapFunctions as GM_DMF
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT


def test_get_adjust_RunPars():
    newfunc = GM_DMF.get_adjust_RunPars()
    confirm_does_nothing(newfunc)


def test_get_adjust_map_core_raw():
    newfunc = GM_DMF.get_adjust_map_core_raw()
    confirm_does_nothing(newfunc)


def test_get_adjust_oscillators():
    newfunc = GM_DMF.get_adjust_oscillators()
    confirm_returns_last(newfunc)


def test_get_post_init():
    newfunc = GM_DMF.get_post_init()
    confirm_does_nothing(newfunc)


def test_get_pre_run():
    newfunc = GM_DMF.get_pre_run()
    confirm_does_nothing(newfunc)


def test_get_pre_frame():
    newfunc = GM_DMF.get_pre_frame()
    confirm_does_nothing(newfunc)


def test_get_post_frame():
    newfunc = GM_DMF.get_post_frame()
    confirm_does_nothing(newfunc)


def test_get_post_run():
    newfunc = GM_DMF.get_post_run()
    confirm_does_nothing(newfunc)


def test_get_change_coup_type():
    for desout in [42, "hello", 3.141592]:
        newfunc = GM_DMF.get_change_coup_type(desout)
        confirm_returns_input(newfunc, desout)


def test_prep_coupling():
    newfunc = GM_DMF.get_prep_coupling()
    confirm_does_nothing(newfunc)


def test_get_str_osc():
    newfunc = GM_DMF.get_str_osc()
    osc1 = GM_CT.CustomClass(**{"used_atoms": [0, 1, 2]})
    osc2 = GM_CT.CustomClass(**{"used_atoms": [3, 4, 5]})
    Syst = GM_CT.CustomClass(**{"resnums": [0, 0, 0, 1, 1, 1]})
    assert newfunc(Syst, None, osc1) == "living on residue number 0"
    assert newfunc(Syst, None, osc2) == "living on residue number 1"


def test_get_get_VEG_ref():
    VEGref_res = ["residues", "0", "2"]
    map_ = GM_CT.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_res
        }
    })
    _ = GM_FH.FileLocations()  # still needed for initialization

    mainfunc = GM_DMF.get_get_VEG_ref(map_)
    subfunc = GM_DMF.VEG_from_residues(VEGref_res[1:])
    confirm_funcs_equal(mainfunc, subfunc)

    VEGref_CoM = ["CoM", "0", "2"]
    map_.rawcore["VEG_reference"] = VEGref_CoM
    mainfunc = GM_DMF.get_get_VEG_ref(map_)
    subfunc = GM_DMF.VEG_from_com(VEGref_CoM[1:])
    confirm_funcs_equal(mainfunc, subfunc)

    VEGref_pos = ["position", "((((0+1)/2.0)+2)/2.0)"]
    map_.rawcore["VEG_reference"] = VEGref_pos
    mainfunc = GM_DMF.get_get_VEG_ref(map_)
    subfunc = GM_DMF.interpret_position(map_, VEGref_pos[1:], "VEG_reference")
    confirm_funcs_equal(mainfunc, subfunc)


def test_VEG_from_residues():
    VEGref_res = ["residues", "0", "2"]
    map_ = GM_CT.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_res
        }
    })
    _ = GM_FH.FileLocations()  # still needed for initialization
    subfunc = GM_DMF.VEG_from_residues(["0", "2"])

    Syst = get_syst_VEGtests()
    osc = GM_CT.CustomClass(**{
        "used_atoms": [0, 1, 2, 3]
    })

    out = np.array([1.5, 10, 20])
    assert np.all(subfunc(map_, Syst, osc) == out)


def test_VEG_from_com():
    VEGref_CoM = ["CoM", "0", "2"]
    map_ = GM_CT.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_CoM
        }
    })
    _ = GM_FH.FileLocations()  # still needed for initialization

    subfunc = GM_DMF.VEG_from_com(["0", "2"])

    Syst = get_syst_VEGtests()
    osc = GM_CT.CustomClass(**{
        "used_atoms": [0, 1, 2, 3]
    })

    out = np.array([1, 10, 20])
    assert np.all(subfunc(map_, Syst, osc) == out)


def test_interpret_position():
    VEGref_pos = ["position", "((((0+1)/2.0)+2)/2.0)"]
    map_ = GM_CT.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_pos
        }
    })
    _ = GM_FH.FileLocations()  # still needed for initialization
    subfunc = GM_DMF.interpret_position(map_, VEGref_pos[1:], "VEG_reference")

    Syst = get_syst_VEGtests()
    osc = GM_CT.CustomClass(**{
        "used_atoms": [0, 1, 2, 3]
    })
    osc.positions_box = (
            Syst.positions[osc.used_atoms] @ Syst.boxvects_inv)

    out = np.array([1.25, 10, 20])
    assert np.all(subfunc(map_, Syst, osc) == out)


def test_MI_MC_9(capsys):
    # too few opening brackets (should be 4 instead of two)
    VEGref_pos = ["position", "((0+1)/2.0)+2)/2.0)"]
    Files = GM_FH.FileLocations()

    map_ = GM_CT.CustomClass(**{
        "rawcore": {
            "VEG_reference": VEGref_pos
        },
        "directory": Files.cwd
    })
    _ = GM_DMF.interpret_position(map_, VEGref_pos[1:], "VEG_reference")
    GM_PT.Printer().print_backlog()
    captured = capsys.readouterr()
    assert captured.out.endswith("MI_MC_9\n")

    # Syst = get_syst_VEGtests()
    # osc = GM_CT.CustomClass(**{
    #     "used_atoms": [0, 1, 2, 3]
    # })
    # osc.positions_box = (
    #         Syst.positions[osc.used_atoms] @ Syst.boxvects_inv)

    # out = np.array([1.25, 10, 20])
    # assert np.all(subfunc(map_, Syst, osc) == out)


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


def get_syst_VEGtests():
    Syst = GM_CT.CustomClass(**{
        "residues": GM_CT.CustomClass(**{
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
    return Syst


# just for coverage....
def test_unused():
    assert GM_DMF.unused_user() is None
