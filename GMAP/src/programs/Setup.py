r"""
Usage:

    GMAP Setup [target directory]
Copies GMAP\sourcefiles and GMAP\maps and places them in the target directory
under the names sourcefiles_copy and maps_copy.

The purpose of Setup is to simplify editing of these files.

Future functions may include a force flag and the abillity to create new
folders.

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
    callcommand : list of str
        This is the user input into the terminal.
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties. Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    """
    Printer.program_state = "running"
    Printer.verbose = 0
    Printer.verbose_logfile = 1

    target = Path(callcommand[1]).resolve()

    target_srcdir = target / "sourcefiles_copy"
    target_mapdir = target / "maps_copy"

    verify_target(target, target_srcdir, target_mapdir, Printer)

    src_dir = Files.sourcedir_hc
    map_dir = Files.mapdir_hc

    shutil.copytree(src_dir, target_srcdir)
    shutil.copytree(map_dir, target_mapdir)

    Printer.print(0, f"Copied folders to {target} succesfully!")


def verify_target(target, target_srcdir, target_mapdir, Printer):
    """Verifies that it is possible to copy the folders to target.

    The target directory should exist and should not contain files named
    sourcefiles_copy or maps_copy. Then the GMAP\\sourcefiles directory
    and the GMAP\\maps directory will be copied into the target
    directory.

    Parameters:
    ----------
    target : :class:'pathlib.WindowsPath' | 'pathlib.PosixPath'
        The object that is the path leading to the target folder.
    target_srcdir : :class:'pathlib.WindowsPath' | 'pathlib.PosixPath'
        The object that is the path that will be the location where the
        sourcefiles folder copy will reside.
    target_mapdir : :class:'pathlib.WindowsPath' | 'pathlib.PosixPath'
        The object that is the path that will be the location where the
        maps folder copy will reside.
    Printer : :class:`GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    """

    if not target.is_dir():
        Printer.warning(
            f"{target} is not a valid directory. Please submit a valid target "
            "target directory.", "Setup_1", True
        )

    if Path(target_srcdir).exists():
        Printer.warning(
            f"The folder {target_srcdir} already exist. Please rename it or "
            "select another target folder.",
            "Setup_2", True
        )

    if Path(target_mapdir).exists():
        Printer.warning(
            f"The folder {target_mapdir} already exist. Please rename it or "
            "select another target folder.",
            "Setup_3", True
        )


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
