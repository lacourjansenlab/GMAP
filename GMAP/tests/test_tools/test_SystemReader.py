"""
tests missing:

(@ apr 26th '24):
148, 159-164, 250, 581, 1050, 1093  (9 missed statements)

- non-rightangled system    (148, 1093)
- MDA system without bond information (both testing it with, and without
  needing this information)   (159-164)
- MDA system which does not contain ascending atom indices starting elsewhere
  than 0 (Do these exist?)   (250)
- An oscillator (and MD file to support it) that has the same atom name
  multiple times in a single residue   (581)
- MDA.Universe FileNotFoundError (can we even trigger this one?)   (1050)

"""


# 3rd party imports
import MDAnalysis as MDA
import numpy as np
import pytest

# local imports
from .test_MapReader import basic_setup
import GMAP.src.tools.SystemReader as GM_SR

# curpath = Path(__file__).resolve()
# test_tools_dir = curpath.parent


class TestSystem:
    def test_set_properties(self):
        mapname = "test_code_build_1"
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname)

        System = GM_SR.System.__new__(GM_SR.System)
        setattr(System, "universe", GM_SR.gen_universe(Printer, RunPars))
        System.set_properties(Printer)

        all_properties = (
            System.atnums, System.atnames, System.resnums, System.resnames,
            System.positions, System.masses, System.charges, System.types,
            System.segids, System.molnums
        )

        assert all(item.shape[0] == 33876 for item in all_properties)
        assert System.natoms == 33876
        assert System.nres == 10773

        assert np.all(System.boxdims == np.array(
            [69.5689, 69.5689, 69.5689], dtype=np.float32))
        assert np.all(System.angles == np.array(
            [90, 90, 90], dtype=np.float32))

        assert np.all(System.atnums == np.arange(System.natoms))
        # assert that residue numbers only increase (so they're unique)
        assert np.all(np.diff(System.resnums) >= 0)
        assert np.all(np.diff(System.molnums) >= 0)

        # first [0] to select 0th axis, second to select first occurence
        first_sol_at = np.where(System.resnames == "SOL")[0][0]
        first_sol_res = System.resnums[first_sol_at]

        for amino_acid in (
            "ARG", "HIS", "LYS", "ASP", "GLU", "SER", "THR", "ASN", "GLN",
            "CYS", "GLY", "PRO", "ALA", "VAL", "ILE", "LEU", "MET", "PHE",
            "TYR", "TRP"
        ):
            # for each amino acid (of the current 'type'), get the array of
            # names of all its constituent atoms.
            names_perres = [
                System.atnames[
                    System.residues.first_ix[resix]:
                    System.residues.last_ix[resix] + 1
                ] for resix in range(1, first_sol_res-1)
                if System.residues.resnames[resix] == amino_acid
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
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname, cmdline)

        System = GM_SR.System.__new__(GM_SR.System)
        setattr(System, "universe", GM_SR.gen_universe(Printer, RunPars))
        System.set_properties(Printer)
        System.basic_boxchecks(Printer, RunPars)
        System.find_influencers(Printer, RunPars)

        print(System.influencers_atix[-20:])
        target = np.array([*range(1960)] + [*range(33868, 33876)])
        assert np.all(System.influencers_atix == target)

        # ----- influencer choice specified for MDA.select_atoms -------

        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_select_atoms", "protein", "or", "resname", "CL\\;"
        ]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname, cmdline)

        System = GM_SR.System.__new__(GM_SR.System)
        setattr(System, "universe", GM_SR.gen_universe(Printer, RunPars))
        System.set_properties(Printer)
        System.basic_boxchecks(Printer, RunPars)
        System.find_influencers(Printer, RunPars)

        print(System.influencers_atix[-20:])
        target = np.array([*range(1960)] + [*range(33868, 33876)])
        assert np.all(System.influencers_atix == target)

        # ----- influencer choice specified in inflfile ----------------

        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_file", "../test_inflfile.txt",
            "--verbose", "4"
        ]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname, cmdline)

        System = GM_SR.System.__new__(GM_SR.System)
        setattr(System, "universe", GM_SR.gen_universe(Printer, RunPars))
        System.set_properties(Printer)
        System.basic_boxchecks(Printer, RunPars)
        System.find_influencers(Printer, RunPars)

        print(System.influencers_atix[-20:])
        target = np.array([*range(1960, 33876)])
        assert np.all(System.influencers_atix == target)

    def test_find_oscillators(self):

        # just AmideSC
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_whitelist", ":protein_cannonical", "CL\\;"
        ]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname, cmdline)

        System = GM_SR.System(Files, Printer, RunPars)

        assert len(System.oscillators) == 17

        # Both AmideBB and AmideSC

        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "-um", "AmideSC", "AmideBB\\;",
            "--influencers_whitelist", ":protein_cannonical", "CL\\;"
        ]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname, cmdline)

        System = GM_SR.System(Files, Printer, RunPars)

        assert len(System.oscillators) == 145

    def test_find_osc_singlebonded(self):
        # just AmideSC
        mapname = "AmideSC"
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname)

        System = GM_SR.System(Files, Printer, RunPars)

        assert len(System.oscillators) == 17

    def test_multiple_res_osc(self):
        # This is a map of a triple ALA subchain - only 1 present in 1AKI
        mapname = "test_multiple_res_osc"
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname)

        System = GM_SR.System(Files, Printer, RunPars)
        System.update_properties(Printer)

        assert len(System.oscillators) == 1

        onlyosc = System.oscillators[0]
        onlyosc.frame_update(Printer, System)
        # triple ALA lies on resnums 8-10, atnums 135-164, select 2nd AmideBB
        assert onlyosc.used_atoms == [153, 154, 147, 155, 156, 157]

        # position C = (46.96, 28.12, 37.08)
        # position N = (46.26, 28.74, 36.11)
        # average    = (46.61, 28.43, 36.595)

        # box dims   = (69.5689, 69.5689, 69.5689)
        # average in (-0.5, 0.5) boxdims:  (-22.9589, 28.4300, -32.9739)
        tocheck = np.round(onlyosc.get_VEG_ref(Printer, System), 4)
        answer = np.round(
            np.array([-22.9589, 28.43, -32.9739], dtype="float32"), 4)

        assert np.all(tocheck == answer)

    def test_SU_NP_5(self, capsys):
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_file",
            "tests/test_tools/Data/infl_file_SU_NP_5_3.txt",
            "--verbose", "4"
        ]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname, cmdline)

        System = GM_SR.System.__new__(GM_SR.System)
        setattr(System, "universe", GM_SR.gen_universe(Printer, RunPars))
        System.set_properties(Printer)
        System.basic_boxchecks(Printer, RunPars)

        with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
            System.find_influencers(Printer, RunPars)

        assert pytest_wrapped_sysexit.type is SystemExit
        captured = capsys.readouterr()
        assert captured.out.endswith("SU_NP_5\n")

    def test_SU_NP_6(self, capsys):
        mapname = "AmideSC"
        cmdline = [
            "-md", "maps\\;",
            "--influencers_select_atoms", "or", "resname", "CL\\;"
        ]
        (
            Files, Printer, RunPars, RefPars, DefPars, InPars,
            CmdPars, mapdict
        ) = parameter_getter(mapname, cmdline)

        System = GM_SR.System.__new__(GM_SR.System)
        setattr(System, "universe", GM_SR.gen_universe(Printer, RunPars))
        System.set_properties(Printer)
        System.basic_boxchecks(Printer, RunPars)

        with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
            System.find_influencers(Printer, RunPars)

        assert pytest_wrapped_sysexit.type is SystemExit
        captured = capsys.readouterr()
        assert captured.out.endswith("SU_NP_6\n")


def test_gen_universe():
    mapname = "test_code_build_1"
    inpardict = {
        "topology_file": ["../../sourcefiles/pdb_1AKI.tpr"],
        "trajectory_file": ["../../sourcefiles/pdb_1AKI_50frame.xtc"]
    }
    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    universe = GM_SR.gen_universe(Printer, RunPars)
    assert isinstance(universe, MDA.Universe)
    assert len(universe.atoms) == 33876


# Also requires a test for a file with a non-orthorhombic box (don't
# currently have one)
def test_check_box_rightangled():
    universe = MDA.Universe(
        "sourcefiles/pdb_1AKI.tpr",
        "sourcefiles/pdb_1AKI_50frame.xtc"
    )
    assert GM_SR.check_box_rightangled(universe)


def test_check_box_charge():
    mapname = "test_code_build_1"
    inpardict = {"neutral_charge_threshold": ["0.001"]}

    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    charges = np.array([
        0.2, 0.4, -0.3, -0.3
    ])

    assert GM_SR.check_box_charge(Printer, RunPars, charges)


# there are 3 of these in gen_universe.
# the 1st one (FileNotFoundError) is already protected by SU_NP_2
def test_MD_SU_1(capsys):

    # ----- ValueError -------------------------------------------------

    cmdline = ["--verbose", "4"]
    mapname = "test_code_build_1"
    inpardict = {
        "topology_file": ["../../sourcefiles/infl_file_base.txt"],
        "trajectory_file": ["../../sourcefiles/pdb_1AKI.tpr"]
    }

    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter(mapname, cmdline, inpardict)

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        _ = GM_SR.gen_universe(Printer, RunPars)

    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("MD_SU_1\n")

    # ----- Other (AttributeError?) ------------------------------------

    mapname = "test_code_build_1"
    inpardict = {
        "topology_file": ["../../sourcefiles/pdb_1AKI_50frame.xtc"],
        "trajectory_file": ["../../sourcefiles/pdb_1AKI.tpr"]
    }

    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        _ = GM_SR.gen_universe(Printer, RunPars)

    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("MD_SU_1\n")


def test_MD_SU_3(capsys):

    mapname = "test_code_build_1"
    inpardict = {"neutral_charge_threshold": ["0.001"]}

    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter(mapname, inpardict=inpardict)

    # First, the total charge is larger than threshold

    # total is 0.1, which is larger than the threshold of 0.001
    charges = np.array([
        0.2, 0.4, -0.3, -0.3, 0.1
    ])

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        _ = GM_SR.check_box_charge(Printer, RunPars, charges)

    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("MD_SU_3\n")

    # Then, total charge is larger than threshold, but only because
    # there is a whole number involved. The decimal part still complies.

    # total is 1.0, which' decimal part is still below the threshold.
    charges = np.array([
        0.2, 0.4, 0.3, 0.1
    ])

    assert not GM_SR.check_box_charge(Printer, RunPars, charges)

    captured = capsys.readouterr()
    assert captured.out.endswith("MD_SU_3\n")


def parameter_getter(mapname, cmdline=None, inpardict=None):

    # prepare inputs
    cmdadd = [
        "-md", "tests/test_tools/Data/maps_for_test_MapReader_1\\;"
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
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = basic_setup(
        cmdline, inpardict, mapname=mapname, finish_before="extract_code")

    # process maps
    for map_ in mapdict.values():
        map_.initialize(Files, Printer)
    # Ditch all maps that contain problems/flaws/issues
    mapdict = {map_.name: map_ for map_ in mapdict.values() if map_.success}
    for map_choice in RunPars.maps_to_use:
        if map_choice not in mapdict:
            assert False  # In main code, this is MI_GEM_1
    requested_mapdict = {
        map_.name: map_ for map_ in mapdict.values()
        if map_.name in RunPars.maps_to_use
    }
    RunPars.requested_mapdict = requested_mapdict
    if any(map_.Core.requires_bonds for map_ in requested_mapdict.values()):
        RunPars.detected_requires_bonds = True
    else:
        RunPars.detected_requires_bonds = False

    return (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    )
