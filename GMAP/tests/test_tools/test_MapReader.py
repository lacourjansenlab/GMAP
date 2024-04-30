"""
Tests all the functions/classes/methods in the file:
src/tools/PhysicsFunctions.py.

Missing tests:

(@ apr 29th '24):
357-365, 740, 1117 (6 missed statements)

(CUHTAT - currently unknown how to access this )
- Map.append_core() - there was some issue with the corefile (CUHTAT) (357-365)
  Any stuff wrong with the corefile will have its own warning call (and not
  use raise) - MI_MC_5
- Map.parse_type was not successful, so we stop map reading  (740)
- The structure of the map has no bonds (but the parameter giving bonds has
  been used) (1117)
"""


# standard lib imports
from pathlib import Path

# 3rd party imports
import pytest
import numpy as np

# local imports
import GMAP.src.tools.DefaultMapFunctions as GM_DMF
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP
import GMAP.src.tools.PrintTools as GM_PT


class TestCode:
    def test_extract_code(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        mapname = "test_extract_code"
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code(Printer))

        assert map_.code.for_testing(4) == 6

    def test_extract_code_nocode(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        mapname = "test_extract_code_nocode"
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code(Printer))

        assert hasattr(map_.code, "for_testing") is False

    def test_GM_adjust_RunPars_custom(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_extract_code"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="adjust_RunPars",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        assert RunPars.neutral_charge_threshold == 0.0001
        map_.code.GM_adjust_RunPars(Files, Printer, map_)
        assert RunPars.neutral_charge_threshold == 0.02

    def test_GM_adjust_RunPars_default(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_extract_code_nocode"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="adjust_RunPars",
            mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code(Printer))
        if not map_.code:
            setattr(map_, "code", GM_DMF.NewModule())

        assert hasattr(map_.code, "GM_adjust_RunPars") is False
        map_.complete_code((
            "adjust_RunPars",
            "adjust_map_core_raw",
            "adjust_oscillators"
        ))
        assert hasattr(map_.code, "GM_adjust_RunPars") is True

    def test_find_core(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_find_core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core(Printer))

        assert map_.rawcore["functional_group"] == [[
            "[CYS]", "N", "H", "CA", "C", "O", "CB", "SG(1)", "[CYS]", "N",
            "H", "CA", "C", "O", "CB", "SG(1)"
        ]]

    def test_find_core_unicodedecodeerror(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;",
            "--prevent_overwrite", "False"
        ]
        inpardict = {}
        mapname = "test_unicodedecodeerror_core"
        fhand = open(
            "tests/test_tools/Data/maps_for_test_MapReader_1/Singles/"
            + mapname + "/core.txt", 'wb'
        )

        # Add some non-UTF-8 characters to the file.
        fhand.write(b'\x80')
        fhand.write(
            b'\xC0' + b'\xC1' + b'\xF5' + b'\xF6' + b'\xF7' + b'\xF8'
            + b'\xF9'
            + b'\xFA' + b'\xFB' + b'\xFC' + b'\xFD' + b'\xFE' + b'\xFF')
        fhand.close()

        (_, Printer, _, _, _, _, _, mapdict) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )
        map_ = mapdict[mapname]

        # setattr(map_, "Core", GM_MR.Core(Printer, map_))
        assert not map_.success
        out, _ = capfd.readouterr()
        assert out.endswith("SU_FH_3\n")

    def test_append_core(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_appending"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.append_core(Printer)

        assert map_.rawcore["influencer_group"] == [
            ["testgroup1", "TST"],
            ["testgroup2", "TST"],
            ["testgroup3", "TST"]
        ]

    def test_Core(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "Core", GM_MR.Core(Printer, map_))

        assert map_.Core.type == "standard"
        found_residues = [
            [residue.resnames for residue in struct.residues]
            for struct in map_.Core.functional_group
        ]
        assert found_residues == [[["CYS"], ["DEF"]], [["A", "B"]]]

    def test_Core_unsuccessful_returns(self, capfd):

        # if not self.success after parse_used_atoms, parse_estatic_atoms,
        # parse_estatic_choice and parse_type
        for i in range(1, 5):
            cmdline = [
                "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
            ]
            inpardict = {}
            mapname = f"test_MI_MC_6_{i}"

            (_, Printer, _, _, _, _, _, mapdict) = basic_setup(
                cmdline, inpardict, finish_before="Core", mapname=mapname
            )
            map_ = mapdict[mapname]

            setattr(map_, "Core", GM_MR.Core(Printer, map_))

            out, _ = capfd.readouterr()
            assert out.endswith("MI_MC_6\n")

        # if not self.success after parse_functional_group
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_2"
        (_, Printer, _, _, _, _, _, mapdict) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "Core", GM_MR.Core(Printer, map_))

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_2\n")

        # using a map without estatic_atoms
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"
        (_, Printer, _, _, _, _, _, mapdict) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "Core", GM_MR.Core(Printer, map_))

        assert map_.Core.electrostatic_atoms == []
        assert map_.Core.electrostatic_choice is None

    def test_code_add_builds_1(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_code_build_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array([[10, 0, 0], [0, 10, 0], [0, 0, 10]])
        Syst = Custom(
            ["boxvects", boxvects],
            ["boxvects_inv", np.linalg.inv(boxvects)]
        )

        positions = np.array([
            [1.5, 1, 0],
            [3, 0, 0],
            [4.5, 1, 0],
            [6, 0, 0]
        ])
        osc = Custom(
            ["positions_box", positions @ Syst.boxvects_inv]
        )

        map_.code_add_builds(Printer)
        r_vec, r_pos = map_.code.GM_get_dipole(
            Printer, map_, Syst, osc
        )
        r_vec_dir = np.array([-1.5, 1, 0])
        assert (np.round(r_vec, 4) == np.round(r_vec_dir, 4)).all()

        assert (
            np.round(r_pos, 4) == np.round(np.array([3.75, 0.5, 0]), 4)
        ).all()

        rotation_matrix = np.round(map_.code.GM_get_rotation_matrix(
            Printer, map_, Syst, osc
        ), 4)

        xvec = np.array([1.5, 1, 0])
        xvec /= GM_MF.vec3_len(xvec)
        yvec = GM_MF.project(xvec, np.array([-1.5, 1, 0]))
        yvec /= GM_MF.vec3_len(yvec)
        zvec = GM_MF.crossprod(xvec, yvec)
        zvec /= GM_MF.vec3_len(zvec)

        test_matrix = np.round(np.array([xvec, yvec, zvec]), 4)
        assert (rotation_matrix == test_matrix).all()

    def test_code_add_builds_2(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_code_build_2"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array([[5, 0, 0], [4, 3, 0], [2, 2, 4]])
        Syst = Custom(
            ["boxvects", boxvects],
            ["boxvects_inv", np.linalg.inv(boxvects)]
        )

        positions = np.array([
            [0, 0, 0],
            [1.5, 1, 0],
            [1.5, 3, 0],
            [3, 0, 0],
            [3, -1, 1],
            [4, 1, 1]
        ])
        osc = Custom(
            ["positions_box", positions @ Syst.boxvects_inv]
        )

        map_.code_add_builds(Printer)
        r_vec, r_pos = map_.code.GM_get_dipole(
            Printer, map_, Syst, osc
        )
        r_vec_dir = np.array([1.125, 1.25, 0])
        assert (np.round(r_vec, 4) == np.round(r_vec_dir, 4)).all()

        # answer should be (2.5, 2.3333, 0), but because yvec is quite short
        # (only (4, 3)), the y coordinate doesnt fit (extends more than half
        # a box), so 1 yvec is subtracted. (2.5, 2.3333, 0) - (4, 3, 0) =
        # (-2.5, -0.6666, 0)
        assert (
            np.round(r_pos, 4) == np.round(np.array([-2.5, -0.666666, 0]), 4)
        ).all()

        rotation_matrix = np.round(map_.code.GM_get_rotation_matrix(
            Printer, map_, Syst, osc
        ), 4)

        zvec = np.array([0, 2, 0], dtype=np.float64)
        zvec /= GM_MF.vec3_len(zvec)
        yvec = GM_MF.project(zvec, np.array([1.5, -1, 0]))
        yvec /= GM_MF.vec3_len(yvec)
        xvec = GM_MF.crossprod(zvec, yvec)
        xvec /= GM_MF.vec3_len(xvec)

        test_matrix = np.round(np.array([xvec, yvec, zvec]), 4)
        assert (rotation_matrix == test_matrix).all()

    def test_code_add_builds_3(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_code_build_3"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array([[5, 0, 0], [4, 3, 0], [2, 2, 4]])
        Syst = Custom(
            ["boxvects", boxvects],
            ["boxvects_inv", np.linalg.inv(boxvects)]
        )

        positions = np.array([
            [0, 0, 0],
            [1, 1, 1],
            [2, 2, 2]
        ])
        osc = Custom(
            ["positions_box", positions @ Syst.boxvects_inv]
        )

        map_.code_add_builds(Printer)
        r_vec, r_pos = map_.code.GM_get_dipole(
            Printer, map_, Syst, osc
        )
        r_vec_dir = np.array([2, 2, 2])
        assert (np.round(r_vec, 4) == np.round(r_vec_dir, 4)).all()

        assert (
            np.round(r_pos, 4) == np.round(np.array([1, 1, 1]), 4)
        ).all()

        rotation_matrix = np.round(map_.code.GM_get_rotation_matrix(
            Printer, map_, Syst, osc
        ), 4)

        zvec = np.array([2, 2, 2], dtype=np.float64)
        zvec /= GM_MF.vec3_len(zvec)
        xvec = GM_MF.project(zvec, np.array([1, 0, 0]))
        xvec /= GM_MF.vec3_len(xvec)
        yvec = GM_MF.crossprod(zvec, xvec)
        yvec /= GM_MF.vec3_len(yvec)

        test_matrix = np.round(np.array([xvec, yvec, zvec]), 4)
        assert (rotation_matrix == test_matrix).all()

    def test_initialize(self, capfd):

        # we tested all substeps, now just to confirm the totality runs, too
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_code_build_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files, Printer)

        assert map_.success

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_2"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files, Printer)

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_2\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_6"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files, Printer)

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_6\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files, Printer)

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_1\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files, Printer)

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_10\n")

    def test_MI_MC_6(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_6_5"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_6\n")

    def test_MI_MC_9(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_9_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_9\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_9_2"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_9\n")

    def test_MI_MC_10(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_10\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_2"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_10\n")

    def test_MI_MR_1(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.extract_code(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_1\n")

    def test_MI_MR_2(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_2"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core(Printer))

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_2\n")

    def test_MI_MR_3(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_3_1"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core(Printer))

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_3\n")

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_3_2"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.append_core(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_3\n")

    def test_MI_MR_4(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_4"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core(Printer))

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_4\n")

    def test_MI_MR_6(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_6"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.append_core(Printer)

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_6\n")


class TestCore:
    def test_parse_functional_group(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        Corebase = GM_MR.Core.__new__(GM_MR.Core)
        setattr(Corebase, "success", True)

        Corebase.parse_functional_group(Printer, map_.rawcore, map_.directory)

        found_residues = [
            [residue.resnames for residue in struct.residues]
            for struct in Corebase.functional_group
        ]
        assert found_residues == [[["CYS"], ["DEF"]], [["A", "B"]]]

        found_bonds = [struct.bonds for struct in Corebase.functional_group]
        assert found_bonds == [[[6, 13]], []]

        found_atoms = [
            [residue.atoms for residue in struct.residues]
            for struct in Corebase.functional_group
        ]
        assert found_atoms == [
            [
                [["N"], ["H"], ["CA"], ["C"], ["O"], ["CB"], ["SG"]],
                [["ND"], ["HD"], ["CAD"], ["CD"], ["OD"], ["CBD"], ["SGD"]]
            ],
            [[
                ["A11", "A12"], ["A2"], ["A3"], ["A41", "A42"], ["A5"], ["A6"],
                ["A7"], ["A8"], ["A9"], ["A10"], ["A11"], ["A12"], ["A13"],
                ["A14"]
            ]]
        ]

        struct = Corebase.functional_group[0]
        assert str(struct) == (
            "Structure([Residue([['CYS'], [['N'], ['H'], ['CA'], ['C'], "
            "['O'], ['CB'], ['SG']]]), Residue([['DEF'], [['ND'], ['HD'], "
            "['CAD'], ['CD'], ['OD'], ['CBD'], ['SGD']]])])"
        )
        assert repr(struct) == (
            "Structure([Residue([['CYS'], [['N'], ['H'], ['CA'], ['C'], "
            "['O'], ['CB'], ['SG']]]), Residue([['DEF'], [['ND'], ['HD'], "
            "['CAD'], ['CD'], ['OD'], ['CBD'], ['SGD']]])])"
        )
        assert str(struct.residues[0]) == (
            "Residue([['CYS'], [['N'], ['H'], ['CA'], ['C'], "
            "['O'], ['CB'], ['SG']]])"
        )

    def test_parse_functional_group_fromfile(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_funcgroupfile"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        Corebase = GM_MR.Core.__new__(GM_MR.Core)
        setattr(Corebase, "success", True)

        Corebase.parse_functional_group(Printer, map_.rawcore, map_.directory)

        found_residues = [
            [residue.resnames for residue in struct.residues]
            for struct in Corebase.functional_group
        ]
        assert found_residues == [[["ASN"]], [["GLN"]]]

        found_bonds = [struct.bonds for struct in Corebase.functional_group]
        assert found_bonds == [[], []]

        found_atoms = [
            [residue.atoms for residue in struct.residues]
            for struct in Corebase.functional_group
        ]
        assert found_atoms == [
            [[["CG"], ["OD1"], ["CB"], ["ND2"], ["HD21"], ["HD22"]]],
            [[["CD"], ["OE1"], ["CG"], ["NE2"], ["HE21"], ["HE22"]]]
        ]

    def test_parse_functional_group_bonds(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_funcgroup_bonded"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        Corebase = GM_MR.Core.__new__(GM_MR.Core)
        setattr(Corebase, "success", True)

        Corebase.parse_functional_group(Printer, map_.rawcore, map_.directory)

        found_bonds = [struct.bonds for struct in Corebase.functional_group]
        assert found_bonds == [[[6, 13]]]

    def test_parse_used_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(Printer, map_, finish_before="used_atoms")
        setattr(CoreBase, "used_atoms", CoreBase.parse_used_atoms(
            Printer, map_.rawcore, map_.directory
        ))
        assert CoreBase.used_atoms == [5, 3, 7, 1, 13, 2, 11]

    def test_parse_estatic_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="estatic_atoms")
        setattr(CoreBase, "electrostatic_atoms", CoreBase.parse_estatic_atoms(
            Printer, map_.rawcore, map_.directory
        ))
        assert CoreBase.electrostatic_atoms == [2, 3]

    def test_estatic_atoms_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="estatic_atoms")
        setattr(CoreBase, "electrostatic_atoms", CoreBase.parse_estatic_atoms(
            Printer, map_.rawcore, map_.directory
        ))
        assert CoreBase.electrostatic_atoms == []

    def test_parse_estatic_choice(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="estatic_choice")
        setattr(
            CoreBase, "electrostatic_choice", CoreBase.parse_estatic_choice(
                Printer, map_.rawcore, map_.directory
            ))
        assert CoreBase.electrostatic_choice == "E"

    # tests something normal program flow could never reach
    def test_estatic_choice_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="estatic_choice")
        setattr(
            CoreBase, "electrostatic_choice", CoreBase.parse_estatic_choice(
                Printer, map_.rawcore, map_.directory
            ))
        assert CoreBase.electrostatic_choice is None

    def test_parse_type(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="type")
        setattr(
            CoreBase, "type", CoreBase.parse_type(
                Printer, map_.rawcore, map_.directory
            ))
        assert CoreBase.type == "standard"

    def test_type_estat_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="type")
        setattr(
            CoreBase, "type", CoreBase.parse_type(
                Printer, map_.rawcore, map_.directory
            ))
        assert CoreBase.type is None

    def test_type_estat_V(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estat_choice_V"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="type")
        setattr(
            CoreBase, "type", CoreBase.parse_type(
                Printer, map_.rawcore, map_.directory
            ))
        assert CoreBase.type is None

    def test_parse_local_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="local_atoms")
        setattr(CoreBase, "local_atoms", CoreBase.parse_local_atoms(
            Printer, map_.rawcore, map_.directory
        ))
        assert CoreBase.local_atoms == [2, 3]

    def test_local_atoms_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_local_None"

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            Printer, map_, finish_before="local_atoms")
        setattr(CoreBase, "local_atoms", CoreBase.parse_local_atoms(
            Printer, map_.rawcore, map_.directory
        ))
        assert CoreBase.local_atoms == []

    def test_MI_MC_1(self, capfd):
        self.basis_test_MI_MC("MI_MC_1", capfd, finish_before="used_atoms")

    def test_MI_MC_2(self, capfd):
        self.basis_test_MI_MC("MI_MC_2", capfd, finish_before="used_atoms")

    def test_MI_MC_3(self, capfd):
        self.basis_test_MI_MC("MI_MC_3", capfd, finish_before="used_atoms")

    def test_MI_MC_4(self, capfd):
        self.basis_test_MI_MC("MI_MC_4", capfd, "test_MI_MC_4_1", "used_atoms")
        self.basis_test_MI_MC("MI_MC_4", capfd, "test_MI_MC_4_2", "used_atoms")
        self.basis_test_MI_MC("MI_MC_4", capfd, "test_MI_MC_4_3", "used_atoms")
        self.basis_test_MI_MC("MI_MC_4", capfd, "test_MI_MC_4_4", "used_atoms")
        self.basis_test_MI_MC("MI_MC_4", capfd, "test_MI_MC_4_5", "used_atoms")
        self.basis_test_MI_MC("MI_MC_4", capfd, "test_MI_MC_4_6", "used_atoms")

    def test_MI_MC_5(self, capfd):
        self.basis_test_MI_MC("MI_MC_5", capfd, "test_MI_MC_5_1", "used_atoms")
        self.basis_test_MI_MC("MI_MC_5", capfd, "test_MI_MC_5_2", "used_atoms")
        self.basis_test_MI_MC("MI_MC_5", capfd, "test_MI_MC_5_3", "used_atoms")
        self.basis_test_MI_MC("MI_MC_5", capfd, "test_MI_MC_5_4", "used_atoms")

    def test_MI_MC_6(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_1", "estatic_atoms")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_2", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_3", "type")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_4", "local_atoms")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_6", "VEG_reference")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_7", "end")

    def test_MI_MC_7(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_1", "estatic_atoms")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_2", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_3", "VEG_reference")

    def test_MI_MC_8(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_1", "estatic_atoms")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_2", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_3", "type")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_4", "local_atoms")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_5", "VEG_reference")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_6", "end")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_7", "end")

    def test_MI_MC_9(self, capfd):
        self.basis_test_MI_MC("MI_MC_9", capfd, finish_before="used_atoms")

    def basis_test_MI_MC(
        self, errcode, capfd, mapname=None, finish_before=None
    ):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;",
            "--prevent_overwrite", "False"
        ]
        inpardict = {}
        if mapname is None:
            mapname = "test_" + errcode

        (
            Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        # Corebase = GM_MR.Core.__new__(GM_MR.Core)
        # setattr(Corebase, "success", True)

        # Corebase.parse_functional_group(
        #     Printer, map_.rawcore, map_.directory)
        _ = basic_setup_core(Printer, map_, finish_before=finish_before)

        out, _ = capfd.readouterr()
        assert out.endswith(errcode + "\n")


class Custom():
    def __init__(self, *args):
        for arg in args:
            setattr(self, arg[0], arg[1])


def test_manage_maps():
    # basically the same as GM_PP.get_parameters, but can take list and dict
    # instead of commandline and inparfile
    maplist = ["AmideSC", "AmideBB"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    GM_MR.manage_maps(Files, Printer, RunPars, mapdict)

    assert all(
        key in RunPars.requested_mapdict.keys()
        for key in maplist
    )
    assert len(RunPars.requested_mapdict.keys()) == len(maplist)

    # ---

    maplist = ["AmideSC"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    GM_MR.manage_maps(Files, Printer, RunPars, mapdict)

    assert all(
        key in RunPars.requested_mapdict.keys()
        for key in maplist
    )
    assert len(RunPars.requested_mapdict.keys()) == len(maplist)


def test_MI_GEM_1(capsys):
    maplist = ["AmideSC", "doesntexist"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        Files, Printer, RunPars, RefPars, DefPars, InPars, CmdPars, mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        GM_MR.manage_maps(Files, Printer, RunPars, mapdict)

    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("MI_GEM_1\n")


def basic_setup(
    cmdline, inpardict, defparfilename=None, refparfilename=None,
    finish_before=None, mapname=None, prevent_overwrite=False
):
    """Sets up a map until it has a RunPars (not yet analyzed the core).

    All steps in here are tested by test_ParameterParser.py. If any
    issues occur within this function, run that file alone, first.
    """

    if "--prevent_overwrite" not in cmdline and not prevent_overwrite:
        cmdline.extend(["--prevent_overwrite", "False"])

    if refparfilename is None:
        refparfilename = Path("sourcefiles/reference_parameters.ref")

    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    RefPars = GM_PP.RefPars(Printer, refparfilename, True)
    if defparfilename:
        DefPars = GM_PP.RawPars.from_file(
            Printer, defparfilename, RefPars, True)
    else:
        DefPars = RefPars

    curpath = Path(__file__).resolve()
    InPars = GM_PP.RawPars.from_dict(
        Printer, curpath, inpardict, RefPars, False
    )

    mapdirs = GM_PP.find_mapdir(Files, Printer, cmdline, InPars, DefPars)
    mapdict = GM_MR.scan_mapdirs(mapdirs)

    for map_ in mapdict.values():
        map_.find_refpars(Printer)

    CmdPars = GM_PP.RawPars.from_cmdline(
        Printer, cmdline, RefPars,
        {name: map_.RefPars for name, map_ in mapdict.items()},
        False
    )

    for map_ in mapdict.values():
        map_.find_rawpars(Printer, CmdPars, InPars, DefPars)

    CmdPars.finalize_map_pars(Printer)
    InPars.finalize_map_pars(Printer)
    if DefPars.fname != RefPars.fname:
        DefPars.finalize_map_pars(Printer)

    RunPars = GM_PP.RunPars(
        Files, Printer, CmdPars, InPars, DefPars, RefPars, True
    )

    for map_ in mapdict.values():
        map_.find_runpars(Files, Printer, RunPars)

    returntuple = (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    )

    if finish_before == "extract_code":
        return returntuple
    # ------------------------------------------------------------------

    map_ = mapdict[mapname]
    setattr(map_, "code", map_.extract_code(Printer))
    if not map_.code:
        setattr(map_, "code", GM_DMF.NewModule())

    map_.complete_code((
        "adjust_RunPars",
        "adjust_map_core_raw",
        "adjust_oscillators"
    ))

    if finish_before == "adjust_RunPars":
        return returntuple
    # ------------------------------------------------------------------

    map_.code.GM_adjust_RunPars(Files, Printer, map_)

    if finish_before == "find_core":
        return returntuple
    # ------------------------------------------------------------------

    setattr(map_, "rawcore", map_.find_core(Printer))

    if finish_before == "append_core":
        return returntuple
    # ------------------------------------------------------------------

    map_.append_core(Printer)
    map_.code.GM_adjust_map_core_raw(Files, Printer, map_)

    if finish_before == "Core":
        return returntuple

    setattr(map_, "Core", GM_MR.Core(Printer, map_))

    if finish_before == "code_add_builds":
        return returntuple

    map_.code_add_builds(Printer)

    return returntuple


def basic_setup_core(Printer, map_, finish_before=None):
    CoreBase = GM_MR.Core.__new__(GM_MR.Core)
    setattr(CoreBase, "success", True)
    CoreBase.parse_functional_group(Printer, map_.rawcore, map_.directory)
    if finish_before == "used_atoms":
        return CoreBase

    setattr(CoreBase, "used_atoms", CoreBase.parse_used_atoms(
        Printer, map_.rawcore, map_.directory
    ))
    if finish_before == "estatic_atoms":
        return CoreBase

    setattr(CoreBase, "electrostatic_atoms", CoreBase.parse_estatic_atoms(
        Printer, map_.rawcore, map_.directory
    ))
    if finish_before == "estatic_choice":
        return CoreBase

    setattr(CoreBase, "electrostatic_choice", CoreBase.parse_estatic_choice(
        Printer, map_.rawcore, map_.directory
    ))
    if finish_before == "type":
        return CoreBase

    setattr(CoreBase, "type", CoreBase.parse_type(
        Printer, map_.rawcore, map_.directory
    ))

    if finish_before == "local_atoms":
        return CoreBase

    setattr(CoreBase, "local_atoms", CoreBase.parse_local_atoms(
        Printer, map_.rawcore, map_.directory
    ))

    if finish_before == "VEG_reference":
        return CoreBase

    CoreBase.check_VEG_reference(
        Printer, map_.rawcore, map_.directory
    )

    if finish_before == "end":  # so we can ctrl+F later
        return CoreBase
