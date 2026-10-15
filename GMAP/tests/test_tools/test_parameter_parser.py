"""
Tests all the functions/classes/methods in the file:
src/tools/parameter_parser.py.

Missing tests:

(@ March 11th '25):
384-385, 446, 1191, 1304, 1855-1856 (7 missed statements)

(CUHTAT - currently unknown how to access this )

- SU_FP_7 (CUHTAT)   (383-384)
- ref_pars parse choice - unknown dtype (CUHTAT)  (445)
- RawPars verify choice - unknown dtype (CUHTAT)  (1190)
- RawPars checkparexist - variable may occur multiple times, but is also
  not expected in deffiles (N/A in refpars)  (1303)
- RunPars unknown loc for -md - SU_NP_3   (CUHTAT, SU_PP_3!)  (1854-1855)

"""

# standard library imports
from pathlib import Path

# 3rd party imports
import numpy as np
import pytest

# local imports
from GMAP.src.programs.GEM import alljobs
import GMAP.src.tools.constants as GM_con
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.file_handler as GM_fh
import GMAP.src.tools.map_reader as GM_mr
import GMAP.src.tools.parameter_parser as GM_pp


class TestRefPars:
    def test_correctness(self):
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )

        assert ref_pars.fname.name == "reference_parameters_1.ref"
        assert ref_pars.options == {
            "verbose": [0, 1, 2, 3, 4],
            "verbose_logfile": [0, 1, 2, 3, 4],
            "command_line_color": ["white", "4bit", "24bit"],
            "output_format": ["bin", "txt"],
            "output_data": ["ham", "dip", "ene", "pos", "dbp", "ram"],
            "estatics_method": ["perres", "perres_nocut"],
            "treat_box": ["auto", "orthorhombic", "triclinic"],
            "hamiltonian_units": ["cm-1", "eV"],
            "energies_units": ["cm-1", "eV"],
            "dipoles_units": ["Debye", "eBohr"],
            "raman_units": ["Ang3", "Bohr3"],
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
        assert ref_pars.choices == {
            "topology_file": [Path("../../../sourcefiles/pdb_1AKI.tpr")],
            "trajectory_file": [Path(
                "../../../sourcefiles/pdb_1AKI_50frame.xtc"
            )],
            "source_directory": [Path("../../../sourcefiles")],
            "VEG_clib_file": [
                Path("VEG" + GM_fh.FileLocations.clib_extension)],
            "log_filename": [Path("log.log")],
            "log_profiling_filename": [Path("prof.out")],
            "log_profiling_tempfile": [Path("prof.temp")],
            "log_profiling_graph_filename": [Path("profout.png")],
            "output_parameter_filename": [Path("parameters.txt")],
            "output_legend_filename": [Path("legend.txt")],
            "output_couplingvis_filename": [Path("couplingvisualization.pdf")],
            "output_estatics_filename": [Path("estatics.txt")],
            "output_hamiltonian_filename": [Path("hamiltonian")],
            "output_dipole_filename": [Path("dipoles")],
            "output_energies_filename": [Path("energies")],
            "output_raman_filename": [Path("raman_tensor")],
            "output_positions_filename": [Path("positions")],
            "output_doublepos_filename": [Path("doublepos")],
            "map_directory": [Path("../../../maps")],
            "maps_to_use": ["AmideSC"],
            "couplings_to_use": [["DipDip", ":All"]],
            "couplings_scale": [[":All", "1"]],
            "dielectric_constant": [1.0],
            "singles_whitelist": [[":All", ":All"]],
            "singles_blacklist": [[":All", ":None"]],
            "influencers_whitelist": [":All"],
            "influencers_blacklist": [":None"],
            "influencers_file": [Path(
                "../../../sourcefiles/infl_file_base.txt"
            )],
            "influencers_select_atoms": ["segid", "*"],
            "influencers": [":All"],
            "verbose": [2],
            "verbose_logfile": [2],
            "safe_mode": [False],
            "dark_mode": [True],
            "command_line_color": ["24bit"],
            "command_line_length": [79],
            "prevent_overwrite": [False],
            "dont_report_error": ["none"],
            "output_format": ["bin"],
            "output_data": ["ham", "dip", "pos"],
            "estatics_method": ["perres"],
            "neutral_charge_threshold": [0.0001],
            "guess_bonds": [False],
            "treat_box": ["auto"],
            "estatic_range": [20.0],
            "estatic_smooth_range": [5.0],
            "start_frame": [0],
            "number_frames": [999999999],
            "stop_frame": [999999999],
            "time_limit": [999999],
            "batch_size": [25],
            "number_cores": [1],
            "profiler": [False],
            "profiler_graph": [False],
            "hamiltonian_units": ["cm-1"],
            "hamiltonian_multiplier": [1],
            "energies_units": ["cm-1"],
            "energies_multiplier": [1],
            "dipoles_units": ["Debye"],
            "dipoles_multiplier": [1],
            "raman_units": ["Ang3"],
            "raman_multiplier": [1],
            "positions_units": ["Ang"],
            "positions_multiplier": [1],
            "doublepos_units": ["Ang"],
            "doublepos_multiplier": [1],
            "positions_center": [0.5, 0.5, 0.5],
            "couplingvis_figsize": [8],
            "couplingvis_dpi": [100],
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
            "path_test_free": [Path("../test_math_functions.py")],
            "path_test_free_new": [Path("test_outfile.txt")],
            "path_test_free_new_list": [
                Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
            ],
            "path_test_dir1": [Path("../../test_tools")],
            "path_test_dir2": [Path("../Data")],
            "path_test_rel11": [Path("test_math_functions.py")],
            "path_test_rel21_new": [Path("test_outfile_2_1.txt")],
            "path_test_rel22_new_list": [
                Path("test_outfile_2_2_1.txt"), Path("test_outfile_2_2_2.txt")
            ],
        }
        assert ref_pars.shorthands == {
            "top": "topology_file",
            "trj": "trajectory_file",
            "sd": "source_directory",
            "dpf": "default_parameter_filename",
            "oef": "output_energies_filename",
            "ohf": "output_hamiltonian_filename",
            "odf": "output_dipole_filename",
            "orf": "output_raman_filename",
            "opf": "output_positions_filename",
            "md": "map_directory",
            "um": "maps_to_use",
            "safe": "safe_mode",
            "dm": "dark_mode",
            "nc": "number_cores",
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
        assert ref_pars.organized_filepars == {
            "source_directory": [
                "default_parameter_filename",
                "VEG_clib_file"],
            "log_directory": [
                "log_filename", "log_profiling_filename",
                "log_profiling_tempfile", "log_profiling_graph_filename"],
            "output_directory": [
                "output_parameter_filename",
                "output_legend_filename", "output_couplingvis_filename",
                "output_estatics_filename", "output_hamiltonian_filename",
                "output_dipole_filename", "output_energies_filename",
                "output_raman_filename",
                "output_positions_filename", "output_doublepos_filename"
            ],
            "path_test_dir1": ["path_test_rel11"],
            "path_test_dir2": [
                "path_test_rel21_new", "path_test_rel22_new_list"
            ]
        }
        assert ref_pars.organized_filepars_id == {
            "sd": "source_directory",
            "lg": "log_directory",
            "op": "output_directory",
            "t1": "path_test_dir1",
            "t2": "path_test_dir2"
        }
        assert ref_pars.allfilepars == [
            "topology_file",
            "trajectory_file",
            "source_directory",
            "default_parameter_filename",
            "VEG_clib_file",
            "log_directory",
            "log_filename",
            "log_profiling_filename",
            "log_profiling_tempfile",
            "log_profiling_graph_filename",
            "output_directory",
            "output_parameter_filename",
            "output_legend_filename",
            "output_couplingvis_filename",
            "output_estatics_filename",
            "output_hamiltonian_filename",
            "output_dipole_filename",
            "output_energies_filename",
            "output_raman_filename",
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
        assert ref_pars.filepars_create == [
            "log_filename",
            "log_profiling_filename",
            "log_profiling_tempfile",
            "log_profiling_graph_filename",
            "output_parameter_filename",
            "output_legend_filename",
            "output_couplingvis_filename",
            "output_estatics_filename",
            "output_hamiltonian_filename",
            "output_dipole_filename",
            "output_energies_filename",
            "output_raman_filename",
            "output_positions_filename",
            "output_doublepos_filename",
            "path_test_free_new",
            "path_test_free_new_list",
            "path_test_rel21_new",
            "path_test_rel22_new_list",
        ]
        assert ref_pars.intpars == [
            "verbose",
            "verbose_logfile",
            "command_line_length",
            "start_frame",
            "number_frames",
            "stop_frame",
            "time_limit",
            "batch_size",
            "number_cores",
            "couplingvis_dpi",
            "int_test_free",
            "int_test_choice",
            "int_test_free_list",
            "int_test_choice_list",
            "int_test_choice_list2",
            "int_test_nodef"
        ]
        assert ref_pars.floatpars == [
            "dielectric_constant",
            "neutral_charge_threshold",
            "estatic_range",
            "estatic_smooth_range",
            "hamiltonian_multiplier",
            "energies_multiplier",
            "dipoles_multiplier",
            "raman_multiplier",
            "positions_multiplier",
            "doublepos_multiplier",
            "positions_center",
            "couplingvis_figsize",
            "float_test_free",
            "float_test_choice",
            "float_test_free_list",
            "float_test_choice_list",
            "float_test_choice_list2"
        ]
        assert ref_pars.boolpars == [
            "safe_mode",
            "dark_mode",
            "prevent_overwrite",
            "guess_bonds",
            "profiler",
            "profiler_graph",
            "bool_test1",
            "bool_test2",
            "bool_test3"
        ]
        assert ref_pars.strpars == [
            "maps_to_use",
            "couplings_to_use",
            "couplings_scale",
            "singles_whitelist",
            "singles_blacklist",
            "influencers_whitelist",
            "influencers_blacklist",
            "influencers_select_atoms",
            "command_line_color",
            "dont_report_error",
            "output_format",
            "output_data",
            "estatics_method",
            "treat_box",
            "hamiltonian_units",
            "energies_units",
            "dipoles_units",
            "raman_units",
            "positions_units",
            "doublepos_units",
            "str_test_free",
            "str_test_choice",
            "str_test_free_list",
            "str_test_choice_list",
            "str_test_choice_list2"
        ]
        assert ref_pars.not_expected_in_deffile == [
            "default_parameter_filename",
            "log_directory",
            "output_directory",
            "int_test_nodef",
            "path_test_nodef"
        ]
        assert ref_pars.maybe_list == [
            "map_directory",
            "maps_to_use",
            "couplings_to_use",
            "couplings_scale",
            "singles_whitelist",
            "singles_blacklist",
            "influencers_whitelist",
            "influencers_blacklist",
            "influencers_select_atoms",
            "dont_report_error",
            "output_format",
            "output_data",
            "positions_center",
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
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_3.ref"),
            True
        )

        assert ref_pars.choices["influencers"] == [
            ":All", "-", "(", ":None", ")"]

        assert ref_pars.choices["command_line_color"] == ["white"]

    def test_SU_FP_1(self):
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )

        with pytest.raises(GM_ex.GmapNotImplementedError, match="SU_FP_1$"):
            GM_pp.RefPars.add_reffile(
                Path("tests/test_tools/Data/reference_parameters_1.ref"),
                ref_pars
            )

    def test_SU_FP_2(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_2.ref",
            "SU_FP_2",
            GM_ex.GmapFileSyntaxError
        )

    def test_SU_FP_3(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_3_1.ref",
            "SU_FP_3",
            GM_ex.GmapKeyError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_3_2.ref",
            "SU_FP_3",
            GM_ex.GmapTypeError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_3_3.ref",
            "SU_FP_3",
            GM_ex.GmapTypeError
        )

    def test_SU_FP_4(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_4_1.ref",
            "SU_FP_4",
            GM_ex.GmapFileSyntaxError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_4_2.ref",
            "SU_FP_4",
            GM_ex.GmapFileSyntaxError
        )

    def test_SU_FP_5(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_5_1.ref",
            "SU_FP_5",
            GM_ex.GmapValueError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_5_2.ref",
            "SU_FP_5",
            GM_ex.GmapValueError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_5_3.ref",
            "SU_FP_5",
            GM_ex.GmapValueError
        )

    def test_SU_FP_6(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_6.ref",
            "SU_FP_6",
            GM_ex.GmapIndexError
        )

    def test_SU_FP_7(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_7_1.ref",
            "SU_FP_7",
            GM_ex.GmapValueError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_7_2.ref",
            "SU_FP_7",
            GM_ex.GmapValueError
        )
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_7_3.ref",
            "SU_FP_7",
            GM_ex.GmapFileSyntaxError
        )

    def test_SU_FP_8(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_8.ref",
            "SU_FP_8",
            GM_ex.GmapParameterError
        )

    def test_SU_FP_9(self):
        self.systest(
            "tests/test_tools/Data/reference_parameters_SU_FP_9.ref",
            "SU_FP_9",
            GM_ex.GmapTypeError, False
        )

    @staticmethod
    def systest(fname, errcode, errclass=None, is_main=True):
        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_pp.RefPars(Path(fname), is_main)


class TestRawPars:
    def test_fromfile(self):
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )
        def_pars = GM_pp.RawPars.from_file(
            Path("tests/test_tools/Data/default_parameters_1.txt"),
            ref_pars, True
        )
        sd = Path("../../../sourcefiles")

        assert def_pars.fname.name == "default_parameters_1.txt"
        assert def_pars.is_default is True
        assert def_pars.choices == {
            "topology_file": [sd / "pdb_1AKI.tpr"],
            "trajectory_file": [sd / "pdb_1AKI_50frame.xtc"],
            "source_directory": [sd],
            "VEG_clib_file": [
                Path("VEG" + GM_fh.FileLocations.clib_extension)],
            "log_filename": [Path("log.log")],
            "log_profiling_filename": [Path("prof.out")],
            "log_profiling_tempfile": [Path("prof.temp")],
            "log_profiling_graph_filename": [Path("profout.png")],
            "output_parameter_filename": [Path("parameters.txt")],
            "output_legend_filename": [Path("legend.txt")],
            "output_couplingvis_filename": [Path("couplingvisualization.pdf")],
            "output_estatics_filename": [Path("estatics.txt")],
            "output_hamiltonian_filename": [Path("hamiltonian")],
            "output_dipole_filename": [Path("dipoles")],
            "output_energies_filename": [Path("energies")],
            "output_raman_filename": [Path("raman_tensor")],
            "output_positions_filename": [Path("positions")],
            "output_doublepos_filename": [Path("doublepos")],
            "map_directory": [Path("../../../maps")],
            "maps_to_use": ["AmideSC"],
            "couplings_to_use": [["DipDip", ":All"]],
            "couplings_scale": [[":All", "1"]],
            "dielectric_constant": [1],
            "singles_whitelist": [[":All", ":All"]],
            "singles_blacklist": [[":All", ":None"]],
            "influencers_whitelist": [":All"],
            "influencers_blacklist": [":None"],
            "influencers_file": [sd/"infl_file_base.txt"],
            "influencers_select_atoms": ["segid", "*"],
            "influencers": [":All"],
            "verbose": [3],
            "verbose_logfile": [1],
            "safe_mode": [False],
            "dark_mode": [True],
            "command_line_color": ["24bit"],
            "command_line_length": [79],
            "prevent_overwrite": [False],
            "dont_report_error": ["none"],
            "output_format": ["bin", "txt"],
            "output_data": ["ham", "dip", "pos"],
            "estatics_method": ["perres"],
            "neutral_charge_threshold": [0.0001],
            "guess_bonds": [False],
            "treat_box": ["auto"],
            "estatic_range": [20.0],
            "estatic_smooth_range": [5.0],
            "start_frame": [0],
            "number_frames": [999999999],
            "stop_frame": [999999999],
            "time_limit": [999999],
            "batch_size": [25],
            "number_cores": [1],
            "profiler": [False],
            "profiler_graph": [False],
            "hamiltonian_units": ["cm-1"],
            "hamiltonian_multiplier": [1],
            "energies_units": ["cm-1"],
            "energies_multiplier": [1],
            "dipoles_units": ["Debye"],
            "dipoles_multiplier": [1],
            "raman_units": ["Ang3"],
            "raman_multiplier": [1],
            "positions_units": ["Ang"],
            "positions_multiplier": [1],
            "doublepos_units": ["Ang"],
            "doublepos_multiplier": [1],
            "positions_center": [0.5, 0.5, 0.5],
            "couplingvis_figsize": [8],
            "couplingvis_dpi": [100],
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
            "path_test_free": [Path("../test_math_functions.py")],
            "path_test_free_new": [Path("tost_outfile.txt")],
            # "path_test_choice": [Path("../test_math_functions.py")],
            "path_test_free_new_list": [
                Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
            ],
            "path_test_dir1": [Path("../../test_tools")],
            "path_test_dir2": [Path("../Data/testout")],
            "path_test_rel11": [Path("test_parameter_parser.py")],
            # "path_test_rel12_choice": [Path("test_math_functions.py")],
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
        # Still missing def_pars.not_found

    def test_fromdict(self):
        ref_pars = TestRawPars.setup_test_SU_WP_base()

        pardict = {
            "verbose": ["4"],
            "hamiltonian_units": ["eV"],
            "energies_units": ["eV"],
            "dipoles_units": ["eBohr"],
            "raman_units": ["Bohr3"],
            "positions_units": ["Bohr"],
            "doublepos_units": ["Bohr"],
            "nobool_test1": [],
            "nobool_test2": ["false"],
            "int_test_free_list": ["88", "44"],
            "path_test_dir2": ["../testout2"]
        }

        in_pars = GM_pp.RawPars.from_dict(
            Path("mydict"), pardict, ref_pars, False
        )

        assert in_pars.fname.name == "mydict"
        assert in_pars.is_default is False
        assert in_pars.choices == {
            "verbose": [4],
            "hamiltonian_units": ["eV"],
            "hamiltonian_multiplier": [GM_con.cm2eV],
            "energies_units": ["eV"],
            "energies_multiplier": [GM_con.cm2eV],
            "dipoles_units": ["eBohr"],
            "dipoles_multiplier": [GM_con.Debye2ea0],
            "raman_units": ["Bohr3"],
            "raman_multiplier": [GM_con.ang2bohr**3],
            "positions_units": ["Bohr"],
            "positions_multiplier": [GM_con.ang2bohr],
            "doublepos_units": ["Bohr"],
            "doublepos_multiplier": [GM_con.ang2bohr],
            "bool_test1": [False],
            "bool_test2": [True],
            "int_test_free_list": [88, 44],
            "path_test_dir2": [Path("../testout2")]
        }
        # Still missing in_pars.not_found

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

        ref_pars, _, _, maprefdict = self.setup_test_SU_WP_cmd(
            cmdline)

        cmd_pars = GM_pp.RawPars.from_cmdline(
            cmdline, ref_pars, maprefdict, False
        )

        assert cmd_pars.fname.name == "command line"
        assert cmd_pars.is_default is False
        assert cmd_pars.choices == {
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
        # Still missing in_pars.not_found
        # Also, test map-shorthand

    def test_variations(self):
        def infltest(cmdline, inflchoice):
            ref_pars, _, _, maprefdict = self.setup_test_SU_WP_cmd(
                cmdline)

            cmd_pars = GM_pp.RawPars.from_cmdline(
                cmdline, ref_pars, maprefdict, False
            )
            assert cmd_pars.choices["influencers"] == inflchoice

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

        ref_pars = TestRawPars.setup_test_SU_WP_base()

        pardict = {
            "verbose": ["4"],
            "raman_units": ["Ang3"],
            "positions_units": ["Ang"],
            "doublepos_units": ["Ang"],
            "safe_mode": ["True"],
            # "nobool_test1": [],
            # "nobool_test2": ["false"],
            # "int_test_free_list": ["88", "44"],
            # "path_test_dir2": ["../testout2"]
        }

        in_pars = GM_pp.RawPars.from_dict(
            Path("mydict"), pardict, ref_pars, False
        )

        assert in_pars.fname.name == "mydict"
        assert in_pars.is_default is False
        assert in_pars.choices == {
            "verbose": [4],
            "raman_units": ["Ang3"],
            "raman_multiplier": [1],
            "positions_units": ["Ang"],
            "positions_multiplier": [1],
            "doublepos_units": ["Ang"],
            "doublepos_multiplier": [1],
            "safe_mode": [True],
            "command_line_color": ["white"],
            # "bool_test1": [False],
            # "bool_test2": [True],
            # "int_test_free_list": [88, 44],
            # "path_test_dir2": [Path("../testout2")]
        }

    def test_SU_WP_1(self):
        cmdline = ["int_test_free", "42"]
        self.systest_cmdline(cmdline, "SU_WP_1", GM_ex.GmapFileSyntaxError)

    def test_SU_WP_2(self):
        cmdline = ["--unknown_map.does_not_exist", "42"]
        self.systest_cmdline(cmdline, "SU_WP_2", GM_ex.GmapKeyError)

        cmdline = ["-AmideSC.noudtp", "22"]
        self.systest_cmdline(cmdline, "SU_WP_2", GM_ex.GmapKeyError)

    def test_SU_WP_3(self):
        cmdline = ["--does_not_exist", "42"]
        self.systest_cmdline(cmdline, "SU_WP_3", GM_ex.GmapKeyError)

        cmdline = ["-noudtp", "22"]
        self.systest_cmdline(cmdline, "SU_WP_3", GM_ex.GmapKeyError)

    def test_SU_WP_4(self):
        cmdline = ["--int_test_free_list"]
        self.systest_cmdline(cmdline, "SU_WP_4", GM_ex.GmapIndexError)

    def test_SU_WP_5(self):
        cmdline = ["--int_test_free_list", "32"]
        self.systest_cmdline(cmdline, "SU_WP_5", GM_ex.GmapIndexError)

        cmdline = ["--int_test_free_list", "32", "-tb1"]
        self.systest_cmdline(cmdline, "SU_WP_5", GM_ex.GmapFileSyntaxError)

    def test_SU_WP_6(self):
        pardict = {
            "thispar_doesntexist": ["42"]
        }
        self.systest_pardict(pardict, "SU_WP_6", GM_ex.GmapKeyError)

    def test_SU_WP_7(self):
        pardict = {
            "int_test_free": []
        }
        self.systest_pardict(
            pardict, "SU_WP_7", GM_ex.GmapFileSyntaxError, isdef=True)

    def test_SU_WP_8(self):
        pardict = {
            "int_test_free": []
        }
        self.systest_pardict(pardict, "SU_WP_8", GM_ex.GmapFileSyntaxError)

    def test_SU_WP_9(self):
        pardict = {
            "int_test_free": ["53", "55"]
        }
        self.systest_pardict(pardict, "SU_WP_9", GM_ex.GmapFileSyntaxError)

    def test_SU_WP_10(self):
        pardict = {
            "bool_test1": ["apple"]
        }
        self.systest_pardict(pardict, "SU_WP_10", GM_ex.GmapValueError)

    def test_SU_WP_11(self):
        pardict = {
            "int_test_choice": ["22"]  # 22 is not a listed choice in reffile
        }
        self.systest_pardict(pardict, "SU_WP_11", GM_ex.GmapValueError)

        pardict = {
            "estatic_range": ["-2"]
        }
        self.systest_pardict(pardict, "SU_WP_11", GM_ex.GmapValueError)

        pardict = {
            "estatic_smooth_range": ["-2"]
        }
        self.systest_pardict(pardict, "SU_WP_11", GM_ex.GmapValueError)

    def test_SU_WP_12(self):
        pardict = {
            "int_test_free": ["apple"]
        }
        self.systest_pardict(pardict, "SU_WP_12", GM_ex.GmapTypeError)

        pardict = {"dont_report_error": ["unavail_unavail"]}
        self.systest_pardict(pardict, "SU_WP_12", GM_ex.GmapFileSyntaxError)

    def test_SU_WP_13(self):
        pardict = {
            "log_directory": ["newdir"]
        }
        self.systest_pardict(
            pardict, "SU_WP_13", GM_ex.GmapParameterError, isdef=True)

    def test_SU_WP_14(self):
        pardict = {
            "int_test_free": ["44"],
            "float_test_free": ["22.2"]
        }
        self.systest_pardict(
            pardict, "SU_WP_14", GM_ex.GmapParameterError, isdef=True)

        cmdline = ["--verbose", "2"]
        self.systest_cmdline(
            cmdline, "SU_WP_14", GM_ex.GmapParameterError, isdef=True)

    def test_SU_WP_15(self):
        pardict = {
            "nonexistentmap.par1": ["1"]
        }
        ref_pars = TestRawPars.setup_test_SU_WP_base()
        in_pars = GM_pp.RawPars.from_dict(
            Path("mydict"), pardict, ref_pars, False
        )

        with pytest.raises(GM_ex.GmapKeyError, match="SU_WP_15$"):
            in_pars.finalize_map_pars()

    def test_SU_WP_16(self):
        pardict = {
            "influencers_whitelist": [":All"],
            "influencers_select_atoms": ["segid", "*"]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "hamiltonian_units": ["cm-1"],
            "hamiltonian_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "energies_units": ["cm-1"],
            "energies_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "dipoles_units": ["Debye"],
            "dipoles_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "raman_units": ["Ang3"],
            "raman_multiplier": [2]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "positions_units": ["Bohr"],
            "positions_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_ex.GmapParameterError, isdef=False)

        # ------------------------

        pardict = {
            "doublepos_units": ["Bohr"],
            "doublepos_multiplier": [1]
        }
        self.systest_pardict(
            pardict, "SU_WP_16", GM_ex.GmapParameterError, isdef=False)

    def test_SU_WP_17(self):
        pardict = {
            "start_frame": [0],
            "number_frames": [5],
            "stop_frame": [10]
        }
        self.systest_pardict(
            pardict, "SU_WP_17", GM_ex.GmapParameterError, isdef=False)

        pardict = {
            "number_frames": [10],
            "stop_frame": [5]
        }
        self.systest_pardict(
            pardict, "SU_WP_17", GM_ex.GmapParameterError, isdef=False)

        pardict = {
            "start_frame": [10],
            "stop_frame": [5]
        }
        self.systest_pardict(
            pardict, "SU_WP_17", GM_ex.GmapParameterError, isdef=False)

    @staticmethod
    def setup_test_SU_WP_cmd(cmdline):
        ref_pars = TestRawPars.setup_test_SU_WP_base()

        in_pars = GM_pp.RawPars.create_empty()

        mapdirs = GM_pp.find_mapdir(cmdline, in_pars, ref_pars)
        mapdict = GM_mr.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        maprefdict = {name: _map.ref_pars for name, _map in mapdict.items()}

        return ref_pars, in_pars, mapdict, maprefdict

    @staticmethod
    def setup_test_SU_WP_base():
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )
        return ref_pars

    @staticmethod
    def systest_cmdline(cmdline, errcode, errclass, isdef=False):
        (
            ref_pars, _, _, maprefdict
        ) = TestRawPars.setup_test_SU_WP_cmd(cmdline)

        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_pp.RawPars.from_cmdline(
                cmdline, ref_pars, maprefdict, isdef
            )

    @staticmethod
    def systest_pardict(pardict, errcode, errclass, isdef=False):
        ref_pars = TestRawPars.setup_test_SU_WP_base()
        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_pp.RawPars.from_dict(
                Path("mydict"), pardict, ref_pars, isdef
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
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]

        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        # Actually create run_pars

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )
        run_pars.manage_dtypes()
        print(ref_pars.choices["output_format"])

        assert run_pars.is_main is True

        # now, assert all choices...
        assert run_pars.topology_file == Path(
            curpath / "../../../sourcefiles/pdb_1AKI.tpr").resolve()
        assert run_pars.trajectory_file == Path(
            curpath / "../../../sourcefiles/pdb_1AKI_50frame.xtc").resolve()
        assert run_pars.source_directory == Path(
            curpath / "../../../sourcefiles").resolve()
        assert run_pars.VEG_clib_file in [
            Path(curpath / ("../../../sourcefiles/VEG_" + fname)).resolve()
            for fname in [
                "Win64bit.dll", "Win32bit.dll", "MacOS.dylib", "Linux.so"]
        ]
        assert run_pars.log_directory == Path(curpath / "../Data").resolve()
        assert run_pars.log_filename == Path(
            curpath / "../Data/log.log").resolve()
        assert run_pars.output_directory == Path(curpath / "../Data").resolve()
        assert run_pars.output_estatics_filename == Path(
            curpath / "../Data/estatics.txt").resolve()
        assert run_pars.output_hamiltonian_filename == Path(
            curpath / "../Data/hamiltonian").resolve()
        assert run_pars.output_dipole_filename == Path(
            curpath / "../Data/dipoles").resolve()
        assert run_pars.output_energies_filename == Path(
            curpath / "../Data/energies").resolve()
        assert run_pars.map_directory == [Path(
            curpath / "../../../maps").resolve()]
        assert run_pars.maps_to_use == ["AmideSC"]
        assert run_pars.influencers == [":All"]

        assert run_pars.verbose == 4
        assert run_pars.verbose_logfile == 1
        assert run_pars.prevent_overwrite is False
        assert run_pars.output_format == ["bin", "txt"]
        assert run_pars.output_data == ["ham", "dip", "pos"]

        assert run_pars.neutral_charge_threshold == 0.0001
        assert run_pars.guess_bonds is False
        assert run_pars.estatic_range == np.float32(20)
        assert run_pars.estatic_smooth_range == np.float32(5)

        assert run_pars.start_frame == 0
        assert run_pars.number_frames == 999999999
        assert run_pars.stop_frame == 999999999

        assert run_pars.str_test_free == "freechoice"
        assert run_pars.str_test_choice == "not_this"
        assert run_pars.str_test_free_list == ["freechoice1", "freechoice2"]
        assert run_pars.str_test_choice_list == ["not_this"]
        assert run_pars.str_test_choice_list2 == ["dont_pick_this", "but_this"]

        assert run_pars.bool_test1 is True
        assert run_pars.bool_test2 is False
        assert run_pars.bool_test3 is False

        assert run_pars.int_test_free == 42
        assert run_pars.int_test_choice == 65
        assert run_pars.int_test_free_list == [88, 44]
        assert run_pars.int_test_choice_list == [64]
        assert run_pars.int_test_choice_list2 == [12, 85]
        assert run_pars.int_test_nodef == 33

        assert run_pars.float_test_free == 6.2
        assert run_pars.float_test_choice == 83.7
        assert run_pars.float_test_free_list == [32.0, 87.0]
        assert run_pars.float_test_choice_list == [99.9]
        assert run_pars.float_test_choice_list2 == [44.5, 33.0]

        assert run_pars.path_test_free == Path(
            curpath / "../test_math_functions.py").resolve()
        assert run_pars.path_test_free_new == Path(
            curpath / "../Data/tost_outfile.txt").resolve()
        # assert run_pars.path_test_choice == Path(
        #     curpath / "../test_Mathfunctions.py").resolve()
        assert run_pars.path_test_free_new_list == [
            Path(curpath / "../Data/test_outfile_0_1.txt").resolve(),
            Path(curpath / "../Data/test_outfile_0_2.txt").resolve()
        ]
        assert run_pars.path_test_dir1 == Path(
            curpath / "..").resolve()
        assert run_pars.path_test_dir2 == Path(
            curpath / "../Data/testout2").resolve()
        assert run_pars.path_test_rel11 == Path(
            curpath / "../test_parameter_parser.py").resolve()
        # assert run_pars.path_test_rel12_choice == Path(
        #     curpath / "../test_math_functions.py").resolve()
        assert run_pars.path_test_rel21_new == Path(
            curpath / "../Data/testout2/tost_outfile_2_1.txt").resolve()
        assert run_pars.path_test_rel22_new_list == [
            Path(curpath / "../../../tast_outfile_2_2_4.txt").resolve(),
            Path(curpath / "../../../tast_outfile_2_2_0.txt").resolve()
        ]
        # assert run_pars.path_test_rel23_new_choice == Path(
        #     curpath / "../Data/testout2/test_outfile_2_3_1.txt").resolve()
        # assert run_pars.path_test_rel24_new_choice_list == [
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
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_2.ref"),
            True
        )
        def_pars = GM_pp.RawPars.from_file(
            Path("tests/test_tools/Data/default_parameters_2.txt"),
            ref_pars, True
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
        all_in_pars = [
            GM_pp.RawPars.from_dict(
                curpath / "../Data/testout/imaginary_inpfile", pardict,
                ref_pars, False
            ) for pardict in pardicts
        ]

        mapdirs = GM_pp.find_mapdir(
            cmdlines[0], all_in_pars[0], def_pars)
        mapdict = GM_mr.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        maprefdict = {name: _map.ref_pars for name, _map in mapdict.items()}

        all_cmd_pars = [
            GM_pp.RawPars.from_cmdline(
                cmdline, ref_pars, maprefdict, False
            ) for cmdline in cmdlines
        ]

        # Actually create run_pars
        allrunpars = []
        for cmd_pars in all_cmd_pars:
            for in_pars in all_in_pars:
                allrunpars.append(GM_pp.RunPars(
                    cmd_pars, in_pars, def_pars, ref_pars, True
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
        for run_pars, exp_ddf, exp_ndf, exp_dnf, exp_nnf in zip(
            allrunpars, expected_ddf, expected_ndf, expected_dnf, expected_nnf
        ):
            # GM_pt.devprint(counter)
            # counter += 1
            assert run_pars.def_def_file == exp_ddf
            assert run_pars.nod_def_file == exp_ndf
            assert run_pars.def_nod_file == exp_dnf
            assert run_pars.nod_nod_file == exp_nnf

    def test_framenumbers(self):
        pardict = {
            "start_frame": ["4"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_math_functions.py")]
        }

        curpath = Path(__file__).resolve()

        cmdline = []

        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        assert run_pars.start_frame == 4
        assert run_pars.number_frames == 999999995
        assert run_pars.stop_frame == 999999999

        pardict = {
            "start_frame": ["4"],
            "number_frames": ["20"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_math_functions.py")]
        }

        curpath = Path(__file__).resolve()

        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        assert run_pars.start_frame == 4
        assert run_pars.number_frames == 20
        assert run_pars.stop_frame == 24

        pardict = {
            "number_frames": ["4"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_math_functions.py")]
        }

        curpath = Path(__file__).resolve()

        cmdline = ["--stop_frame", "8"]

        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        assert run_pars.start_frame == 4
        assert run_pars.number_frames == 4
        assert run_pars.stop_frame == 8

        pardict = {
            "stop_frame": ["4"],
            "int_test_nodef": ["33"],
            "path_test_nodef": [Path("test_math_functions.py")]
        }

        curpath = Path(__file__).resolve()

        cmdline = ["--stop_frame", "8"]

        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        assert run_pars.start_frame == 0
        assert run_pars.number_frames == 8
        assert run_pars.stop_frame == 8

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
            "path_test_nodef": [Path("test_math_functions.py")]
        }

        curpath = Path(__file__).resolve()
        cmdline = ["-md", "maps", "tests/test_tools/Data/test_mapdir\\;"]

        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = self.setup_for_runpars(pardict, curpath, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )
        assert run_pars.pair_v_coupling_dict == {
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
        assert run_pars.coupling_v_pair_dict == {
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

        _ = GM_pp.RawPars.from_file(
            curpath.parent/"Data"/"rawpars_coupling.txt", ref_pars,
            False
        )

    def test_resolve_singles_BWlist(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "singles_whitelist": [["AmideSC", "2"], ["AmideSC", "4"]]
        }
        curpath = Path("")
        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = TestRunPars.setup_for_runpars(pardict, curpath, cmdline)

        runpars = GM_pp.RunPars(cmd_pars, in_pars, def_pars, ref_pars, True)
        assert len(runpars.singles_whitelist_dict["AmideSC"]) == 2

        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "singles_whitelist": [
                ["AmideSC", "2"], ["AmideSC", "4"], [":All", "2"]]
        }
        curpath = Path("")
        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = TestRunPars.setup_for_runpars(pardict, curpath, cmdline)

        runpars = GM_pp.RunPars(cmd_pars, in_pars, def_pars, ref_pars, True)
        assert len(runpars.singles_whitelist_dict["AmideSC"]) == 3

    def test_final_resolve_coupling_scale(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_scale": [["DipDip", "2"]]
        }
        curpath = Path("")
        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = TestRunPars.setup_for_runpars(pardict, curpath, cmdline)

        runpars = GM_pp.RunPars(cmd_pars, in_pars, def_pars, ref_pars, True)
        runpars.requested_pairmapdict = {"map": "dummy"}
        runpars.final_resolve_coupling_scale()
        assert runpars.coupling_scale_factors_dict == {
            "map": 1.0,
            "DipDip": 2.0
        }

    def test_SU_NP_1(self):
        cmdline = [
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        self.systest_runpars(cmdline, "SU_NP_1", GM_ex.GmapParameterError)

        cmdline = [
            "--int_test_nodef", "22"
        ]
        self.systest_runpars(cmdline, "SU_NP_1", GM_ex.GmapParameterError)

    def test_SU_NP_2(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_free", "this_file_doesnt_exist.really"
        ]
        self.systest_runpars(cmdline, "SU_NP_2", GM_ex.GmapFileNotFoundError)

        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py",
            "--path_test_free_new", "this/file/location/doesnt_exist.really"
        ]
        self.systest_runpars(cmdline, "SU_NP_2", GM_ex.GmapFileNotFoundError)

        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_rel21_new", "this/file/location/doesnt_exist.really"
        ]
        self.systest_runpars(cmdline, "SU_NP_2", GM_ex.GmapFileNotFoundError)

    def test_SU_NP_3(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_dir1", "this_directory_doesnt_exist"
        ]
        self.systest_runpars(cmdline, "SU_NP_3", GM_ex.GmapNotADirectoryError)

        # cmdline = [
        #     "--map_directory", "doesntexist\\;"
        # ]
        # self.systest_runpars(cmdline, "SU_NP_3", capsys)

    def test_SU_NP_7(self):
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py",
            "--estatic_smooth_range", "40"
        ]
        pardict = {"estatic_range": ["10"]}
        self.systest_runpars(
            cmdline, "SU_NP_7", GM_ex.GmapParameterError, pardict)

        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py",
            "--estatics_method", "perres_nocut"
        ]
        pardict = {"estatic_smooth_range": ["20"]}
        self.systest_runpars(
            cmdline, "SU_NP_7", GM_ex.GmapParameterError, pardict)

    def test_SU_NP_8(self):
        # invalid length (no couppairs given)
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # invalid couppair choice (group not chosen/available)
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None", "doesnexist:AmideBB"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # invalid amount of items in coupling choice 'pair' (not 1 colon)
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None", "AmideSC:AmideBB:CystBridge"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # first item in coupling choice pair is 'nothing'
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_to_use": [
                ["None", ":CystBridge"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # invalid length for coupling scaling
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_scale": [
                ["DipDip"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # invalid coupling scale choice (can't be float'ed)
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"],
            "couplings_scale": [
                ["DipDip", "one"],
            ]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapValueError, pardict)

        # --------------------------------------------------------------

        # singles_B/Wlist have fewer than 2 arguments
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py",
            "--singles_whitelist", ":All\\;"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapFileSyntaxError, pardict)

        # --------------------------------------------------------------

        # singles_B/Wlist has invalid map choice
        cmdline = [
            "--int_test_nodef", "22",
            "--path_test_nodef", "tests/test_tools/test_math_functions.py",
            "--singles_whitelist", ":notvalid", "choice\\;"
        ]
        pardict = {
            "maps_to_use": ["AmideSC", "AmideBB", "CystBridge"]
        }
        self.systest_runpars(
            cmdline, "SU_NP_8", GM_ex.GmapFileSyntaxError, pardict)

    @staticmethod
    def setup_for_runpars(pardict, inparspath, cmdline):
        # setup - Create all necessary objects.
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_1.ref"),
            True
        )
        def_pars = GM_pp.RawPars.from_file(
            Path("tests/test_tools/Data/default_parameters_1.txt"),
            ref_pars, True
        )

        in_pars = GM_pp.RawPars.from_dict(
            inparspath, pardict, ref_pars, False
        )

        mapdirs = GM_pp.find_mapdir(cmdline, in_pars, def_pars)
        mapdict = GM_mr.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        maprefdict = {name: _map.ref_pars for name, _map in mapdict.items()}

        cmd_pars = GM_pp.RawPars.from_cmdline(
            cmdline, ref_pars, maprefdict, False
        )

        return ref_pars, def_pars, in_pars, mapdict, cmd_pars

    @staticmethod
    def systest_runpars(cmdline, errcode, errclass, pardict=None):
        if pardict is None:
            pardict = {}
        curpath = Path("")
        (
            ref_pars, def_pars, in_pars, _, cmd_pars
        ) = TestRunPars.setup_for_runpars(pardict, curpath, cmdline)

        with pytest.raises(errclass, match=f"{errcode}$"):
            _ = GM_pp.RunPars(
                cmd_pars, in_pars, def_pars, ref_pars, True
            )


class TestMapPars:
    def test_maprefpars(self):
        # Assumes that RefPars and RawPars work correctly!!
        pardict = {
            "map_directory": ["Data/test_mapdir"]
        }
        cmdline = []

        curpath = Path(__file__).resolve()

        _, _, _, mapdict = TestMapPars.setup_maprefpars(
            pardict, cmdline)

        # counter = 1
        print([*mapdict.keys()])
        for mapname, map_ in mapdict.items():
            if mapname == "CystBridge":
                continue

            map_.find_refpars()
            counter = mapname[-1]
            fname_tofind = Path(curpath / "../Data/test_mapdir/Singles")
            fname_tofind /= f"testmap{counter}/parameters.ref"
            # counter += 1
            print(map_.ref_pars.fname)
            print(fname_tofind.resolve())
            assert map_.ref_pars.fname == fname_tofind.resolve()
            assert map_.ref_pars.options == {
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
                #     Path("../../../../test_parameter_parser.py"),
                #     Path("../../../../test_math_functions.py")
                # ],
                # "path_test_rel12_choice": [
                #     Path("test_parameter_parser.py"),
                #     Path("test_math_functions.py")
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
            assert map_.ref_pars.choices == {
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
                "path_test_free": [Path("../../../../test_math_functions.py")],
                "path_test_free_new": [Path("test_outfile.txt")],
                # "path_test_choice": [
                #     Path("../../../../test_parameter_parser.py")],
                "path_test_free_new_list": [
                    Path("test_outfile_0_1.txt"), Path("test_outfile_0_2.txt")
                ],
                "path_test_dir1": [Path("../../../../../test_tools")],
                "path_test_dir2": [Path("../../../../Data")],
                "path_test_rel11": [Path("test_math_functions.py")],
                # "path_test_rel12_choice": [Path("test_parameter_parser.py")],
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
            assert map_.ref_pars.shorthands == {
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
            assert map_.ref_pars.organized_filepars == {
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
            assert map_.ref_pars.organized_filepars_id == {
                "t1": "path_test_dir1",
                "t2": "path_test_dir2"
            }
            assert map_.ref_pars.allfilepars == [
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
            assert map_.ref_pars.filepars_create == [
                "path_test_free_new",
                "path_test_free_new_list",
                "path_test_rel21_new",
                "path_test_rel22_new_list",
                # "path_test_rel23_new_choice",
                # "path_test_rel24_new_choice_list"
            ]
            assert map_.ref_pars.intpars == [
                "int_test_free",
                "int_test_choice",
                "int_test_free_list",
                "int_test_choice_list",
                "int_test_choice_list2"
            ]
            assert map_.ref_pars.floatpars == [
                "float_test_free",
                "float_test_choice",
                "float_test_free_list",
                "float_test_choice_list",
                "float_test_choice_list2"
            ]
            assert map_.ref_pars.boolpars == [
                "bool_test1",
                "bool_test2",
                "bool_test3"
            ]
            assert map_.ref_pars.strpars == [
                "str_test_free",
                "str_test_choice",
                "str_test_free_list",
                "str_test_choice_list",
                "str_test_choice_list2"
            ]
            assert map_.ref_pars.not_expected_in_deffile == []
            assert map_.ref_pars.maybe_list == [
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

        _, _, in_pars, cmd_pars, mapdict = self.setup_maprawpars(
            pardict, cmdline)

        assert cmd_pars.not_found == {}
        assert in_pars.not_found == {}

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.in_pars.choices == {"int_test_free": [42]}
        assert testmap1.cmd_pars.choices == {"int_test_choice": [65]}
        assert testmap2.in_pars.choices == {"float_test_free": [88.8]}
        assert testmap2.cmd_pars.choices == {
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

        _, _, in_pars, cmd_pars, mapdict = self.setup_maprawpars(
            pardict, cmdline, Path(
                "tests/test_tools/Data/default_parameters_2_formap.txt"))

        assert cmd_pars.not_found == {}
        assert in_pars.not_found == {}

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.in_pars.choices == {"int_test_free": [42]}
        assert testmap1.cmd_pars.choices == {"int_test_choice": [65]}
        assert testmap2.in_pars.choices == {"float_test_free": [88.8]}
        assert testmap2.cmd_pars.choices == {
            "bool_test1": [False], "bool_test2": [False]}

    def test_SU_WP_6(self):
        pardict = {"map_directory": ["Data/test_mapdir"]}
        cmdline = []
        deffilepath = Path(
            "tests/test_tools/Data/default_parameters_2_formap_SU_WP_6.txt"
        )
        (
            ref_pars, def_pars, in_pars, mapdict
        ) = TestMapPars.setup_maprefpars(pardict, cmdline, deffilepath)

        for map_ in mapdict.values():
            map_.find_refpars()

        cmd_pars = GM_pp.RawPars.from_cmdline(
            cmdline, ref_pars,
            {name: map_.ref_pars for name, map_ in mapdict.items()},
            False
        )

        with pytest.raises(GM_ex.GmapKeyError, match="SU_WP_6$"):
            for map_ in mapdict.values():
                map_.find_rawpars(cmd_pars, in_pars, def_pars)

    def test_SU_WP_14(self):
        pardict = {"map_directory": ["Data/test_mapdir"]}
        cmdline = []
        deffilepath = Path(
            "tests/test_tools/Data/default_parameters_2_formap_SU_WP_14.txt"
        )
        (
            ref_pars, def_pars, in_pars, mapdict
        ) = TestMapPars.setup_maprefpars(pardict, cmdline, deffilepath)

        for map_ in mapdict.values():
            map_.find_refpars()

        cmd_pars = GM_pp.RawPars.from_cmdline(
            cmdline, ref_pars,
            {name: map_.ref_pars for name, map_ in mapdict.items()},
            False
        )

        with pytest.raises(GM_ex.GmapParameterError, match="SU_WP_14$"):
            for map_ in mapdict.values():
                map_.find_rawpars(cmd_pars, in_pars, def_pars)

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
            ref_pars, def_pars, in_pars, cmd_pars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        for map_ in mapdict.values():
            map_.find_runpars(run_pars)

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.run_pars.is_main is False
        assert testmap2.run_pars.is_main is False

        assert testmap1.run_pars.int_test_free == 42
        assert testmap1.run_pars.int_test_choice == 65

        assert testmap2.run_pars.float_test_free == 88.8
        assert testmap2.run_pars.bool_test1 is False
        assert testmap2.run_pars.bool_test2 is False

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
            ref_pars, def_pars, in_pars, cmd_pars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline, Path(
                "tests/test_tools/Data/default_parameters_2_formap.txt"))

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        for map_ in mapdict.values():
            map_.find_runpars(run_pars)

        testmap1 = mapdict["testmap1"]
        testmap2 = mapdict["testmap2"]

        assert testmap1.run_pars.is_main is False
        assert testmap2.run_pars.is_main is False

        assert testmap1.run_pars.int_test_free == 42
        assert testmap1.run_pars.int_test_choice == 65

        assert testmap2.run_pars.float_test_free == 88.8
        assert testmap2.run_pars.bool_test1 is False
        assert testmap2.run_pars.bool_test2 is False

    def test_SU_MR_1(self):
        # setup - Create all necessary objects.
        ref_pars = GM_pp.RefPars(
            Path(
                "tests/test_tools/Data/reference_parameters_2.ref"),
            True
        )
        def_pars = ref_pars

        pardict = {
            "map_directory": ["Data/test_mapdir"],
            "testmap1.int_test_free": ["42"],
            "testmap2.float_test_free": ["88.8"]
        }

        curpath = Path(__file__).resolve()
        in_pars = GM_pp.RawPars.from_dict(
            curpath, pardict, ref_pars, False
        )

        cmdline = [
            "-testmap1.ti2", "65",
            "--testmap2.nobool_test1",
            "-testmap2.notb2"
        ]

        mapdirs = GM_pp.find_mapdir(cmdline, in_pars, def_pars)
        mapdict = GM_mr.scan_mapdirs(mapdirs, "Singles")
        for map_ in mapdict.values():
            map_.find_refpars()

        cmd_pars = GM_pp.RawPars.from_cmdline(
            cmdline, ref_pars,
            {name: _map.ref_pars for name, _map in mapdict.items()},
            False
        )
        cmd_pars.not_found["testmap1.booltest.1"] = ["True"]

        with pytest.raises(GM_ex.GmapValueError, match="SU_MR_1$"):
            for map_ in mapdict.values():
                map_.find_rawpars(cmd_pars, in_pars, def_pars)

    def test_SU_NP_2(self):
        pardict = {}
        cmdline = [
            "-md", "tests/test_tools/Data/test_mapdir\\;",
            "--testmap1.path_test_free", "this_file_doesnt_exist.really"
        ]

        (
            ref_pars, def_pars, in_pars, cmd_pars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        with pytest.raises(GM_ex.GmapFileNotFoundError, match="SU_NP_2$"):
            for map_ in mapdict.values():
                map_.find_runpars(run_pars)

    def test_SU_NP_3(self):
        pardict = {}
        cmdline = [
            "-md", "tests/test_tools/Data/test_mapdir\\;",
            "--testmap1.path_test_dir1", "this_directory_doesnt_exist"
        ]

        (
            ref_pars, def_pars, in_pars, cmd_pars, mapdict
        ) = self.setup_maprawpars(
            pardict, cmdline)

        run_pars = GM_pp.RunPars(
            cmd_pars, in_pars, def_pars, ref_pars, True
        )

        with pytest.raises(GM_ex.GmapNotADirectoryError, match="SU_NP_3$"):
            for map_ in mapdict.values():
                map_.find_runpars(run_pars)

    @staticmethod
    def setup_maprefpars(pardict, cmdline, defparfilename=None):
        # setup - Create all necessary objects.
        # ref_pars = GM_PP.RefPars(
        #     Path(
        #         "tests/test_tools/Data/reference_parameters_2.ref"),
        #     True
        # )
        ref_pars = GM_pp.RefPars(
            Path(
                "sourcefiles/reference_parameters.ref"
            ), True
        )
        if defparfilename:
            def_pars = GM_pp.RawPars.from_file(
                defparfilename, ref_pars, True)
        else:
            def_pars = ref_pars

        curpath = Path(__file__).resolve()
        in_pars = GM_pp.RawPars.from_dict(
            curpath, pardict, ref_pars, False
        )

        mapdirs = GM_pp.find_mapdir(cmdline, in_pars, def_pars)
        mapdict = GM_mr.scan_mapdirs(mapdirs, "Singles")

        return ref_pars, def_pars, in_pars, mapdict

    @staticmethod
    def setup_maprawpars(pardict, cmdline, defparfilename=None):
        (
            ref_pars, def_pars, in_pars, mapdict
        ) = TestMapPars.setup_maprefpars(pardict, cmdline, defparfilename)

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

        return ref_pars, def_pars, in_pars, cmd_pars, mapdict


def test_get_parameters():
    in_parfile = Path("tests/test_tools/Data/input_parameters_1.txt").resolve()
    argslist = []

    (
        run_pars, mapdict, pairs_mapdict, cmd_pars, in_pars, def_pars, ref_pars
    ) = GM_pp.get_parameters(
        in_parfile, argslist
    )

    # A huuuuge amount of tests would be needed here, but all of GM_PP
    # has already been tested separately.
    assert in_pars.fname.name == "input_parameters_1.txt"
    assert def_pars == ref_pars
    assert len(mapdict) == 8
    assert cmd_pars.choices == {}

    (
        run_pars, mapdict, pairs_mapdict, cmd_pars, in_pars, def_pars, ref_pars
    ) = GM_pp.get_parameters(
        None, argslist
    )

    assert in_pars.choices == {}

    argslist = ["-dpf", "tests/test_tools/Data/default_parameters.txt"]

    (
        run_pars, mapdict, pairs_mapdict, cmd_pars, in_pars, def_pars, ref_pars
    ) = GM_pp.get_parameters(
        in_parfile, argslist
    )

    assert def_pars.fname.name == "default_parameters.txt"


def test_parse_commandline():
    callcommand = [
        "GEM", "run",
        "tests/test_tools/Data/input_parameters_1.txt", "-verbose", "3"
    ]

    job, in_parfile, cmd_pars = GM_pp.parse_commandline(
        callcommand, alljobs, "GMAP",
        expect_inputfile=True, expect_parameters=True
    )
    assert job == "run"
    assert in_parfile == Path(
        "tests/test_tools/Data/input_parameters_1.txt").resolve()
    assert cmd_pars == ["-verbose", "3"]

    callcommand = [
        "GEM", "run", "-verbose", "3"
    ]
    job, in_parfile, cmd_pars = GM_pp.parse_commandline(
        callcommand, alljobs, "GMAP",
        expect_inputfile=False, expect_parameters=True
    )
    assert job == "run"
    assert in_parfile is None
    assert cmd_pars == ["-verbose", "3"]

    callcommand = [
        "GEM", "run", "-verbose", "3"
    ]
    job, in_parfile, cmd_pars = GM_pp.parse_commandline(
        callcommand, alljobs, "GMAP",
        expect_inputfile=False, expect_parameters=False
    )
    assert job == "run"
    assert in_parfile is None
    assert cmd_pars == []

    callcommand = [
        "GEM", "run", "tests/test_tools/Data/input_parameters_1.txt",
        "-verbose", "3"
    ]

    job, in_parfile, cmd_pars = GM_pp.parse_commandline(
        callcommand, alljobs, "GMAP",
        expect_inputfile=True, expect_parameters=False
    )
    assert job == "run"
    assert in_parfile == Path(
        "tests/test_tools/Data/input_parameters_1.txt").resolve()
    assert cmd_pars == []


def test_find_defparfile():
    argslist = [
        "-sd", "sourcefiles",
        "-dpf", "reference_parameters.ref"
    ]

    pardict = GM_pp.find_defparfile_in_cmd(argslist)

    assert pardict == {
        "source_directory": ["sourcefiles"],
        "default_parameter_filename": ["reference_parameters.ref"]
    }


def test_parse_influencerfile():
    file = Path("sourcefiles/infl_file_base.txt")
    groupdict = {
        "All": set("ABC")
    }
    groupdict = GM_pp.parse_influencerfile(file, groupdict)
    assert groupdict == {
        "All": set("ABC"),
        "choice": set("ABC")
    }

    otherfile = Path("tests/test_tools/Data/infl_file.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    groupdict = GM_pp.parse_influencerfile(otherfile, groupdict)
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

    physfile = Path("tests/test_tools/Data/test_inflfile.txt")
    groupdict = {
        "All": set([
            "SOL", "TIP3", "WAT", "K", "K+", "NA", "NA+", "Na+", "CL", "CLA",
            "Cl-", "DMPC", "POP", "LYSH", "HSD", "HIE"])
    }
    groupdict = GM_pp.parse_influencerfile(physfile, groupdict)
    assert groupdict == {
        "All": set([
            "SOL", "TIP3", "WAT", "K", "K+", "NA", "NA+", "Na+", "CL", "CLA",
            "Cl-", "DMPC", "POP", "LYSH", "HSD", "HIE"]),
        "Water": set(["SOL", "TIP3", "WAT"]),
        "K": set(["K", "K+"]),
        "Na": set(["NA", "NA+", "Na+"]),
        "Cl": set(["CL", "CLA", "Cl-"]),
        "Ions": set(["K", "K+", "NA", "NA+", "Na+", "CL", "CLA", "Cl-"]),
        "Solvent": set([
            "SOL", "TIP3", "WAT", "K", "K+", "NA", "NA+", "Na+", "CL", "CLA",
            "Cl-"]),
        "Lipid": set(["DMPC", "POP"]),
        "Protein_ext": set(["LYSH", "HSD", "HIE"]),
        "choice": set([
            "SOL", "TIP3", "WAT", "K", "K+", "NA", "NA+", "Na+", "CL", "CLA",
            "Cl-"])
    }


def test_parse_influencer_par():
    assert GM_pp.parse_influencer_par("A B C") == "A | B | C"
    assert GM_pp.parse_influencer_par("A & B C") == "A & B C"


def test_SU_FP_1():
    in_parfile = Path("tests/test_tools/Data/input_parameters_1.txt").resolve()

    # this map no longer exists
    # argslist = ["-dpf", "maps/Singles/testmap1/parameters.ref"]
    argslist = ["-dpf", "tests/test_tools/Data/reference_parameters_2.ref"]

    with pytest.raises(GM_ex.GmapNotImplementedError, match="SU_FP_1$"):
        _ = GM_pp.get_parameters(
            in_parfile, argslist
        )


def test_SU_GEM_1():
    in_parfile = Path("tests/test_tools/Data/input_parameters_1.txt").resolve()
    argslist = ["-dpf", "__init__.py"]

    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_GEM_1$"):
        _ = GM_pp.get_parameters(
            in_parfile, argslist
        )


def test_SU_PP_1():
    callcommand = [
        "GEM", "not_available_job_choice", "../test_inpar.txt", "-verbose", "3"
    ]

    with pytest.raises(GM_ex.GmapKeyError, match="SU_PP_1$"):
        _ = GM_pp.parse_commandline(
            callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )


def test_SU_PP_2():
    callcommand = [
        "GEM", "run"
    ]

    with pytest.raises(GM_ex.GmapParameterError, match="SU_PP_2$"):
        _ = GM_pp.parse_commandline(
            callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )


def test_SU_PP_3():
    callcommand = [
        "GEM", "run", "../doesnt_exist.really", "-verbose", "3"
    ]

    with pytest.raises(GM_ex.GmapFileNotFoundError, match="SU_PP_3$"):
        _ = GM_pp.parse_commandline(
            callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )

    callcommand = [
        "GEM", "run", "-verbose", "3"
    ]
    with pytest.raises(GM_ex.GmapFileNotFoundError, match="SU_PP_3$"):
        _ = GM_pp.parse_commandline(
            callcommand, alljobs, "GMAP",
            expect_inputfile=True, expect_parameters=True
        )

    # -------

    ref_pars = GM_pp.RefPars(
        Path(
            "tests/test_tools/Data/reference_parameters_2.ref"),
        True
    )
    def_pars = ref_pars

    curpath = Path(__file__).resolve()
    in_pars = GM_pp.RawPars.from_dict(
        curpath, {}, ref_pars, False
    )

    cmdline = ["-md", "this/dir/doesnt_exist\\;"]

    with pytest.raises(GM_ex.GmapNotADirectoryError, match="SU_PP_3$"):
        _ = GM_pp.find_mapdir(
            cmdline, in_pars, def_pars)


def test_SU_PP_4():
    argslist = [
        "-sd", "sourcefiles",
        "--source_directory", "sourcefiles",
        "-dpf", "reference_parameters.ref"
    ]

    with pytest.raises(GM_ex.GmapParameterError, match="SU_PP_4$"):
        _ = GM_pp.find_defparfile_in_cmd(argslist)


def test_SU_WP_4():
    argslist = [
        "-sd",
        "-dpf", "reference_parameters.ref"
    ]
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_WP_4$"):
        _ = GM_pp.find_defparfile_in_cmd(argslist)

    argslist = [
        "-sd", "sourcefiles",
        "-dpf"
    ]
    with pytest.raises(GM_ex.GmapIndexError, match="SU_WP_4$"):
        _ = GM_pp.find_defparfile_in_cmd(argslist)


def test_SU_WP_5():
    argslist = [
        "-md", "someloc"
    ]
    with pytest.raises(GM_ex.GmapIndexError, match="SU_WP_5$"):
        _ = GM_pp.find_par_in_cmd(
            argslist, ("-md",), "map_directory", True)

    argslist = [
        "-md", "someloc", "-otherpar"
    ]
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_WP_5$"):
        _ = GM_pp.find_par_in_cmd(
            argslist, ("-md",), "map_directory", True)


def test_SU_NP_4():
    file = Path("tests/test_tools/Data/infl_file_SU_NP_4.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_4$"):
        groupdict = GM_pp.parse_influencerfile(file, groupdict)


def test_SU_NP_5():
    file = Path("tests/test_tools/Data/infl_file_SU_NP_5_1.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_5$"):
        groupdict = GM_pp.parse_influencerfile(file, groupdict)

    file = Path("tests/test_tools/Data/infl_file_SU_NP_5_2.txt")
    groupdict = {
        "All": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    }
    with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_5$"):
        groupdict = GM_pp.parse_influencerfile(file, groupdict)
