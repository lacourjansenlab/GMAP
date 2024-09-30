# # standard library imports
# from pathlib import Path

# 3rd party imports
import pytest
from pathlib import Path

# local imports
import GMAP.src.programs.Setup as GM_Setup
# from GMAP.src.programs import Setup as GM_Setup
import GMAP.src.tools.Exceptions as GM_Ex
from GMAP.src.tools import FileHandler as GM_FH
from GMAP.src.tools import PrintTools as GM_PT

# The tests below test error codes!


# Tests if not existing folder raises correct error
def test_Setup_1(tmp_path):
    sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    not_a_directory = tmp_path / "not_a_directory"

    with pytest.raises(GM_Ex.GmapNotADirectoryError, match="Setup_1$"):
        GM_Setup.verify_target(
            not_a_directory, sourcefiles_dir, mapfiles_dir)


def test_Setup_2(tmp_path):  # Tests if sourcedir doesn't exist yet
    sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    sourcefiles_dir.mkdir()

    with pytest.raises(GM_Ex.GmapIsADirectoryError, match="Setup_2$"):
        GM_Setup.verify_target(
            tmp_path, sourcefiles_dir, mapfiles_dir)


def test_Setup_3(tmp_path):   # Tests if mapdir doesn't exist yet
    sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    mapfiles_dir.mkdir()

    with pytest.raises(GM_Ex.GmapIsADirectoryError, match="Setup_3$"):
        GM_Setup.verify_target(
            tmp_path, sourcefiles_dir, mapfiles_dir)


# The tests below test functions!


def test_verify_target(tmp_path):
    sourcefiles_dir, mapfiles_dir = base_tests(tmp_path)

    assert GM_Setup.verify_target(
        tmp_path, sourcefiles_dir, mapfiles_dir
    ) is None


def test_Setup(tmp_path, capsys):
    callcommand = ["Setup", tmp_path]
    Files = GM_FH.FileLocations()

    src_dir = Files.sourcedir_hc
    map_dir = Files.mapdir_hc

    sourcefiles_original = [file.name for file in Path(src_dir).iterdir()]
    map_original = [file.name for file in Path(map_dir).iterdir()]

    GM_Setup.Setup(callcommand, Files)

    captured = capsys.readouterr()
    assert captured.out.endswith(
        GM_PT.word_wrap(f"Copied folders to {tmp_path} successfully!\n"))

    target_srcdir = tmp_path / "sourcefiles_copy"
    target_mapdir = tmp_path / "maps_copy"

    sourcefiles_copies = [file.name for file in Path(target_srcdir).iterdir()]
    map_copies = [file.name for file in Path(target_mapdir).iterdir()]

    assert target_srcdir.exists()
    assert target_mapdir.exists()

    assert sourcefiles_original == sourcefiles_copies
    assert map_original == map_copies


def base_tests(tmp_path):  # Not a test
    _ = GM_FH.FileLocations()

    sourcefiles_dir = tmp_path / "sourcefiles_dir"
    mapfiles_dir = tmp_path / "mapfiles_dir"

    return sourcefiles_dir, mapfiles_dir
