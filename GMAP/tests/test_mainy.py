# Standard library imports
import pytest
# Local imports
import GMAP
import GMAP.mainy as mainy
from GMAP.src.tools import PrintTools as GM_PT


def test_cmd_interface(capsys):
    callcommand = ["GMAP", "nothing", "nothing"]
    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        mainy.cmd_interface(callcommand)
    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("SU_GM_1\n")

    callcommand = ["GMAP", "HeLp"]
    mainy.cmd_interface(callcommand)
    captured = capsys.readouterr()
    assert captured.out.endswith(GM_PT.prettifier(GMAP.__doc__) + "\n")

    callcommand = ["GMAP", "GEM"]
    mainy.cmd_interface(callcommand)
    assert mainy.cmd_interface(callcommand) is None

# The other functions are used by test_cmd_interface so this should be enough
# testing.
