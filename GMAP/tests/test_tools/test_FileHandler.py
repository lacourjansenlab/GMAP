"""
Tests all the functions/classes/methods in the file:
src/tools/FileHandler.py.

Missing tests:

(@ June 24th '24):
105, 109-121, 344, 515-520, 538-543 (22 missed statements)

(CUHTAT - currently unknown how to access this)
- Program is run using any OS other than windows 64 bit (105, 119-121)
  (CUHTAT; at least within one single run, probably impossible)
- the reference parameter file could not be found (SU_FH_2) (CUHTAT) (344)
- output files are not cleared yet.  (515-543)  (this happens in GEM, just
  before the per-frame loop)
"""


# standard library imports
from pathlib import Path

# 3rd party imports
import numpy as np
import pytest

# local imports
from GMAP.src.tools import FileHandler as GM_FH
from GMAP.src.tools import PrintTools as GM_PT


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
    RunPars = EmptyClass(**{
        "output_hamiltonian_filename": cwd / "hamiltonian",
        "output_dipole_filename": cwd / "dipoles",
        "output_energies_filename": cwd / "energies",
        "output_data": ["ham", "dip", "ene"],
        "output_format": ["bin", "txt"]
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
    hamfname = RunPars.output_hamiltonian_filename
    dipfname = RunPars.output_dipole_filename
    enefname = RunPars.output_energies_filename

    # clear files
    for fname in (hamfname, dipfname, enefname):
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


def test_SU_FH_1(capsys):
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)
    cwd = Path(".")

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        _ = GM_FH.get_def_parfile(Files, Printer, {
            "default_parameter_filename": [cwd/"doesntexist.dfa"]
        })

    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("SU_FH_1\n")


class EmptyClass:
    def __init__(self, **kwargs):
        for parname, val in kwargs.items():
            setattr(self, parname, val)
        return
