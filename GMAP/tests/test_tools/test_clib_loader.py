"""
Tests all the functions/classes/methods in the file:
src/tools/clib_loader.py.

Missing tests:

(@ August 2nd '24):
  (0 missed statements)

- None!

To hide this file from the overview, incomplete tests were added for the
following:

- None!

"""

# 3rd party imports
import numpy as np
import pytest

# local imports
from .test_system_reader import parameter_getter
import GMAP.src.tools.clib_loader as GM_cl
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.exceptions as GM_ex


class TestVClib:
    def test_calcVEG_perres_mm_triclin(self):
        cmdline = ["-md", "maps\\;"]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline, load_clib=False)

        VEGlib = GM_cl.VEG_CLib(run_pars)
        run_pars.estatic_range = np.float32(60)
        run_pars.estatic_smooth_range = np.float32(5)

        system = get_System_1()
        oscillator = get_oscillator_1()
        VEGlib.calc_CoM_box(system)

        VEGlib.calcVEG_perres_mm_triclin(system, run_pars, oscillator)

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

        print(oscillator.VEGout)
        print(ans)
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
        print(ans)
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

        # gradients
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
        ]], dtype="float32").sum(2).round(9)
        print(ans)
        assert np.all(oscillator.VEGout[:, 4:].round(9) == ans)
        # assert False

    def test_calcVEG_perres_mm_rhombic(self):
        cmdline = ["-md", "maps\\;"]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline, load_clib=False)

        VEGlib = GM_cl.VEG_CLib(run_pars)
        run_pars.estatic_range = np.float32(60)
        run_pars.estatic_smooth_range = np.float32(5)

        system = get_System_1()
        oscillator = get_oscillator_1()
        VEGlib.calc_CoM_box(system)
        VEGlib.CoM_frombox(system)

        VEGlib.calcVEG_perres_mm_rhombic(system, run_pars, oscillator)

        # All results are the same ones as from the triclinic method.
        # see the test for the triclinic for the calculation of these
        # values.

        # potentials
        ans = np.array([
            [0.01666666666667, 0.01817581095026],
            [-0.002557953278597537, -0.0027717718596666],
            [0, 0],
            [-0.015139585119952648, -0.013882521453]
        ], dtype="float32").sum(0).round(7)

        print(oscillator.VEGout)
        print(ans)
        assert np.all(oscillator.VEGout[:, 0].round(7) == ans)

        # fields
        ans = np.array([
            [-0.00026373028008539759035468, -0.00024092927695267593],
            [-0.00024418964909623079469788, -0.000268496579170856763],
            [-0.00034421994730017355881788, -0.000345621800206041948]
        ], dtype="float32").round(8)
        print(ans)
        assert np.all(oscillator.VEGout[:, 1:4].round(8) == ans.T)

        # gradients
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
        ]], dtype="float32").sum(2).round(9)
        print(ans)
        assert np.all(oscillator.VEGout[:, 4:].round(9) == ans)

    def test_calcVEG_perres_mm_influencers(self):
        cmdline = ["-md", "maps\\;"]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline, load_clib=False)

        VEGlib = GM_cl.VEG_CLib(run_pars)
        run_pars.estatic_range = np.float32(60)
        run_pars.estatic_smooth_range = np.float32(5)

        # same system as the previous test, but 1 residue is now not an
        # influencer
        system = get_System_1()
        system.influencers_atix_c = np.ctypeslib.as_ctypes(
            np.array([0, 1, 2, 3], dtype="int32"))
        system.n_influencers = np.int32(4)
        oscillator = get_oscillator_1()
        VEGlib.calc_CoM_box(system)

        VEGlib.calcVEG_perres_mm_triclin(system, run_pars, oscillator)

        # Do not remove!!! These are the calculations to get to the correct
        # answer!
        # NNdtIS = not needed due to influencer setting

        # positions = np.array([
        #     [8, 28, 68],
        #     [11, 31, 71],
        #     [28, 68, 8],
        #     [31, 71, 11],
        #     [68, 8, 28],
        #     [71, 11, 31]
        # ], dtype="float32")
        # so, 4 points to take dist to. VEGref = 10, 30, 70
        # CoM's = (30, 70, 10), (NNdtIS)
        # dists = sqrt(20**2 + 40**2 + 40**2), NNdtIS
        # dists = 60, NNdtIS
        # dists_at_res2 = sqrt(18**2 + 38**2 + 38**2),  ch=1
        #                 sqrt(21**2 + 41**2 + 41**2)   ch=-1
        #               = 56.6745092612, 61.6684684421
        # weights_res2 = 1, 0.16630631158
        # res3 NNdtIS

        # atdiff_0-2 = (20, 40, 40), (23, 43, 43)
        # atdiff_0_3 = NNdtIS
        # atdist_0 = 60, 65.0153827951, NNdtIS
        # pot_0 = 1/60 + -0.166/65.015 + NNdtIS

        # atdiff_1_2 = (17, 37, 37), (20, 40, 40)
        # atdiff_1_3 = NNdtIS
        # atdist_1 = 55.01817788139, 60, NNdtIS
        # pot_1 = 1/55.018 + -0.166/60 + NNdtIS

        # potentials
        ans = np.array([
            [0.01666666666667, 0.01817581095026],
            [-0.002557953278597537, -0.0027717718596666],
            [0, 0],  # NNdtIS
            [0, 0]  # NNdtIS
        ], dtype="float32").sum(0).round(6)
        assert np.all(oscillator.VEGout[:, 0].round(6) == ans)

    def test_calcVEG_perres_mm_triclin_nocut(self):
        cmdline = ["-md", "maps\\;"]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline, load_clib=False)

        VEGlib = GM_cl.VEG_CLib(run_pars)
        run_pars.estatic_range = np.float32(60)
        run_pars.estatic_smooth_range = np.float32(5)

        system = get_System_1()
        oscillator = get_oscillator_1()
        VEGlib.calc_CoM_box(system)

        VEGlib.calcVEG_perres_mm_triclin_nocut(system, run_pars, oscillator)

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
        # weights_res2 = 1, 1
        # dists_at_res3 = sqrt(42**2 + 22**2 + 42**2),  ch=1
        #                 sqrt(39**2 + 19**2 + 39**2)   ch=-1
        #               = 63.3403504884, 58.3352380641
        # weights_res3 = 1, 1

        # atdiff_0-2 = (20, 40, 40), (23, 43, 43)
        # atdiff_0_3 = (40, 20, 40), (37, 17, 37)
        # atdist_0 = 60, 65,0153827951, 60, 55,01817788139
        # pot_0 = 1/60 + -1/65.015 + 1/60 + -1/55.018

        # atdiff_1_2 = (17, 37, 37), (20, 40, 40)
        # atdiff_1_3 = (43, 23, 43), (40, 20, 40)
        # atdist_1 = 55,01817788139, 60, 65,0153827951, 60
        # pot_1 = 1/55.018 + -1/60 + 1/65.015 + -1/60

        # potentials
        ans = np.array([
            [0.01666666666667, 0.0181758109502614],
            [-0.0153809753478, -0.01666666666667],
            [0.01666666666667, 0.0153809753478],
            [-0.0181758109502614, -0.01666666666667]
        ], dtype="float32").sum(0).round(7)

        print(oscillator.VEGout)
        print(ans)
        assert np.all(oscillator.VEGout[:, 0].round(7) == ans)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!! From here: comma as decimal point for copy-paste into and !!!!!
        # !!!!! from the windows calculator (which cannot deal with '.')  !!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # weights_res2 = 1, 1
        # weights_res3 = 1, 1

        # atdiff_0-2 = -(20, 40, 40), -(23, 43, 43)
        # atdiff_0_3 = (40, 20, 40), (37, 17, 37)
        # atdist_0 = 60, 65,0153827951, 60, 55,01817788139
        # prefac = weighted_charge / d^3
        #        = 4,629629629629629e-6, -3,6387450550830776644e-6,
        #          4,629629629629629e-6, -6,0045627903534862002e-6
        # Ex_0 = sum(prefac * diffX)
        #      = -0,0000458850943835756231262
        # Ey_0 = -0,0000382041226600295058342
        # Ez_0 = -0,0000657027858745066498382

        # atdiff_1_2 = -(17, 37, 37), -(20, 40, 40)
        # atdiff_1_3 = (43, 23, 43), (40, 20, 40)
        # atdist_1 = 55,01817788139, 60, 65,0153827951, 60
        # prefac = weighted_charge / d^3
        #        = 6,0045627903534862002e-6, -4,629629629629629e-6,
        #          3,6387450550830776644e-6, -4,629629629629629e-6
        # Ex_1 = -0,0000382041226600295058342
        # Ey_1 = -0,0000458850943835756231262
        # Ez_1 = -0,0000657027858745066498382

        # fields
        ans = np.array([
            [-0.0000458850943835756231262, -0.0000382041226600295058342],
            [-0.0000382041226600295058342, -0.0000458850943835756231262],
            [-0.0000657027858745066498382, -0.0000657027858745066498382]
        ], dtype="float32").round(8)
        assert np.all(oscillator.VEGout[:, 1:4].round(8) == ans.T)

        # weights_res2 = 1, 0,16630631158
        # weights_res3 = 0, 0,83295238718

        # Gxx, Gyy, Gzz = prefac - (diffXYZ * diffXYX * prefac2)
        # Gxy, Gxz, Gyz = -(diffXYZ * diffXYZ * prefac2)

        # atdiff_0-2 = -(20, 40, 40), -(23, 43, 43)
        # atdiff_0_3 = (40, 20, 40), (37, 17, 37)
        # atdist_0 = 60, 65,0153827951, 60, 55,01817788139
        # prefac = 4,629629629629629e-6, -3,6387450550830776644e-6,
        #          4,629629629629629e-6, -6,0045627903534862002e-6
        # prefac2 = 3,858024691358024e-9, -2,58250181340579986135e-9,
        #           3,858024691358024e-9, -5,95100395827659699780e-9

        # atdiff_1_2 = -(17, 37, 37), -(20, 40, 40)
        # atdiff_1_3 = (43, 23, 43), (40, 20, 40)
        # atdist_1 = 55,01817788139, 60, 65,0153827951, 60
        # prefac = weighted_charge / d^3
        #        = 6,0045627903534862002e-6, -4,629629629629629e-6,
        #          3,6387450550830776644e-6, -4,629629629629629e-6
        # prefac2 = 5,9510039582765969978e-9, -3,858024691358024e-9
        #           2,5825018134057998613e-9, -3,858024691358024e-9

        # gradients
        ans = np.array([[
            # atom 1
            [
                0.000003086419, -0.000002272601,
                -0.000001543209, 0.000002142361],  # Gxx
            [
                -0.000001543209, 0.000001136300,
                0.000003086419, -0.000004284722],  # Gyy
            [
                -0.000001543209, 0.000001136300,
                -0.000001543209, 0.000002142361],  # Gzz
            [
                -0.000003086419, 0.000002554094,
                -0.000003086419, 0.000003743181],  # Gxy
            [
                -0.000003086419, 0.000002554094,
                -0.000006172839, 0.000008146924],  # Gxz
            [
                -0.000006172839, 0.000004775045,
                -0.000003086419, 0.000003743181]   # Gyz
        ], [
            # atom 2
            [
                0.000004284722, -0.000003086419,
                -0.000001136300, 0.000001543209],  # Gxx
            [
                -0.000002142361, 0.000001543209,
                0.000002272601, -0.000003086419],  # Gyy
            [
                -0.000002142361, 0.000001543209,
                -0.000001136300, 0.000001543209],  # Gzz
            [
                -0.000003743181, 0.000003086419,
                -0.000002554094, 0.000003086419],  # Gxy
            [
                -0.000003743181, 0.0000030864191,
                -0.000004775045, 0.000006172839],  # Gxz
            [
                -0.000008146924, 0.000006172839,
                -0.000002554094, 0.000003086419]   # Gyz
        ]], dtype="float32").sum(2).round(10)
        assert np.all(oscillator.VEGout[:, 4:].round(10) == ans)

    def test_calcVEG_perres_mm_rhombic_nocut(self):
        cmdline = ["-md", "maps\\;"]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline, load_clib=False)

        VEGlib = GM_cl.VEG_CLib(run_pars)
        run_pars.estatic_range = np.float32(60)
        run_pars.estatic_smooth_range = np.float32(5)

        system = get_System_1()
        oscillator = get_oscillator_1()
        VEGlib.calc_CoM_box(system)
        VEGlib.CoM_frombox(system)

        VEGlib.calcVEG_perres_mm_rhombic_nocut(system, run_pars, oscillator)

        # same system, so same answers as for the triclinic version of this
        # function. See that one for explanation for all these values.

        # potentials
        ans = np.array([
            [0.01666666666667, 0.0181758109502614],
            [-0.0153809753478, -0.01666666666667],
            [0.01666666666667, 0.0153809753478],
            [-0.0181758109502614, -0.01666666666667]
        ], dtype="float32").sum(0).round(7)

        print(oscillator.VEGout)
        print(ans)
        assert np.all(oscillator.VEGout[:, 0].round(7) == ans)

        # fields
        ans = np.array([
            [-0.0000458850943835756231262, -0.0000382041226600295058342],
            [-0.0000382041226600295058342, -0.0000458850943835756231262],
            [-0.0000657027858745066498382, -0.0000657027858745066498382]
        ], dtype="float32").round(8)
        assert np.all(oscillator.VEGout[:, 1:4].round(8) == ans.T)
        print(ans)

        # gradients
        ans = np.array([[
            # atom 1
            [
                0.000003086419, -0.000002272601,
                -0.000001543209, 0.000002142361],  # Gxx
            [
                -0.000001543209, 0.000001136300,
                0.000003086419, -0.000004284722],  # Gyy
            [
                -0.000001543209, 0.000001136300,
                -0.000001543209, 0.000002142361],  # Gzz
            [
                -0.000003086419, 0.000002554094,
                -0.000003086419, 0.000003743181],  # Gxy
            [
                -0.000003086419, 0.000002554094,
                -0.000006172839, 0.000008146924],  # Gxz
            [
                -0.000006172839, 0.000004775045,
                -0.000003086419, 0.000003743181]   # Gyz
        ], [
            # atom 2
            [
                0.000004284722, -0.000003086419,
                -0.000001136300, 0.000001543209],  # Gxx
            [
                -0.000002142361, 0.000001543209,
                0.000002272601, -0.000003086419],  # Gyy
            [
                -0.000002142361, 0.000001543209,
                -0.000001136300, 0.000001543209],  # Gzz
            [
                -0.000003743181, 0.000003086419,
                -0.000002554094, 0.000003086419],  # Gxy
            [
                -0.000003743181, 0.0000030864191,
                -0.000004775045, 0.000006172839],  # Gxz
            [
                -0.000008146924, 0.000006172839,
                -0.000002554094, 0.000003086419]   # Gyz
        ]], dtype="float32").sum(2).round(10)
        print(ans)
        assert np.all(oscillator.VEGout[:, 4:].round(10) == ans)

    def test_CL_VG_1(self):
        """This test will fail if the singletons are not cleared!!!!
        """

        cmdline = ["-md", "maps\\;"]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter("AmideSC", cmdline, load_clib=False)

        run_pars.VEG_clib_file = (
            run_pars.VEG_clib_file.parent / "doesntexist.txt")
        matchstr = "CL_VG_1$"
        with pytest.raises(GM_ex.GmapOSError, match=matchstr):
            _ = GM_cl.VEG_CLib(run_pars)

        run_pars.VEG_clib_file = (
            run_pars.VEG_clib_file.parent / "VEG.obj")
        with pytest.raises(GM_ex.GmapOSError, match=matchstr):
            _ = GM_cl.VEG_CLib(run_pars)

        run_pars.VEG_clib_file = (
            run_pars.VEG_clib_file.parent)
        with pytest.raises(GM_ex.GMAPexception, match=matchstr):
            _ = GM_cl.VEG_CLib(run_pars)


def get_System_1():
    positions = np.array([
        [8, 28, 68],
        [11, 31, 71],
        [28, 68, 8],
        [31, 71, 11],
        [68, 8, 28],
        [71, 11, 31]
    ], dtype="float32")
    positions_box = np.array([
        [0.08, 0.28, 0.68],
        [0.11, 0.31, 0.71],
        [0.28, 0.68, 0.08],
        [0.31, 0.71, 0.11],
        [0.68, 0.08, 0.28],
        [0.71, 0.11, 0.31]
    ], dtype="float32")
    masses = np.array([1, 2, 1, 2, 1, 2], dtype="float32")
    # charges = np.array([1, -1, 0, 1, 0, 0], dtype="float32")
    charges = np.array([1, -1, 1, -1, 1, -1], dtype="float32")
    influencers = np.array([0, 1, 2, 3, 4, 5], dtype="int32")  # all atoms!
    n_influencers = np.int32(6)
    boxvects = np.array([
            [100, 0, 0],
            [0, 100, 0],
            [0, 0, 100]
    ], dtype="float32")
    boxvects_inv = np.linalg.inv(boxvects).astype("float32")
    res_first_ix = np.array([0, 2, 4], dtype="int32")
    res_last_ix = np.array([1, 3, 5], dtype="int32")
    nres = np.int32(3)
    # residues_CoM = GM_pf.system_CoM(
    #     positions, masses, boxvects_inv, boxvects,
    #     res_first_ix, res_last_ix, nres
    # )
    residues_CoM = np.zeros((nres, 3), dtype="float32")

    boxdims = np.array([100, 100, 100], dtype="float32")
    halfbox = np.array([50, 50, 50], dtype="float32")

    return GM_ct.CustomClass(**{
        "positions_c": np.ctypeslib.as_ctypes(np.ravel(positions)),
        "positions_box_c": np.ctypeslib.as_ctypes(np.ravel(positions_box)),
        "masses_c": np.ctypeslib.as_ctypes(masses),
        "charges_c": np.ctypeslib.as_ctypes(charges),
        "influencers_atix_c": np.ctypeslib.as_ctypes(influencers),
        "n_influencers": n_influencers,
        "residues": GM_ct.CustomClass(**{
            "CoM_box_c": np.ctypeslib.as_ctypes(np.ravel(residues_CoM)),
            "CoM_c": np.ctypeslib.as_ctypes(np.ravel(residues_CoM)),
            "first_ix_c": np.ctypeslib.as_ctypes(res_first_ix),
            "last_ix_c": np.ctypeslib.as_ctypes(res_last_ix)
        }),
        "nres": nres,
        "boxvects_c": np.ctypeslib.as_ctypes(np.ravel(boxvects)),
        "boxvects_inv_c": np.ctypeslib.as_ctypes(np.ravel(boxvects_inv)),
        "halfbox_c": np.ctypeslib.as_ctypes(halfbox),
        "boxdims_c": np.ctypeslib.as_ctypes(boxdims)
    })


def get_oscillator_1():
    estat_ats = np.array([0, 1], dtype="int32")
    VEG_refpos = np.array([10, 30, 70], dtype="float32")
    VEGout = np.zeros((2, 10), dtype="float32")
    return GM_ct.CustomClass(**{
        "electrostatic_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_estatic_atoms": np.int32(2),
        "VEG_refpos_c": np.ctypeslib.as_ctypes(VEG_refpos),
        "local_atoms_c": np.ctypeslib.as_ctypes(estat_ats),
        "n_local_atoms": np.int32(2),
        "VEGout": VEGout,
        "VEGout_c": np.ctypeslib.as_ctypes(np.ravel(VEGout)),
        "map": GM_ct.CustomClass(**{
            "core": GM_ct.CustomClass(**{
                "electrostatic_choice_c": 3  # we want gradients!!!
            })
        })
    })
