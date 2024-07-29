"""
Tests all the functions/classes/methods in the file:
src/tools/PhysicsFunctions.py.

Missing tests:

(@ July 22nd '24):
328-336, 1097, 1484 (6 missed statements)

(CUHTAT - currently unknown how to access this )
- Map.append_core() - there was some issue with the corefile (CUHTAT)
  (353-361)
  Any stuff wrong with the corefile will have its own warning call (and not
  use raise) - MI_MC_5
- SingleCore.parse_type was not successful, so we stop map reading  (1125)
- The structure of the map has no bonds (but the parameter giving bonds has
  been used) (1513)
"""


# standard lib imports
from pathlib import Path

# 3rd party imports
import pytest
import numpy as np

# local imports
import GMAP.src.tools.DefaultMapFunctions as GM_DMF
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP


class TestCode:
    def test_extract_code(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        mapname = "test_extract_code"
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code())

        assert map_.code.for_testing(4) == 6

    def test_extract_code_nocode(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        mapname = "test_extract_code_nocode"
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code())

        assert hasattr(map_.code, "for_testing") is False

    def test_GM_adjust_RunPars_custom(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_extract_code"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="adjust_RunPars",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        assert RunPars.neutral_charge_threshold == 0.0001
        map_.code.GM_adjust_RunPars(Files, map_)
        assert RunPars.neutral_charge_threshold == 0.02

    def test_GM_adjust_RunPars_default(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_extract_code_nocode"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="adjust_RunPars",
            mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code())
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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core())

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

        (_, _, _, _, _, _, mapdict, pairs_mapdict) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )
        map_ = mapdict[mapname]

        # setattr(map_, "Core", GM_MR.SingleCore(map_))
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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.append_core()

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "Core", GM_MR.SingleCore(map_))

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

            (_, _, _, _, _, _, mapdict, _) = basic_setup(
                cmdline, inpardict, finish_before="Core", mapname=mapname
            )
            map_ = mapdict[mapname]

            setattr(map_, "Core", GM_MR.SingleCore(map_))

            out, _ = capfd.readouterr()
            assert out.endswith("MI_MC_6\n")

        # if not self.success after parse_functional_group
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_2"
        (_, _, _, _, _, _, mapdict, _) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "Core", GM_MR.SingleCore(map_))

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_2\n")

        # using a map without estatic_atoms
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"
        (_, _, _, _, _, _, mapdict, _) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "Core", GM_MR.SingleCore(map_))

        assert map_.Core.electrostatic_atoms == []
        assert map_.Core.electrostatic_choice is None

    def test_code_add_builds_1(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;",
            "--verbose", "4", "--verbose_logfile", "4"
        ]
        inpardict = {}
        mapname = "test_code_build_1"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
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

        map_.code_add_builds()
        r_vec, r_pos = map_.code.GM_get_dipole_dir(
            map_, Syst, osc
        )
        r_vec_dir = np.array([-1.5, 1, 0])  # not normalized
        r_vec_dir /= np.linalg.norm(r_vec_dir)
        r_vec_dir = r_vec_dir.astype("float32")
        assert (np.round(r_vec, 4) == np.round(r_vec_dir, 4)).all()

        assert (
            np.round(r_pos, 4) == np.round(np.array([3.75, 0.5, 0]), 4)
        ).all()

        rotation_matrix = np.round(map_.code.GM_get_rotation_matrix(
            map_, Syst, osc
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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array(
            [[5, 0, 0], [4, 3, 0], [2, 2, 4]], dtype="float32")
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

        map_.code_add_builds()
        r_vec, r_pos = map_.code.GM_get_dipole_dir(
            map_, Syst, osc
        )
        r_vec_dir = np.array([1.125, 1.25, 0])  # not normalized
        r_vec_dir /= np.linalg.norm(r_vec_dir)
        r_vec_dir = r_vec_dir.astype("float32")
        assert (np.round(r_vec, 4) == np.round(r_vec_dir, 4)).all()

        # answer should be (2.5, 2.3333, 0), but because yvec is quite short
        # (only (4, 3)), the y coordinate doesnt fit (extends more than half
        # a box), so 1 yvec is subtracted. (2.5, 2.3333, 0) - (4, 3, 0) =
        # (-2.5, -0.6666, 0)
        assert (
            np.round(r_pos, 4) == np.round(np.array(
                [-2.5, -0.666666, 0], dtype="float32"), 4)
        ).all()

        rotation_matrix = np.round(map_.code.GM_get_rotation_matrix(
            map_, Syst, osc
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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array(
            [[5, 0, 0], [4, 3, 0], [2, 2, 4]], dtype="float32")
        Syst = Custom(
            ["boxvects", boxvects],
            ["boxvects_inv", np.linalg.inv(boxvects)]
        )

        positions = np.array([
            [0, 0, 0],
            [1, 1, 1],
            [2, 2, 2]
        ], dtype="float32")
        osc = Custom(
            ["positions_box", positions @ Syst.boxvects_inv]
        )

        map_.code_add_builds()
        r_vec, r_pos = map_.code.GM_get_dipole_dir(
            map_, Syst, osc
        )

        # this answer is wrong, as we correct for pbc.
        # r_vec_dir = np.array([2, 2, 2], dtype="float32")  # not_normalized
        # r_vec_dir /= np.linalg.norm(r_vec_dir)

        r_vec_dir = np.array([0, 0, -2], dtype="float32")  # not_normalized
        r_vec_dir /= np.linalg.norm(r_vec_dir)
        assert (np.round(r_vec, 4) == np.round(r_vec_dir, 4)).all()

        assert (
            np.round(r_pos, 4) == np.round(np.array([1, 1, 1]), 4)
        ).all()

        rotation_matrix = np.round(map_.code.GM_get_rotation_matrix(
            map_, Syst, osc
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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files)

        assert map_.success

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_2"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files)

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files)

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files)

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize(Files)

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_6\n")

    def test_MI_MC_9(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_9_1"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_9\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_9_2"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_9\n")

    def test_MI_MC_10(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_1"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_10\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_2"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        map_.code_add_builds()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_10\n")

    def test_MI_MR_1(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_1"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.extract_code()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_1\n")

    def test_MI_MR_2(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_2"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core())

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_2\n")

    def test_MI_MR_3(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_3_1"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core())

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_3\n")

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_3_2"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.append_core()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_3\n")

    def test_MI_MR_4(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_4"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="find_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        setattr(map_, "rawcore", map_.find_core())

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_4\n")

    def test_MI_MR_6(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_6"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.append_core()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_6\n")


class TestPairMap:
    def test_pair_nocore(self):
        curpath = Path(__file__).resolve()
        mapdir = curpath.parent / "Data/maps_for_test_pairmaps"
        mapdir /= "Pairs/nocore"
        file = mapdir / "parameters.ref"
        file.unlink(missing_ok=True)

        out = self.run_basic_pairmap("nocore")
        coupmap = out[7]["nocore"]
        assert coupmap.success is True

    def test_pair_nocode(self):
        out = self.run_basic_pairmap("nocode")
        coupmap = out[7]["nocode"]
        assert coupmap.success is True

    def test_pair_faultycore(self):
        out = self.run_basic_pairmap("faulty_core")
        coupmap = out[7]["faulty_core"]
        assert coupmap.success is False

    def test_pair_faultyappend(self):
        out = self.run_basic_pairmap("faulty_append_core")
        coupmap = out[7]["faulty_append_core"]
        assert coupmap.success is False

    def test_missing_singles(self, capsys):
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("missing_singles")

        mapdict = {
            map_.name: map_ for map_ in mapdict.values() if map_.success}
        RunPars.available_maps_pairs = mapdict

        requested_mapdict = {
            map_.name: map_ for map_ in mapdict.values()
            if map_.name in RunPars.coupling_v_pair_dict.keys()
        }
        RunPars.requested_pairmapdict = requested_mapdict
        with pytest.raises(GM_Ex.GmapKeyError, match="MI_MC_2$"):
            pairs_mapdict["missing_singles"].check_singles(RunPars)

    def test_missing_pairs(self, capsys):
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("missing_pairs")

        mapdict = {
            map_.name: map_ for map_ in mapdict.values() if map_.success}
        RunPars.available_maps_pairs = mapdict

        requested_mapdict = {
            map_.name: map_ for map_ in mapdict.values()
            if map_.name in RunPars.coupling_v_pair_dict.keys()
        }
        RunPars.requested_pairmapdict = requested_mapdict
        with pytest.raises(GM_Ex.GmapKeyError, match="MI_MC_2$"):
            pairs_mapdict["missing_pairs"].check_pairs(RunPars)

    def test_BWlists(self):
        out = self.run_basic_pairmap("allWL_AmBL")
        coupmap = out[7]["allWL_AmBL"]
        assert coupmap.Core.allowed_singles == []

        out = self.run_basic_pairmap("AmWL_nBL")
        coupmap = out[7]["AmWL_nBL"]
        assert coupmap.Core.allowed_singles == ["AmideSC"]

    def test_valid_combinations(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_pairmaps\\;",
            "--prevent_overwrite", "False",
            "-um", "AmideSC1", "AmideSC2", "AmideSC3", "AmideSC4\\;",
            "--couplings_to_use", "test_valid_combinations_all", ":All\\;",
            "--couplings_to_use", "test_valid_combinations_same_spec",
            ":same\\;",
            "--couplings_to_use", "test_valid_combinations_diff",
            "AmideSC1:AmideSC2\\;",
        ]
        inpardict = {}
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname="x"
        )
        GM_MR.manage_maps_singles(Files, RunPars, mapdict)

        coupmap = pairs_mapdict["test_valid_combinations_all"]
        coupmap.initialize(Files)
        all_singles = ["AmideSC1", "AmideSC2", "AmideSC3", "AmideSC4"]
        for osc1 in all_singles:
            for osc2 in all_singles:
                assert (osc1, osc2) in coupmap.Core.valid_combinations

        coupmap = pairs_mapdict["test_valid_combinations_diff"]
        coupmap.initialize(Files)
        all_singles = ["AmideSC1", "AmideSC2", "AmideSC3", "AmideSC4"]
        for osc1 in all_singles:
            for osc2 in all_singles:
                if osc1 == osc2:
                    assert (osc1, osc2) not in coupmap.Core.valid_combinations
                else:
                    assert (osc1, osc2) in coupmap.Core.valid_combinations

        coupmap = pairs_mapdict["test_valid_combinations_same_spec"]
        coupmap.initialize(Files)
        all_singles = ["AmideSC1", "AmideSC2", "AmideSC3", "AmideSC4"]
        for osc1 in all_singles:
            for osc2 in all_singles:
                if osc1 == osc2:
                    assert (osc1, osc2) in coupmap.Core.valid_combinations
                elif "AmideSC1" in (osc1, osc2):
                    assert (osc1, osc2) in coupmap.Core.valid_combinations
                elif "AmideSC2" in (osc1, osc2) and "AmideSC4" in (osc1, osc2):
                    assert (osc1, osc2) in coupmap.Core.valid_combinations
                else:
                    assert (osc1, osc2) not in coupmap.Core.valid_combinations

    def test_MI_MC_11(self, capsys):
        self.run_basic_pairmap("test_MI_MC_11_1")
        captured = capsys.readouterr()
        assert captured.out.endswith("MI_MC_11\n")

        self.run_basic_pairmap("test_MI_MC_11_2")
        captured = capsys.readouterr()
        assert captured.out.endswith("MI_MC_11\n")

    def test_MI_MM_3(self, capsys):
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("test_MI_MM_3")
        with pytest.raises(GM_Ex.GmapKeyError, match="MI_MM_3$"):
            GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)

    def test_MI_MM_4(self, capsys):
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("test_MI_MM_4")
        with pytest.raises(GM_Ex.GmapKeyError, match="MI_MM_4$"):
            GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)

    def run_basic_pairmap(self, mapname):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_pairmaps\\;",
            "--prevent_overwrite", "False",
            "-um", "AmideSC\\;",
            "--couplings_to_use", mapname, ":All\\;"
        ]
        inpardict = {}
        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )

        GM_MR.manage_maps_singles(Files, RunPars, mapdict)
        pairs_mapdict[mapname].initialize(Files)

        return (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        )

    # def get_basic_vars(self, mapname):
    #     cmdline = [
    #         "-md", "tests/test_tools/Data/maps_for_test_pairmaps\\;",
    #         "--prevent_overwrite", "False"
    #     ]
    #     inpardict = {}

    #     (
    #         Files, RunPars, RefPars, DefPars, InPars, CmdPars,
    #         mapdict, pairs_mapdict
    #     ) = basic_setup(
    #         cmdline, inpardict, finish_before="Core", mapname=mapname
    #     )

    #     map_ = mapdict[mapname]

    #     # Corebase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
    #     # setattr(Corebase, "success", True)

    #     # Corebase.parse_functional_group(
    #     #     map_.rawcore, map_.directory)
    #     _ = basic_setup_core(map_, finish_before=finish_before)


class TestSingleCore:
    def test_parse_functional_group(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        Corebase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
        setattr(Corebase, "success", True)

        Corebase.parse_functional_group(map_.rawcore, map_.directory)

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        Corebase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
        setattr(Corebase, "success", True)

        Corebase.parse_functional_group(map_.rawcore, map_.directory)

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        Corebase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
        setattr(Corebase, "success", True)

        Corebase.parse_functional_group(map_.rawcore, map_.directory)

        found_bonds = [struct.bonds for struct in Corebase.functional_group]
        assert found_bonds == [[[6, 13]]]

    def test_parse_used_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(map_, finish_before="used_atoms")
        setattr(CoreBase, "used_atoms", CoreBase.parse_used_atoms(
            map_.rawcore, map_.directory
        ))
        assert CoreBase.used_atoms == [5, 3, 7, 1, 13, 2, 11]

    def test_parse_estatic_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="estatic_atoms")
        setattr(CoreBase, "electrostatic_atoms", CoreBase.parse_estatic_atoms(
            map_.rawcore, map_.directory
        ))
        assert CoreBase.electrostatic_atoms == [2, 3]

    def test_estatic_atoms_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="estatic_atoms")
        setattr(CoreBase, "electrostatic_atoms", CoreBase.parse_estatic_atoms(
            map_.rawcore, map_.directory
        ))
        assert CoreBase.electrostatic_atoms == []

    def test_parse_estatic_choice(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="estatic_choice")
        setattr(
            CoreBase, "electrostatic_choice", CoreBase.parse_estatic_choice(
                map_.rawcore, map_.directory
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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="estatic_choice")
        setattr(
            CoreBase, "electrostatic_choice", CoreBase.parse_estatic_choice(
                map_.rawcore, map_.directory
            ))
        assert CoreBase.electrostatic_choice is None

    def test_parse_type(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="type")
        setattr(
            CoreBase, "type", CoreBase.parse_type(
                map_.rawcore, map_.directory
            ))
        assert CoreBase.type == "standard"

    def test_type_estat_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="type")
        setattr(
            CoreBase, "type", CoreBase.parse_type(
                map_.rawcore, map_.directory
            ))
        assert CoreBase.type is None

    def test_type_estat_V(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estat_choice_V"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="type")
        setattr(
            CoreBase, "type", CoreBase.parse_type(
                map_.rawcore, map_.directory
            ))
        assert CoreBase.type is None

    def test_parse_local_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="local_atoms")
        setattr(CoreBase, "local_atoms", CoreBase.parse_local_atoms(
            map_.rawcore, map_.directory
        ))
        assert CoreBase.local_atoms == [2, 3]

    def test_local_atoms_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_local_None"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="local_atoms")
        setattr(CoreBase, "local_atoms", CoreBase.parse_local_atoms(
            map_.rawcore, map_.directory
        ))
        assert CoreBase.local_atoms == []

    def test_parse_dipoles(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_maglong"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = CoreBase.parse_dipoles(
            map_.rawcore, map_.directory)
        assert dip_gas == np.float32(0.3)
        assert np.all(dip_arr == np.array([
            [0, 1, 2, 3, 0, 0, 0, 0, 0, 0],
            [5, 6, 7, 8, 0, 0, 0, 0, 0, 0]]))

        # -------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_xyzgood"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = CoreBase.parse_dipoles(
            map_.rawcore, map_.directory)
        assert np.all(dip_gas == np.array([0.3, 0.2, 0.1], dtype="float32"))
        assert np.all(dip_arr == np.array([
            [
                [0, 1, 2, 3, 0, 0, 0, 0, 0, 0],
                [4, 5, 6, 7, 0, 0, 0, 0, 0, 0]
            ], [
                [1, 2, 3, 4, 0, 0, 0, 0, 0, 0],
                [5, 6, 7, 8, 0, 0, 0, 0, 0, 0]
            ], [
                [2, 3, 4, 5, 0, 0, 0, 0, 0, 0],
                [6, 7, 8, 9, 0, 0, 0, 0, 0, 0]]]))

        # ------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_NA"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = CoreBase.parse_dipoles(
            map_.rawcore, map_.directory)
        assert dip_gas == np.float32(0.3)
        assert dip_arr is None

        # ------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_magG"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = CoreBase.parse_dipoles(
            map_.rawcore, map_.directory)
        assert dip_gas == np.float32(0.3)
        assert np.all(dip_arr == np.arange(10, dtype="float32"))

    def test_parse_frequency(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_maglong"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="frequency")
        freq_gas, freq_arr_lin, freq_arr_quad = CoreBase.parse_frequency(
            map_.rawcore, map_.directory)
        assert freq_gas == np.float32(1234)
        assert np.all(freq_arr_lin == np.array([
            [0, 1, 2, 3, 0, 0, 0, 0, 0, 0],
            [5, 6, 7, 8, 0, 0, 0, 0, 0, 0]]))
        assert np.all(freq_arr_quad == np.array([
            [1, 2, 3, 4, 0, 0, 0, 0, 0, 0],
            [6, 7, 8, 9, 0, 0, 0, 0, 0, 0]]))

        # ------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_NA"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="frequency")
        freq_gas, freq_arr_lin, freq_arr_quad = CoreBase.parse_frequency(
            map_.rawcore, map_.directory)
        assert freq_gas == np.float32(1234)
        assert freq_arr_lin is None

        # ------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_magG"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="frequency")
        freq_gas, freq_arr_lin, freq_arr_quad = CoreBase.parse_frequency(
            map_.rawcore, map_.directory)
        assert freq_gas == np.float32(1234)
        assert np.all(freq_arr_lin == np.arange(10, dtype="float32"))

    def test_bohr_consts(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_bohr_const"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="positions")

        assert np.all(CoreBase.dipole_data_array.round(2) == np.array([
            # wrong way?
            # [
            #     [0, 3.571065, 7.14213, 10.713195, 0, 0, 0, 0, 0, 0],
            #     [7.5589046, 17.855324, 21.42639, 24.997456, 0, 0, 0,
            #      0, 0, 0],
            # ], [
            #     [1.8897262, 7.14213, 10.713195, 14.28426, 0, 0, 0, 0, 0, 0],
            #     [9.448631, 21.42639, 24.997456, 28.56852, 0, 0, 0, 0, 0, 0],
            # ], [
            #     [3.7794523, 10.713195, 14.28426, 17.855324, 0, 0, 0,
            #      0, 0, 0],
            #     [11.338357, 24.997456, 28.56852, 32.139584, 0, 0, 0,
            #      0, 0, 0],
            # ]
            [
                [0, 0.280, 0.560, 0.840, 0, 0, 0, 0, 0, 0],
                [2.1167, 1.400, 1.680, 1.960, 0, 0, 0, 0, 0, 0],
            ], [
                [0.529, 0.560, 0.840, 1.120, 0, 0, 0, 0, 0, 0],
                [2.645886, 1.680, 1.960, 2.240, 0, 0, 0, 0, 0, 0],
            ], [
                [1.058, 0.840, 1.120, 1.400, 0, 0, 0, 0, 0, 0],
                [3.175, 1.960, 2.240, 2.520, 0, 0, 0, 0, 0, 0],
            ]
        ], dtype="float32").round(2))

        assert np.all(
            CoreBase.frequency_data_array_linear.round(2) == np.array([
                # [0, 3.571065, 7.14213, 10.713195, 0, 0, 0, 0, 0, 0],
                # [7.5589046, 17.855324, 21.42639, 24.997456, 0, 0, 0,
                #  0, 0, 0],
                [0, 0.280, 0.560, 0.840, 0, 0, 0, 0, 0, 0],
                [2.1167, 1.400, 1.680, 1.960, 0, 0, 0, 0, 0, 0]
            ], dtype="float32").round(2))
        assert CoreBase.frequency_data_array_quadratic is None

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
        ]
        inpardict = {}
        mapname = "test_bohr_const2"

        (
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )
        map_ = mapdict[mapname]
        CoreBase = basic_setup_core(
            map_, finish_before="positions")

        assert np.all(CoreBase.dipole_data_array.round(2) == np.array([
            # [0, 3.571065, 7.14213, 10.713195, 0, 0, 0, 0, 0, 0],
            # [7.5589046, 17.855324, 21.42639, 24.997456, 0, 0, 0, 0, 0, 0],
            [0, 0.280, 0.560, 0.840, 0, 0, 0, 0, 0, 0],
            [2.1167, 1.400, 1.680, 1.960, 0, 0, 0, 0, 0, 0]
        ], dtype="float32").round(2))

        assert np.all(
            CoreBase.frequency_data_array_quadratic.round(2) == np.array([
                # [0, 12.752504, 25.505009, 38.257515, 0, 0, 0, 0, 0, 0],
                # [14.28426, 63.76252, 76.51503, 89.26753, 0, 0, 0, 0, 0, 0],
                [0, 0.078, 0.1568, 0.235, 0, 0, 0, 0, 0, 0],
                [1.120, 0.392, 0.470, 0.548, 0, 0, 0, 0, 0, 0],
            ], dtype="float32").round(2))
        assert CoreBase.frequency_data_array_linear is None

    def test_MI_MC_1(self, capfd):
        self.basis_test_MI_MC("MI_MC_1", capfd, finish_before="used_atoms")

    def test_MI_MC_2(self, capfd):
        self.basis_test_MI_MC("MI_MC_2", capfd, finish_before="used_atoms")

    def test_MI_MC_3(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_3", capfd, "test_MI_MC_3_1", "used_atoms")
        self.basis_test_MI_MC(
            "MI_MC_3", capfd, "test_MI_MC_3_2", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_3", capfd, "test_MI_MC_3_3", "length_units")

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
            "MI_MC_6", capfd, "test_MI_MC_6_1", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_2", "estatic_atoms")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_3", "local_atoms")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_4", "type")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_6", "VEG_reference")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_7", "dipoles")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_8", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_6", capfd, "test_MI_MC_6_9", "length_units")

    def test_MI_MC_7(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_1", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_2", "local_atoms")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_3", "type")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_4", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_5", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_6", "length_units")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_7", "length_units")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_8", "positions")

    def test_MI_MC_8(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_1", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_2", "estatic_atoms")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_3", "local_atoms")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_4", "type")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_5", "VEG_reference")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_6", "dipoles")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_7", "dipoles")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_8", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_9", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_10", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_11", "frequency")
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_12", "length_units")

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
            Files, RunPars, RefPars, DefPars, InPars, CmdPars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="Core", mapname=mapname
        )

        map_ = mapdict[mapname]

        # Corebase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
        # setattr(Corebase, "success", True)

        # Corebase.parse_functional_group(
        #     map_.rawcore, map_.directory)
        _ = basic_setup_core(map_, finish_before=finish_before)

        out, _ = capfd.readouterr()
        assert out.endswith(errcode + "\n")


class Custom():
    def __init__(self, *args):
        for arg in args:
            setattr(self, arg[0], arg[1])


def test_coup_map_dependence(capfd):
    cmdline = []
    inpardict = {
        "map_directory": [Path("Data/maps_for_test_pair-single_dependence")],
        "maps_to_use": ["Sing-hasall"],
        "couplings_to_use": [["NeedsBoth", ":All"]]
    }
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, singles_mapdict, pairs_mapdict
    ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_MR.manage_maps_singles(Files, RunPars, singles_mapdict)
    GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)

    assert len(RunPars.requested_mapdict) == 1
    assert len(RunPars.requested_pairmapdict) == 1


def test_manage_maps_singles():
    # basically the same as GM_PP.get_parameters, but can take list and dict
    # instead of commandline and inparfile
    maplist = ["AmideSC", "AmideBB"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        Files, RunPars, RefPars, DefPars, InPars, CmdPars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    GM_MR.manage_maps_singles(Files, RunPars, mapdict)

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
        Files, RunPars, RefPars, DefPars, InPars, CmdPars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    GM_MR.manage_maps_singles(Files, RunPars, mapdict)

    assert all(
        key in RunPars.requested_mapdict.keys()
        for key in maplist
    )
    assert len(RunPars.requested_mapdict.keys()) == len(maplist)


def test_manage_maps_pairs():
    maplist = ["AmideSC", "AmideBB"]
    inpars = {
        "maps_to_use": maplist,
        "couplings_to_use": [["None", "AmideSC:AmideBB"], ["DipDip", ":same"]]
    }
    (
        Files, RunPars, RefPars, DefPars, InPars, CmdPars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")
    GM_MR.manage_maps_singles(Files, RunPars, mapdict)
    GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)


def test_scan_mapdirs():
    curpath = Path(__file__).resolve()
    mapdir = curpath.parent / "Data/maps_for_test_pair-single_dependence"
    mapdirs = [mapdir]
    found_maps = GM_MR.scan_mapdirs(mapdirs, "doesntexist")
    assert len(found_maps) == 0


def test_map_vac_freq_dip():
    maplist = ["test_vac_dipfreq"]
    inpars = {
        "maps_to_use": maplist,
        "map_directory": ["Data/maps_for_test_MapReader_1"]
    }
    (
        Files, RunPars, RefPars, DefPars, InPars, CmdPars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")
    GM_MR.manage_maps_singles(Files, RunPars, mapdict)

    map_ = mapdict["test_vac_dipfreq"]
    # dipole_gas_phase      0.3

    # frequency_gas_phase   1200
    freq = map_.code.GM_calculate_frequency(map_, None, None)
    assert freq == 1200

    dip_size = map_.code.GM_get_dipole_mag(map_, None, None)
    assert dip_size == np.float32(0.3)


def test_MI_MM_1(capsys):
    maplist = ["AmideSC", "doesntexist"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        Files, RunPars, RefPars, DefPars, InPars, CmdPars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    with pytest.raises(GM_Ex.GmapKeyError, match="MI_MM_1$"):
        GM_MR.manage_maps_singles(Files, RunPars, mapdict)

    # ------------------------------------------------------------------

    maplist = ["AmideSC", "AmideBB"]
    inpars = {
        "maps_to_use": maplist,
        "couplings_to_use": [["doesntexist", ":All"]]
    }
    (
        Files, RunPars, RefPars, DefPars, InPars, CmdPars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")
    GM_MR.manage_maps_singles(Files, RunPars, mapdict)

    with pytest.raises(GM_Ex.GmapKeyError, match="MI_MM_1$"):
        GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)


def test_MI_MM_2(capsys):

    # missing a required/requested keyword
    cmdline = []
    inpardict = {
        "map_directory": [Path("Data/maps_for_test_pair-single_dependence")],
        "maps_to_use": ["Sing-hasfunc"],
        "couplings_to_use": [["NeedsBoth", ":All"]]
    }
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, singles_mapdict, pairs_mapdict
    ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_MR.manage_maps_singles(Files, RunPars, singles_mapdict)
    with pytest.raises(GM_Ex.GmapKeyError, match="MI_MM_2$"):
        GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)

    # ------------------------------------------------------------------

    # missing a required/requested function
    cmdline = []
    inpardict = {
        "map_directory": [Path("Data/maps_for_test_pair-single_dependence")],
        "maps_to_use": ["Sing-haskey"],
        "couplings_to_use": [["NeedsBoth", ":All"]]
    }
    (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, singles_mapdict, pairs_mapdict
    ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_MR.manage_maps_singles(Files, RunPars, singles_mapdict)
    with pytest.raises(GM_Ex.GmapKeyError, match="MI_MM_2$"):
        GM_MR.manage_maps_pairs(Files, RunPars, pairs_mapdict)


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

    RefPars = GM_PP.RefPars(refparfilename, True)
    if defparfilename:
        DefPars = GM_PP.RawPars.from_file(
            defparfilename, RefPars, True)
    else:
        DefPars = RefPars

    curpath = Path(__file__).resolve()
    InPars = GM_PP.RawPars.from_dict(
        curpath, inpardict, RefPars, False
    )

    mapdirs = GM_PP.find_mapdir(Files, cmdline, InPars, DefPars)
    singles_mapdict = GM_MR.scan_mapdirs(mapdirs, "Singles")
    pairs_mapdict = GM_MR.scan_mapdirs(mapdirs, "Pairs")
    mapdict = singles_mapdict | pairs_mapdict

    for map_ in mapdict.values():
        map_.find_refpars()

    CmdPars = GM_PP.RawPars.from_cmdline(
        cmdline, RefPars,
        {name: map_.RefPars for name, map_ in mapdict.items()},
        False
    )

    for map_ in mapdict.values():
        map_.find_rawpars(CmdPars, InPars, DefPars)

    CmdPars.finalize_map_pars()
    InPars.finalize_map_pars()
    if DefPars.fname != RefPars.fname:
        DefPars.finalize_map_pars()

    RunPars = GM_PP.RunPars(
        Files, CmdPars, InPars, DefPars, RefPars, True
    )

    for map_ in mapdict.values():
        map_.find_runpars(Files, RunPars)

    returntuple = (
        Files, RunPars, RefPars, DefPars, InPars,
        CmdPars, singles_mapdict, pairs_mapdict
    )

    if finish_before == "extract_code":
        return returntuple
    # ------------------------------------------------------------------

    map_ = singles_mapdict[mapname]
    setattr(map_, "code", map_.extract_code())
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

    map_.code.GM_adjust_RunPars(Files, map_)

    if finish_before == "find_core":
        return returntuple
    # ------------------------------------------------------------------

    setattr(map_, "rawcore", map_.find_core())

    if finish_before == "append_core":
        return returntuple
    # ------------------------------------------------------------------

    map_.append_core()
    map_.code.GM_adjust_map_core_raw(Files, map_)

    if finish_before == "Core":
        return returntuple

    setattr(map_, "Core", GM_MR.SingleCore(map_))

    if finish_before == "code_add_builds":
        return returntuple

    map_.code_add_builds()

    return returntuple


def basic_setup_core(map_, finish_before=None):
    CoreBase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
    setattr(CoreBase, "success", True)

    setattr(CoreBase, "can_output", CoreBase.parse_can_output(
        map_.rawcore, map_.RunPars, map_.directory))
    if finish_before == "func_group":
        return CoreBase

    CoreBase.parse_functional_group(map_.rawcore, map_.directory)
    if finish_before == "used_atoms":
        return CoreBase

    setattr(CoreBase, "used_atoms", CoreBase.parse_used_atoms(
        map_.rawcore, map_.directory))
    if finish_before == "estatic_choice":
        return CoreBase

    setattr(CoreBase, "electrostatic_choice", CoreBase.parse_estatic_choice(
        map_.rawcore, map_.directory))
    if finish_before == "estatic_atoms":
        return CoreBase

    setattr(CoreBase, "electrostatic_atoms", CoreBase.parse_estatic_atoms(
        map_.rawcore, map_.directory))
    if finish_before == "local_atoms":
        return CoreBase

    setattr(CoreBase, "local_atoms", CoreBase.parse_local_atoms(
        map_.rawcore, map_.directory))
    if finish_before == "type":
        return CoreBase

    setattr(CoreBase, "type", CoreBase.parse_type(
        map_.rawcore, map_.directory))
    if finish_before == "VEG_reference":
        return CoreBase

    CoreBase.check_VEG_reference(map_.rawcore, map_.directory)
    if finish_before == "dipoles":
        return CoreBase

    dipgas, arr = CoreBase.parse_dipoles(map_.rawcore, map_.directory)
    setattr(CoreBase, "dipole_gas_phase", dipgas)
    setattr(CoreBase, "dipole_data_array", arr)

    if finish_before == "frequency":
        return CoreBase

    freqgas, arr_lin, arr_quad = CoreBase.parse_frequency(
        map_.rawcore, map_.directory)
    setattr(CoreBase, "frequency_gas_phase", freqgas)
    setattr(CoreBase, "frequency_data_array_linear", arr_lin)
    setattr(CoreBase, "frequency_data_array_quadratic", arr_quad)

    if finish_before == "length_units":
        return CoreBase

    setattr(CoreBase, "length_units", CoreBase.parse_length_units(
        map_.rawcore, map_.directory))

    if finish_before == "change_arrays":
        return CoreBase

    CoreBase.change_map_units_decision()

    if finish_before == "positions":  # so we can ctrl+F later
        return CoreBase

    CoreBase.parse_positions(map_.rawcore, map_.directory)

    if finish_before == "end":
        return CoreBase
