
import sys
import ctypes as ct
from pathlib import Path
import datetime

import GMAP
import GMAP.src.tools.WarnSys as GM_WS


class FileLocations:
    def __init__(self) -> None:
        self.exec_os = FindExOs()
        self.script_dir = Path(GMAP.__file__).parent.resolve()
        self.cwd = Path(".").resolve()
        self.now = datetime.datetime.now()
        self.now_str = self.now.strftime("%Y-%m-%d_%H-%M-%S")

        self.sourcedir_hc = self.script_dir / "sourcefiles"
        self.mapdir_hc = self.script_dir / "maps"



def FindExOs():
    exec_os = None

    if sys.platform == "win32":
        bits = ct.sizeof(ct.c_void_p)*8
        if bits == 32:
            exec_os = "Win32bit"
        elif bits == 64:
            exec_os = "Win64bit"
        else:
            GM_WS.Warning(
                "Environment was determined to be windows, but it is neither a"
                "32, nor 64 bit version. It appears to be "
                + str(bits) + " bit. Please contact the developers to "
                "solve this."
            )
    elif sys.platform == "darwin":
        exec_os = "MacOS"
    elif sys.platform == "linux":
        exec_os = "Linux"
    else:
        GM_WS.Warning(
            "executing OS not recognised... sys.platform ="
            + str(sys.platform)
            + ". Please contact the developers to solve this. "
        )
        
    return exec_os
