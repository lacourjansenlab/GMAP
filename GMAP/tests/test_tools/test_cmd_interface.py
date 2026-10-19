"""
Tests all the functions/classes/methods in the file:
src/tools/cmd_interface.py.

Missing tests:

(@ Sept 20th '24):
  (0 missed statements)

- None!

To hide this file from the overview, incomplete tests were added for the
following:

- the actual call to the requested program
  The program's function is tested by its own test file, but triggered
  GEMs SU_PP_1 here (thats the fastest way to fail within a program
  invoked by this script)

"""

# Standard library imports
import subprocess

# 3rd party imports
import pytest

# Local imports
import GMAP
from GMAP.src.tools.exceptions import GmapAttributeError, GmapKeyError
import GMAP.src.tools.cmd_interface as GM_ci
import GMAP.src.tools.print_tools as GM_pt


@pytest.mark.nofiles
def test_cmd_interface(capsys):
    callcommand = ["GMAP", "nothing", "nothing"]
    with pytest.raises(GmapAttributeError, match="SU_GM_1"):
        GM_ci.cmd_interface(callcommand)

    callcommand = ["GMAP"]  # == GMAP help help
    GM_ci.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_pt.word_wrap(GMAP.__doc__) + "\n")

    callcommand = ["GMAP", "HeLp"]  # == GMAP help help
    GM_ci.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_pt.word_wrap(GMAP.__doc__) + "\n")

    callcommand = ["GMAP", "GEM"]  # == GMAP GEM help
    GM_ci.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_pt.word_wrap(GMAP.GEM.__doc__) + "\n")

    callcommand = ["GMAP", "help", "GEM"]
    GM_ci.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_pt.word_wrap(GMAP.GEM.__doc__) + "\n")

    callcommand = ["GMAP", "help", "nothing"]
    with pytest.raises(GmapAttributeError, match="SU_GM_1$"):
        GM_ci.cmd_interface(callcommand)

    # test program invokke
    callcommand = ["GMAP", "GEM", "doesntexist"]
    with pytest.raises(GmapKeyError, match="SU_PP_1"):
        GM_ci.cmd_interface(callcommand)


def test_calldict():
    callcommand = ["GMAP", "GEM", "run", "inpfile", "--safe_mode", "-v", "4"]
    all_args = GM_ci.calldict(callcommand)
    assert all_args == {
        "GMAP": ["GEM", "run", "inpfile"],
        "--safe_mode": [],
        "-v": ["4"]
    }


def test_get_safe_dark():
    callcommand = ["GMAP", "GEM", "run", "inpfile", "--safe_mode", "-v", "4"]
    all_args = GM_ci.calldict(callcommand)
    safe, dark = GM_ci.get_safe_dark(all_args)
    assert (safe, dark) == (True, True)

    callcommand = [
        "GMAP", "GEM", "run", "inpfile", "--safe_mode", "-v", "4", "-nodm"]
    all_args = GM_ci.calldict(callcommand)
    safe, dark = GM_ci.get_safe_dark(all_args)
    assert (safe, dark) == (True, False)

    callcommand = [
        "GMAP", "GEM", "run", "inpfile", "--safe_mode", "false", "-v", "4",
        "-dm"]
    all_args = GM_ci.calldict(callcommand)
    safe, dark = GM_ci.get_safe_dark(all_args)
    assert (safe, dark) == (False, True)


def test_main():
    callcommand = ["GMAP", "nothing", "nothing"]
    captured = subprocess.run(callcommand, capture_output=True)
    stderr = captured.stderr
    # On windows the \r will be generated, not on linux/mac
    assert stderr.endswith(b"SU_GM_1\r\n") or stderr.endswith(b"SU_GM_1\n")

    callcommand = ["GMAP"]  # == GMAP help help
    captured = subprocess.run(callcommand, capture_output=True)
    # On windows
    outbytes = (GM_pt.word_wrap(GMAP.__doc__) + "\n").replace(
        "\n", "\r\n").encode('utf-8')
    # On linux/mac
    outbyteslinux = (GM_pt.word_wrap(GMAP.__doc__) + "\n").encode('utf-8')
    assert (
        captured.stdout.endswith(outbytes)
        or captured.stdout.endswith(outbyteslinux))
