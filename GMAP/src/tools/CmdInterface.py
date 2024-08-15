
import sys

# local imports
import GMAP
# from GMAP.src import programs
from GMAP.src.tools.Exceptions import GmapAttributeError
import GMAP.src.tools.FileHandler as GM_FH
from GMAP.src.tools.PrintTools import Printer
# from GMAP.src.tools.PrintTools import devprint as dpr


def _report_unknown_choice():
    """Wrapper for warning call SU_GM_1."""

    Printer().warning(
        "\nChoice of program wasn't recognized. Please type the following "
        "for more\ninformation on how to use this package:\n\nGMAP\n\n",
        "SU_GM_1", True, GMAPerrclass=GmapAttributeError
    )


def cmd_interface(callcommand):
    """Directs the user to the correct program.

    Interpret what program the user would like to use, and direct the
    order to it. Or, when requested, print the help of GMAP or that of
    the specific tool instead.

    Parameters
    ----------
    callcommand : list of str
        Basically, the return value of sys.argv. What the user has
        actually requested from the program.
    """

    # The very first initialization the program needs/assumes. Also initializes
    # the printing tool (Printer()).
    Files = GM_FH.FileLocations()

    # Deduce whether we should be running in safe mode / dark mode.
    final_callcommand = []
    safe_mode = False
    dark_mode = True
    for item in callcommand:
        match item.lower():
            case "-safe" | "--safe_mode":
                safe_mode = True
            case "-nodm" | "--nodark_mode":
                dark_mode = False
            case "-dm" | "--dark_mode":
                dark_mode = True
            case _:
                pass
        final_callcommand.append(item)
    callcommand = final_callcommand
    Printer().setenv(safe_mode, dark_mode)
    colors = Printer().colors

    # Now, load/print logo!
    with open(Files.script_dir / "logo.txt") as lfile:
        logostr = lfile.read()
    # convert abbr to actual color markers
    # logostr = logostr.replace("P", "\033[38;2;229;140;140m")
    # logostr = logostr.replace("G", "\033[38;2;140;229;140m")
    # logostr = logostr.replace("P", "\033[38;2;240;96;112m")
    # logostr = logostr.replace("G", "\033[38;2;128;240;112m")
    logostr = logostr.replace("P", colors.pink)
    logostr = logostr.replace("G", colors.green)
    logostr += "\033[0m"

    Printer().print(1, "\n\n" + logostr + "\n")
    Printer().print(
        1,
        "\nFor the most up-to-date version of GMAP, reporting bugs/issues, "
        "suggesting improvements for the program, questions, or any other "
        "kind of feedback, go to github.com/Kimvana/GMAP\n"
    )

    allhelps = ["help", "h", "-h"]
    if len(callcommand) == 1:
        callcommand.append(allhelps[0])
    if len(callcommand) == 2:
        callcommand.append(allhelps[0])

    choice = callcommand[1]
    subch = callcommand[2]

    if choice.lower() in allhelps:
        cmd_to_help(allhelps, subch)

    elif choice in GMAP.alltools:
        cmd_to_tools(Files, allhelps, callcommand, choice, subch)

    else:
        _report_unknown_choice()


def cmd_to_help(allhelps, subch):
    """Determines what help to print.

    Parameters
    ----------
    allhelps : list of str
        All items in this list are strings the user might use to get
        help to be printed.
    subch : str
        Used by user to indicate intent.
    """

    printer = Printer()
    if subch.lower() in allhelps:
        printer.print(0, GMAP.__doc__)
        printer.quit_early()
    elif subch in GMAP.alltools:
        modch = getattr(GMAP, subch)
        printer.print(0, modch.__doc__)
        printer.quit_early()
    else:
        _report_unknown_choice()


def cmd_to_tools(Files, allhelps, callcommand, choice, subch):
    """Determines which tool to invoke.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    allhelps : list of str
        All items in this list are strings the user might use to get
        help to be printed.
    callcommand : list of str
        Basically, the return value of sys.argv. What the user has
        actually requested from the program.
    choice : str
        Used by user to indicate intent.
    subch : str
        Used by user to indicate intent.
    """

    printer = Printer()
    modch = getattr(GMAP, choice)
    if subch.lower() in allhelps:
        printer.print(0, modch.__doc__)
        printer.quit_early()
    else:
        getattr(modch, choice)(callcommand[1:], Files)


def main():
    """The entrypoint for the entire GMAP program. GMAP aliases here.

    Collects the command line instructions, and passes them to the
    function interpreting these.
    """

    callcommand = sys.argv
    cmd_interface(callcommand)
