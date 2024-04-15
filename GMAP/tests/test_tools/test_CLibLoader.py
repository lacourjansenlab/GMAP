# local imports
from .test_SystemReader import parameter_getter
import GMAP.src.tools.CLibLoader as GM_CL


def test_smth():
    cmdline = ["-md", "maps\\;"]
    (
        Files, Printer, RunPars, RefPars, DefPars, InPars,
        CmdPars, mapdict
    ) = parameter_getter("AmideSC", cmdline)

    VEGlib = GM_CL.VEG_CLib(Printer, RunPars)

    assert VEGlib.testadd(2, 3) == 5

    newlib = GM_CL.VEG_CLib()
    assert newlib.testadd(3, 4) == 7
