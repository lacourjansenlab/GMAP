
# standard library imports
from pathlib import Path

# 3rd party imports
import pytest

# local imports
from GMAP.src.tools import CmdInterface as GM_CLI
from GMAP.src.programs import GEM as GM_GEM
from GMAP.src.tools import FileHandler as GM_FH
from GMAP.src.tools import PrintTools as GM_PT


# Now, we also test whether the program can actually run.
def test_if_runs():
    GM_CLI.cmd_interface(["GMAP", "GEM", "run", "../test_inpar.txt"])


def test_get_parameters():
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    in_parfile = Path("../test_inpar.txt").resolve()
    argslist = []

    (
        RunPars, mapdict, CmdPars, InPars, DefPars, RefPars
    ) = GM_GEM.get_parameters(
        Files, Printer, in_parfile, argslist
    )

    # A huuuuge amount of tests would be needed here, but all of GM_PP
    # has already been tested separately.
    assert InPars.fname.name == "test_inpar.txt"
    assert DefPars == RefPars
    assert len(mapdict) == 6
    assert CmdPars.choices == {}

    (
        RunPars, mapdict, CmdPars, InPars, DefPars, RefPars
    ) = GM_GEM.get_parameters(
        Files, Printer, None, argslist
    )

    assert InPars.choices == {}

    argslist = ["-dpf", "../test_defpar.txt"]

    (
        RunPars, mapdict, CmdPars, InPars, DefPars, RefPars
    ) = GM_GEM.get_parameters(
        Files, Printer, in_parfile, argslist
    )

    assert DefPars.fname.name == "test_defpar.txt"


def test_SU_FP_1(capsys):
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    in_parfile = Path("../test_inpar.txt").resolve()
    argslist = ["-dpf", "maps/Singles/testmap1/parameters.ref"]

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        _ = GM_GEM.get_parameters(
            Files, Printer, in_parfile, argslist
        )
    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("SU_FP_1\n")


def test_SU_GEM_1(capsys):
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)

    in_parfile = Path("../test_inpar.txt").resolve()
    argslist = ["-dpf", "__main__.py"]

    with pytest.raises(SystemExit) as pytest_wrapped_sysexit:
        _ = GM_GEM.get_parameters(
            Files, Printer, in_parfile, argslist
        )
    assert pytest_wrapped_sysexit.type is SystemExit
    captured = capsys.readouterr()
    assert captured.out.endswith("SU_GEM_1\n")
