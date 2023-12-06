
import sys
import ctypes as ct
from pathlib import Path
import datetime

import GMAP
import GMAP.src.tools.PrintTools as GM_PT


class FileLocations:
    def __init__(self) -> None:
        self.exec_os = FindExOs()
        self.script_dir = Path(GMAP.__file__).parent.resolve()
        self.cwd = Path(".").resolve()
        self.now = datetime.datetime.now()
        self.now_str = self.now.strftime("%Y-%m-%d_%H-%M-%S")

        self.sourcedir_hc = self.script_dir / "sourcefiles"
        self.mapdir_hc = self.script_dir / "maps"
        self.refparfilename_hc = "default_parameters.ref"


def FindExOs():
    """
    Determines with os the system is running on.
    """
    exec_os = None

    if sys.platform == "win32":
        bits = ct.sizeof(ct.c_void_p)*8
        if bits == 32:
            exec_os = "Win32bit"
        elif bits == 64:
            exec_os = "Win64bit"
        else:
            GM_PT.Warning(
                "Environment was determined to be windows, but it is neither a"
                f" 32, nor 64 bit version. It appears to be {bits} bit. Please"
                " contact the developers to solve this.",
                True
            )
    elif sys.platform == "darwin":
        exec_os = "MacOS"
    elif sys.platform == "linux":
        exec_os = "Linux"
    else:
        GM_PT.Warning(
            f"executing OS not recognised... sys.platform = {sys.platform}. "
            "Please contact the developers to solve this. ",
            True
        )

    return exec_os


def get_def_parfile(FILES, cmd_pardict, in_parfile=None, in_pardict={}):
    """
    Given the parameter information on the command line, a new FILES instance,
    and, optionally, an input parameters file and its contents, finds out
    the location of the default parameters file.

    If the user specified anything (either the sourcedir or the name of the
    default parameter file), the program checks that. If nothing is present
    there or if it isn't a file, an error is raised, and the program quits.
    """
    file_is_hc = False
    if "source_directory" in cmd_pardict:
        dirname = FILES.cwd / cmd_pardict["source_directory"][0]
        if "default_parameter_filename" in cmd_pardict:
            name = dirname / cmd_pardict["default_parameter_filename"][0]
        elif "default_parameter_filename" in in_pardict:
            name = dirname / in_pardict["default_parameter_filename"][0]
        else:
            name = dirname / FILES.refparfilename_hc

    elif "default_parameter_filename" in cmd_pardict:
        name = FILES.cwd / cmd_pardict["default_parameter_filename"][0]

    # now, no info in the cmd line, only in files
    elif "source_directory" in in_pardict:
        dirname = in_parfile.parent / in_pardict["source_directory"][0]
        if "default_parameter_filename" in in_pardict:
            name = dirname / in_pardict["default_parameter_filename"][0]
        else:
            name = dirname / FILES.refparfilename_hc

    elif "default_parameter_filename" in in_pardict:
        name = in_parfile / in_pardict["default_parameter_filename"][0]

    # now, no info in input file either - grab default from installation
    else:
        name = FILES.sourcedir_hc / FILES.refparfilename_hc
        file_is_hc = True

    file_found = try_file(name)

    if not file_found:
        GM_PT.Warning(
            f"\nThe requested default parameter file {name} could not be "
            "found, or is not a file. "
            "Please make sure you specified it correctly.\n",
            True
        )

    # We need a file to check if the default file is complete (AIM did this
    # using )
    if file_is_hc:
        check_file_found = file_found
    else:
        name = FILES.sourcedir_hc / FILES.refparfilename_hc
        check_file_found = try_file(name)
        if not check_file_found:
            GM_PT.Warning(
                "\nThe requested default parameter file requires the presence "
                f"of the file {name}, but this file could not be found. "
                "Please make sure you specified it correctly.\n",
                True
            )

    return file_found


def try_file(fname):
    """
    Checks if the given location is a file. If so,
    returns pathlib.Path.resolve(location), otherwise, returns None.
    """
    if fname.is_file():
        return fname.resolve()
    else:
        return None


def check_file_readability(fname):
    try:
        with open(fname) as file:
            for _ in file:
                pass
    except UnicodeDecodeError:
        GM_PT.Warning(
            f"\n The file {fname} is of the wrong type, please make sure "
            "it is a plain text file. ",
            True
        )
