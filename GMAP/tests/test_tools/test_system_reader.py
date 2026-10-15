"""
tests missing:

(@ July 22nd '24):
167, 178-183, 264, 491, 613, 1362, 1406  (10 missed statements)

- non-rightangled system    (167, 1406)
- MDA system without bond information (both testing it with, and without
  needing this information)   (178-183)
- MDA system which does not contain ascending atom indices starting elsewhere
  than 0 (Do these exist?)   (264)
- The universe doesn't contain any requested oscillators (491)
- An oscillator (and MD file to support it) that has the same atom name
  multiple times in a single residue   (613)
- MDA.Universe FileNotFoundError (can we even trigger this one?)   (1362)

"""


# 3rd party imports
import MDAnalysis as MDA
import numpy as np
import pytest

# local imports
from .test_map_reader import basic_setup
import GMAP.src.tools.clib_loader as GM_cl
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.map_reader as GM_mr
import GMAP.src.tools.system_reader as GM_sr

# curpath = Path(__file__).resolve()
# test_tools_dir = curpath.parent


class TestSystem:
    def test_set_properties(self):
        mapname = "test_code_build_1"
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname)

        system = GM_sr.System.__new__(GM_sr.System)
        setattr(system, "universe", GM_sr.gen_universe(run_pars))
        system.set_properties()

        all_properties = (
            system.atnums, system.atnames, system.resnums, system.resnames,
            system.positions, system.masses, system.charges, system.types,
            system.segids
        )

        assert all(item.shape[0] == 33876 for item in all_properties)
        assert system.natoms == 33876
        assert system.nres == 10773

        assert np.all(system.boxdims == np.array(
            [69.5689, 69.5689, 69.5689], dtype=np.float32))
        assert np.all(system.angles == np.array(
            [90, 90, 90], dtype=np.float32))

        assert np.all(system.atnums == np.arange(system.natoms))
        # assert that residue numbers only increase (so they're unique)
        assert np.all(np.diff(system.resnums) >= 0)

        # first [0] to select 0th axis, second to select first occurence
        first_sol_at = np.where(system.resnames == "SOL")[0][0]
        first_sol_res = system.resnums[first_sol_at]

        for amino_acid in (
            "ARG", "HIS", "LYS", "ASP", "GLU", "SER", "THR", "ASN", "GLN",
            "CYS", "GLY", "PRO", "ALA", "VAL", "ILE", "LEU", "MET", "PHE",
            "TYR", "TRP"
        ):
            # for each amino acid (of the current 'type'), get the array of
            # names of all its constituent atoms.
            names_perres = [
                system.atnames[
                    system.residues.first_ix[resix]:
                    system.residues.last_ix[resix] + 1
                ] for resix in range(1, first_sol_res-1)
                if system.residues.resnames[resix] == amino_acid
            ]
            if names_perres:
                assert all(
                    np.all(arr == names_perres[0]) for arr in names_perres
                )
                atnames = names_perres[0]
                assert atnames[0] == "N"
                if amino_acid == "PRO":
                    assert atnames[1] == "CA"
                else:
                    assert atnames[1] == "H"
                    assert atnames[2] == "CA"
                assert atnames[-2] == "C"
                assert atnames[-1] == "O"

    def test_find_influencers(self):

        # ----- influencer choice given in cmdline directly ------------
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_whitelist", ":protein_cannonical", "CL\\;"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System.__new__(GM_sr.System)
        setattr(system, "universe", GM_sr.gen_universe(run_pars))
        system.set_properties()
        system.basic_boxchecks(run_pars)
        system.find_influencers(run_pars)

        print(system.influencers_atix[-20:])
        target = np.array([*range(1960)] + [*range(33868, 33876)])
        assert np.all(system.influencers_atix == target)

        # ----- influencer choice specified for MDA.select_atoms -------

        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_select_atoms", "protein", "or", "resname", "CL\\;"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System.__new__(GM_sr.System)
        setattr(system, "universe", GM_sr.gen_universe(run_pars))
        system.set_properties()
        system.basic_boxchecks(run_pars)
        system.find_influencers(run_pars)

        print(system.influencers_atix[-20:])
        target = np.array([*range(1960)] + [*range(33868, 33876)])
        assert np.all(system.influencers_atix == target)

        # ----- influencer choice specified in inflfile ----------------

        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_file", "tests/test_tools/Data/test_inflfile.txt",
            "--verbose", "4"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System.__new__(GM_sr.System)
        setattr(system, "universe", GM_sr.gen_universe(run_pars))
        system.set_properties()
        system.basic_boxchecks(run_pars)
        system.find_influencers(run_pars)

        print(system.influencers_atix[-20:])
        target = np.array([*range(1960, 33876)])
        assert np.all(system.influencers_atix == target)

        # ----- influencer choice specified in inflfile ----------------
        # but all in file are used!

        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_file", "tests/test_tools/Data/test_inflfile2.txt",
            "--verbose", "4"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System.__new__(GM_sr.System)
        setattr(system, "universe", GM_sr.gen_universe(run_pars))
        system.set_properties()
        system.basic_boxchecks(run_pars)
        system.find_influencers(run_pars)

        print(system.influencers_atix[-20:])
        target = np.array([*range(0, 33876)])
        assert np.all(system.influencers_atix == target)

    def test_find_oscillators(self):

        # just AmideSC
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_whitelist", ":protein_cannonical", "CL\\;"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System(run_pars)

        assert len(system.oscillators) == 17

        # Both AmideBB and AmideSC

        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "-um", "AmideSC", "AmideBB\\;",
            "--influencers_whitelist", ":protein_cannonical", "CL\\;"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System(run_pars)

        assert len(system.oscillators) == 145

    def test_find_osc_singlebonded(self):
        # just AmideSC
        mapname = "AmideSC"
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname)

        system = GM_sr.System(run_pars)

        assert len(system.oscillators) == 17

    def test_multiple_res_osc(self):
        # This is a map of a triple ALA subchain - only 1 present in 1AKI
        mapname = "test_multiple_res_osc"
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, ["--dont_report_error", "MI__\\;"])

        system = GM_sr.System(run_pars)
        system.update_properties(run_pars)

        assert len(system.oscillators) == 1

        onlyosc = system.oscillators[0]
        onlyosc.frame_update(system)
        # triple ALA lies on resnums 8-10, atnums 135-164, select 2nd AmideBB
        assert onlyosc.used_atoms == [153, 154, 147, 155, 156, 157]

        # position C = (46.96, 28.12, 37.08)
        # position N = (46.26, 28.74, 36.11)
        # average    = (46.61, 28.43, 36.595)

        # box dims   = (69.5689, 69.5689, 69.5689)
        # average in (-0.5, 0.5) boxdims:  (-22.9589, 28.4300, -32.9739)
        tocheck = np.round(onlyosc.get_VEG_ref(system), 4)
        answer = np.round(
            np.array([-22.9589, 28.43, -32.9739], dtype="float32"), 4)

        assert np.all(tocheck == answer)

    def test_SU_NP_5(self):
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_file",
            "tests/test_tools/Data/infl_file_SU_NP_5_3.txt",
            "--verbose", "4"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System.__new__(GM_sr.System)
        setattr(system, "universe", GM_sr.gen_universe(run_pars))
        system.set_properties()
        system.basic_boxchecks(run_pars)

        with pytest.raises(GM_ex.GmapFileSyntaxError, match="SU_NP_5$"):
            system.find_influencers(run_pars)

    def test_SU_NP_6(self):
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_select_atoms", "or", "resname", "CL\\;"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System.__new__(GM_sr.System)
        setattr(system, "universe", GM_sr.gen_universe(run_pars))
        system.set_properties()
        system.basic_boxchecks(run_pars)

        with pytest.raises(GM_ex.GMAPexception, match="SU_NP_6$"):
            system.find_influencers(run_pars)

    def test_MD_SU_6(self):
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps",
            "tests/test_tools/Data/maps_for_test_pair-single_dependence\\;",
            "--couplings_to_use", "AneedsB", ":All\\;"
        ]
        (
            run_pars, ref_pars, def_pars, in_parss,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)
        system = GM_sr.System(run_pars)

        with pytest.raises(GM_ex.GmapParameterError, match="MD_SU_6$"):
            system.order_oscillators_pairs(run_pars)


class TestOscillator:
    def test_str_osc(self):
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_whitelist", ":protein_cannonical", "CL\\;"
        ]
        (
            run_pars, ref_pars, def_pars, in_pars,
            cmd_pars, mapdict, pairs_mapdict
        ) = parameter_getter(mapname, cmdline)

        system = GM_sr.System(run_pars)
        oscstr = str(system.oscillators[0])
        exp = "Oscillator of type AmideSC living on the residue ASN18"
        assert oscstr == exp

    def test_rotate_VEG(self):
        oscillator = GM_sr.Oscillator.__new__(GM_sr.Oscillator)
        oscillator.VEGout = np.arange(40).reshape((4, 10))
        oscillator.rotation_matrix = np.array([
            [0, 1, 0], [0, 0, 1], [1, 0, 0]])

        oscillator.rotate_VEG()

        ans = np.array([
            [0, 2, 3, 1, 5, 6, 4, 9, 7, 8],
            [10, 12, 13, 11, 15, 16, 14, 19, 17, 18],
            [20, 22, 23, 21, 25, 26, 24, 29, 27, 28],
            [30, 32, 33, 31, 35, 36, 34, 39, 37, 38]
        ])
        assert np.all(oscillator.VEGout.round(4) == ans.round(4))


def test_gen_universe():
    mapname = "test_code_build_1"
    inpardict = {
        "topology_file": ["../../sourcefiles/pdb_1AKI.tpr"],
        "trajectory_file": ["../../sourcefiles/pdb_1AKI_50frame.xtc"]
    }
    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    universe = GM_sr.gen_universe(run_pars)
    assert isinstance(universe, MDA.Universe)
    assert len(universe.atoms) == 33876


# Also requires a test for a file with a non-orthorhombic box (don't
# currently have one)
def test_check_box_rightangled():
    universe = MDA.Universe(
        "sourcefiles/pdb_1AKI.tpr",
        "sourcefiles/pdb_1AKI_50frame.xtc"
    )
    assert GM_sr.check_box_rightangled(universe)


def test_check_box_charge():
    mapname = "test_code_build_1"
    inpardict = {"neutral_charge_threshold": ["0.001"]}

    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    charges = np.array([
        0.2, 0.4, -0.3, -0.3
    ])

    assert GM_sr.check_box_charge(run_pars, charges)


# there are 3 of these in gen_universe.
# the 1st one (FileNotFoundError) is already protected by SU_NP_2
def test_MD_SU_1():

    # ----- ValueError -------------------------------------------------

    cmdline = ["--verbose", "4"]
    mapname = "test_code_build_1"
    inpardict = {
        "topology_file": ["../../sourcefiles/infl_file_base.txt"],
        "trajectory_file": ["../../sourcefiles/pdb_1AKI.tpr"]
    }

    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter(mapname, cmdline, inpardict)

    with pytest.raises(GM_ex.GmapValueError, match="MD_SU_1$"):
        _ = GM_sr.gen_universe(run_pars)

    # ----- Other (AttributeError?) ------------------------------------

    mapname = "test_code_build_1"
    inpardict = {
        "topology_file": ["../../sourcefiles/pdb_1AKI_50frame.xtc"],
        "trajectory_file": ["../../sourcefiles/pdb_1AKI.tpr"]
    }

    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    with pytest.raises(GM_ex.GmapMDFileError, match="MD_SU_1$"):
        _ = GM_sr.gen_universe(run_pars)


def test_MD_SU_3(capsys):

    mapname = "test_code_build_1"
    inpardict = {"neutral_charge_threshold": ["0.001"]}

    (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    # First, the total charge is larger than threshold

    # total is 0.1, which is larger than the threshold of 0.001
    charges = np.array([
        0.2, 0.4, -0.3, -0.3, 0.1
    ])

    with pytest.raises(GM_ex.GmapParameterError, match="MD_SU_3$"):
        _ = GM_sr.check_box_charge(run_pars, charges)

    # Then, total charge is larger than threshold, but only because
    # there is a whole number involved. The decimal part still complies.

    # total is 1.0, which' decimal part is still below the threshold.
    charges = np.array([
        0.2, 0.4, 0.3, 0.1
    ])

    assert not GM_sr.check_box_charge(run_pars, charges)

    captured = capsys.readouterr()
    assert captured.out.endswith("MD_SU_3\n")


def parameter_getter(mapname, cmdline=None, inpardict=None, load_clib=True):

    # prepare inputs
    cmdadd = [
        "-md", "tests/test_tools/Data/maps_for_test_map_reader_1\\;",
        "--couplings_to_use", "None", ":All\\;"
    ]
    if cmdline is None:
        cmdline = cmdadd
    elif "-md" not in cmdline and "--map_directory" not in cmdline:
        cmdline.extend(cmdadd)

    if inpardict is None:
        inpardict = {"maps_to_use": [mapname]}
    elif "maps_to_use" not in inpardict:
        inpardict["maps_to_use"] = [mapname]

    # generate parameter structures
    (
        run_pars, ref_pars, def_pars, in_pars, cmd_pars,
        mapdict, pairs_mapdict
    ) = basic_setup(
        cmdline, inpardict, mapname=mapname, finish_before="extract_code")

    # # process maps
    # for map_ in mapdict.values():
    #     map_.initialize()
    # # Ditch all maps that contain problems/flaws/issues
    # mapdict = {map_.name: map_ for map_ in mapdict.values() if map_.success}
    # for map_choice in run_pars.maps_to_use:
    #     if map_choice not in mapdict:
    #         assert False  # In main code, this is MI_MM_1
    # requested_mapdict = {
    #     map_.name: map_ for map_ in mapdict.values()
    #     if map_.name in run_pars.maps_to_use
    # }
    # run_pars.requested_mapdict = requested_mapdict
    # if any(map_.core.requires_bonds for map_ in requested_mapdict.values()):
    #     run_pars.detected_requires_bonds = True
    # else:
    #     run_pars.detected_requires_bonds = False

    GM_mr.manage_maps_singles(run_pars, mapdict)
    GM_mr.manage_maps_pairs(run_pars, pairs_mapdict)

    if load_clib:
        _ = GM_cl.VEG_CLib(run_pars)

    return (
        run_pars, ref_pars, def_pars, in_pars,
        cmd_pars, mapdict, pairs_mapdict
    )
