# standard lib imports
import sys

# local imports
import GMAP
# from GMAP.src import programs
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT
# from GMAP.src.tools.PrintTools import devprint as dpr


def _report_unknown_choice(Printer):
    """Wrapper for warning call SU_GM_1."""
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
        if subch.lower() in allhelps:
            Printer.print(0, GMAP.__doc__)
            Printer.quit_early()
        elif subch in GMAP.alltools:
            modch = getattr(GMAP, subch)
            Printer.print(0, modch.__doc__)
            Printer.quit_early()
        else:
            _report_unknown_choice(Printer)

    # else:
    #     dpr(dir(programs))
    #     dpr(choice in dir(programs))
    #     modch = getattr(
    #         programs, choice, _report_unknown_choice(Printer))
    #     if subch.lower() in allhelps:
    #         Printer.print(0, modch.__doc__)
    #     else:
    #         getattr(modch, choice)(callcommand[1:], Files, Printer)
    #         # modch.main(callcommand[1:], FILES)

    elif choice in GMAP.alltools:
        modch = getattr(GMAP, choice)
        if subch.lower() in allhelps:
            Printer.print(0, modch.__doc__)
        else:
            getattr(modch, choice)(callcommand[1:], Files, Printer)
            # modch.main(callcommand[1:], FILES)
    else:
        _report_unknown_choice(Printer)


def main(callcommand):
    cmd_interface(callcommand)


if __name__ == "__main__":
    callcommand = sys.argv
    main(callcommand)
