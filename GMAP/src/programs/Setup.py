r"""
Usage:

    GMAP Setup [target directory]
Copies GMAP\sourcefiles and GMAP\maps and places them in the target directory
under the names sourcefiles_copy and maps_copy.

The purpose of Setup is to simplify editing of these files.

For more information, check the manual on N/A.
"""

# standard lib imports
import shutil
import sys
from pathlib import Path

# local imports
# from GMAP.src.tools.PrintTools import devprint as dpr
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT


def Setup(callcommand, Files, Printer):
    """Copies the maps and src dirs and copies them to a new map.

    Setup copies the maps folder and the src folder and copies them to
    a new folder that is specified by the user with an absolute path.
    src and maps will both go into the same folder.

    Parameters:
    ----------
    target : str
             This is the folder to which the user copies the maps.
    """

    target = callcommand[1]

    if not Path(target).is_dir():
        Printer.warning(
            f"{target} is not a valid directory, please submit a valid target "
            "target directory.", "SU_Setup_1", True
        )

    target_srcdir = target + "\\sourcefiles_copy"
    target_mapdir = target + "\\maps_copy"

    if Path(target_srcdir).exists():
        Printer.warning(
            f"The folder {target_srcdir} already exist. Please rename it or "
            "select another target folder.",
            "SU_Setup_2", True
        )
    if Path(target_srcdir).exists():
        Printer.warning(
            f"The folder {target_mapdir} already exist. Please rename it or "
            "select another target folder.",
            "SU_Setup_3", True
        )

    src_dir = Files.sourcedir_hc
    map_dir = Files.mapdir_hc

    shutil.copytree(src_dir, target_srcdir)
    shutil.copytree(map_dir, target_mapdir)


def main():
    """Fakes behaviour as if called from __main__.

    During normal operation (user types 'GMAP ...' in the command line),
    this function should never be called. This function replicates the
    'normal' behaviour so partial tests are possible.
    """

    callcommand = sys.argv
    if len(callcommand) == 1:
        print(__doc__)
    else:
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        Setup(callcommand, Files, Printer)


if __name__ == "__main__":
    main()
