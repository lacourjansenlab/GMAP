
import sys

# local imports
import GMAP
# from GMAP.src import programs
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT
# from GMAP.src.tools.PrintTools import devprint as dpr


def _report_unknown_choice(Printer):
    """Wrapper for warning call SU_GM_1.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    """
    Printer.warning(
        "\nChoice of program wasn't recognized. Please type the following "
        "for more\ninformation on how to use this package:\n\nGMAP\n\n",
        "SU_GM_1", True
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

    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)
    with open(Files.script_dir / "logo.txt") as lfile:
        logostr = lfile.read()

    Printer.print(1, logostr)

    allhelps = ["help", "h", "-h"]

    if len(callcommand) == 1:
        callcommand.append(allhelps[0])
    if len(callcommand) == 2:
        callcommand.append(allhelps[0])

    choice = callcommand[1]
    subch = callcommand[2]

    if choice.lower() in allhelps:
        cmd_to_help(Printer, allhelps, subch)

    elif choice in GMAP.alltools:
        cmd_to_tools(Files, Printer, allhelps, callcommand, choice, subch)

    else:
        _report_unknown_choice(Printer)


def cmd_to_help(Printer, allhelps, subch):
    """Determines what help to print.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    allhelps : list of str
        All items in this list are strings the user might use to get
        help to be printed.
    subch : str
        Used by user to indicate intent.
    """

    if subch.lower() in allhelps:
        Printer.print(0, GMAP.__doc__)
        Printer.quit_early()
    elif subch in GMAP.alltools:
        modch = getattr(GMAP, subch)
        Printer.print(0, modch.__doc__)
        Printer.quit_early()
    else:
        _report_unknown_choice(Printer)


def cmd_to_tools(Files, Printer, allhelps, callcommand, choice, subch):
    """Determines which tool to invoke.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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

    modch = getattr(GMAP, choice)
    if subch.lower() in allhelps:
        Printer.print(0, modch.__doc__)
    else:
        getattr(modch, choice)(callcommand[1:], Files, Printer)


def main():
    callcommand = sys.argv
    cmd_interface(callcommand)
