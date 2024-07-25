"""
Tests all the functions/classes/methods in the file:
src/tools/ParameterParser.py.

Missing tests:

(@ July 22nd '24):
370-371, 431, 1110, 1220, 1671-1672, 2045 (8 missed statements)

(CUHTAT - currently unknown how to access this )
- SU_FP_7 (CUHTAT)   (370-371)
- RefPars parse choice - unknown dtype (CUHTAT)  (431)
- RawPars verify choice - unknown dtype (CUHTAT)  (1110)
- RawPars checkparexist - variable may occur multiple times, but is also
  not expected in deffiles (N/A in refpars)  (1220)
- RunPars unknown loc for -md - SU_NP_3   (CUHTAT, SU_PP_3!)  (1671-1672)
- RunPars framenums - empty source (CUHTAT)   (2045)
"""

# standard library imports
from pathlib import Path

# 3rd party imports
import numpy as np
import pytest

# local imports
from GMAP.src.programs.GEM import alljobs
import GMAP.src.tools.constants as GM_con
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.ParameterParser as GM_PP


class TestRefPars:
    def test_correctness(self):
        _ = GM_FH.FileLocations()  # still needed for initialization
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )

        assert RefPars.fname.name == "reference_parameters_1.ref"
        assert RefPars.options == {
            "verbose": [0, 1, 2, 3, 4],
            "verbose_logfile": [0, 1, 2, 3, 4],
            "output_format": ["bin", "txt"],
            "output_data": ["ham", "dip", "ene", "pos", "dbp"],
            "hamiltonian_units": ["cm-1", "eV"],
            "energies_units": ["cm-1", "eV"],
            "dipoles_units": ["Debye", "eBohr"],
            "positions_units": ["Ang", "Bohr", "nm"],
            "doublepos_units": ["Ang", "Bohr", "nm"],
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
        }
        assert RefPars.choices == {
            "topology_file": [Path("../../../sourcefiles/pdb_1AKI.tpr")],
            "trajectory_file": [Path(
                "../../../sourcefiles/pdb_1AKI_50frame.xtc"
            )],
            "source_directory": [Path("../../../sourcefiles")],
            "VEG_clib_file": [Path("VEG.dll")],
            "log_filename": [Path("log.log")],
            "output_estatics_filename": [Path("estatics.txt")],
            "output_hamiltonian_filename": [Path("hamiltonian")],
            "output_dipole_filename": [Path("dipoles")],
            "output_energies_filename": [Path("energies")],
            "output_positions_filename": [Path("positions")],
            "output_doublepos_filename": [Path("doublepos")],
            "map_directory": [Path("../../../maps")],
            "maps_to_use": ["AmideSC"],
            "couplings_to_use": ["DipDip", ":All"],
            "influencers_whitelist": [":All"],
            "influencers_blacklist": [":None"],
            "influencers_file": [Path(
                "../../../sourcefiles/infl_file_base.txt"
            )],
            "influencers_select_atoms": ["segid", "*"],
            "influencers": [":All"],
            "verbose": [2],
            "verbose_logfile": [2],
            "prevent_overwrite": [False],
            "output_format": ["bin"],
            "output_data": ["ham", "dip", "pos"],
            "neutral_charge_threshold": [0.0001],
            "guess_bonds": [False],
            "estatic_range": [20.0],
            "estatic_smooth_range": [5.0],
            "start_frame": [0],
            "number_frames": [999999999],
            "stop_frame": [999999999],
            "hamiltonian_units": ["cm-1"],
            "hamiltonian_multiplier": [1],
            "energies_units": ["cm-1"],
            "energies_multiplier": [1],
            "dipoles_units": ["Debye"],
            "dipoles_multiplier": [1],
            "positions_units": ["Ang"],
            "positions_multiplier": [1],
            "doublepos_units": ["Ang"],
            "doublepos_multiplier": [1],
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
            "path_test_free_new_list": [
                Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
            ],
            "path_test_dir1": [Path("../../test_tools")],
            "path_test_dir2": [Path("../Data")],
            "path_test_rel11": [Path("test_MathFunctions.py")],
            "path_test_rel21_new": [Path("test_outfile_2_1.txt")],
            "path_test_rel22_new_list": [
                Path("test_outfile_2_2_1.txt"), Path("test_outfile_2_2_2.txt")
            ],
        }
        assert RefPars.shorthands == {
            "top": "topology_file",
            "trj": "trajectory_file",
            "sd": "source_directory",
            "dpf": "default_parameter_filename",
            "oef": "output_energies_filename",
            "ohf": "output_hamiltonian_filename",
            "odf": "output_dipole_filename",
            "opf": "output_positions_filename",
            "md": "map_directory",
            "um": "maps_to_use",
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
            "ti6": "int_test_nodef",
            "tf1": "float_test_free",
            "tf2": "float_test_choice",
            "tf3": "float_test_free_list",
            "tf4": "float_test_choice_list",
            "tf5": "float_test_choice_list2",
            "tp1": "path_test_free",
            "tp2": "path_test_free_new",
            "tp4": "path_test_dir1",
            "tp5": "path_test_dir2",
            "tp6": "path_test_rel11",
            "tp8": "path_test_rel21_new",
            "tp9": "path_test_rel22_new_list",
        }
        assert RefPars.organized_filepars == {
            "source_directory": [
                "default_parameter_filename",
                "VEG_clib_file"],
            "log_directory": ["log_filename"],
            "output_directory": [
                "output_estatics_filename", "output_hamiltonian_filename",
                "output_dipole_filename", "output_energies_filename",
                "output_positions_filename", "output_doublepos_filename"
            ],
            "path_test_dir1": ["path_test_rel11"],
            "path_test_dir2": [
                "path_test_rel21_new", "path_test_rel22_new_list"
            ]
        }
        assert RefPars.organized_filepars_id == {
            "sd": "source_directory",
            "lg": "log_directory",
            "op": "output_directory",
            "t1": "path_test_dir1",
            "t2": "path_test_dir2"
        }
        assert RefPars.allfilepars == [
            "topology_file",
            "trajectory_file",
            "source_directory",
            "default_parameter_filename",
            "VEG_clib_file",
            "log_directory",
            "log_filename",
            "output_directory",
            "output_estatics_filename",
            "output_hamiltonian_filename",
            "output_dipole_filename",
            "output_energies_filename",
            "output_positions_filename",
            "output_doublepos_filename",
            "map_directory",
            "influencers_file",
            "path_test_free",
            "path_test_free_new",
            "path_test_free_new_list",
            "path_test_dir1",
            "path_test_dir2",
            "path_test_rel11",
            "path_test_rel21_new",
            "path_test_rel22_new_list",
            "path_test_nodef"
        ]
        assert RefPars.filepars_create == [
            "log_filename",
            "output_estatics_filename",
            "output_hamiltonian_filename",
            "output_dipole_filename",
            "output_energies_filename",
            "output_positions_filename",
            "output_doublepos_filename",
            "path_test_free_new",
            "path_test_free_new_list",
            "path_test_rel21_new",
            "path_test_rel22_new_list",
        ]
        assert RefPars.intpars == [
            "verbose",
            "verbose_logfile",
            "start_frame",
            "number_frames",
            "stop_frame",
            "int_test_free",
            "int_test_choice",
            "int_test_free_list",
            "int_test_choice_list",
            "int_test_choice_list2",
            "int_test_nodef"
        ]
        assert RefPars.floatpars == [
            "neutral_charge_threshold",
            "estatic_range",
            "estatic_smooth_range",
            "hamiltonian_multiplier",
            "energies_multiplier",
            "dipoles_multiplier",
            "positions_multiplier",
            "doublepos_multiplier",
            "float_test_free",
            "float_test_choice",
            "float_test_free_list",
            "float_test_choice_list",
            "float_test_choice_list2"
        ]
        assert RefPars.boolpars == [
            "prevent_overwrite",
            "guess_bonds",
            "bool_test1",
            "bool_test2",
            "bool_test3"
        ]
        assert RefPars.strpars == [
            "maps_to_use",
            "couplings_to_use",
            "influencers_whitelist",
            "influencers_blacklist",
            "influencers_select_atoms",
            "output_format",
            "output_data",
            "hamiltonian_units",
            "energies_units",
            "dipoles_units",
            "positions_units",
            "doublepos_units",
            "str_test_free",
            "str_test_choice",
            "str_test_free_list",
            "str_test_choice_list",
            "str_test_choice_list2"
        ]
        assert RefPars.not_expected_in_deffile == [
            "default_parameter_filename",
            "log_directory",
            "output_directory",
            "int_test_nodef",
            "path_test_nodef"
        ]
        assert RefPars.maybe_list == [
            "map_directory",
            "maps_to_use",
            "couplings_to_use",
            "influencers_whitelist",
            "influencers_blacklist",
            "influencers_select_atoms",
            "output_format",
            "output_data",
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
            "influencers",
        ]

    def test_variations(self):
        _ = GM_FH.FileLocations()  # still needed for initialization
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_3.ref"),
            True
        )

        assert RefPars.choices["influencers"] == [
            ":All", "-", "(", ":None", ")"]

    def test_SU_FP_1(self):
        _ = GM_FH.FileLocations()  # still needed for initialization
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )

        with pytest.raises(GM_Ex.GmapNotImplementedError, match="SU_FP_1$"):
            GM_PP.RefPars.add_reffile(
                Path("tests/test_tools/Data/reference_parameters_1.ref"),
                RefPars
            )

    def test_SU_FP_2(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_2.ref",
            "SU_FP_2",
            GM_Ex.GmapFileSyntaxError
        )

    def test_SU_FP_3(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_3_1.ref",
            "SU_FP_3",
            GM_Ex.GmapKeyError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_3_2.ref",
            "SU_FP_3",
            GM_Ex.GmapTypeError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_3_3.ref",
            "SU_FP_3",
            GM_Ex.GmapTypeError
        )

    def test_SU_FP_4(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_4_1.ref",
            "SU_FP_4",
            GM_Ex.GmapFileSyntaxError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_4_2.ref",
            "SU_FP_4",
            GM_Ex.GmapFileSyntaxError
        )

    def test_SU_FP_5(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_5_1.ref",
            "SU_FP_5",
            GM_Ex.GmapValueError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_5_2.ref",
            "SU_FP_5",
            GM_Ex.GmapValueError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_5_3.ref",
            "SU_FP_5",
            GM_Ex.GmapValueError
        )

    def test_SU_FP_6(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_6.ref",
            "SU_FP_6",
            GM_Ex.GmapIndexError
        )

    def test_SU_FP_7(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_7_1.ref",
            "SU_FP_7",
            GM_Ex.GmapValueError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_7_2.ref",
            "SU_FP_7",
            GM_Ex.GmapValueError
        )

    def test_SU_FP_8(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_8.ref",
            "SU_FP_8",
            GM_Ex.GmapParameterError
        )

    def test_SU_FP_9(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_9.ref",
            "SU_FP_9",
            GM_Ex.GmapTypeError, False
        )

    @staticmethod
    def systest(fname, errcode, errclass=None, is_main=True):
        _ = GM_FH.FileLocations()  # still needed for initialization

        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_PP.RefPars(Path(fname), is_main)


class TestRawPars:
    def test_fromfile(self):
        _ = GM_FH.FileLocations()  # still needed for initialization
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )
        DefPars = GM_PP.RawPars.from_file(
            Path("tests/test_tools/Data/default_parameters_1.txt"),
            RefPars, True
        )
        sd = Path("../../../sourcefiles")

        assert DefPars.fname.name == "default_parameters_1.txt"
        assert DefPars.is_default is True
        assert DefPars.choices == {
            "topology_file": [sd / "pdb_1AKI.tpr"],
            "trajectory_file": [sd / "pdb_1AKI_50frame.xtc"],
            "source_directory": [sd],
            "VEG_clib_file": [Path("VEG.dll")],
            "log_filename": [Path("log.log")],
            "output_estatics_filename": [Path("estatics.txt")],
            "output_hamiltonian_filename": [Path("hamiltonian")],
            "output_dipole_filename": [Path("dipoles")],
            "output_energies_filename": [Path("energies")],
            "output_positions_filename": [Path("positions")],
            "output_doublepos_filename": [Path("doublepos")],
            "map_directory": [Path("../../../maps")],
            "maps_to_use": ["AmideSC"],
            "couplings_to_use": [["DipDip", ":All"]],
            "influencers_whitelist": [":All"],
            "influencers_blacklist": [":None"],
            "influencers_file": [sd/"infl_file_base.txt"],
            "influencers_select_atoms": ["segid", "*"],
            "influencers": [":All"],
            "verbose": [3],
            "verbose_logfile": [1],
            "prevent_overwrite": [False],
            "output_format": ["bin", "txt"],
            "output_data": ["ham", "dip", "pos"],
            "neutral_charge_threshold": [0.0001],
            "guess_bonds": [False],
            "estatic_range": [20.0],
            "estatic_smooth_range": [5.0],
            "start_frame": [0],
            "number_frames": [999999999],
            "stop_frame": [999999999],
            "hamiltonian_units": ["cm-1"],
            "hamiltonian_multiplier": [1],
            "energies_units": ["cm-1"],
            "energies_multiplier": [1],
            "dipoles_units": ["Debye"],
            "dipoles_multiplier": [1],
            "positions_units": ["Ang"],
            "positions_multiplier": [1],
            "doublepos_units": ["Ang"],
            "doublepos_multiplier": [1],
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
            # "path_test_choice": [Path("../test_MathFunctions.py")],
            "path_test_free_new_list": [
                Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
            ],
            "path_test_dir1": [Path("../../test_tools")],
            "path_test_dir2": [Path("../Data/testout")],
            "path_test_rel11": [Path("test_ParameterParser.py")],
            # "path_test_rel12_choice": [Path("test_MathFunctions.py")],
            "path_test_rel21_new": [Path("tost_outfile_2_1.txt")],
            "path_test_rel22_new_list": [
                Path("test_outfile_2_2_1.txt"), Path("tost_outfile_2_2_2.txt")
            ],
            # "path_test_rel23_new_choice": [Path("test_outfile_2_3_1.txt")],
            # "path_test_rel24_new_choice_list": [
            #     Path("test_outfile_2_4_1.txt"),
            #     Path("test_outfile_2_4_4.txt")
            # ]
        }
        # Still missing DefPars.not_found

    def test_fromdict(self):
        _, RefPars = TestRawPars.setup_test_SU_WP_base()

        pardict = {
            "verbose": ["4"],
            "hamiltonian_units": ["eV"],
            "energies_units": ["eV"],
            "dipoles_units": ["eBohr"],
            "positions_units": ["Bohr"],
            "doublepos_units": ["Bohr"],
            "nobool_test1": [],
            "nobool_test2": ["false"],
            "int_test_free_list": ["88", "44"],
            "path_test_dir2": ["../testout2"]
        }

        InPars = GM_PP.RawPars.from_dict(
            Path("mydict"), pardict, RefPars, False
        )

        assert InPars.fname.name == "mydict"
        assert InPars.is_default is False
        assert InPars.choices == {
            "verbose": [4],
            "hamiltonian_units": ["eV"],
            "hamiltonian_multiplier": [GM_con.cm2eV],
            "energies_units": ["eV"],
            "energies_multiplier": [GM_con.cm2eV],
            "dipoles_units": ["eBohr"],
            "dipoles_multiplier": [GM_con.Debye2ea0],
            "positions_units": ["Bohr"],
            "positions_multiplier": [GM_con.ang2bohr],
            "doublepos_units": ["Bohr"],
            "doublepos_multiplier": [GM_con.ang2bohr],
            "bool_test1": [False],
            "bool_test2": [True],
            "int_test_free_list": [88, 44],
            "path_test_dir2": [Path("../testout2")]
        }
        # Still missing InPars.not_found

    def test_fromcmd(self):
        cmdline = [
            "--int_test_free", "42",
            "-tb1",
            "--nobool_test2",
            "-notb3",
            "-tp9", "tast_outfile_2_2_4.txt", "tast_outfile_2_2_0.txt\\;",
            "--log_directory", "tests/test_tools/Data",
            "--hamiltonian_units", "cm-1",
            "--energies_units", "cm-1",
            "--dipoles_units", "Debye",
            "--positions_units", "nm",
            "--doublepos_units", "nm"
        ]

        _, RefPars, _, _, maprefdict = self.setup_test_SU_WP_cmd(
            cmdline)

        CmdPars = GM_PP.RawPars.from_cmdline(
            cmdline, RefPars, maprefdict, False
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
            "log_directory": [Path("tests/test_tools/Data")],
            "hamiltonian_units": ["cm-1"],
            "hamiltonian_multiplier": [1],
            "energies_units": ["cm-1"],
            "energies_multiplier": [1],
            "dipoles_units": ["Debye"],
            "dipoles_multiplier": [1],
            "positions_units": ["nm"],
            "positions_multiplier": [0.1],
            "doublepos_units": ["nm"],
            "doublepos_multiplier": [0.1],
        }
        # Still missing InPars.not_found
        # Also, test map-shorthand

    def test_variations(self):
        def infltest(cmdline, inflchoice):
            _, RefPars, _, _, maprefdict = self.setup_test_SU_WP_cmd(
                cmdline)

            CmdPars = GM_PP.RawPars.from_cmdline(
                cmdline, RefPars, maprefdict, False
            )
            assert CmdPars.choices["influencers"] == inflchoice

        infltest(
            ["--influencers_blacklist", ":None\\;"],
            [":All", "-", "(", ":None", ")"]
        )

        infltest(
            ["--influencers_file", "sourcefiles/infl_file_base.txt"],
            Path("sourcefiles/infl_file_base.txt")
        )

        infltest(
            ["--influencers_select_atoms", "segid", "A\\;"],
            "segid A"
        )

        _, RefPars = TestRawPars.setup_test_SU_WP_base()

        pardict = {
            "verbose": ["4"],
            "positions_units": ["Ang"],
            "doublepos_units": ["Ang"],
            # "nobool_test1": [],
            # "nobool_test2": ["false"],
            # "int_test_free_list": ["88", "44"],
            # "path_test_dir2": ["../testout2"]
        }

        InPars = GM_PP.RawPars.from_dict(
            Path("mydict"), pardict, RefPars, False
        )

        assert InPars.fname.name == "mydict"
        assert InPars.is_default is False
        assert InPars.choices == {
            "verbose": [4],
            "positions_units": ["Ang"],
            "positions_multiplier": [1],
            "doublepos_units": ["Ang"],
            "doublepos_multiplier": [1],
            # "bool_test1": [False],
            # "bool_test2": [True],
            # "int_test_free_list": [88, 44],
            # "path_test_dir2": [Path("../testout2")]
        }

    def test_SU_WP_1(self):
        cmdline = ["int_test_free", "42"]
        self.systest_cmdline(cmdline, "SU_WP_1", GM_Ex.GmapFileSyntaxError)

    def test_SU_WP_2(self):
        cmdline = ["--unknown_map.does_not_exist", "42"]
        self.systest_cmdline(cmdline, "SU_WP_2", GM_Ex.GmapKeyError)

        cmdline = ["-AmideSC.noudtp", "22"]
        self.systest_cmdline(cmdline, "SU_WP_2", GM_Ex.GmapKeyError)

    def test_SU_WP_3(self):
        cmdline = ["--does_not_exist", "42"]
        self.systest_cmdline(cmdline, "SU_WP_3", GM_Ex.GmapKeyError)

        cmdline = ["-noudtp", "22"]
        self.systest_cmdline(cmdline, "SU_WP_3", GM_Ex.GmapKeyError)

    def test_SU_WP_4(self):
        cmdline = ["--int_test_free_list"]
        self.systest_cmdline(cmdline, "SU_WP_4", GM_Ex.GmapIndexError)

    def test_SU_WP_5(self):
        cmdline = ["--int_test_free_list", "32"]
        self.systest_cmdline(cmdline, "SU_WP_5", GM_Ex.GmapIndexError)

        cmdline = ["--int_test_free_list", "32", "-tb1"]
        self.systest_cmdline(cmdline, "SU_WP_5", GM_Ex.GmapFileSyntaxError)

    def test_SU_WP_6(self):
        pardict = {
            "thispar_doesntexist": ["42"]
        }
        self.systest_pardict(pardict, "SU_WP_6", GM_Ex.GmapKeyError)

    def test_SU_WP_7(self):
        pardict = {
            "int_test_free": []
        }
        self.systest_pardict(
            pardict, "SU_WP_7", GM_Ex.GmapFileSyntaxError, isdef=True)

    def test_SU_WP_8(self):
        pardict = {
            "int_test_free": []
        }
        self.systest_pardict(pardict, "SU_WP_8", GM_Ex.GmapFileSyntaxError)

    def test_SU_WP_9(self):
        pardict = {
            "int_test_free": ["53", "55"]
        }
        self.systest_pardict(pardict, "SU_WP_9", GM_Ex.GmapFileSyntaxError)

    def test_SU_WP_10(self):
        pardict = {
            "bool_test1": ["apple"]
        }
        self.systest_pardict(pardict, "SU_WP_10", GM_Ex.GmapValueError)

    def test_SU_WP_11(self):
        pardict = {
            "int_test_choice": ["22"]  # 22 is not a listed choice in reffile
        }
        self.systest_pardict(pardict, "SU_WP_11", GM_Ex.GmapValueError)

        pardict = {
            "estatic_range": ["-2"]
        }
        self.systest_pardict(pardict, "SU_WP_11", GM_Ex.GmapValueError)

        pardict = {
            "estatic_smooth_range": ["-2"]
        }
        self.systest_pardict(pardict, "SU_WP_11", GM_Ex.GmapValueError)

    def test_SU_WP_12(self):
        pardict = {
            "int_test_free": ["apple"]
        }
        self.systest_pardict(pardict, "SU_WP_12", GM_Ex.GmapTypeError)

    def test_SU_WP_13(self):
        pardict = {
            "log_directory": ["newdir"]
        }
        self.systest_pardict(
            pardict, "SU_WP_13", GM_Ex.GmapParameterError, isdef=True)

    def test_SU_WP_14(self):
        pardict = {
            "int_test_free": ["44"],
            "float_test_free": ["22.2"]
        }
        self.systest_pardict(
            pardict, "SU_WP_14", GM_Ex.GmapParameterError, isdef=True)

        cmdline = ["--verbose", "2"]
        self.systest_cmdline(
            cmdline, "SU_WP_14", GM_Ex.GmapParameterError, isdef=True)

    def test_SU_WP_15(self):
        pardict = {
            "nonexistentmap.par1": ["1"]
        }
        _, RefPars = TestRawPars.setup_test_SU_WP_base()
        InPars = GM_PP.RawPars.from_dict(
            Path("mydict"), pardict, RefPars, False
        )

        with pytest.raises(GM_Ex.GmapKeyError, match="SU_WP_15$"):
            InPars.finalize_map_pars()

    def test_SU_WP_16(self):
        pardict = {
            "influencers_whitelist": [":All"],
            "influencers_select_atoms": ["segid", "*"]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_Ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "hamiltonian_units": ["cm-1"],
            "hamiltonian_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_Ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "energies_units": ["cm-1"],
            "energies_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_Ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "dipoles_units": ["Debye"],
            "dipoles_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_Ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "positions_units": ["Bohr"],
            "positions_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_Ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "doublepos_units": ["Bohr"],
            "doublepos_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_Ex.GmapParameterError, isdef=False)

    def test_SU_WP_17(self):
        pardict = {
            "start_frame": [0],
            "number_frames": [5],
            "stop_frame": [10]
        }
        self.systest_pardict(
            pardict, "SU_WP_17", GM_Ex.GmapParameterError, isdef=False)

        pardict = {
            "number_frames": [10],
            "stop_frame": [5]
        }
        self.systest_pardict(
            pardict, "SU_WP_17", GM_Ex.GmapParameterError, isdef=False)

        pardict = {
            "start_frame": [10],
            "stop_frame": [5]
        }
        self.systest_pardict(
            pardict, "SU_WP_17", GM_Ex.GmapParameterError, isdef=False)

    @staticmethod
    def setup_test_SU_WP_cmd(cmdline):
        Files, RefPars = TestRawPars.setup_test_SU_WP_base()

        InPars = GM_PP.RawPars.create_empty()

        mapdirs = GM_PP.find_mapdir(Files, cmdline, InPars, RefPars)
        mapdict = GM_MR.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        maprefdict = {name: _map.RefPars for name, _map in mapdict.items()}

        return Files, RefPars, InPars, mapdict, maprefdict

    @staticmethod
    def setup_test_SU_WP_base():
        Files = GM_FH.FileLocations()
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )
        return Files, RefPars

    @staticmethod
    def systest_cmdline(cmdline, errcode, errclass, isdef=False):
        (
            _, RefPars, _, _, maprefdict
        ) = TestRawPars.setup_test_SU_WP_cmd(cmdline)

        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_PP.RawPars.from_cmdline(
                cmdline, RefPars, maprefdict, isdef
            )

    @staticmethod
    def systest_pardict(pardict, errcode, errclass, isdef=False):
        _, RefPars = TestRawPars.setup_test_SU_WP_base()
        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_PP.RawPars.from_dict(
                Path("mydict"), pardict, RefPars, isdef
            )


class TestRunPars:
    def test_correctness(self):
        # Assumes that RefPars and RawPars work correctly!!!

        pardict = {
            "verbose": ["4"],
            "nobool_test1": [],
            "int_test_free_list": ["88", "44"],
            "path_test_dir2": ["Data/testout2"],
            "int_test_nodef": ["33"],
        }

        curpath = Path(__file__).resolve()

        cmdline = [
            "--int_test_free", "42",
            "-tb1",
            "--nobool_test2",
            "-notb3",
            "-tp9", "tast_outfile_2_2_4.txt", "tast_outfile_2_2_0.txt\\;",
            "--log_directory", "tests/test_tools/Data",
            "--output_directory", "tests/test_tools/Data",
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py"
        ]

        (
            Files, RefPars, DefPars, InPars, _, CmdPars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        # Actually create RunPars

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )
        RunPars.manage_dtypes()
        print(RefPars.choices["output_format"])

        assert RunPars.is_main is True

        # now, assert all choices...
        assert RunPars.topology_file == Path(
            curpath / "../../../sourcefiles/pdb_1AKI.tpr").resolve()
        assert RunPars.trajectory_file == Path(
            curpath / "../../../sourcefiles/pdb_1AKI_50frame.xtc").resolve()
        assert RunPars.source_directory == Path(
            curpath / "../../../sourcefiles").resolve()
        assert RunPars.VEG_clib_file == Path(
            curpath / "../../../sourcefiles/VEG.dll").resolve()
        assert RunPars.log_directory == Path(curpath / "../Data").resolve()
        assert RunPars.log_filename == Path(
            curpath / "../Data/log.log").resolve()
        assert RunPars.output_directory == Path(curpath / "../Data").resolve()
        assert RunPars.output_estatics_filename == Path(
            curpath / "../Data/estatics.txt").resolve()
        assert RunPars.output_hamiltonian_filename == Path(
            curpath / "../Data/hamiltonian").resolve()
        assert RunPars.output_dipole_filename == Path(
            curpath / "../Data/dipoles").resolve()
        assert RunPars.output_energies_filename == Path(
            curpath / "../Data/energies").resolve()
        assert RunPars.map_directory == [Path(
            curpath / "../../../maps").resolve()]
        assert RunPars.maps_to_use == ["AmideSC"]
        assert RunPars.influencers == [":All"]

        assert RunPars.verbose == 4
        assert RunPars.verbose_logfile == 1
        assert RunPars.prevent_overwrite is False
        assert RunPars.output_format == ["bin", "txt"]
        assert RunPars.output_data == ["ham", "dip", "pos"]

        assert RunPars.neutral_charge_threshold == 0.0001
        assert RunPars.guess_bonds is False
        assert RunPars.estatic_range == np.float32(20)
        assert RunPars.estatic_smooth_range == np.float32(5)

        assert RunPars.start_frame == 0
        assert RunPars.number_frames == 999999999
        assert RunPars.stop_frame == 999999999

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
        assert RunPars.int_test_nodef == 33

        assert RunPars.float_test_free == 6.2
        assert RunPars.float_test_choice == 83.7
        assert RunPars.float_test_free_list == [32.0, 87.0]
        assert RunPars.float_test_choice_list == [99.9]
        assert RunPars.float_test_choice_list2 == [44.5, 33.0]

        assert RunPars.path_test_free == Path(
            curpath / "../test_MathFunctions.py").resolve()
        assert RunPars.path_test_free_new == Path(
            curpath / "../Data/tost_outfile.txt").resolve()
        # assert RunPars.path_test_choice == Path(
        #     curpath / "../test_Mathfunctions.py").resolve()
        assert RunPars.path_test_free_new_list == [
            Path(curpath / "../Data/test_outfile_0_1.txt").resolve(),
            Path(curpath / "../Data/test_outfile_0_2.txt").resolve()
        ]
        assert RunPars.path_test_dir1 == Path(
            curpath / "..").resolve()
        assert RunPars.path_test_dir2 == Path(
            curpath / "../Data/testout2").resolve()
        assert RunPars.path_test_rel11 == Path(
            curpath / "../test_ParameterParser.py").resolve()
        # assert RunPars.path_test_rel12_choice == Path(
        #     curpath / "../test_MathFunctions.py").resolve()
        assert RunPars.path_test_rel21_new == Path(
            curpath / "../Data/testout2/tost_outfile_2_1.txt").resolve()
        assert RunPars.path_test_rel22_new_list == [
            Path(curpath / "../../../tast_outfile_2_2_4.txt").resolve(),
            Path(curpath / "../../../tast_outfile_2_2_0.txt").resolve()
        ]
        # assert RunPars.path_test_rel23_new_choice == Path(
        #     curpath / "../Data/testout2/test_outfile_2_3_1.txt").resolve()
        # assert RunPars.path_test_rel24_new_choice_list == [
        #     Path(
        #         curpath / "../Data/testout2/test_outfile_2_4_1.txt"
        #     ).resolve(),
        #     Path(
        #         curpath / "../Data/testout2/test_outfile_2_4_4.txt"
        #     ).resolve()
        # ]

    def test_filetree(self):
        # Assumes that RefPars and RawPars work correctly!!!

        # setup - Create all necessary objects.
        Files = GM_FH.FileLocations()
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_2.ref"),
            True
        )
        DefPars = GM_PP.RawPars.from_file(
            Path("tests/test_tools/Data/default_parameters_2.txt"),
            RefPars, True
        )

        pardicts = []
        cmdlines = []
        for dodir in range(2):
            for dofile in range(2):
                pardicts.append({})
                cmdlines.append([])
                for opt1 in ("def", "nod"):
                    for opt2 in ("def", "nod"):
                        if dodir:
                            pardicts[-1][f"{opt1}_{opt2}_dir"] = [
                                "../test_inp"]
                            cmdlines[-1].append(f"--{opt1}_{opt2}_dir")
                            cmdlines[-1].append(
                                "tests/test_tools/Data/test_cmd")
                        if dofile:
                            pardicts[-1][f"{opt1}_{opt2}_file"] = [
                                "frominp.txt"]
                            cmdlines[-1].append(f"--{opt1}_{opt2}_file")
                            cmdlines[-1].append("fromcmd.txt")

        curpath = Path(__file__).resolve()
        allInPars = [
            GM_PP.RawPars.from_dict(
                curpath / "../Data/testout/imaginary_inpfile", pardict,
                RefPars, False
            ) for pardict in pardicts
        ]

        mapdirs = GM_PP.find_mapdir(
            Files, cmdlines[0], allInPars[0], DefPars)
        mapdict = GM_MR.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        maprefdict = {name: _map.RefPars for name, _map in mapdict.items()}

        allCmdPars = [
            GM_PP.RawPars.from_cmdline(
                cmdline, RefPars, maprefdict, False
            ) for cmdline in cmdlines
        ]

        # Actually create RunPars
        allrunpars = []
        for CmdPars in allCmdPars:
            for InPars in allInPars:
                allrunpars.append(GM_PP.RunPars(
                    Files, CmdPars, InPars, DefPars, RefPars, True
                ))

        # orders:
        # nothing in cmdline, nothing in input
        # nothing in cmdline, only file in input
        # nothing in cmdline, only dir in input
        # nothing in cmdline, both in input
        # only file in cmdline, nothing in input
        # only file in cmdline, only file in input
        # only file in cmdline, only dir in input
        # only file in cmdline, both in input
        # only dir in cmdline, nothing in input
        # only dir in cmdline, only file in input
        # only dir in cmdline, only dir in input
        # only dir in cmdline, both in input
        # both in cmdline, nothing in input
        # both in cmdline, only file in input
        # both in cmdline, only dir in input
        # both in cmdline, both in input
        onlyfile = Path(curpath / "../../../fromcmd.txt").resolve()
        both = Path(curpath / "../Data/test_cmd/fromcmd.txt").resolve()
        expected_ddf = [
            Path(curpath / "../Data/test_def/fromdef.txt").resolve(),
            Path(curpath / "../Data/testout/frominp.txt").resolve(),
            Path(curpath / "../Data/test_inp/fromdef.txt").resolve(),
            Path(curpath / "../Data/test_inp/frominp.txt").resolve(),
            onlyfile, onlyfile, onlyfile, onlyfile,
            Path(curpath / "../Data/test_cmd/fromdef.txt").resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            Path(curpath / "../Data/test_cmd/fromdef.txt").resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            both, both, both, both
        ]
        expected_ndf = [
            Path(curpath / "../Data/fromdef.txt").resolve(),
            Path(curpath / "../Data/testout/frominp.txt").resolve(),
            Path(curpath / "../Data/test_inp/fromdef.txt").resolve(),
            Path(curpath / "../Data/test_inp/frominp.txt").resolve(),
            onlyfile, onlyfile, onlyfile, onlyfile,
            Path(curpath / "../Data/test_cmd/fromdef.txt").resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            Path(curpath / "../Data/test_cmd/fromdef.txt").resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            both, both, both, both
        ]
        expected_dnf = [
            Path(
                curpath / "../Data/test_def/name_not_defined_0.txt"
            ).resolve(),
            Path(curpath / "../Data/testout/frominp.txt").resolve(),
            Path(
                curpath / "../Data/test_inp/name_not_defined_4.txt"
            ).resolve(),
            Path(curpath / "../Data/test_inp/frominp.txt").resolve(),
            onlyfile, onlyfile, onlyfile, onlyfile,
            Path(
                curpath / "../Data/test_cmd/name_not_defined_16.txt"
            ).resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            Path(
                curpath / "../Data/test_cmd/name_not_defined_20.txt"
            ).resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            both, both, both, both
        ]
        expected_nnf = [
            Path(curpath / "../../../name_not_defined_1.txt").resolve(),
            Path(curpath / "../Data/testout/frominp.txt").resolve(),
            Path(
                curpath / "../Data/test_inp/name_not_defined_5.txt"
            ).resolve(),
            Path(curpath / "../Data/test_inp/frominp.txt").resolve(),
            onlyfile, onlyfile, onlyfile, onlyfile,
            Path(
                curpath / "../Data/test_cmd/name_not_defined_17.txt"
            ).resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            Path(
                curpath / "../Data/test_cmd/name_not_defined_21.txt"
            ).resolve(),
            Path(curpath / "../Data/test_cmd/frominp.txt").resolve(),
            both, both, both, both
        ]

        # counter = 0
        for RunPars, exp_ddf, exp_ndf, exp_dnf, exp_nnf in zip(
            allrunpars, expected_ddf, expected_ndf, expected_dnf, expected_nnf
        ):
            # GM_PT.devprint(counter)
            # counter += 1
            assert RunPars.def_def_file == exp_ddf
            assert RunPars.nod_def_file == exp_ndf
            assert RunPars.def_nod_file == exp_dnf
            assert RunPars.nod_nod_file == exp_nnf

    def test_framenumbers(self):
        pardict = {
            "start_frame": ["4"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_MathFunctions.py")]
        }

        curpath = Path(__file__).resolve()

        cmdline = []

        (
            Files, RefPars, DefPars, InPars, _, CmdPars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        assert RunPars.start_frame == 4
        assert RunPars.number_frames == 999999995
        assert RunPars.stop_frame == 999999999

        pardict = {
            "start_frame": ["4"],
            "number_frames": ["20"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_MathFunctions.py")]
        }

        curpath = Path(__file__).resolve()

        (
            Files, RefPars, DefPars, InPars, _, CmdPars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        assert RunPars.start_frame == 4
        assert RunPars.number_frames == 20
        assert RunPars.stop_frame == 24

        pardict = {
            "number_frames": ["4"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_MathFunctions.py")]
        }

        curpath = Path(__file__).resolve()

        cmdline = ["--stop_frame", "8"]

        (
            Files, RefPars, DefPars, InPars, _, CmdPars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        assert RunPars.start_frame == 4
        assert RunPars.number_frames == 4
        assert RunPars.stop_frame == 8

        pardict = {
            "stop_frame": ["4"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_MathFunctions.py")]
        }

        curpath = Path(__file__).resolve()

        cmdline = ["--stop_frame", "8"]

        (
            Files, RefPars, DefPars, InPars, _, CmdPars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        assert RunPars.start_frame == 0
        assert RunPars.number_frames == 8
        assert RunPars.stop_frame == 8

    def test_coupchoices(self):
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None", ":diff"],
                ["DipDip", ":same"],
                ["None", "CystBridge:"],
                ["DipDip", "CystBridge:CystBridge", "AmideSC:AmideBB"]
            ],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_MathFunctions.py")]
        }

        curpath = Path(__file__).resolve()
        cmdline = []

        (
            Files, RefPars, DefPars, InPars, _, CmdPars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )
        assert RunPars.pair_v_coupling_dict == {
            ("AmideSC", "AmideSC"): "DipDip",
            ("AmideSC", "AmideBB"): "DipDip",
            ("AmideSC", "CystBridge"): None,
            ("AmideBB", "AmideSC"): "DipDip",
            ("AmideBB", "AmideBB"): "DipDip",
            ("AmideBB", "CystBridge"): None,
            ("CystBridge", "AmideSC"): None,
            ("CystBridge", "AmideBB"): None,
            ("CystBridge", "CystBridge"): "DipDip"
        }
        assert RunPars.coupling_v_pair_dict == {
            "DipDip": [
                ("AmideSC", "AmideSC"),
                ("AmideSC", "AmideBB"),
                ("AmideBB", "AmideSC"),
                ("AmideBB", "AmideBB"),
                ("CystBridge", "CystBridge")
            ],
            None: [
                ("AmideSC", "CystBridge"),
                ("AmideBB", "CystBridge"),
                ("CystBridge", "AmideSC"),
                ("CystBridge", "AmideBB")
            ]
        }

        _ = GM_PP.RawPars.from_file(
            curpath.parent/"Data"/"rawpars_coupling.txt", RefPars,
            False
        )

    def test_SU_NP_1(self):
        cmdline = [
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py"
        ]
        self.systest_runpars(cmdline, "SU_NP_1", GM_Ex.GmapParameterError)

        cmdline = [
            "--int_test_nodef", "22"
        ]
        self.systest_runpars(cmdline, "SU_NP_1", GM_Ex.GmapParameterError)

    def test_SU_NP_2(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_free", "this_file_doesnt_exist.really"
        ]
        self.systest_runpars(cmdline, "SU_NP_2", GM_Ex.GmapFileNotFoundError)

        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py",
            "--path_test_free_new", "this/file/location/doesnt_exist.really"
        ]
        self.systest_runpars(cmdline, "SU_NP_2", GM_Ex.GmapFileNotFoundError)

        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_rel21_new", "this/file/location/doesnt_exist.really"
        ]
        self.systest_runpars(cmdline, "SU_NP_2", GM_Ex.GmapFileNotFoundError)

    def test_SU_NP_3(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_dir1", "this_directory_doesnt_exist"
        ]
        self.systest_runpars(cmdline, "SU_NP_3", GM_Ex.GmapNotADirectoryError)

        # cmdline = [
        #     "--map_directory", "doesntexist\\;"
        # ]
        # self.systest_runpars(cmdline, "SU_NP_3", capsys)

    def test_SU_NP_7(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py",
            "--estatic_smooth_range", "40"
        ]
        pardict = {"estatic_range": ["10"]}
        self.systest_runpars(cmdline, "SU_NP_7", GM_Ex.GmapValueError, pardict)

    def test_SU_NP_8(self):
        # invalid length (no couppairs given)
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_Ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # invalid couppair choice (group not chosen/available)
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None", "doesnexist:AmideBB"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_Ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # invalid amount of items in 'pair' (not 1 colon)
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None", "AmideSC:AmideBB:CystBridge"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_Ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # first item in pair is 'nothing'
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_MathFunctions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None", ":CystBridge"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_Ex.GmapFileSyntaxError, pardict)

    @staticmethod
    def setup_for_runpars(pardict, inparspath, cmdline):
        # setup - Create all necessary objects.
        Files = GM_FH.FileLocations()
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )
        DefPars = GM_PP.RawPars.from_file(
            Path("tests/test_tools/Data/default_parameters_1.txt"),
            RefPars, True
        )

        InPars = GM_PP.RawPars.from_dict(
            inparspath, pardict, RefPars, False
        )

        mapdirs = GM_PP.find_mapdir(Files, cmdline, InPars, DefPars)
        mapdict = GM_MR.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        maprefdict = {name: _map.RefPars for name, _map in mapdict.items()}

        CmdPars = GM_PP.RawPars.from_cmdline(
            cmdline, RefPars, maprefdict, False
        )

        return Files, RefPars, DefPars, InPars, mapdict, CmdPars

    @staticmethod
    def systest_runpars(cmdline, errcode, errclass, pardict=None):
        if pardict is None:
            pardict = {}
        curpath = Path("")
        (
            Files, RefPars, DefPars, InPars, _, CmdPars
        ) = TestRunPars.setup_for_runpars(pardict, curpath, cmdline)

        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_PP.RunPars(
                Files, CmdPars, InPars, DefPars, RefPars, True
            )


class TestMapPars:
    def test_maprefpars(self):
        # Assumes that RefPars and RawPars work correctly!!
        pardict = {
            "map_directory": ["Data/test_mapdir"]
        }
        cmdline = []

        curpath = Path(__file__).resolve()

        _, _, _, _, mapdict = TestMapPars.setup_maprefpars(
            pardict, cmdline)

        counter = 1
        for map_ in mapdict.values():
            map_.find_refpars()

            fname_tofind = Path(curpath / "../Data/test_mapdir/Singles")
            fname_tofind /= f"testmap{counter}/parameters.ref"
            counter += 1
            assert map_.RefPars.fname == fname_tofind.resolve()
            assert map_.RefPars.options == {
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
                # "path_test_choice": [
                #     Path("../../../../test_ParameterParser.py"),
                #     Path("../../../../test_MathFunctions.py")
                # ],
                # "path_test_rel12_choice": [
                #     Path("test_ParameterParser.py"),
                #     Path("test_MathFunctions.py")
                # ],
                # "path_test_rel23_new_choice": [
                #     Path("test_outfile_2_3_1.txt"),
                #     Path("test_outfile_2_3_2.txt")
                # ],
                # "path_test_rel24_new_choice_list": [
                #     Path("test_outfile_2_4_1.txt"),
                #     Path("test_outfile_2_4_2.txt"),
                #     Path("test_outfile_2_4_3.txt"),
                #     Path("test_outfile_2_4_4.txt")
                # ]

            }
            assert map_.RefPars.choices == {
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
                "path_test_free": [Path("../../../../test_MathFunctions.py")],
                "path_test_free_new": [Path("test_outfile.txt")],
                # "path_test_choice": [
                #     Path("../../../../test_ParameterParser.py")],
                "path_test_free_new_list": [
                    Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
                ],
                "path_test_dir1": [Path("../../../../../test_tools")],
                "path_test_dir2": [Path("../../../../Data")],
                "path_test_rel11": [Path("test_MathFunctions.py")],
                # "path_test_rel12_choice": [Path("test_ParameterParser.py")],
                "path_test_rel21_new": [Path("test_outfile_2_1.txt")],
                "path_test_rel22_new_list": [
                    Path("test_outfile_2_2_1.txt"),
                    Path("test_outfile_2_2_2.txt")
                ],
                # "path_test_rel23_new_choice": [
                #     Path("test_outfile_2_3_2.txt")],
                # "path_test_rel24_new_choice_list": [
                #     Path("test_outfile_2_4_3.txt"),
                #     Path("test_outfile_2_4_4.txt")
                # ]
            }
            assert map_.RefPars.shorthands == {
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
                # "tp3": "path_test_choice",
                "tp4": "path_test_dir1",
                "tp5": "path_test_dir2",
                "tp6": "path_test_rel11",
                # "tp7": "path_test_rel12_choice",
                "tp8": "path_test_rel21_new",
                "tp9": "path_test_rel22_new_list",
                # "tp10": "path_test_rel23_new_choice",
                # "tp11": "path_test_rel24_new_choice_list"
            }
            assert map_.RefPars.organized_filepars == {
                "path_test_dir1": [
                    "path_test_rel11",
                    # "path_test_rel12_choice"
                ],
                "path_test_dir2": [
                    "path_test_rel21_new", "path_test_rel22_new_list",
                    # "path_test_rel23_new_choice",
                    # "path_test_rel24_new_choice_list"
                ]
            }
            assert map_.RefPars.organized_filepars_id == {
                "t1": "path_test_dir1",
                "t2": "path_test_dir2"
            }
            assert map_.RefPars.allfilepars == [
                "path_test_free",
                "path_test_free_new",
                # "path_test_choice",
                "path_test_free_new_list",
                "path_test_dir1",
                "path_test_dir2",
                "path_test_rel11",
                # "path_test_rel12_choice",
                "path_test_rel21_new",
                "path_test_rel22_new_list",
                # "path_test_rel23_new_choice",
                # "path_test_rel24_new_choice_list"
            ]
            assert map_.RefPars.filepars_create == [
                "path_test_free_new",
                "path_test_free_new_list",
                "path_test_rel21_new",
                "path_test_rel22_new_list",
                # "path_test_rel23_new_choice",
                # "path_test_rel24_new_choice_list"
            ]
            assert map_.RefPars.intpars == [
                "int_test_free",
                "int_test_choice",
                "int_test_free_list",
                "int_test_choice_list",
                "int_test_choice_list2"
            ]
            assert map_.RefPars.floatpars == [
                "float_test_free",
                "float_test_choice",
                "float_test_free_list",
                "float_test_choice_list",
                "float_test_choice_list2"
            ]
            assert map_.RefPars.boolpars == [
                "bool_test1",
                "bool_test2",
                "bool_test3"
            ]
            assert map_.RefPars.strpars == [
                "str_test_free",
                "str_test_choice",
                "str_test_free_list",
                "str_test_choice_list",
                "str_test_choice_list2"
            ]
            assert map_.RefPars.not_expected_in_deffile == []
            assert map_.RefPars.maybe_list == [
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
                # "path_test_rel24_new_choice_list"
            ]

    def test_maprawpars(self):
        pardict = {
            "map_directory": ["Data/test_mapdir"],
            "testmap1.int_test_free": ["42"],
            "testmap2.float_test_free": ["88.8"]
        }

        cmdline = [
            "-testmap1.ti2", "65",
            "--testmap2.nobool_test1",
            "-testmap2.notb2"
        ]

        _, _, _, InPars, CmdPars, mapdict = self.setup_maprawpars(
            pardict, cmdline)

        assert CmdPars.not_found == {}
        assert InPars.not_found == {}

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.InPars.choices == {"int_test_free": [42]}
        assert testmap1.CmdPars.choices == {"int_test_choice": [65]}
        assert testmap2.InPars.choices == {"float_test_free": [88.8]}
        assert testmap2.CmdPars.choices == {
            "bool_test1": [False], "bool_test2": [False]}

    def test_maprawpars2(self):
        pardict = {
            "map_directory": ["Data/test_mapdir"],
            "testmap1.int_test_free": ["42"],
            "testmap2.float_test_free": ["88.8"]
        }

        cmdline = [
            "-testmap1.ti2", "65",
            "--testmap2.nobool_test1",
            "-testmap2.notb2"
        ]

        _, _, _, InPars, CmdPars, mapdict = self.setup_maprawpars(
            pardict, cmdline, Path(
                "tests/test_tools/Data/default_parameters_2_formap.txt"))

        assert CmdPars.not_found == {}
        assert InPars.not_found == {}

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.InPars.choices == {"int_test_free": [42]}
        assert testmap1.CmdPars.choices == {"int_test_choice": [65]}
        assert testmap2.InPars.choices == {"float_test_free": [88.8]}
        assert testmap2.CmdPars.choices == {
            "bool_test1": [False], "bool_test2": [False]}

    def test_SU_WP_6(self):
        pardict = {"map_directory": ["Data/test_mapdir"]}
        cmdline = []
        deffilepath = Path(
            "tests/test_tools/Data/default_parameters_2_formap_SU_WP_6.txt"
        )
        (
            Files, RefPars, DefPars, InPars, mapdict
        ) = TestMapPars.setup_maprefpars(pardict, cmdline, deffilepath)

        for map_ in mapdict.values():
            map_.find_refpars()

        CmdPars = GM_PP.RawPars.from_cmdline(
            cmdline, RefPars,
            {name: map_.RefPars for name, map_ in mapdict.items()},
            False
        )

        with pytest.raises(GM_Ex.GmapKeyError, match="SU_WP_6$"):
            for map_ in mapdict.values():
                map_.find_rawpars(CmdPars, InPars, DefPars)

    def test_SU_WP_14(self):
        pardict = {"map_directory": ["Data/test_mapdir"]}
        cmdline = []
        deffilepath = Path(
            "tests/test_tools/Data/default_parameters_2_formap_SU_WP_14.txt"
        )
        (
            Files, RefPars, DefPars, InPars, mapdict
        ) = TestMapPars.setup_maprefpars(pardict, cmdline, deffilepath)

        for map_ in mapdict.values():
            map_.find_refpars()

        CmdPars = GM_PP.RawPars.from_cmdline(
            cmdline, RefPars,
            {name: map_.RefPars for name, map_ in mapdict.items()},
            False
        )

        with pytest.raises(GM_Ex.GmapParameterError, match="SU_WP_14$"):
            for map_ in mapdict.values():
                map_.find_rawpars(CmdPars, InPars, DefPars)

    def test_maprunpars(self):
        pardict = {
            "map_directory": ["Data/test_mapdir"],
            "testmap1.int_test_free": ["42"],
            "testmap2.float_test_free": ["88.8"]
        }

        cmdline = [
            "-testmap1.ti2", "65",
            "--testmap2.nobool_test1",
            "-testmap2.notb2"
        ]

        (
            Files, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        for map_ in mapdict.values():
            map_.find_runpars(Files, RunPars)

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.RunPars.is_main is False
        assert testmap2.RunPars.is_main is False

        assert testmap1.RunPars.int_test_free == 42
        assert testmap1.RunPars.int_test_choice == 65

        assert testmap2.RunPars.float_test_free == 88.8
        assert testmap2.RunPars.bool_test1 is False
        assert testmap2.RunPars.bool_test2 is False

    def test_maprunpars2(self):
        pardict = {
            "map_directory": ["Data/test_mapdir"],
            "testmap1.int_test_free": ["42"],
            "testmap2.float_test_free": ["88.8"]
        }

        cmdline = [
            "-testmap1.ti2", "65",
            "--testmap2.nobool_test1",
            "-testmap2.notb2"
        ]

        (
            Files, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline, Path(
                "tests/test_tools/Data/default_parameters_2_formap.txt"))

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        for map_ in mapdict.values():
            map_.find_runpars(Files, RunPars)

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.RunPars.is_main is False
        assert testmap2.RunPars.is_main is False

        assert testmap1.RunPars.int_test_free == 42
        assert testmap1.RunPars.int_test_choice == 65

        assert testmap2.RunPars.float_test_free == 88.8
        assert testmap2.RunPars.bool_test1 is False
        assert testmap2.RunPars.bool_test2 is False

    def test_SU_MR_1(self):
        # setup - Create all necessary objects.
        Files = GM_FH.FileLocations()
        RefPars = GM_PP.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_2.ref"),
            True
        )
        DefPars = RefPars

        pardict = {
            "map_directory": ["Data/test_mapdir"],
            "testmap1.int_test_free": ["42"],
            "testmap2.float_test_free": ["88.8"]
        }

        curpath = Path(__file__).resolve()
        InPars = GM_PP.RawPars.from_dict(
            curpath, pardict, RefPars, False
        )

        cmdline = [
            "-testmap1.ti2", "65",
            "--testmap2.nobool_test1",
            "-testmap2.notb2"
        ]

        mapdirs = GM_PP.find_mapdir(Files, cmdline, InPars, DefPars)
        mapdict = GM_MR.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        CmdPars = GM_PP.RawPars.from_cmdline(
            cmdline, RefPars,
            {name: _map.RefPars for name, _map in mapdict.items()},
            False
        )
        CmdPars.not_found["testmap1.booltest.1"] = ["True"]

        with pytest.raises(GM_Ex.GmapValueError, match="SU_MR_1$"):
            for map_ in mapdict.values():
                map_.find_rawpars(CmdPars, InPars, DefPars)

    def test_SU_NP_2(self):
        pardict = {}
        cmdline = [
            "-md", "tests/test_tools/Data/test_mapdir\\;",
            "--testmap1.path_test_free", "this_file_doesnt_exist.really"
        ]

        (
            Files, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        with pytest.raises(GM_Ex.GmapFileNotFoundError, match="SU_NP_2$"):
            for map_ in mapdict.values():
                map_.find_runpars(Files, RunPars)

    def test_SU_NP_3(self):
        pardict = {}
        cmdline = [
            "-md", "tests/test_tools/Data/test_mapdir\\;",
            "--testmap1.path_test_dir1", "this_directory_doesnt_exist"
        ]

        (
            Files, RefPars, DefPars, InPars, CmdPars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline)

        RunPars = GM_PP.RunPars(
            Files, CmdPars, InPars, DefPars, RefPars, True
        )

        with pytest.raises(GM_Ex.GmapNotADirectoryError, match="SU_NP_3$"):
            for map_ in mapdict.values():
                map_.find_runpars(Files, RunPars)

    @staticmethod
    def setup_maprefpars(pardict, cmdline, defparfilename=None):
        # setup - Create all necessary objects.
        Files = GM_FH.FileLocations()
        # RefPars = GM_PP.RefPars(
        #     Path(
        #         "tests/test_tools/Data/reference_parameters_2.ref"),
        #     True
        # )
        RefPars = GM_PP.RefPars(
            Path(
                "sourcefiles/reference_parameters.ref"
            ), True
        )
        if defparfilename:
            DefPars = GM_PP.RawPars.from_file(
                defparfilename, RefPars, True)
        else:
            DefPars = RefPars

        curpath = Path(__file__).resolve()
        InPars = GM_PP.RawPars.from_dict(
            curpath, pardict, RefPars, False
        )

        mapdirs = GM_PP.find_mapdir(Files, cmdline, InPars, DefPars)
        mapdict = GM_MR.scan_mapdirs(mapdirs, "Singles")

        return Files, RefPars, DefPars, InPars, mapdict

    @staticmethod
    def setup_maprawpars(pardict, cmdline, defparfilename=None):
        (
            Files, RefPars, DefPars, InPars, mapdict
        ) = TestMapPars.setup_maprefpars(pardict, cmdline, defparfilename)

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

        return Files, RefPars, DefPars, InPars, CmdPars, mapdict


def test_get_parameters():
    Files = GM_FH.FileLocations()

    in_parfile = Path("../test_inpar.txt").resolve()
    argslist = []

    (
        RunPars, mapdict, pairs_mapdict, CmdPars, InPars, DefPars, RefPars
    ) = GM_PP.get_parameters(
        Files, in_parfile, argslist
    )

    # A huuuuge amount of tests would be needed here, but all of GM_PP
    # has already been tested separately.
    assert InPars.fname.name == "test_inpar.txt"
    assert DefPars == RefPars
    assert len(mapdict) == 4
    assert CmdPars.choices == {}

    (
        RunPars, mapdict, pairs_mapdict, CmdPars, InPars, DefPars, RefPars
    ) = GM_PP.get_parameters(
        Files, None, argslist
    )

    assert InPars.choices == {}

    argslist = ["-dpf", "../test_defpar.txt"]

    (
        RunPars, mapdict, pairs_mapdict, CmdPars, InPars, DefPars, RefPars
    ) = GM_PP.get_parameters(
        Files, in_parfile, argslist
    )

    assert DefPars.fname.name == "test_defpar.txt"


def test_parse_commandline():
    Files = GM_FH.FileLocations()
    callcommand = [
        "GEM", "run", "../test_inpar.txt", "-verbose", "3"
    ]

    job, in_parfile, cmd_pars = GM_PP.parse_commandline(
        Files, callcommand, alljobs, "GMAP",
        expect_inputfile=True, expect_parameters=True
    )
    assert job == "run"
    assert in_parfile == Path("../test_inpar.txt").resolve()
    assert cmd_pars == ["-verbose", "3"]

    callcommand = [
        "GEM", "run", "-verbose", "3"
    ]
    job, in_parfile, cmd_pars = GM_PP.parse_commandline(
        Files, callcommand, alljobs, "GMAP",
        expect_inputfile=False, expect_parameters=True
    )
    assert job == "run"
    assert in_parfile is None
    assert cmd_pars == ["-verbose", "3"]

    callcommand = [
        "GEM", "run", "-verbose", "3"
    ]
    job, in_parfile, cmd_pars = GM_PP.parse_commandline(
        Files, callcommand, alljobs, "GMAP",
        expect_inputfile=False, expect_parameters=False
    )
    assert job == "run"
    assert in_parfile is None
    assert cmd_pars == []

    callcommand = [
        "GEM", "run", "../test_inpar.txt", "-verbose", "3"
    ]

    job, in_parfile, cmd_pars = GM_PP.parse_commandline(
        Files, callcommand, alljobs, "GMAP",
        expect_inputfile=True, expect_parameters=False
    )
    assert job == "run"
    assert in_parfile == Path("../test_inpar.txt").resolve()
    assert cmd_pars == []


def test_find_defparfile():
    _ = GM_FH.FileLocations()  # still needed for initialization
    argslist = [
        "-sd", "sourcefiles",
        "-dpf", "reference_parameters.ref"
    ]

    pardict = GM_PP.find_defparfile_in_cmd(argslist)

    assert pardict == {
        "source_directory": ["sourcefiles"],
        "default_parameter_filename": ["reference_parameters.ref"]
    }


def test_parse_influencerfile():
    _ = GM_FH.FileLocations()  # still needed for initialization

    file = Path("sourcefiles/infl_file_base.txt")
    groupdict = {
        "All": set("ABC")
    }
    groupdict = GM_PP.parse_influencerfile(file, groupdict)

    assert groupdict == {
        "All": set("ABC"),
        "choice": set("ABC")
    }

    otherfile = Path("tests/test_tools/Data/infl_file.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    groupdict = GM_PP.parse_influencerfile(otherfile, groupdict)

    assert groupdict == {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        "vowels": set("AEIOU"),
        "consonants": set("BCDFGHJKLMNPQRSTVWXYZ"),
        "straight_only": set("AEFHIKLMNTVWXYZ"),
        "curved_only": set("CJOQSU"),
        "curvestr": set("BDGPR"),
        "straight_only_vowels": set("AEI"),
        "curved_or_vowel": set("ACEIJQS"),
        "choice": set("ACEIJKQS")
    }


def test_parse_influencer_par():
    assert GM_PP.parse_influencer_par("A B C") == "A | B | C"
    assert GM_PP.parse_influencer_par("A & B C") == "A & B C"


def test_SU_FP_1():
    Files = GM_FH.FileLocations()

    in_parfile = Path("../test_inpar.txt").resolve()

    # this map no longer exists
    # argslist = ["-dpf", "maps/Singles/testmap1/parameters.ref"]
    argslist = ["-dpf", "tests/test_tools/Data/reference_parameters_2.ref"]

    with pytest.raises(GM_Ex.GmapNotImplementedError, match="SU_FP_1$"):
        _ = GM_PP.get_parameters(
            Files, in_parfile, argslist
        )


def test_SU_GEM_1():
    Files = GM_FH.FileLocations()

    in_parfile = Path("../test_inpar.txt").resolve()
    argslist = ["-dpf", "__init__.py"]

    with pytest.raises(GM_Ex.GmapFileSyntaxError, match="SU_GEM_1$"):
        _ = GM_PP.get_parameters(
            Files, in_parfile, argslist
        )


def test_SU_PP_1():
    Files = GM_FH.FileLocations()
    callcommand = [
        "GEM", "not_available_job_choice", "../test_inpar.txt", "-verbose", "3"
    ]

    with pytest.raises(GM_Ex.GmapKeyError, match="SU_PP_1$"):
        _ = GM_PP.parse_commandline(
            Files, callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )


def test_SU_PP_2():
    Files = GM_FH.FileLocations()
    callcommand = [
        "GEM", "run"
    ]

    with pytest.raises(GM_Ex.GmapParameterError, match="SU_PP_2$"):
        _ = GM_PP.parse_commandline(
            Files, callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )


def test_SU_PP_3():
    Files = GM_FH.FileLocations()
    callcommand = [
        "GEM", "run", "../doesnt_exist.really", "-verbose", "3"
    ]

    with pytest.raises(GM_Ex.GmapFileNotFoundError, match="SU_PP_3$"):
        _ = GM_PP.parse_commandline(
            Files, callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )
    # with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
    #     _ = GM_PP.parse_commandline(
    #         Files, callcommand, alljobs, "GMAP",
    #         expect_inputfile=True, expect_parameters=True
    #     )
    # assert pytest_wrapped_sysexit.type is SystemExit
    # captured = capsys.readouterr()
    # assert captured.out.endswith("SU_PP_3\n")

    callcommand = [
        "GEM", "run", "-verbose", "3"
    ]
    with pytest.raises(GM_Ex.GmapFileNotFoundError, match="SU_PP_3$"):
        _ = GM_PP.parse_commandline(
            Files, callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )

    # -------

    Files = GM_FH.FileLocations()
    RefPars = GM_PP.RefPars(
        Path(
            "tests/test_tools/Data/reference_parameters_2.ref"),
        True
    )
    DefPars = RefPars

    curpath = Path(__file__).resolve()
    InPars = GM_PP.RawPars.from_dict(
        curpath, {}, RefPars, False
    )

    cmdline = ["-md", "this/dir/doesnt_exist\\;"]

    with pytest.raises(GM_Ex.GmapNotADirectoryError, match="SU_PP_3$"):
        _ = GM_PP.find_mapdir(
            Files, cmdline, InPars, DefPars)


def test_SU_PP_4():
    _ = GM_FH.FileLocations()  # still needed for initialization
    argslist = [
        "-sd", "sourcefiles",
        "--source_directory", "sourcefiles",
        "-dpf", "reference_parameters.ref"
    ]

    with pytest.raises(GM_Ex.GmapParameterError, match="SU_PP_4$"):
        _ = GM_PP.find_defparfile_in_cmd(argslist)


def test_SU_WP_4():
    _ = GM_FH.FileLocations()  # still needed for initialization
    argslist = [
        "-sd",
        "-dpf", "reference_parameters.ref"
    ]
    with pytest.raises(GM_Ex.GmapFileSyntaxError, match="SU_WP_4$"):
        _ = GM_PP.find_defparfile_in_cmd(argslist)

    argslist = [
        "-sd", "sourcefiles",
        "-dpf"
    ]
    with pytest.raises(GM_Ex.GmapIndexError, match="SU_WP_4$"):
        _ = GM_PP.find_defparfile_in_cmd(argslist)


def test_SU_WP_5():
    _ = GM_FH.FileLocations()  # still needed for initialization
    argslist = [
        "-md", "someloc"
    ]
    with pytest.raises(GM_Ex.GmapIndexError, match="SU_WP_5$"):
        _ = GM_PP.find_par_in_cmd(
            argslist, ("-md",), "map_directory", True)

    argslist = [
        "-md", "someloc", "-otherpar"
    ]
    with pytest.raises(GM_Ex.GmapFileSyntaxError, match="SU_WP_5$"):
        _ = GM_PP.find_par_in_cmd(
            argslist, ("-md",), "map_directory", True)


def test_SU_NP_4():
    _ = GM_FH.FileLocations()  # still needed for initialization

    file = Path("tests/test_tools/Data/infl_file_SU_NP_4.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    with pytest.raises(GM_Ex.GmapFileSyntaxError, match="SU_NP_4$"):
        groupdict = GM_PP.parse_influencerfile(file, groupdict)


def test_SU_NP_5():
    _ = GM_FH.FileLocations()  # still needed for initialization

    file = Path("tests/test_tools/Data/infl_file_SU_NP_5_1.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    with pytest.raises(GM_Ex.GmapFileSyntaxError, match="SU_NP_5$"):
        groupdict = GM_PP.parse_influencerfile(file, groupdict)

    file = Path("tests/test_tools/Data/infl_file_SU_NP_5_2.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    with pytest.raises(GM_Ex.GmapFileSyntaxError, match="SU_NP_5$"):
        groupdict = GM_PP.parse_influencerfile(file, groupdict)
