# # standard library imports
# from pathlib import Path

# 3rd party imports
import pytest

# local imports
from GMAP.src.programs import Setup as GM_Setup
from GMAP.src.tools import FileHandler as GM_FH
from GMAP.src.tools import PrintTools as GM_PT

# The tests below test error codes!


# Tests if not existing folder raises correct error
def test_Setup_1(capsys, tmp_path):
    Printer, sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    not_a_directory = tmp_path / "not_a_directory"

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        GM_Setup.verify_target(not_a_directory, sourcefiles_dir,
                               mapfiles_dir, Printer)
    assert pytest_wrapped_sysexit.type is SystemExit

    captured = capsys.readouterr()
    assert captured.out.endswith("Setup_1\n")


def test_Setup_2(capsys, tmp_path):  # Tests if sourcedir doesn't exist yet
    Printer, sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    sourcefiles_dir.mkdir()

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        GM_Setup.verify_target(tmp_path, sourcefiles_dir,
                               mapfiles_dir, Printer)
    assert pytest_wrapped_sysexit.type is SystemExit

    captured = capsys.readouterr()
    assert captured.out.endswith("Setup_2\n")


def test_Setup_3(capsys, tmp_path):   # Tests if mapdir doesn't exist yet
    Printer, sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    mapfiles_dir.mkdir()

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        GM_Setup.verify_target(tmp_path, sourcefiles_dir,
                               mapfiles_dir, Printer)
    assert pytest_wrapped_sysexit.type is SystemExit

    captured = capsys.readouterr()
    assert captured.out.endswith("Setup_3\n")

# The tests below test functions!


def test_verify_target(tmp_path):
    Printer, sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    GM_Setup.verify_target(tmp_path, sourcefiles_dir, mapfiles_dir, Printer)


def test_Setup(tmp_path, capsys):
    callcommand = ["Setup", tmp_path]
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    GM_Setup.Setup(callcommand, Files, Printer)

    captured = capsys.readouterr()
    assert captured.out.endswith(f"Copied folders to\n{tmp_path}\n"
                                 "succesfully!\n")


def base_tests(tmp_path):  # Not a test
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    sourcefiles_dir = tmp_path / "sourcefiles_dir"
    mapfiles_dir = tmp_path / "mapfiles_dir"

    return Printer, sourcefiles_dir, mapfiles_dir
