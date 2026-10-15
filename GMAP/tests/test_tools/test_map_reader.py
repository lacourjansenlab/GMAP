"""
Tests all the functions/classes/methods in the file:
src/tools/physics_functions.py.

Missing tests:

(@ January 10nd '25):
330-338, 1603  (5 missed statements)

(CUHTAT - currently unknown how to access this )

- Map.append_core() - there was some issue with the corefile (CUHTAT)
  (330-338)
  Any stuff wrong with the corefile will have its own warning call (and not
  use raise) - MI_MC_5
- The structure of the map has no bonds (but the parameter giving bonds has
  been used) (1603)

"""


# standard lib imports
from pathlib import Path

# 3rd party imports
import pytest
import numpy as np

# local imports
import GMAP.src.tools.default_map_functions as GM_dmf
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.math_functions as GM_mf
import GMAP.src.tools.map_reader as GM_mr
import GMAP.src.tools.parameter_parser as GM_pp


class TestCode:
    def test_extract_code(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        mapname = "test_extract_code"
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code())

        assert map_.code.for_testing(4) == 6

    def test_extract_code_nocode(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        mapname = "test_extract_code_nocode"
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code())

        assert hasattr(map_.code, "for_testing") is False

    def test_GM_adjust_run_pars_custom(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_extract_code"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parss,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="adjust_run_pars",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        assert run_pars.neutral_charge_threshold == 0.0001
        map_.code.GM_adjust_run_pars(map_)
        assert run_pars.neutral_charge_threshold == 0.02

    def test_GM_adjust_run_pars_default(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_extract_code_nocode"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parss,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="adjust_run_pars",
            mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]
        setattr(map_, "code", map_.extract_code())
        if not map_.code:
            setattr(map_, "code", GM_dmf.NewModule())

        assert hasattr(map_.code, "GM_adjust_run_pars") is False
        map_.complete_code((
            "adjust_run_pars",
            "adjust_map_core_raw",
            "adjust_oscillators"
        ))
        assert hasattr(map_.code, "GM_adjust_run_pars") is True

    def test_find_core(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_find_core"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parsss,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;",
            "--prevent_overwrite", "False"
        ]
        inpardict = {}
        mapname = "test_unicodedecodeerror_core"
        fhand = open(
            "tests/test_tools/Data/maps_for_test_map_reader_1/Singles/"
            + mapname + "/core.txt", 'wb'
        )

        # Add some non-UTF-8 characters to the file.
        fhand.write(b'\x80')
        fhand.write(
            b'\xC0' + b'\xC1' + b'\xF5' + b'\xF6' + b'\xF7' + b'\xF8'
            + b'\xF9'
            + b'\xFA' + b'\xFB' + b'\xFC' + b'\xFD' + b'\xFE' + b'\xFF')
        fhand.close()

        (_, _, _, _, _, mapdict, pairs_mapdict) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )
        map_ = mapdict[mapname]

        # setattr(map_, "core", GM_MR.SingleCore(map_))
        assert not map_.success
        out, _ = capfd.readouterr()
        assert out.endswith("SU_FH_3\n")

    def test_append_core(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_appending"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parss,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "core", GM_mr.SingleCore(map_))

        assert map_.core.type == "standard"
        found_residues = [
            [residue.resnames for residue in struct.residues]
            for struct in map_.core.functional_group
        ]
        assert found_residues == [[["CYS"], ["DEF"]], [["A", "B"]]]

    def test_core_unsuccessful_returns(self, capfd):

        # if not self.success after parse_used_atoms, parse_estatic_atoms,
        # parse_estatic_choice and parse_type
        for i in range(1, 5):
            cmdline = [
                "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
            ]
            inpardict = {}
            mapname = f"test_MI_MC_6_{i}"

            (_, _, _, _, _, mapdict, _) = basic_setup(
                cmdline, inpardict, finish_before="core", mapname=mapname
            )
            map_ = mapdict[mapname]

            setattr(map_, "core", GM_mr.SingleCore(map_))

            out, _ = capfd.readouterr()
            assert out.endswith("MI_MC_6\n")

        # if not self.success after parse_functional_group
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_2"
        (_, _, _, _, _, mapdict, _) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "core", GM_mr.SingleCore(map_))

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_2\n")

        # using a map without estatic_atoms
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"
        (_, _, _, _, _, mapdict, _) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]

        setattr(map_, "core", GM_mr.SingleCore(map_))

        assert map_.core.electrostatic_atoms == []
        assert map_.core.electrostatic_choice is None

    def test_code_add_builds_1(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;",
            "--verbose", "4", "--verbose_logfile", "4"
        ]
        inpardict = {}
        mapname = "test_code_build_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array([[10, 0, 0], [0, 10, 0], [0, 0, 10]])
        system = Custom(
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
            ["positions_box", positions @ system.boxvects_inv]
        )

        map_.code_add_builds()
        r_vec, r_pos = map_.code.GM_get_dipole_dir(
            map_, system, osc
        )
        r_vec_dir = np.array([-1.5, 1, 0])  # not normalized
        r_vec_dir /= np.linalg.norm(r_vec_dir)
        r_vec_dir = r_vec_dir.astype("float32")
        assert (np.round(r_vec, 4) == np.round(r_vec_dir, 4)).all()

        assert (
            np.round(r_pos, 4) == np.round(np.array([3.75, 0.5, 0]), 4)
        ).all()

        rotation_matrix = np.round(map_.code.GM_get_rotation_matrix(
            map_, system, osc
        ), 4)

        xvec = np.array([1.5, 1, 0])
        xvec /= GM_mf.vec3_len(xvec)
        yvec = GM_mf.project(xvec, np.array([-1.5, 1, 0]))
        yvec /= GM_mf.vec3_len(yvec)
        zvec = GM_mf.crossprod(xvec, yvec)
        zvec /= GM_mf.vec3_len(zvec)

        test_matrix = np.round(np.array([xvec, yvec, zvec]), 4)
        assert (rotation_matrix == test_matrix).all()

    def test_code_add_builds_2(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_code_build_2"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array(
            [[5, 0, 0], [4, 3, 0], [2, 2, 4]], dtype="float32")
        system = Custom(
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
            ["positions_box", positions @ system.boxvects_inv]
        )

        map_.code_add_builds()
        r_vec, r_pos = map_.code.GM_get_dipole_dir(
            map_, system, osc
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
            map_, system, osc
        ), 4)

        zvec = np.array([0, 2, 0], dtype=np.float64)
        zvec /= GM_mf.vec3_len(zvec)
        yvec = GM_mf.project(zvec, np.array([1.5, -1, 0]))
        yvec /= GM_mf.vec3_len(yvec)
        xvec = GM_mf.crossprod(zvec, yvec)
        xvec /= GM_mf.vec3_len(xvec)

        test_matrix = np.round(np.array([xvec, yvec, zvec]), 4)
        assert (rotation_matrix == test_matrix).all()

    def test_code_add_builds_3(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_code_build_3"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="code_add_builds",
            mapname=mapname
        )
        map_ = mapdict[mapname]

        boxvects = np.array(
            [[5, 0, 0], [4, 3, 0], [2, 2, 4]], dtype="float32")
        system = Custom(
            ["boxvects", boxvects],
            ["boxvects_inv", np.linalg.inv(boxvects)]
        )

        positions = np.array([
            [0, 0, 0],
            [1, 1, 1],
            [2, 2, 2]
        ], dtype="float32")
        osc = Custom(
            ["positions_box", positions @ system.boxvects_inv]
        )

        map_.code_add_builds()
        r_vec, r_pos = map_.code.GM_get_dipole_dir(
            map_, system, osc
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
            map_, system, osc
        ), 4)

        zvec = np.array([2, 2, 2], dtype=np.float64)
        zvec /= GM_mf.vec3_len(zvec)
        xvec = GM_mf.project(zvec, np.array([1, 0, 0]))
        xvec /= GM_mf.vec3_len(xvec)
        yvec = GM_mf.crossprod(zvec, xvec)
        yvec /= GM_mf.vec3_len(yvec)

        test_matrix = np.round(np.array([xvec, yvec, zvec]), 4)
        assert (rotation_matrix == test_matrix).all()

    def test_initialize(self, capfd):

        # we tested all substeps, now just to confirm the totality runs, too
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_code_build_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize()

        assert map_.success

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_2"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize()

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_2\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_6"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize()

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_6\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize()

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_1\n")

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize()

        assert not map_.success

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MC_10\n")

    def test_MI_MC_6(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_6_5"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_9_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_9_2"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MC_10_2"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.extract_code()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_1\n")

    def test_MI_MR_2(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_2"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_3_1"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_3_2"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_4"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_6"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="append_core", mapname=mapname
        )

        # only test the map made for testing this funtionality
        map_ = mapdict[mapname]

        map_.append_core()

        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_6\n")

    def test_MI_MR_7(self, capfd):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_MI_MR_7"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )
        map_ = mapdict[mapname]
        map_.initialize()
        out, _ = capfd.readouterr()
        assert out.endswith("MI_MR_7\n")


class TestPairMap:
    def test_pair_nocore(self):
        curpath = Path(__file__).resolve()
        mapdir = curpath.parent / "Data/maps_for_test_pairmaps"
        mapdir /= "Pairs/nocore"
        file = mapdir / "parameters.ref"
        file.unlink(missing_ok=True)

        out = self.run_basic_pairmap("nocore")
        coupmap = out[6]["nocore"]
        assert coupmap.success is True

    def test_pair_nocode(self):
        out = self.run_basic_pairmap("nocode")
        coupmap = out[6]["nocode"]
        assert coupmap.success is True

    def test_pair_faultycore(self):
        out = self.run_basic_pairmap("faulty_core")
        coupmap = out[6]["faulty_core"]
        assert coupmap.success is False

    def test_pair_faultyappend(self):
        out = self.run_basic_pairmap("faulty_append_core")
        coupmap = out[6]["faulty_append_core"]
        assert coupmap.success is False

    def test_missing_singles(self, capsys):
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("missing_singles")

        mapdict = {
            map_.name: map_ for map_ in mapdict.values() if map_.success}
        run_pars.available_maps_pairs = mapdict

        requested_mapdict = {
            map_.name: map_ for map_ in mapdict.values()
            if map_.name in run_pars.coupling_v_pair_dict.keys()
        }
        run_pars.requested_pairmapdict = requested_mapdict
        with pytest.raises(GM_ex.GmapKeyError, match="MI_MC_2$"):
            pairs_mapdict["missing_singles"].check_singles(run_pars)

    def test_missing_pairs(self, capsys):
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("missing_pairs")

        mapdict = {
            map_.name: map_ for map_ in mapdict.values() if map_.success}
        run_pars.available_maps_pairs = mapdict

        requested_mapdict = {
            map_.name: map_ for map_ in mapdict.values()
            if map_.name in run_pars.coupling_v_pair_dict.keys()
        }
        run_pars.requested_pairmapdict = requested_mapdict
        with pytest.raises(GM_ex.GmapKeyError, match="MI_MC_2$"):
            pairs_mapdict["missing_pairs"].check_pairs(run_pars)

    def test_BWlists(self):
        out = self.run_basic_pairmap("allWL_AmBL")
        coupmap = out[6]["allWL_AmBL"]
        assert coupmap.core.allowed_singles == []

        out = self.run_basic_pairmap("AmWL_nBL")
        coupmap = out[6]["AmWL_nBL"]
        assert coupmap.core.allowed_singles == ["AmideSC"]

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
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname="x"
        )
        GM_mr.manage_maps_singles(run_pars, mapdict)

        coupmap = pairs_mapdict["test_valid_combinations_all"]
        coupmap.initialize()
        all_singles = ["AmideSC1", "AmideSC2", "AmideSC3", "AmideSC4"]
        for osc1 in all_singles:
            for osc2 in all_singles:
                assert (osc1, osc2) in coupmap.core.valid_combinations

        coupmap = pairs_mapdict["test_valid_combinations_diff"]
        coupmap.initialize()
        all_singles = ["AmideSC1", "AmideSC2", "AmideSC3", "AmideSC4"]
        for osc1 in all_singles:
            for osc2 in all_singles:
                if osc1 == osc2:
                    assert (osc1, osc2) not in coupmap.core.valid_combinations
                else:
                    assert (osc1, osc2) in coupmap.core.valid_combinations

        coupmap = pairs_mapdict["test_valid_combinations_same_spec"]
        coupmap.initialize()
        all_singles = ["AmideSC1", "AmideSC2", "AmideSC3", "AmideSC4"]
        for osc1 in all_singles:
            for osc2 in all_singles:
                if osc1 == osc2:
                    assert (osc1, osc2) in coupmap.core.valid_combinations
                elif "AmideSC1" in (osc1, osc2):
                    assert (osc1, osc2) in coupmap.core.valid_combinations
                elif "AmideSC2" in (osc1, osc2) and "AmideSC4" in (osc1, osc2):
                    assert (osc1, osc2) in coupmap.core.valid_combinations
                else:
                    assert (osc1, osc2) not in coupmap.core.valid_combinations

    def test_MI_MC_11(self, capsys):
        self.run_basic_pairmap("test_MI_MC_11_1")
        captured = capsys.readouterr()
        assert captured.out.endswith("MI_MC_11\n")

        self.run_basic_pairmap("test_MI_MC_11_2")
        captured = capsys.readouterr()
        assert captured.out.endswith("MI_MC_11\n")

    def test_MI_MM_3(self, capsys):
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("test_MI_MM_3")
        with pytest.raises(GM_ex.GmapKeyError, match="MI_MM_3$"):
            GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)

    def test_MI_MM_4(self, capsys):
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = self.run_basic_pairmap("test_MI_MM_4")
        with pytest.raises(GM_ex.GmapKeyError, match="MI_MM_4$"):
            GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)

    def run_basic_pairmap(self, mapname):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_pairmaps\\;",
            "--prevent_overwrite", "False",
            "-um", "AmideSC\\;",
            "--couplings_to_use", mapname, ":All\\;"
        ]
        inpardict = {}
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="extract_code", mapname=mapname
        )

        GM_mr.manage_maps_singles(run_pars, mapdict)
        pairs_mapdict[mapname].initialize()

        return (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        )

    # def get_basic_vars(self, mapname):
    #     cmdline = [
    #         "-md", "tests/test_tools/Data/maps_for_test_pairmaps\\;",
    #         "--prevent_overwrite", "False"
    #     ]
    #     inpardict = {}

    #     (
    #         run_pars, ref_pars, def_pars, in_pars, cmd_pars,
    #         mapdict, pairs_mapdict
    #     ) = basic_setup(
    #         cmdline, inpardict, finish_before="core", mapname=mapname
    #     )

    #     map_ = mapdict[mapname]

    #     # corebase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
    #     # setattr(corebase, "success", True)

    #     # corebase.parse_functional_group(
    #     #     map_.rawcore, map_.directory)
    #     _ = basic_setup_core(map_, finish_before=finish_before)


class TestSingleCore:
    # ham first values true and false are tested in these maps:
    # test_core   (ham_first   True)
    # test_funcgroupfile  (ham_first    f)
    def test_parse_functional_group(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parss,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )

        map_ = mapdict[mapname]

        corebase = GM_mr.SingleCore.__new__(GM_mr.SingleCore)
        setattr(corebase, "success", True)

        corebase.parse_functional_group(map_.rawcore, map_.directory)

        found_residues = [
            [residue.resnames for residue in struct.residues]
            for struct in corebase.functional_group
        ]
        assert found_residues == [[["CYS"], ["DEF"]], [["A", "B"]]]

        found_bonds = [struct.bonds for struct in corebase.functional_group]
        assert found_bonds == [[[6, 13]], []]

        found_atoms = [
            [residue.atoms for residue in struct.residues]
            for struct in corebase.functional_group
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

        struct = corebase.functional_group[0]
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_funcgroupfile"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )

        map_ = mapdict[mapname]

        corebase = GM_mr.SingleCore.__new__(GM_mr.SingleCore)
        setattr(corebase, "success", True)

        corebase.parse_functional_group(map_.rawcore, map_.directory)

        found_residues = [
            [residue.resnames for residue in struct.residues]
            for struct in corebase.functional_group
        ]
        assert found_residues == [[["ASN"]], [["GLN"]]]

        found_bonds = [struct.bonds for struct in corebase.functional_group]
        assert found_bonds == [[], []]

        found_atoms = [
            [residue.atoms for residue in struct.residues]
            for struct in corebase.functional_group
        ]
        assert found_atoms == [
            [[["CG"], ["OD1"], ["CB"], ["ND2"], ["HD21"], ["HD22"]]],
            [[["CD"], ["OE1"], ["CG"], ["NE2"], ["HE21"], ["HE22"]]]
        ]

    def test_parse_functional_group_bonds(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_funcgroup_bonded"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parss,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )

        map_ = mapdict[mapname]

        corebase = GM_mr.SingleCore.__new__(GM_mr.SingleCore)
        setattr(corebase, "success", True)

        corebase.parse_functional_group(map_.rawcore, map_.directory)

        found_bonds = [struct.bonds for struct in corebase.functional_group]
        assert found_bonds == [[[6, 13]]]

    def test_allow_ranges(self):
        # Should test for cases:
        # "All", "alL", "0-12","0-6,5-11","13-10", "5101870-3"
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_AllowRanges"
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parss,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(map_, finish_before="used_atoms")
        setattr(corebase, "used_atoms", corebase.parse_used_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.used_atoms == [5, 3, 7, 8, 9, 10, 11, 12, 13]

        map_.rawcore["used_atoms"] = ["All"]
        corebase = basic_setup_core(map_, finish_before="used_atoms")
        setattr(corebase, "used_atoms", corebase.parse_used_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.used_atoms == [i for i in range(14)]

        map_.rawcore["used_atoms"] = ["0-12"]
        corebase = basic_setup_core(map_, finish_before="used_atoms")
        setattr(corebase, "used_atoms", corebase.parse_used_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.used_atoms == [i for i in range(13)]

        map_.rawcore["used_atoms"] = ["12-0"]
        corebase = basic_setup_core(map_, finish_before="used_atoms")
        setattr(corebase, "used_atoms", corebase.parse_used_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.used_atoms == [i for i in range(12, -1, -1)]

    def test_parse_used_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_parss,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(map_, finish_before="used_atoms")
        setattr(corebase, "used_atoms", corebase.parse_used_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.used_atoms == [5, 3, 7, 1, 13, 2, 11]

    def test_parse_estatic_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="estatic_atoms")
        setattr(corebase, "electrostatic_atoms", corebase.parse_estatic_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.electrostatic_atoms == [2, 3]

    def test_estatic_atoms_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="estatic_atoms")
        setattr(corebase, "electrostatic_atoms", corebase.parse_estatic_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.electrostatic_atoms == []

    def test_parse_estatic_choice(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="estatic_choice")
        setattr(
            corebase, "electrostatic_choice", corebase.parse_estatic_choice(
                map_.rawcore, map_.directory
            ))
        assert corebase.electrostatic_choice == "E"

    # tests something normal program flow could never reach
    def test_estatic_choice_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            run_parss, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="estatic_choice")
        setattr(
            corebase, "electrostatic_choice", corebase.parse_estatic_choice(
                map_.rawcore, map_.directory
            ))
        assert corebase.electrostatic_choice is None

    def test_parse_type(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            run_parss, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="type")
        setattr(
            corebase, "type", corebase.parse_type(
                map_.rawcore, map_.directory
            ))
        assert corebase.type == "standard"

    def test_type_estat_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estatic_None"

        (
            run_parss, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="type")
        setattr(
            corebase, "type", corebase.parse_type(
                map_.rawcore, map_.directory
            ))
        assert corebase.type is None

    def test_type_estat_V(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_estat_choice_V"

        (
            run_parss, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="type")
        setattr(
            corebase, "type", corebase.parse_type(
                map_.rawcore, map_.directory
            ))
        assert corebase.type is None

    def test_parse_local_atoms(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_Core"

        (
            run_parss, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="local_atoms")
        setattr(corebase, "local_atoms", corebase.parse_local_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.local_atoms == [2, 3]

    def test_local_atoms_None(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_local_None"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="local_atoms")
        setattr(corebase, "local_atoms", corebase.parse_local_atoms(
            map_.rawcore, map_.directory
        ))
        assert corebase.local_atoms == []

    def test_parse_dipoles(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_maglong"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = corebase.parse_dipoles(
            map_.rawcore, map_.directory)
        assert dip_gas == np.float32(0.3)
        assert np.all(dip_arr == np.array([
            [0, 1, 2, 3, 0, 0, 0, 0, 0, 0],
            [5, 6, 7, 8, 0, 0, 0, 0, 0, 0]]))

        # -------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_xyzgood"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = corebase.parse_dipoles(
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_NA"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = corebase.parse_dipoles(
            map_.rawcore, map_.directory)
        assert dip_gas == np.float32(0.3)
        assert dip_arr is None

        # ------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_magG"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="dipoles")
        dip_gas, dip_arr = corebase.parse_dipoles(
            map_.rawcore, map_.directory)
        assert dip_gas == np.float32(0.3)
        assert np.all(dip_arr == np.arange(10, dtype="float32"))

    def test_parse_frequency(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_maglong"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="frequency")
        freq_gas, freq_arr_lin, freq_arr_quad = corebase.parse_frequency(
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
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_NA"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="frequency")
        freq_gas, freq_arr_lin, freq_arr_quad = corebase.parse_frequency(
            map_.rawcore, map_.directory)
        assert freq_gas == np.float32(1234)
        assert freq_arr_lin is None

        # ------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_dipoles_datafile_magG"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="frequency")
        freq_gas, freq_arr_lin, freq_arr_quad = corebase.parse_frequency(
            map_.rawcore, map_.directory)
        assert freq_gas == np.float32(1234)
        assert np.all(freq_arr_lin == np.arange(10, dtype="float32"))

    def test_bohr_consts(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_bohr_const"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="positions")

        assert np.all(corebase.dipole_data_array.round(2) == np.array([
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
            corebase.frequency_data_array_linear.round(2) == np.array([
                # [0, 3.571065, 7.14213, 10.713195, 0, 0, 0, 0, 0, 0],
                # [7.5589046, 17.855324, 21.42639, 24.997456, 0, 0, 0,
                #  0, 0, 0],
                [0, 0.280, 0.560, 0.840, 0, 0, 0, 0, 0, 0],
                [2.1167, 1.400, 1.680, 1.960, 0, 0, 0, 0, 0, 0]
            ], dtype="float32").round(2))
        assert corebase.frequency_data_array_quadratic is None

        # --------------------------------------------------------------

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_bohr_const2"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="positions")

        assert np.all(corebase.dipole_data_array.round(2) == np.array([
            # [0, 3.571065, 7.14213, 10.713195, 0, 0, 0, 0, 0, 0],
            # [7.5589046, 17.855324, 21.42639, 24.997456, 0, 0, 0, 0, 0, 0],
            [0, 0.280, 0.560, 0.840, 0, 0, 0, 0, 0, 0],
            [2.1167, 1.400, 1.680, 1.960, 0, 0, 0, 0, 0, 0]
        ], dtype="float32").round(2))

        assert np.all(
            corebase.frequency_data_array_quadratic.round(2) == np.array([
                # [0, 12.752504, 25.505009, 38.257515, 0, 0, 0, 0, 0, 0],
                # [14.28426, 63.76252, 76.51503, 89.26753, 0, 0, 0, 0, 0, 0],
                [0, 0.078, 0.1568, 0.235, 0, 0, 0, 0, 0, 0],
                [1.120, 0.392, 0.470, 0.548, 0, 0, 0, 0, 0, 0],
            ], dtype="float32").round(2))
        assert corebase.frequency_data_array_linear is None

    def test_freqmult(self):

        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_freqmult"

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="positions")

        assert np.all(
            corebase.frequency_data_array_linear == np.array([
                [0, 2, 4, 6, 0, 0, 0, 0, 0, 0],
                [8, 10, 12, 14, 0, 0, 0, 0, 0, 0]
            ], dtype="float32").round(2))

    def test_posonlymap(self):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
        ]
        inpardict = {}
        mapname = "test_posonly"
        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )
        map_ = mapdict[mapname]
        corebase = basic_setup_core(
            map_, finish_before="end")
        assert corebase.success

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
            "MI_MC_7", capfd, "test_MI_MC_7_8", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_9", "estatic_choice")
        self.basis_test_MI_MC(
            "MI_MC_7", capfd, "test_MI_MC_7_10", "estatic_choice")

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
        self.basis_test_MI_MC(
            "MI_MC_8", capfd, "test_MI_MC_8_13", "estatic_choice")

    def test_MI_MC_9(self, capfd):
        self.basis_test_MI_MC("MI_MC_9", capfd, finish_before="used_atoms")

    def test_MI_MC_12(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_12", capfd, "test_MI_MC_12_1", "ham_first")
        self.basis_test_MI_MC(
            "MI_MC_12", capfd, "test_MI_MC_12_2", "func_group")
        self.basis_test_MI_MC(
            "MI_MC_12", capfd, "test_MI_MC_12_3", "positions")

    def test_MI_MC_13(self, capfd):
        self.basis_test_MI_MC(
            "MI_MC_13", capfd, "test_MI_MC_13_1", "positions")
        self.basis_test_MI_MC(
            "MI_MC_13", capfd, "test_MI_MC_13_2", "positions")

    def basis_test_MI_MC(
        self, errcode, capfd, mapname=None, finish_before=None
    ):
        cmdline = [
            "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;",
            "--prevent_overwrite", "False"
        ]
        inpardict = {}
        if mapname is None:
            mapname = "test_" + errcode

        (
            run_pars, ref_pars, def_pars, in_pars, cmd_pars,
            mapdict, pairs_mapdict
        ) = basic_setup(
            cmdline, inpardict, finish_before="core", mapname=mapname
        )

        map_ = mapdict[mapname]

        # corebase = GM_MR.SingleCore.__new__(GM_MR.SingleCore)
        # setattr(corebase, "success", True)

        # corebase.parse_functional_group(
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
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, singles_mapdict, pairs_mapdict
    ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_mr.manage_maps_singles(run_pars, singles_mapdict)
    GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)

    assert len(run_pars.requested_mapdict) == 1
    assert len(run_pars.requested_pairmapdict) == 1


def test_manage_maps_singles():
    # basically the same as GM_PP.get_parameters, but can take list and dict
    # instead of commandline and inparfile
    maplist = ["AmideSC", "AmideBB"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    GM_mr.manage_maps_singles(run_pars, mapdict)

    assert all(
        key in run_pars.requested_mapdict.keys()
        for key in maplist
    )
    assert len(run_pars.requested_mapdict.keys()) == len(maplist)

    # ---

    maplist = ["AmideSC"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    GM_mr.manage_maps_singles(run_pars, mapdict)

    assert all(
        key in run_pars.requested_mapdict.keys()
        for key in maplist
    )
    assert len(run_pars.requested_mapdict.keys()) == len(maplist)


def test_manage_maps_pairs():
    maplist = ["AmideSC", "AmideBB"]
    inpars = {
        "maps_to_use": maplist,
        "couplings_to_use": [["None", "AmideSC:AmideBB"], ["DipDip", ":same"]]
    }
    (
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")
    GM_mr.manage_maps_singles(run_pars, mapdict)
    GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)


def test_scan_mapdirs():
    curpath = Path(__file__).resolve()
    mapdir = curpath.parent / "Data/maps_for_test_pair-single_dependence"
    mapdirs = [mapdir]
    found_maps = GM_mr.scan_mapdirs(mapdirs, "doesntexist")
    assert len(found_maps) == 0


def test_map_vac_freq_dip():
    maplist = ["test_vac_dipfreq"]
    inpars = {
        "maps_to_use": maplist,
        "map_directory": ["Data/maps_for_test_map_reader_1"]
    }
    (
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")
    GM_mr.manage_maps_singles(run_pars, mapdict)

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
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")

    with pytest.raises(GM_ex.GmapKeyError, match="MI_MM_1$"):
        GM_mr.manage_maps_singles(run_pars, mapdict)

    # ------------------------------------------------------------------

    maplist = ["AmideSC", "AmideBB"]
    inpars = {
        "maps_to_use": maplist,
        "couplings_to_use": [["doesntexist", ":All"]]
    }
    (
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup([], inpars, finish_before="extract_code")
    GM_mr.manage_maps_singles(run_pars, mapdict)

    with pytest.raises(GM_ex.GmapKeyError, match="MI_MM_1$"):
        GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)


def test_MI_MM_2(capsys):

    # missing a required/requested keyword
    cmdline = []
    inpardict = {
        "map_directory": [Path("Data/maps_for_test_pair-single_dependence")],
        "maps_to_use": ["Sing-hasfunc"],
        "couplings_to_use": [["NeedsBoth", ":All"]]
    }
    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, singles_mapdict, pairs_mapdict
    ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_mr.manage_maps_singles(run_pars, singles_mapdict)
    with pytest.raises(GM_ex.GmapKeyError, match="MI_MM_2$"):
        GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)

    # ------------------------------------------------------------------

    # missing a required/requested function
    cmdline = []
    inpardict = {
        "map_directory": [Path("Data/maps_for_test_pair-single_dependence")],
        "maps_to_use": ["Sing-haskey"],
        "couplings_to_use": [["NeedsBoth", ":All"]]
    }
    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, singles_mapdict, pairs_mapdict
    ) = basic_setup(cmdline, inpardict, finish_before="extract_code")

    GM_mr.manage_maps_singles(run_pars, singles_mapdict)
    with pytest.raises(GM_ex.GmapKeyError, match="MI_MM_2$"):
        GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)


def test_MI_MM_5(capsys):
    cmdline = [
        "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;"
    ]
    maplist = ["test_posonly"]
    inpars = {
        "maps_to_use": maplist
    }
    (
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup(cmdline, inpars, finish_before="extract_code")

    with pytest.raises(GM_ex.GmapKeyError, match="MI_MM_5$"):
        GM_mr.manage_maps_singles(run_pars, mapdict)


def basic_setup(
    cmdline, inpardict, defparfilename=None, refparfilename=None,
    finish_before=None, mapname=None, prevent_overwrite=False
):
    """Sets up a map until it has a run_pars (not yet analyzed the core).

    All steps in here are tested by test_parameter_parser.py. If any
    issues occur within this function, run that file alone, first.
    """

    if "--prevent_overwrite" not in cmdline and not prevent_overwrite:
        cmdline.extend(["--prevent_overwrite", "False"])

    if refparfilename is None:
        refparfilename = Path("sourcefiles/reference_parameters.ref")

    ref_pars = GM_pp.RefPars(refparfilename, True)
    if defparfilename:
        def_pars = GM_pp.RawPars.from_file(
            defparfilename, ref_pars, True)
    else:
        def_pars = ref_pars

    curpath = Path(__file__).resolve()
    in_pars = GM_pp.RawPars.from_dict(
        curpath, inpardict, ref_pars, False
    )

    mapdirs = GM_pp.find_mapdir(cmdline, in_pars, def_pars)
    singles_mapdict = GM_mr.scan_mapdirs(mapdirs, "Singles")
    pairs_mapdict = GM_mr.scan_mapdirs(mapdirs, "Pairs")
    mapdict = singles_mapdict | pairs_mapdict

    for map_ in mapdict.values():
        map_.find_refpars()

    cmd_pars = GM_pp.RawPars.from_cmdline(
        cmdline, ref_pars,
        {name: map_.ref_pars for name, map_ in mapdict.items()},
        False
    )

    for map_ in mapdict.values():
        map_.find_rawpars(cmd_pars, in_pars, def_pars)

    cmd_pars.finalize_map_pars()
    in_pars.finalize_map_pars()
    if def_pars.fname != ref_pars.fname:
        def_pars.finalize_map_pars()

    run_pars = GM_pp.RunPars(
        cmd_pars, in_pars, def_pars, ref_pars, True
    )

    for map_ in mapdict.values():
        map_.find_runpars(run_pars)

    returntuple = (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, singles_mapdict, pairs_mapdict
    )

    if finish_before == "extract_code":
        return returntuple
    # ------------------------------------------------------------------

    map_ = singles_mapdict[mapname]
    setattr(map_, "code", map_.extract_code())
    if not map_.code:
        setattr(map_, "code", GM_dmf.NewModule())

    map_.complete_code((
        "adjust_run_pars",
        "adjust_map_core_raw",
        "adjust_oscillators"
    ))

    if finish_before == "adjust_run_pars":
        return returntuple
    # ------------------------------------------------------------------

    map_.code.GM_adjust_run_pars(map_)

    if finish_before == "find_core":
        return returntuple
    # ------------------------------------------------------------------

    setattr(map_, "rawcore", map_.find_core())

    if finish_before == "append_core":
        return returntuple
    # ------------------------------------------------------------------

    map_.append_core()
    map_.code.GM_adjust_map_core_raw(map_)

    if finish_before == "core":
        return returntuple

    setattr(map_, "core", GM_mr.SingleCore(map_))

    if finish_before == "code_add_builds":
        return returntuple

    map_.code_add_builds()

    return returntuple


def basic_setup_core(map_, finish_before=None):
    corebase = GM_mr.SingleCore.__new__(GM_mr.SingleCore)
    setattr(corebase, "success", True)

    setattr(corebase, "can_output", corebase.parse_can_output(
        map_.rawcore, map_.run_pars, map_.directory))
    if finish_before == "ham_first":
        return corebase

    setattr(corebase, "ham_first", corebase.parse_ham_first(
        map_.rawcore, map_.directory))
    if finish_before == "func_group":
        return corebase

    corebase.parse_functional_group(map_.rawcore, map_.directory)
    if finish_before == "used_atoms":
        return corebase

    setattr(corebase, "used_atoms", corebase.parse_used_atoms(
        map_.rawcore, map_.directory))
    if finish_before == "estatic_choice":
        return corebase

    setattr(corebase, "electrostatic_choice", corebase.parse_estatic_choice(
        map_.rawcore, map_.directory))
    if finish_before == "estatic_atoms":
        return corebase

    setattr(corebase, "electrostatic_atoms", corebase.parse_estatic_atoms(
        map_.rawcore, map_.directory))
    if finish_before == "local_atoms":
        return corebase

    setattr(corebase, "local_atoms", corebase.parse_local_atoms(
        map_.rawcore, map_.directory))
    if finish_before == "type":
        return corebase

    setattr(corebase, "type", corebase.parse_type(
        map_.rawcore, map_.directory))
    if finish_before == "VEG_reference":
        return corebase

    corebase.check_VEG_reference(map_.rawcore, map_.directory)
    if finish_before == "dipoles":
        return corebase

    dipgas, arr = corebase.parse_dipoles(map_.rawcore, map_.directory)
    setattr(corebase, "dipole_gas_phase", dipgas)
    setattr(corebase, "dipole_data_array", arr)

    if finish_before == "frequency":
        return corebase

    freqgas, arr_lin, arr_quad = corebase.parse_frequency(
        map_.rawcore, map_.directory)
    setattr(corebase, "frequency_gas_phase", freqgas)
    setattr(corebase, "frequency_data_array_linear", arr_lin)
    setattr(corebase, "frequency_data_array_quadratic", arr_quad)

    if finish_before == "length_units":
        return corebase

    setattr(corebase, "length_units", corebase.parse_length_units(
        map_.rawcore, map_.directory))

    if finish_before == "freq_multiplier":
        return corebase

    setattr(corebase, "freq_multiplier", corebase.parse_multiply_freq(
        map_.rawcore, map_.directory))

    if finish_before == "change_arrays":
        return corebase

    corebase.change_map_units_decision()

    if finish_before == "positions":  # so we can ctrl+F later
        return corebase

    corebase.parse_positions(map_.rawcore, map_.directory)

    if finish_before == "end":
        return corebase
