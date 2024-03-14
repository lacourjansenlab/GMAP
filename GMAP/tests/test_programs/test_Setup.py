# standard library imports
from pathlib import Path

# 3rd party imports
import pytest

# local imports
from GMAP.src.programs import Setup as GM_Setup
from GMAP.src.tools import FileHandler as GM_FH
from GMAP.src.tools import PrintTools as GM_PT




def test_verify_target(): # Tests if unexpected errors are not raised
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    GM_Setup.verify_target(".", "uniquename1", "uniquename2", Printer)

def test_Setup_1(capsys): # Tests if not existing folder raises correct error
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)
    
    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        GM_Setup.verify_target(":::Z:::", "", "", Printer)
    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswidth("Setup_1")

def test_Setup_2(capsys):    # Tests if sourcedir doesn't exist yet 
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)
    
    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        GM_Setup.verify_target(Path("."), "","uniquename2", Printer)
    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswidth("Setup_2")

def test_Setup_3(capsys):   # Tests if mapdir doesn't exist yet
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        GM_Setup.verify_target(".", "uniquename1", "", Printer)
    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswidth("Setup_3")

def test_Setup(capsys):
    callcommand = ["Setup", ""]
