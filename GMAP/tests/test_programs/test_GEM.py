
# standard lib imports
import filecmp

# 3rd party imports
import pytest

# local imports
import GMAP.src.tools.cmd_interface as GM_ci


# Now, we also test whether the program can actually run.
@pytest.mark.nofiles
def test_if_runs(tmp_path):
    with open(tmp_path / "input_parameters.txt", "w") as fhand:
        fhand.write("output_directory  out\n")
        fhand.write("log_directory   out\n")
    (tmp_path / "out").mkdir()

    GM_ci.cmd_interface([
        "GMAP", "GEM", "run",
        str((tmp_path / "input_parameters.txt").resolve())])


@pytest.mark.nofiles
def test_early_quit(tmp_path):
    with open(tmp_path / "input_parameters.txt", "w") as fhand:
        fhand.write("output_directory  out\n")
        fhand.write("log_directory   out\n")
    (tmp_path / "out").mkdir()
    GM_ci.cmd_interface([
        "GMAP", "GEM", "run",
        str((tmp_path / "input_parameters.txt").resolve()),
        "--number_frames", "25",
        "--batch_size", "10",
        "--time_limit", "0"
    ])

    with open(tmp_path / "out" / "log.log", encoding="utf-8") as fhand:
        for line in fhand:
            line = line.strip()
            if line.startswith("Frames treated"):
                assert line.split()[2] == "0-10"
            if line.startswith("Frames requested"):
                assert line.split()[2] == "0-25"
            if line.startswith("Frames available"):
                assert line.split()[2] == "0-51"


@pytest.mark.nofiles
def test_parallel_run(tmp_path):
    # make directories
    dir_onecore = tmp_path / "onecore"
    dir_onecore.mkdir()
    dir_twocore = tmp_path / "twocore"
    dir_twocore.mkdir()

    # Perform single core run
    with open(tmp_path / "input_parameters.txt", "w") as fhand:
        fhand.write("output_directory  onecore\n")
        fhand.write("log_directory   onecore\n")
        fhand.write("output_format    bin txt\n")
        fhand.write("output_data     ham dip ene pos dbp ram\n")
    GM_ci.cmd_interface([
        "GMAP", "GEM", "run",
        str((tmp_path / "input_parameters.txt").resolve())])

    # Perform parallel (2-)core run
    with open(tmp_path / "input_parameters.txt", "w") as fhand:
        fhand.write("output_directory  twocore\n")
        fhand.write("log_directory   twocore\n")
        fhand.write("output_format    bin txt\n")
        fhand.write("output_data     ham dip ene pos dbp ram\n")
    GM_ci.cmd_interface([
        "GMAP", "GEM", "run",
        str((tmp_path / "input_parameters.txt").resolve()),
        "-nc", "2"])

    with open(dir_onecore/"hamiltonian.txt") as fhand:
        one = fhand.readlines()
        print(one)
    with open(dir_twocore/"hamiltonian.txt") as fhand:
        two = fhand.readlines()
        print(two)

    print(type(one))
    print(len(one), len(two))
    print([line.split()[0] for line in one])
    print([line.split()[0] for line in two])

    for filename in [
        "hamiltonian", "dipoles", "energies", "positions", "doublepos",
        "raman_tensor"
    ]:
        for suffix in ["bin", "txt"]:
            assert filecmp.cmp(
                dir_onecore / (filename + "." + suffix),
                dir_twocore / (filename + "." + suffix),
                shallow=False
            )
