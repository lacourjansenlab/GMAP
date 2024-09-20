"""
Tests all the functions/classes/methods in the file:
src/tools/CmdInterface.py.

Missing tests:

(@ Sept 20th '24):
  (0 missed statements)

- None!

To hide this file from the overview, incomplete tests were added for the
following:
- the actual call to the requested program - the program's function is
  tested by its own test file, but triggered GEMs SU_PP_1 here (thats
  the fastest way to fail within a program invoked by this script)
"""

# Standard library imports
import pytest
import subprocess

# Local imports
import GMAP
from GMAP.src.tools.Exceptions import GmapAttributeError, GmapKeyError
import GMAP.src.tools.CmdInterface as GM_CI
import GMAP.src.tools.PrintTools as GM_PT


def test_cmd_interface(capsys):
    callcommand = ["GMAP", "nothing", "nothing"]
    with pytest.raises(GmapAttributeError, match="SU_GM_1"):
        GM_CI.cmd_interface(callcommand)

    callcommand = ["GMAP"]  # == GMAP help help
    GM_CI.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_PT.word_wrap(GMAP.__doc__) + "\n")

    callcommand = ["GMAP", "HeLp"]  # == GMAP help help
    GM_CI.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_PT.word_wrap(GMAP.__doc__) + "\n")

    callcommand = ["GMAP", "GEM"]  # == GMAP GEM help
    GM_CI.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_PT.word_wrap(GMAP.GEM.__doc__) + "\n")

    callcommand = ["GMAP", "help", "GEM"]
    GM_CI.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_PT.word_wrap(GMAP.GEM.__doc__) + "\n")

    callcommand = ["GMAP", "help", "nothing"]
    with pytest.raises(GmapAttributeError, match="SU_GM_1$"):
        GM_CI.cmd_interface(callcommand)

    # test program invokke
    callcommand = ["GMAP", "GEM", "doesntexist"]
    with pytest.raises(GmapKeyError, match="SU_PP_1"):
        GM_CI.cmd_interface(callcommand)


def test_calldict():
    callcommand = ["GMAP", "GEM", "run", "inpfile", "--safe_mode", "-v", "4"]
    all_args = GM_CI.calldict(callcommand)
    assert all_args == {
        "GMAP": ["GEM", "run", "inpfile"],
        "--safe_mode": [],
        "-v": ["4"]
    }


def test_get_safe_dark():
    callcommand = ["GMAP", "GEM", "run", "inpfile", "--safe_mode", "-v", "4"]
    all_args = GM_CI.calldict(callcommand)
    safe, dark = GM_CI.get_safe_dark(all_args)
    assert (safe, dark) == (True, True)

    callcommand = [
        "GMAP", "GEM", "run", "inpfile", "--safe_mode", "-v", "4", "-nodm"]
    all_args = GM_CI.calldict(callcommand)
    safe, dark = GM_CI.get_safe_dark(all_args)
    assert (safe, dark) == (True, False)

    callcommand = [
        "GMAP", "GEM", "run", "inpfile", "--safe_mode", "false", "-v", "4",
        "-dm"]
    all_args = GM_CI.calldict(callcommand)
    safe, dark = GM_CI.get_safe_dark(all_args)
    assert (safe, dark) == (False, True)


def test_main():
    callcommand = ["GMAP", "nothing", "nothing"]
    captured = subprocess.run(callcommand, capture_output=True)
    assert captured.stderr.endswith(b"SU_GM_1\r\n")

    callcommand = ["GMAP"]  # == GMAP help help
    captured = subprocess.run(callcommand, capture_output=True)
    outbytes = (GM_PT.word_wrap(GMAP.__doc__) + "\n").replace(
        "\n", "\r\n").encode('utf-8')
    assert captured.stdout.endswith(outbytes)
