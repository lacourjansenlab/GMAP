# own lib imports
from GMAP.src.tools import FileHandler as GM_FH
from GMAP.src.tools import MapReader as GM_MR
from GMAP.src.tools import ParameterParser as GM_PP
from GMAP.src.tools import PrintTools as GM_PT

# 3rd party lib imports
from pathlib import Path
import pytest


class TestRefPars:
    def test_correctness(self):
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        RefPars = GM_PP.RefPars(
            Printer, Path(
                "tests/test_tools/Data/reference_parameters_1.ref")
        )

        assert RefPars.fname.name == "reference_parameters_1.ref"
        assert RefPars.options == {
            "verbose": [0, 1, 2, 3, 4],
            "verbose_logfile": [0, 1, 2, 3, 4],
            "str_test_choice": ["pick_this", "not_this", "or_this"],
            "str_test_choice_list": [
                "pick_this", "and_this", "not_this", "or_this"
            ],
            "str_test_choice_list2": [
                "dont_pick_this", "pick_this", "also_not_this", "but_this"
            ],
            "int_test_choice": [53, 34, 65],
            "int_test_choice_list": [64, 32, 93, 57],
            "int_test_choice_list2": [96, 63, 12, 85],
            "float_test_choice": [83.7, 66.6],
            "float_test_choice_list": [99.9, 71.5, 43.0, 88.4],
            "float_test_choice_list2": [44.5, 33.0, 12.8, 42.7],
            "path_test_choice": [
                Path("../test_ParameterParser.py"),
                Path("../test_MathFunctions.py")
            ],
            "path_test_rel12_choice": [
                Path("test_ParameterParser.py"),
                Path("test_MathFunctions.py")
            ],
            "path_test_rel23_new_choice": [
                Path("test_outfile_2_3_1.txt"),
                Path("test_outfile_2_3_2.txt")
            ],
            "path_test_rel24_new_choice_list": [
                Path("test_outfile_2_4_1.txt"),
                Path("test_outfile_2_4_2.txt"),
                Path("test_outfile_2_4_3.txt"),
                Path("test_outfile_2_4_4.txt")
            ]

        }
        assert RefPars.choices == {
            "source_directory": [Path("../../../sourcefiles")],
            "log_filename": [Path("log.log")],
            "map_directory": [Path("../../../maps")],
            "verbose": [2],
            "verbose_logfile": [2],
            "prevent_overwrite": [True],
            "str_test_free": ["freechoice"],
            "str_test_choice": ["pick_this"],
            "str_test_free_list": ["freechoice1", "freechoice2"],
            "str_test_choice_list": ["pick_this", "and_this"],
            "str_test_choice_list2": ["pick_this", "but_this"],
            "bool_test1": [True],
            "bool_test2": [True],
            "bool_test3": [False],
            "int_test_free": [243],
            "int_test_choice": [34],
            "int_test_free_list": [46, 72],
            "int_test_choice_list": [64, 32],
            "int_test_choice_list2": [63, 85],
            "float_test_free": [4.2],
            "float_test_choice": [83.7],
            "float_test_free_list": [32.0, 64.1],
            "float_test_choice_list": [99.9, 71.5],
            "float_test_choice_list2": [33.0, 42.7],
            "path_test_free": [Path("../test_MathFunctions.py")],
            "path_test_free_new": [Path("test_outfile.txt")],
            "path_test_choice": [Path("../test_ParameterParser.py")],
            "path_test_free_new_list": [
                Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
            ],
            "path_test_dir1": [Path("../../test_tools")],
            "path_test_dir2": [Path("../Data")],
            "path_test_rel11": [Path("test_MathFunctions.py")],
            "path_test_rel12_choice": [Path("test_ParameterParser.py")],
            "path_test_rel21_new": [Path("test_outfile_2_1.txt")],
            "path_test_rel22_new_list": [
                Path("test_outfile_2_2_1.txt"), Path("test_outfile_2_2_2.txt")
            ],
            "path_test_rel23_new_choice": [Path("test_outfile_2_3_2.txt")],
            "path_test_rel24_new_choice_list": [
                Path("test_outfile_2_4_3.txt"), Path("test_outfile_2_4_4.txt")
            ]
        }
        assert RefPars.shorthands == {
            "sd": "source_directory",
            "dpf": "default_parameter_filename",
            "md": "map_directory",
            "ts1": "str_test_free",
            "ts2": "str_test_choice",
            "ts3": "str_test_free_list",
            "ts4": "str_test_choice_list",
            "ts5": "str_test_choice_list2",
            "tb1": "bool_test1",
            "tb2": "bool_test2",
            "tb3": "bool_test3",
            "ti1": "int_test_free",
            "ti2": "int_test_choice",
            "ti3": "int_test_free_list",
            "ti4": "int_test_choice_list",
            "ti5": "int_test_choice_list2",
            "tf1": "float_test_free",
            "tf2": "float_test_choice",
            "tf3": "float_test_free_list",
            "tf4": "float_test_choice_list",
            "tf5": "float_test_choice_list2",
            "tp1": "path_test_free",
            "tp2": "path_test_free_new",
            "tp3": "path_test_choice",
            "tp4": "path_test_dir1",
            "tp5": "path_test_dir2",
            "tp6": "path_test_rel11",
            "tp7": "path_test_rel12_choice",
            "tp8": "path_test_rel21_new",
            "tp9": "path_test_rel22_new_list",
            "tp10": "path_test_rel23_new_choice",
            "tp11": "path_test_rel24_new_choice_list"
        }
        assert RefPars.organized_filepars == {
            "source_directory": ["default_parameter_filename"],
            "log_directory": ["log_filename"],
            "path_test_dir1": ["path_test_rel11", "path_test_rel12_choice"],
            "path_test_dir2": [
                "path_test_rel21_new", "path_test_rel22_new_list",
                "path_test_rel23_new_choice", "path_test_rel24_new_choice_list"
            ]
        }
        assert RefPars.organized_filepars_id == {
            "sd": "source_directory",
            "lg": "log_directory",
            "t1": "path_test_dir1",
            "t2": "path_test_dir2"
        }
        assert RefPars.allfilepars == [
            "source_directory",
            "default_parameter_filename",
            "log_directory",
            "log_filename",
            "map_directory",
            "path_test_free",
            "path_test_free_new",
            "path_test_choice",
            "path_test_free_new_list",
            "path_test_dir1",
            "path_test_dir2",
            "path_test_rel11",
            "path_test_rel12_choice",
            "path_test_rel21_new",
            "path_test_rel22_new_list",
            "path_test_rel23_new_choice",
            "path_test_rel24_new_choice_list"
        ]
        assert RefPars.filepars_create == [
            "log_filename",
            "path_test_free_new",
            "path_test_free_new_list",
            "path_test_rel21_new",
            "path_test_rel22_new_list",
            "path_test_rel23_new_choice",
            "path_test_rel24_new_choice_list"
        ]
        assert RefPars.intpars == [
            "verbose",
            "verbose_logfile",
            "int_test_free",
            "int_test_choice",
            "int_test_free_list",
            "int_test_choice_list",
            "int_test_choice_list2"
        ]
        assert RefPars.floatpars == [
            "float_test_free",
            "float_test_choice",
            "float_test_free_list",
            "float_test_choice_list",
            "float_test_choice_list2"
        ]
        assert RefPars.boolpars == [
            "prevent_overwrite",
            "bool_test1",
            "bool_test2",
            "bool_test3"
        ]
        assert RefPars.strpars == [
            "str_test_free",
            "str_test_choice",
            "str_test_free_list",
            "str_test_choice_list",
            "str_test_choice_list2"
        ]
        assert RefPars.not_expected_in_deffile == [
            "default_parameter_filename",
            "log_directory"
        ]
        assert RefPars.maybe_list == [
            "map_directory",
            "str_test_free_list",
            "str_test_choice_list",
            "str_test_choice_list2",
            "int_test_free_list",
            "int_test_choice_list",
            "int_test_choice_list2",
            "float_test_free_list",
            "float_test_choice_list",
            "float_test_choice_list2",
            "path_test_free_new_list",
            "path_test_rel22_new_list",
            "path_test_rel24_new_choice_list"
        ]

    def test_SU_FP_1(self, capsys):
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        RefPars = GM_PP.RefPars(
            Printer, Path(
                "tests/test_tools/Data/reference_parameters_1.ref")
        )

        with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
            GM_PP.RefPars.add_reffile(
                Printer,
                Path("tests/test_tools/Data/reference_parameters_1.ref"),
                RefPars
            )
        assert pytest_wrapped_sysexit.type is SystemExit
        captured = capsys.readouterr()
        assert captured.out.endswith("SU_FP_1\n")


class TestRawPars:
    def test_fromfile(self):
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        RefPars = GM_PP.RefPars(
            Printer, Path(
                "tests/test_tools/Data/reference_parameters_1.ref")
        )
        DefPars = GM_PP.RawPars.from_file(
            Printer,
            Path("tests/test_tools/Data/default_parameters_1.txt"),
            RefPars, True
        )

        assert DefPars.fname.name == "default_parameters_1.txt"
        assert DefPars.is_default is True
        assert DefPars.choices == {
            "source_directory": [Path("../../../sourcefiles")],
            "log_filename": [Path("log.log")],
            "map_directory": [Path("../../../maps")],
            "verbose": [3],
            "verbose_logfile": [1],
            "prevent_overwrite": [True],
            "str_test_free": ["freechoice"],
            "str_test_choice": ["not_this"],
            "str_test_free_list": ["freechoice1", "freechoice2"],
            "str_test_choice_list": ["not_this"],
            "str_test_choice_list2": ["dont_pick_this", "but_this"],
            "bool_test1": [True],
            "bool_test2": [False],
            "bool_test3": [True],
            "int_test_free": [243],
            "int_test_choice": [65],
            "int_test_free_list": [46, 77],
            "int_test_choice_list": [64],
            "int_test_choice_list2": [12, 85],
            "float_test_free": [6.2],
            "float_test_choice": [83.7],
            "float_test_free_list": [32.0, 87.0],
            "float_test_choice_list": [99.9],
            "float_test_choice_list2": [44.5, 33.0],
            "path_test_free": [Path("../test_MathFunctions.py")],
            "path_test_free_new": [Path("tost_outfile.txt")],
            "path_test_choice": [Path("../test_MathFunctions.py")],
            "path_test_free_new_list": [
                Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
            ],
            "path_test_dir1": [Path("../../test_tools")],
            "path_test_dir2": [Path("../testout")],
            "path_test_rel11": [Path("test_ParameterParser.py")],
            "path_test_rel12_choice": [Path("test_MathFunctions.py")],
            "path_test_rel21_new": [Path("tost_outfile_2_1.txt")],
            "path_test_rel22_new_list": [
                Path("test_outfile_2_2_1.txt"), Path("tost_outfile_2_2_2.txt")
            ],
            "path_test_rel23_new_choice": [Path("test_outfile_2_3_1.txt")],
            "path_test_rel24_new_choice_list": [
                Path("test_outfile_2_4_1.txt"), Path("test_outfile_2_4_4.txt")
            ]
        }
        # Still missing DefPars.not_found

    def test_fromdict(self):
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        RefPars = GM_PP.RefPars(
            Printer, Path(
                "tests/test_tools/Data/reference_parameters_1.ref")
        )

        pardict = {
            "verbose": ["4"],
            "nobool_test1": [],
            "int_test_free_list": ["88", "44"],
            "path_test_dir2": ["../testout2"]
        }

        InPars = GM_PP.RawPars.from_dict(
            Printer, Path("mydict"), pardict, RefPars, False
        )

        assert InPars.fname.name == "mydict"
        assert InPars.is_default is False
        assert InPars.choices == {
            "verbose": [4],
            "bool_test1": [False],
            "int_test_free_list": [88, 44],
            "path_test_dir2": [Path("../testout2")]
        }
        # Still missing InPars.not_found

    def test_fromcmd(self):
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        RefPars = GM_PP.RefPars(
            Printer, Path(
                "tests/test_tools/Data/reference_parameters_1.ref")
        )

        cmdline = [
            "--int_test_free", "42",
            "-tb1",
            "--nobool_test2",
            "-notb3",
            "-tp9", "tast_outfile_2_2_4.txt", "tast_outfile_2_2_0.txt\\;",
            "--log_directory", "tests/test_tools/Data"
        ]

        InPars = GM_PP.RawPars.create_empty()

        mapdirs = GM_PP.find_mapdir(Files, Printer, cmdline, InPars, RefPars)
        mapdict = GM_MR.scan_mapdirs(mapdirs)
        for _map in mapdict.values():
            _map.find_refpars(Printer)

        CmdPars = GM_PP.RawPars.from_cmdline(
            Printer, cmdline, RefPars, mapdict, False
        )

        assert CmdPars.fname.name == "command line"
        assert CmdPars.is_default is False
        assert CmdPars.choices == {
            "int_test_free": [42],
            "bool_test1": [True],
            "bool_test2": [False],
            "bool_test3": [False],
            "path_test_rel22_new_list": [
                Path("tast_outfile_2_2_4.txt"),
                Path("tast_outfile_2_2_0.txt")
            ],
            "log_directory": [Path("tests/test_tools/Data")]
        }
        # Still missing InPars.not_found
        # Also, test map-shorthand


class TestRunPars:
    def test_correctness(self):
        # Assumes that RefPars and RawPars work correctly!!!

        # setup - Create all necessary objects.
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        RefPars = GM_PP.RefPars(
            Printer, Path(
                "tests/test_tools/Data/reference_parameters_1.ref")
        )
        DefPars = GM_PP.RawPars.from_file(
            Printer,
            Path("tests/test_tools/Data/default_parameters_1.txt"),
            RefPars, True
        )

        pardict = {
            "verbose": ["4"],
            "nobool_test1": [],
            "int_test_free_list": ["88", "44"],
            "path_test_dir2": ["testout2"]
        }

        curpath = Path("D:/github/GEMAIM-dev/GMAP/tests/test_tools")
        curpath /= "test_ParameterParser.py"
        InPars = GM_PP.RawPars.from_dict(
            Printer, curpath, pardict, RefPars, False
        )

        cmdline = [
            "--int_test_free", "42",
            "-tb1",
            "--nobool_test2",
            "-notb3",
            "-tp9", "tast_outfile_2_2_4.txt", "tast_outfile_2_2_0.txt\\;",
            "--log_directory", "tests/test_tools/Data"
        ]

        mapdirs = GM_PP.find_mapdir(Files, Printer, cmdline, InPars, RefPars)
        mapdict = GM_MR.scan_mapdirs(mapdirs)
        for _map in mapdict.values():
            _map.find_refpars(Printer)

        CmdPars = GM_PP.RawPars.from_cmdline(
            Printer, cmdline, RefPars, mapdict, False
        )

        # Actually create RunPars

        RunPars = GM_PP.RunPars(
            Files, Printer, CmdPars, InPars, DefPars, RefPars, True
        )

        assert RunPars.is_main is True

        # now, assert all choices...
        assert RunPars.source_directory == Path(
            curpath / "../../../sourcefiles").resolve()
        assert RunPars.log_directory == Path(curpath / "../Data").resolve()
        assert RunPars.log_filename == Path(
            curpath / "../Data/log.log").resolve()
        assert RunPars.map_directory == [Path(
            curpath / "../../../maps").resolve()]
        assert RunPars.verbose == 4
        assert RunPars.verbose_logfile == 1
        assert RunPars.prevent_overwrite is True

        assert RunPars.str_test_free == "freechoice"
        assert RunPars.str_test_choice == "not_this"
        assert RunPars.str_test_free_list == ["freechoice1", "freechoice2"]
        assert RunPars.str_test_choice_list == ["not_this"]
        assert RunPars.str_test_choice_list2 == ["dont_pick_this", "but_this"]

        assert RunPars.bool_test1 is True
        assert RunPars.bool_test2 is False
        assert RunPars.bool_test3 is False

        assert RunPars.int_test_free == 42
        assert RunPars.int_test_choice == 65
        assert RunPars.int_test_free_list == [88, 44]
        assert RunPars.int_test_choice_list == [64]
        assert RunPars.int_test_choice_list2 == [12, 85]

        assert RunPars.float_test_free == 6.2
        assert RunPars.float_test_choice == 83.7
        assert RunPars.float_test_free_list == [32.0, 87.0]
        assert RunPars.float_test_choice_list == [99.9]
        assert RunPars.float_test_choice_list2 == [44.5, 33.0]

        assert RunPars.path_test_free == Path(
            curpath / "../test_MathFunctions.py").resolve()
        assert RunPars.path_test_free_new == Path(
            curpath / "../Data/tost_outfile.txt").resolve()
        assert RunPars.path_test_choice == Path(
            curpath / "../test_Mathfunctions.py").resolve()
        assert RunPars.path_test_free_new_list == [
            Path(curpath / "../Data/test_outfile_0_1.txt").resolve(),
            Path(curpath / "../Data/test_outfile_0_2.txt").resolve()
        ]
        assert RunPars.path_test_dir1 == Path(
            curpath / "..").resolve()
        assert RunPars.path_test_dir2 == Path(
            curpath / "../testout2").resolve()
        assert RunPars.path_test_rel11 == Path(
            curpath / "../test_ParameterParser.py").resolve()
        assert RunPars.path_test_rel12_choice == Path(
            curpath / "../test_MathFunctions.py").resolve()
        assert RunPars.path_test_rel21_new == Path(
            curpath / "../testout2/tost_outfile_2_1.txt").resolve()
        assert RunPars.path_test_rel22_new_list == [
            Path(curpath / "../../../tast_outfile_2_2_4.txt").resolve(),
            Path(curpath / "../../../tast_outfile_2_2_0.txt").resolve()
        ]
        assert RunPars.path_test_rel23_new_choice == Path(
            curpath / "../testout2/test_outfile_2_3_1.txt").resolve()
        assert RunPars.path_test_rel24_new_choice_list == [
            Path(curpath / "../testout2/test_outfile_2_4_1.txt").resolve(),
            Path(curpath / "../testout2/test_outfile_2_4_4.txt").resolve()
        ]
