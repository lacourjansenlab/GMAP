"""
Tests all the functions/classes/methods in the file:
src/tools/CLibLoader.py.

Missing tests:

(@ July 22nd '24):
  (0 missed statements)

- Nothing is missing!
"""

# 3rd party imports
import numpy as np
import pytest

# local imports
from .test_SystemReader import parameter_getter
import GMAP.src.tools.CLibLoader as GM_CL
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.PhysicsFunctions as GM_PF


class TestVClib:
    def test_calcVEG_perres_mm(self):
        cmdline = ["-md", "maps\\;"]
        (
            Files, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline)

        VEGlib = GM_CL.VEG_CLib(RunPars)
        RunPars.estatic_range = np.float32(60)
        RunPars.estatic_smooth_range = np.float32(5)

        System = get_System_1()
        oscillator = get_oscillator_1()

        VEGlib.calcVEG_perres_mm(System, RunPars, oscillator)

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
        # pot_1 = 1/55.018 + -0.166/60 + 0/65.015 + -0.832/60

        # potentials
        ans = np.array([
            [0.01666666666667, 0.01817581095026],
            [-0.002557953278597537, -0.0027717718596666],
            [0, 0],
            [-0.015139585119952648, -0.013882521453]
        ], dtype="float32").sum(0).round(7)
        assert np.all(oscillator.VEGout[:, 0].round(7) == ans)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!! From here: comma as decimal point for copy-paste into and !!!!!
        # !!!!! from the windows calculator (which cannot deal with '.')  !!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # weights_res2 = 1, 0,16630631158
        # weights_res3 = 0, 0,83295238718

        # atdiff_0-2 = -(20, 40, 40), -(23, 43, 43)
        # atdiff_0_3 = (40, 20, 40), (37, 17, 37)
        # atdist_0 = 60, 65,0153827951, 60, 55,01817788139
        # prefac = weighted_charge / d^3
        #        = 4,629629629629629e-6,   -6,0514626889083057684e-7,
        #          0, -5,001514910197138206e-6
        # Ex_0 = sum(prefac * diffX)
        #      = -0,00026373028008539759035468
        # Ey_0 = -0,00024418964909623079469788
        # Ez_0 = -0,00034421994730017355881788

        # atdiff_1_2 = -(17, 37, 37), -(20, 40, 40)
        # atdiff_1_3 = (43, 23, 43), (40, 20, 40)
        # atdist_1 = 55,01817788139, 60, 65,0153827951, 60
        # prefac = weighted_charge / d^3
        #        = 6,004562790353486e-6,  -7,699366276851851e-7,
        #          0, -3,85626105175925925e-6
        # Ex_1 = -0,00024092927695267593
        # Ey_1 = -0,000268496579170856763
        # Ez_1 = -0,000345621800206041948

        # fields
        ans = np.array([
            [-0.00026373028008539759035468, -0.00024092927695267593],
            [-0.00024418964909623079469788, -0.000268496579170856763],
            [-0.00034421994730017355881788, -0.000345621800206041948]
        ], dtype="float32").round(8)
        assert np.all(oscillator.VEGout[:, 1:4].round(8) == ans.T)

        # weights_res2 = 1, 0,16630631158
        # weights_res3 = 0, 0,83295238718

        # Gxx, Gyy, Gzz = prefac - (diffXYZ * diffXYX * prefac2)
        # Gxy, Gxz, Gyz = -(diffXYZ * diffXYZ * prefac2)

        # atdiff_0-2 = -(20, 40, 40), -(23, 43, 43)
        # atdiff_0_3 = (40, 20, 40), (37, 17, 37)
        # atdist_0 = 60, 65,0153827951, 60, 55,01817788139
        # prefac = 4,629629629629629e-6,   -6,0514626889083057684e-7,
        #          0, -5,001514910197138206e-6
        # prefac2 = 3,85802469135802416667e-9, -4,2948635123617997e-10,
        #           0, -4,95690295316412058756e-9

        # atdiff_1_2 = -(17, 37, 37), -(20, 40, 40)
        # atdiff_1_3 = (43, 23, 43), (40, 20, 40)
        # atdist_1 = 55,01817788139, 60, 65,0153827951, 60
        # prefac = weighted_charge / d^3
        #        = 6,004562790353486e-6,  -7,699366276851851e-7,
        #          0, -3,85626105175925925e-6
        # prefac2 = 5,9510039582765967993e-9, -6,41613856404320916e-10
        #           0, -0,000000003213550876466049375

        ans = np.array([[
            # atom 1
            [0.000003086419, -0.000000377947, 0.000001784485],  # Gxx
            [-0.000001543209, 0.000000188973, -0.000003568969],  # Gyy
            [-0.000001543209, 0.000000188973, 0.000001784485],  # Gzz
            [-0.000003086419, 0.000000424762, 0.000003117891],  # Gxy
            [-0.000003086419, 0.000000424762, 0.000006786000],  # Gxz
            [-0.000006172839, 0.000000794120, 0.000003117891]   # Gyz
        ], [
            # atom 2
            [0.000004284722, -0.000000513291, 0.000001285420],  # Gxx
            [-0.000002142361, 0.000000256645, -0.000002570840],  # Gyy
            [-0.000002142361, 0.000000256645, 0.000001285420],  # Gzz
            [-0.000003743181, 0.000000513291, 0.000002570840],  # Gxy
            [-0.000003743181, 0.000000513291, 0.000005141681],  # Gxz
            [-0.000008146924, 0.000001026582, 0.000002570840]   # Gyz
        ]], dtype="float32").sum(2).round(10)
        assert np.all(oscillator.VEGout[:, 4:].round(10) == ans)

    def test_CL_VG_1(self):
        """This test will fail if the singletons are not cleared!!!!
        """

        cmdline = ["-md", "maps\\;"]
        (
            Files, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline)

        RunPars.VEG_clib_file = (
            RunPars.VEG_clib_file.parent / "doesntexist.txt")
        with pytest.raises(GM_Ex.GmapFileNotFoundError, match="CL_VG_1$"):
            _ = GM_CL.VEG_CLib(RunPars)

        RunPars.VEG_clib_file = (
            RunPars.VEG_clib_file.parent / "VEG.obj")
        with pytest.raises(GM_Ex.GmapOSError, match="CL_VG_1$"):
            _ = GM_CL.VEG_CLib(RunPars)

        RunPars.VEG_clib_file = (
            RunPars.VEG_clib_file.parent)
        with pytest.raises(GM_Ex.GMAPexception, match="CL_VG_1$"):
            _ = GM_CL.VEG_CLib(RunPars)


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
        "positions_c": np.ctypeslib.as_ctypes(np.ravel(positions)),
        "charges_c": np.ctypeslib.as_ctypes(charges),
        "residues": GM_CT.CustomClass(**{
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
    VEGout = np.zeros((2, 10), dtype="float32")
    return GM_CT.CustomClass(**{
        "electrostatic_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_estatic_atoms": np.int32(2),
        "VEG_refpos_c": np.ctypeslib.as_ctypes(VEG_refpos),
        "local_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_local_atoms": np.int32(2),
        "VEGout": VEGout,
        "VEGout_c": np.ctypeslib.as_ctypes(np.ravel(VEGout)),
        "Map": GM_CT.CustomClass(**{
            "Core": GM_CT.CustomClass(**{
                "electrostatic_choice_c": 3  # we want gradients!!!
            })
        })
    })
