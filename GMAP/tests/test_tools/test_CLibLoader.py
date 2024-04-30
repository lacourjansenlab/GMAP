"""
Tests all the functions/classes/methods in the file:
src/tools/CLibLoader.py.

Missing tests:

(@ apr 30th '24):
99-100, 159 (3 missed statements)

- Unknown file (CL_VG_1)  (99, 100)

(CUHTAT - currently unknown how to access this )
- SU_FP_7 (CUHTAT)   (369-370)
- RefPars parse choice - unknown dtype (CUHTAT)  (429)
- RawPars verify choice - unknown dtype (CUHTAT)  (1080)
- RunPars unknown loc for -md - SU_NP_3   (CUHTAT, SU_PP_3!)  (1543-1544)
- RunPars framenums - empty source (CUHTAT)   (1810)
"""

# 3rd party imports
import numpy as np
import pytest

# local imports
from .test_SystemReader import parameter_getter
import GMAP.src.tools.CLibLoader as GM_CL
import GMAP.src.tools.PhysicsFunctions as GM_PF


# Otherwise, the created singleton will leak between tests.
# https://github.com/pytest-dev/pytest-mock/issues/100
@pytest.fixture(autouse=True)
def reset_singletons():
    GM_CL.Singleton._instances = {}


class TestVClib:
    def test_calcPot_perres_mm(self):
        cmdline = ["-md", "maps\\;"]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter("AmideSC", cmdline)

        VEGlib = GM_CL.VEG_CLib(Printer, RunPars)
        RunPars.estatic_range = np.float32(60)
        RunPars.estatic_smooth_range = np.float32(5)

        System = get_System_1()
        oscillator = get_oscillator_1()

        VEGlib.calcPot_perres_mm(System, RunPars, oscillator)

        # Do not remove!!! These are the calculations to get to the correct
        # answer!

        # positions = np.array([
        #     [8, 28, 68],
        #     [11, 31, 71],
        #     [28, 68, 8],
        #     [31, 71, 11],
        #     [68, 8, 28],
        #     [71, 11, 31]
        # ], dtype="float32")
        # so, 4 points to take dist to. VEGref = 10, 30, 70
        # CoM's = (30, 70, 10), (70, 10, 30)
        # dists = sqrt(20**2 + 40**2 + 40**2), sqrt(40**2 + 20**2 + 40**2)
        # dists = 60, 60
        # dists_at_res2 = sqrt(18**2 + 38**2 + 38**2),  ch=1
        #                 sqrt(21**2 + 41**2 + 41**2)   ch=-1
        #               = 56.6745092612, 61.6684684421
        # weights_res2 = 1, 0.16630631158
        # dists_at_res3 = sqrt(42**2 + 22**2 + 42**2),  ch=1
        #                 sqrt(39**2 + 19**2 + 39**2)   ch=-1
        #               = 63.3403504884, 58.3352380641
        # weights_res3 = 0, 0.83295238718

        # atdiff_0-2 = (20, 40, 40), (23, 43, 43)
        # atdiff_0_3 = (40, 20, 40), (37, 17, 37)
        # atdist_0 = 60, 65.0153827951, 60, 55.01817788139
        # pot_0 = 1/60 + -0.166/65.015 + 0/60 + -0.832/55.018

        # atdiff_1_2 = (17, 37, 37), (20, 40, 40)
        # atdiff_1_3 = (43, 23, 43), (40, 20, 40)
        # atdist_1 = 55.01817788139, 60, 65.0153827951, 60

        ans = np.array([
            [0.01666666666667, 0.01817581095026],
            [-0.002557953278597537, -0.0027717718596666],
            [0, 0],
            [-0.015139585119952648, -0.013882521453]
        ], dtype="float32").sum(0).round(6)
        assert np.all(oscillator.VEGout.round(6) == ans)

    def test_CL_VG_1(self, capsys):
        cmdline = ["-md", "maps\\;"]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter("AmideSC", cmdline)
        RunPars.VEG_clib_file = (
            RunPars.VEG_clib_file.parent / "doesntexist.txt")

        with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
            _ = GM_CL.VEG_CLib(Printer, RunPars)
        assert pytest_wrapped_sysexit.type is SystemExit
        captured = capsys.readouterr()
        assert captured.out.endswith("CL_VG_1\n")


class EmptyClass:
    def __init__(self, **kwargs):
        for parname, val in kwargs.items():
            setattr(self, parname, val)
        return


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
        "positions_c": np.ctypeslib.as_ctypes(np.ravel(positions)),
        "charges_c": np.ctypeslib.as_ctypes(charges),
        "residues": EmptyClass(**{
            "CoM_c": np.ctypeslib.as_ctypes(np.ravel(residues_CoM)),
            "first_ix_c": np.ctypeslib.as_ctypes(res_first_ix),
            "last_ix_c": np.ctypeslib.as_ctypes(res_last_ix)
        }),
        "nres": nres,
        "halfbox_c": np.ctypeslib.as_ctypes(halfbox),
        "boxdims_c": np.ctypeslib.as_ctypes(boxdims)
    })


def get_oscillator_1():
    estat_ats = np.array([0, 1], dtype="int32")
    VEG_refpos = np.array([10, 30, 70], dtype="float32")
    VEGout = np.zeros((2,), dtype="float32")
    return EmptyClass(**{
        "electrostatic_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_estatic_atoms": np.int32(2),
        "VEG_refpos_c": np.ctypeslib.as_ctypes(VEG_refpos),
        "local_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_local_atoms": np.int32(2),
        "VEGout": VEGout,
        "VEGout_c": np.ctypeslib.as_ctypes(VEGout),
    })
