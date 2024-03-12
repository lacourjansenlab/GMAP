"""
tests still missing, and why:

- MI_MR_5 - unsure how to trigger.
"""


# standard lib imports
from pathlib import Path

# 3rd party imports
# import pytest

# local imports
import GMAP.src.tools.DefaultMapFunctions as GM_DMF
import GMAP.src.tools.FileHandler as GM_FH
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
    def test_here(self):
        pass


def basic_setup(
    cmdline, inpardict, defparfilename=None, refparfilename=None,
    finish_before=None, mapname=None
):
    """Sets up a map until it has a RunPars (not yet analyzed the core).

    All steps in here are tested by test_ParameterParser.py. If any
    issues occur within this function, run that file alone, first.
    """

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
