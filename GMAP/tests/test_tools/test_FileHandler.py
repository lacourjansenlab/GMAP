"""
Tests all the functions/classes/methods in the file:
src/tools/FileHandler.py.

Missing tests:

(@ August 2nd '24):
97, 101-113, 333, 536-547, 565-570 (26 missed statements)

(CUHTAT - currently unknown how to access this)
- Program is run using any OS other than windows 64 bit (97, 101-113)
  (CUHTAT; at least within one single run, probably impossible)
- the reference parameter file could not be found (SU_FH_2) (CUHTAT) (333)
- output files are not cleared yet.  (536-570)  (this happens in GEM, just
  before the per-frame loop)
"""


# standard library imports
from pathlib import Path

# 3rd party imports
import numpy as np
import pytest

# local imports
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.FileHandler as GM_FH


def test_get_bare_file():
    Files = GM_FH.FileLocations()
    cmd_pardict = {
        "logofile": [Path("logo.txt")]
    }
    files_hc = [Path("default.hc")]
    floc_hc = Path(".")
    flocs = GM_FH.get_bare_file(
        Files, "logofile", files_hc, floc_hc, cmd_pardict)
    assert flocs == [(floc_hc / "logo.txt").resolve()]


def test_write_output():
    cwd = Path(".").resolve()
    RunPars = GM_CT.CustomClass(**{
        "output_hamiltonian_filename": cwd / "hamiltonian",
        "output_dipole_filename": cwd / "dipoles",
        "output_energies_filename": cwd / "energies",
        "output_raman_filename": cwd / "raman_tensor",
        "output_positions_filename": cwd / "positions",
        "output_doublepos_filename": cwd / "doublepos",
        "output_data": ["ham", "dip", "ene", "pos", "dbp", "ram"],
        "output_format": ["bin", "txt"],
        "hamiltonian_multiplier": 1,
        "energies_multiplier": 1,
        "dipoles_multiplier": 1,
        "raman_multiplier": 1,
        "positions_multiplier": 1,
        "doublepos_multiplier": 1
    })

    framenum = 2
    outputs = {}
    outputs["hamiltonian"] = np.array([
        [100, 1, 2, 3],
        [1, 100, 4, 5],
        [2, 4, 100, 6],
        [3, 5, 6, 100]
    ], dtype="float32")
    outputs["dipoles"] = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [3, 4, 5]
    ], dtype="float32")
    outputs["energies"] = np.array([
        [100, 101, 102, 103]
    ], dtype="float32")
    outputs["raman"] = np.array([
        [1, 2, 3, 4, 5, 6],
        [7, 8, 9, 10, 11, 12],
        [13, 14, 15, 16, 17, 18],
        [19, 20, 21, 22, 23, 24]
    ], dtype='float32')
    outputs["positions"] = np.array([
        [4, 5, 6],
        [7, 8, 9],
        [1, 2, 3],
        [3, 4, 5]
    ], dtype="float32")
    outputs["doublepos"] = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [3, 4, 5],
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [3, 4, 5]
    ], dtype="float32")
    hamfname = RunPars.output_hamiltonian_filename
    dipfname = RunPars.output_dipole_filename
    enefname = RunPars.output_energies_filename
    ramfname = RunPars.output_raman_filename
    posfname = RunPars.output_positions_filename
    dbpfname = RunPars.output_doublepos_filename

    # clear files
    for fname in (hamfname, dipfname, enefname, ramfname, posfname, dbpfname):
        with open(fname.parent / f"{fname.name}.bin", "wb"):
            pass
        with open(fname.parent / f"{fname.name}.txt", "w"):
            pass

    GM_FH.write_output(RunPars, framenum, outputs)

    # -----  test contents hamiltonian  -----

    with open(str(hamfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        binham = np.fromfile(fhand, dtype="float32")[1:]
    squareham = np.zeros((4, 4))
    squareham[np.triu_indices_from(squareham)] = binham
    squareham = squareham + squareham.T - np.diag(np.diag(squareham))
    assert np.all(squareham == outputs["hamiltonian"])

    txtham = np.loadtxt(
        str(RunPars.output_hamiltonian_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    squareham = np.zeros((4, 4))
    squareham[np.triu_indices_from(squareham)] = txtham
    squareham = squareham + squareham.T - np.diag(np.diag(squareham))
    assert np.all(squareham == outputs["hamiltonian"])

    # -----  test contents energies  -----

    with open(str(enefname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    # bindip = bindip.reshape((3, 4)).T
    assert np.all(bindip == outputs["energies"])

    txtdip = np.loadtxt(
        str(RunPars.output_energies_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    # txtdip = txtdip.reshape((3, 4)).T
    assert np.all(txtdip == outputs["energies"])

    # -----  test contents dipoles  -----

    with open(str(dipfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    bindip = bindip.reshape((3, 4)).T
    assert np.all(bindip == outputs["dipoles"])

    txtdip = np.loadtxt(
        str(RunPars.output_dipole_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 4)).T
    assert np.all(txtdip == outputs["dipoles"])

    # -----  test contents raman  -----

    with open(str(ramfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        binram = np.fromfile(fhand, dtype="float32")[1:]
    binram = binram.reshape((6, 4)).T
    assert np.all(binram == outputs["raman"])

    txtram = np.loadtxt(
        str(RunPars.output_raman_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtram = txtram.reshape((6, 4)).T
    assert np.all(txtram == outputs["raman"])

    # -----  test contents positions  -----

    with open(str(posfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    bindip = bindip.reshape((3, 4)).T
    assert np.all(bindip == outputs["positions"])

    txtdip = np.loadtxt(
        str(RunPars.output_positions_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 4)).T
    assert np.all(txtdip == outputs["positions"])

    # -----  test contents doublepos  -----

    with open(str(dbpfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    bindip = bindip.reshape((3, 8)).T
    assert np.all(bindip == outputs["doublepos"])

    txtdip = np.loadtxt(
        str(RunPars.output_doublepos_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 8)).T
    assert np.all(txtdip == outputs["doublepos"])


def test_write_output_multiplied():
    cwd = Path(".").resolve()
    RunPars = GM_CT.CustomClass(**{
        "output_hamiltonian_filename": cwd / "hamiltonian",
        "output_dipole_filename": cwd / "dipoles",
        "output_energies_filename": cwd / "energies",
        "output_raman_filename": cwd / "raman_tensor",
        "output_positions_filename": cwd / "positions",
        "output_doublepos_filename": cwd / "doublepos",
        "output_data": ["ham", "dip", "ene", "pos", "dbp", "ram"],
        "output_format": ["bin", "txt"],
        "hamiltonian_multiplier": 2,
        "energies_multiplier": 3,
        "dipoles_multiplier": 4,
        "raman_multiplier": 5,
        "positions_multiplier": 6,
        "doublepos_multiplier": 7,
    })

    framenum = 2
    outputs = {}
    outputs["hamiltonian"] = np.array([
        [100, 1, 2, 3],
        [1, 100, 4, 5],
        [2, 4, 100, 6],
        [3, 5, 6, 100]
    ], dtype="float32")
    outputs["dipoles"] = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [3, 4, 5]
    ], dtype="float32")
    outputs["energies"] = np.array([
        [100, 101, 102, 103]
    ], dtype="float32")
    outputs["raman"] = np.array([
        [1, 2, 3, 4, 5, 6],
        [7, 8, 9, 10, 11, 12],
        [13, 14, 15, 16, 17, 18],
        [19, 20, 21, 22, 23, 24]
    ], dtype='float32')
    outputs["positions"] = np.array([
        [4, 5, 6],
        [7, 8, 9],
        [1, 2, 3],
        [3, 4, 5]
    ], dtype="float32")
    outputs["doublepos"] = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [3, 4, 5],
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [3, 4, 5]
    ], dtype="float32")
    hamfname = RunPars.output_hamiltonian_filename
    dipfname = RunPars.output_dipole_filename
    enefname = RunPars.output_energies_filename
    ramfname = RunPars.output_raman_filename
    posfname = RunPars.output_positions_filename
    dbpfname = RunPars.output_doublepos_filename

    # clear files
    for fname in (hamfname, dipfname, enefname, ramfname, posfname, dbpfname):
        with open(fname.parent / f"{fname.name}.bin", "wb"):
            pass
        with open(fname.parent / f"{fname.name}.txt", "w"):
            pass

    GM_FH.write_output(RunPars, framenum, outputs)

    # -----  test contents hamiltonian  -----

    with open(str(hamfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        binham = np.fromfile(fhand, dtype="float32")[1:]
    squareham = np.zeros((4, 4))
    squareham[np.triu_indices_from(squareham)] = binham
    squareham = squareham + squareham.T - np.diag(np.diag(squareham))
    assert np.all(squareham == outputs["hamiltonian"])

    txtham = np.loadtxt(
        str(RunPars.output_hamiltonian_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    squareham = np.zeros((4, 4))
    squareham[np.triu_indices_from(squareham)] = txtham
    squareham = squareham + squareham.T - np.diag(np.diag(squareham))
    assert np.all(squareham == outputs["hamiltonian"])

    # -----  test contents energies  -----

    with open(str(enefname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    # bindip = bindip.reshape((3, 4)).T
    assert np.all(bindip == outputs["energies"])

    txtdip = np.loadtxt(
        str(RunPars.output_energies_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    # txtdip = txtdip.reshape((3, 4)).T
    assert np.all(txtdip == outputs["energies"])

    # -----  test contents dipoles  -----

    with open(str(dipfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    bindip = bindip.reshape((3, 4)).T
    assert np.all(bindip == outputs["dipoles"])

    txtdip = np.loadtxt(
        str(RunPars.output_dipole_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 4)).T
    assert np.all(txtdip == outputs["dipoles"])

    # -----  test contents raman  -----

    with open(str(ramfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        binram = np.fromfile(fhand, dtype="float32")[1:]
    binram = binram.reshape((6, 4)).T
    assert np.all(binram == outputs["raman"])

    txtram = np.loadtxt(
        str(RunPars.output_raman_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtram = txtram.reshape((6, 4)).T
    assert np.all(txtram == outputs["raman"])

    # -----  test contents positions  -----

    with open(str(posfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    bindip = bindip.reshape((3, 4)).T
    assert np.all(bindip == outputs["positions"])

    txtdip = np.loadtxt(
        str(RunPars.output_positions_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 4)).T
    assert np.all(txtdip == outputs["positions"])

    # -----  test contents doublepos  -----

    with open(str(dbpfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        bindip = np.fromfile(fhand, dtype="float32")[1:]
    bindip = bindip.reshape((3, 8)).T
    assert np.all(bindip == outputs["doublepos"])

    txtdip = np.loadtxt(
        str(RunPars.output_doublepos_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 8)).T
    assert np.all(txtdip == outputs["doublepos"])


def test_write_legend():
    def get_resnum_text(resnum):
        return f"living on residue number {resnum}"

    class MockOsc:
        def __init__(self, **kwargs):
            for parname, val in kwargs.items():
                setattr(self, parname, val)

        def __str__(self):
            return (
                f"Oscillator of type {self.Map.name} "
                f"{self.Map.code.GM_str_osc(self.ix)}"
            )

    cwd = Path(".").resolve()
    RunPars = GM_CT.CustomClass(**{
        "output_legend_filename": cwd / "legend.txt"
    })
    map_ = GM_CT.CustomClass(**{
        "code": GM_CT.CustomClass(**{"GM_str_osc": get_resnum_text}),
        "name": "mockmap"
    })
    System = GM_CT.CustomClass(**{"oscillators": [MockOsc(**{
        "Map": map_,
        "ix": ix
    }) for ix in range(4)]})

    outfname = RunPars.output_legend_filename

    GM_FH.write_legend(RunPars, System)

    with open(str(outfname)) as fhand:
        contents = fhand.read()
        assert contents == (
            "at index 0: Oscillator of type mockmap living on residue number "
            "0\nat index 1: Oscillator of type mockmap living on residue "
            "number 1\nat index 2: Oscillator of type mockmap living on "
            "residue number 2\nat index 3: Oscillator of type mockmap living "
            "on residue number 3\n"
        )


def test_SU_FH_1():
    Files = GM_FH.FileLocations()
    cwd = Path(".")

    with pytest.raises(GM_Ex.GmapFileNotFoundError, match="SU_FH_1$"):
        _ = GM_FH.get_def_parfile(Files, {
            "default_parameter_filename": [cwd/"doesntexist.dfa"]
        })
