"""
Tests all the functions/classes/methods in the file:
src/tools/file_handler.py.

Missing tests:

(@ January 10th '25):
125, 129-141, 358 (8 missed statements)

(CUHTAT - currently unknown how to access this)

- Program is run using any OS other than windows 64 bit (125, 129-141)
  (CUHTAT; at least within one single run, probably impossible)
- the reference parameter file could not be found (SU_FH_2) (CUHTAT) (358)

"""


# standard library imports
import datetime
from pathlib import Path
import sys

# 3rd party imports
import numpy as np
import pytest

# local imports
import GMAP.src.tools.cmd_interface as GM_ci
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.constants as GM_con
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.file_handler as GM_fh


class TestFileLocations:
    @pytest.mark.nofiles
    def test_sinprops(self):
        now = datetime.datetime.now()
        files = GM_fh.FileLocations(now=now)
        cmd = tuple(sys.argv)
        cmd = (Path(cmd[0]).name,) + cmd[1:]
        assert files.callcommand == " ".join(cmd)
        assert files.now_str == now.strftime("%Y-%m-%d_%H-%M-%S")
        curpath = Path(__file__).resolve()
        assert files.sourcedir_hc == (
            curpath / "../../../sourcefiles").resolve()
        assert files.mapdir_hc == (curpath / "../../../maps").resolve()
        assert files.exec_os in GM_con.clib_ext_dict.keys()
        assert files.clib_extension in GM_con.clib_ext_dict.values()


def test_get_bare_file():
    cmd_pardict = {
        "logofile": [Path("logo.txt")]
    }
    files_hc = [Path("default.hc")]
    floc_hc = Path(".")
    flocs = GM_fh.get_bare_file(
        "logofile", files_hc, floc_hc, cmd_pardict)
    assert flocs == [(floc_hc / "logo.txt").resolve()]


def test_write_output():
    cwd = Path(".").resolve()
    run_pars = GM_ct.CustomClass(**{
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
    hamfname = run_pars.output_hamiltonian_filename
    dipfname = run_pars.output_dipole_filename
    enefname = run_pars.output_energies_filename
    ramfname = run_pars.output_raman_filename
    posfname = run_pars.output_positions_filename
    dbpfname = run_pars.output_doublepos_filename

    # clear files
    for fname in (hamfname, dipfname, enefname, ramfname, posfname, dbpfname):
        with open(fname.parent / f"{fname.name}.bin", "wb"):
            pass
        with open(fname.parent / f"{fname.name}.txt", "w"):
            pass

    GM_fh.write_output(run_pars, framenum, outputs)

    # -----  test contents hamiltonian  -----

    with open(str(hamfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        binham = np.fromfile(fhand, dtype="float32")[1:]
    squareham = np.zeros((4, 4))
    squareham[np.triu_indices_from(squareham)] = binham
    squareham = squareham + squareham.T - np.diag(np.diag(squareham))
    assert np.all(squareham == outputs["hamiltonian"])

    txtham = np.loadtxt(
        str(run_pars.output_hamiltonian_filename) + ".txt",
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
        str(run_pars.output_energies_filename) + ".txt",
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
        str(run_pars.output_dipole_filename) + ".txt",
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
        str(run_pars.output_raman_filename) + ".txt",
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
        str(run_pars.output_positions_filename) + ".txt",
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
        str(run_pars.output_doublepos_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 8)).T
    assert np.all(txtdip == outputs["doublepos"])


def test_write_output_multiplied():
    cwd = Path(".").resolve()
    run_pars = GM_ct.CustomClass(**{
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
    hamfname = run_pars.output_hamiltonian_filename
    dipfname = run_pars.output_dipole_filename
    enefname = run_pars.output_energies_filename
    ramfname = run_pars.output_raman_filename
    posfname = run_pars.output_positions_filename
    dbpfname = run_pars.output_doublepos_filename

    # clear files
    for fname in (hamfname, dipfname, enefname, ramfname, posfname, dbpfname):
        with open(fname.parent / f"{fname.name}.bin", "wb"):
            pass
        with open(fname.parent / f"{fname.name}.txt", "w"):
            pass

    GM_fh.write_output(run_pars, framenum, outputs)

    # -----  test contents hamiltonian  -----

    with open(str(hamfname) + ".bin", "rb") as fhand:
        # skip first, that is frame ix
        binham = np.fromfile(fhand, dtype="float32")[1:]
    squareham = np.zeros((4, 4))
    squareham[np.triu_indices_from(squareham)] = binham
    squareham = squareham + squareham.T - np.diag(np.diag(squareham))
    assert np.all(squareham == outputs["hamiltonian"])

    txtham = np.loadtxt(
        str(run_pars.output_hamiltonian_filename) + ".txt",
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
        str(run_pars.output_energies_filename) + ".txt",
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
        str(run_pars.output_dipole_filename) + ".txt",
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
        str(run_pars.output_raman_filename) + ".txt",
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
        str(run_pars.output_positions_filename) + ".txt",
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
        str(run_pars.output_doublepos_filename) + ".txt",
        dtype="float32"
    )[1:]  # skip first, that is frame ix
    txtdip = txtdip.reshape((3, 8)).T
    assert np.all(txtdip == outputs["doublepos"])


def test_clear_output_multiple(tmp_path):
    ohf = tmp_path / "hamfile"
    ohf_txt = ohf.parent / f"{ohf.name}.txt"
    ohf_bin = ohf.parent / f"{ohf.name}.bin"

    oef = tmp_path / "enefile"
    oef_txt = oef.parent / f"{oef.name}.txt"
    oef_bin = oef.parent / f"{oef.name}.bin"

    odf = tmp_path / "dipfile"
    odf_txt = odf.parent / f"{odf.name}.txt"
    odf_bin = odf.parent / f"{odf.name}.bin"

    orf = tmp_path / "ramfile"
    orf_txt = orf.parent / f"{orf.name}.txt"
    orf_bin = orf.parent / f"{orf.name}.bin"

    opf = tmp_path / "posfile"
    opf_txt = opf.parent / f"{opf.name}.txt"
    opf_bin = opf.parent / f"{opf.name}.bin"

    odpf = tmp_path / "dbpfile"
    odpf_txt = odpf.parent / f"{odpf.name}.txt"
    odpf_bin = odpf.parent / f"{odpf.name}.bin"

    txtfiles = (ohf_txt, oef_txt, odf_txt, orf_txt, opf_txt, odpf_txt)
    binfiles = (ohf_bin, oef_bin, odf_bin, orf_bin, opf_bin, odpf_bin)

    for fname in txtfiles:
        with open(fname, "w") as fhand:
            fhand.write("123")
        with open(fname, "r") as fhand:
            assert len(fhand.read()) == 3

    for fname in binfiles:
        with open(fname, "wb") as fhand:
            fhand.write(bytes([1, 2, 3]))
        with open(fname, "rb") as fhand:
            assert len(fhand.read()) == 3

    runpars = GM_ct.CustomClass(**{
        "output_data": ["ham", "ene", "dip", "ram", "pos", "dbp"],
        "output_hamiltonian_filename": ohf,
        "output_energies_filename": oef,
        "output_dipole_filename": odf,
        "output_raman_filename": orf,
        "output_positions_filename": opf,
        "output_doublepos_filename": odpf,
        "output_format": ["bin", "txt"]
    })

    GM_fh.clear_output(runpars)

    for fname in txtfiles:
        print(fname)
        with open(fname, "r") as fhand:
            assert len(fhand.read()) == 0

    for fname in binfiles:
        with open(fname, "rb") as fhand:
            assert len(fhand.read()) == 0


def test_write_legend():
    def get_resnum_text(resnum):
        return f"living on residue number {resnum}"

    class MockOsc:
        def __init__(self, **kwargs):
            for parname, val in kwargs.items():
                setattr(self, parname, val)

        def __str__(self):
            return (
                f"Oscillator of type {self.map.name} "
                f"{self.map.code.GM_str_osc(self.ix)}"
            )

    cwd = Path(".").resolve()
    run_pars = GM_ct.CustomClass(**{
        "output_legend_filename": cwd / "legend.txt"
    })
    map_ = GM_ct.CustomClass(**{
        "code": GM_ct.CustomClass(**{"GM_str_osc": get_resnum_text}),
        "name": "mockmap"
    })
    system = GM_ct.CustomClass(**{"oscillators": [MockOsc(**{
        "map": map_,
        "ix": ix
    }) for ix in range(4)]})

    outfname = run_pars.output_legend_filename

    GM_fh.write_legend(run_pars, system)

    with open(str(outfname)) as fhand:
        contents = fhand.read()
        assert contents == (
            "at index 0: Oscillator of type mockmap living on residue number "
            "0\nat index 1: Oscillator of type mockmap living on residue "
            "number 1\nat index 2: Oscillator of type mockmap living on "
            "residue number 2\nat index 3: Oscillator of type mockmap living "
            "on residue number 3\n"
        )


@pytest.mark.nofiles
def test_write_parameter_file(tmp_path):
    # curdir = Path(__file__).resolve().parent

    # perform first run
    with open(tmp_path / "input_parameters.txt", "w") as fhand:
        fhand.write("")
    (tmp_path / "run1").mkdir()
    GM_ci.cmd_interface([
        "GMAP", "GEM", "run",
        str((tmp_path / "input_parameters.txt").resolve()),
        "--number_frames", "2",
        "--output_directory", str((tmp_path / "run1").resolve()),
        "--log_directory", str((tmp_path / "run1").resolve()),
        "--estatics_method", "perres_nocut",
        "--estatic_smooth_range", "0",
        "--verbose", "1",
        "--verbose_logfile", "4",
        "--output_format", "txt\\;",
        "--maps_to_use", "AmideBB", "AmideSC\\;",  # default is SC only
        # add 3 coupling lines to see if multiline parameters are written
        # correctly.
        "--couplings_to_use", "DipDip", ":All\\;",
        "--couplings_to_use", "None", "AmideSC:\\;",
        "--couplings_to_use", "DipDip", "AmideSC:\\;"
    ])

    # check if first run went without any major errors
    with open(tmp_path / "run1/log.log", encoding="utf-8") as fhand:
        output = fhand.read()
    assert output.endswith(
        "  ░░▒▒▓▓██ That was all for today, folks. Thank you, and good night! "
        "██▓▓▒▒░░\n"
    )

    # as all individual file names have the exact directory location mentioned,
    # move all files, and re-fill that same old directory
    (tmp_path / "run1").rename(tmp_path / "run2")

    # perform second run
    (tmp_path / "run1").mkdir()

    GM_ci.cmd_interface([
        "GMAP", "GEM", "run",
        str((tmp_path / "run2/parameters.txt").resolve()),
        "--number_frames", "2",
        # "--output_directory", str((tmp_path / "run2").resolve()),
        # "--log_directory", str((tmp_path / "run2").resolve())
    ])

    # check if second run went without any major errors
    with open(tmp_path / "run2/log.log", encoding="utf-8") as fhand:
        output = fhand.read()
    assert output.endswith(
        "  ░░▒▒▓▓██ That was all for today, folks. Thank you, and good night! "
        "██▓▓▒▒░░\n"
    )

    # see if outputs of the two runs are equal
    with open(tmp_path / "run1/parameters.txt", encoding="utf-8") as fhand:
        pars1 = fhand.read()
    with open(tmp_path / "run2/parameters.txt", encoding="utf-8") as fhand:
        pars2 = fhand.read()

    # different paths are expected
    pars2.replace("run2", "run1")
    assert pars1 == pars2


def test_SU_FH_1():
    cwd = Path(".")

    with pytest.raises(GM_ex.GmapFileNotFoundError, match="SU_FH_1$"):
        _ = GM_fh.get_def_parfile({
            "default_parameter_filename": [cwd/"doesntexist.dfa"]
        })
