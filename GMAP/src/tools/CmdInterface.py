
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
    Files.save_callcommand(callcommand)

    # Deduce whether we should be running in safe mode / dark mode.
    # These 'special' flags should be caught separately to avoid issues like
    # 'GMAP -nodm' throwing an error.
    all_args = calldict(callcommand)
    safe_mode, dark_mode = get_safe_dark(all_args)
    Printer().setenv(safe_mode, dark_mode)

    print_logo(Files)  # Print the GMAP logo + base text below

    # get first entry form args dict -> the GMAP call (before first parameter)
    gmapcall, extras = next(iter(all_args.items()))
    call = [gmapcall] + extras

    allhelps = ["help", "h", "-h"]
    if len(call) == 1:
        call.append(allhelps[0])
    if len(call) == 2:
        call.append(allhelps[0])

    choice = call[1]
    subch = call[2]

    if choice.lower() in allhelps:
        cmd_to_help(allhelps, subch)

    elif choice in GMAP.alltools:
        cmd_to_tools(Files, allhelps, callcommand, choice, subch)

    else:
        _report_unknown_choice()


def calldict(callcommand):
    """Create a dict off of the call command.

    Naive logic leads the keys to be a string starting with '-', and the
    values to be the choices. Values can be empty lists. The first entry
    is different - its the program call!

    Parameters
    ----------
    callcommand : list of str
        The command used to invoke the program

    Returns
    -------
    all_args : dict
        A dictionary representation of the callcommand
    """

    # First, split args into dict. Here, the parameter name becomes the key
    # (except for the first one, that's program name, but dicts are ordered!)
    # and it's choice(s) become the value.
    current_arg = [callcommand[0]]
    all_args = {}
    for item in callcommand[1:]:
        if item.startswith("-"):
            # lets hope that doubles will never appear (they shouldn't, AFAIK)
            all_args[current_arg[0]] = current_arg[1:]
            current_arg = [item]
        else:
            current_arg.append(item)
    else:
        all_args[current_arg[0]] = current_arg[1:]

    return all_args


def get_safe_dark(all_args):
    """Determine whether the program has been requested to run in safe
    or dark mode

    Parameters
    ----------
    all_args : dict
        A dictionary representation of the callcommand

    Returns
    -------
    safe_mode : bool
        Indicates whether the program should run in safe mode (no fancy
        outputs, currently only disables colored output)
    dark_mode : bool
        Indicates whether the program should run in dark mode (colors
        chosen for a dark background)
    """

    safe_mode = False
    dark_mode = True
    # See if any urgent print-related settings are given.
    for parameter, choice in all_args.items():
        choice_lower = [item.lower() for item in choice]

        # If the user requests to run in safe mode
        if parameter.lower() in ("-safe", "--safe_mode"):
            # asks safe mode, and doesn't explicitly turn it off
            if not any(item in choice_lower for item in ("f", "false")):
                safe_mode = True
            else:
                safe_mode = False

        # if the user asks to NOT use dark mode
        if (
            (  # asks nodark, and doesn't explicity turn nodark off
                parameter.lower() in ("-nodm", "--nodark_mode")
                and not (any(item in choice_lower for item in ("f", "false")))
            ) or (  # asks dark, but explicitly turns dark off
                parameter.lower() in ("-dm", "--dark_mode")
                and (any(item in choice_lower for item in ("f", "false")))
            )
        ):
            dark_mode = False
        elif parameter.lower() in (
            "-nodm", "--nodark_mode", "-dm", "--dark_mode"
        ):
            dark_mode = True
    return safe_mode, dark_mode


def print_logo(Files):
    """Prints the program logo and corresponding text.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties. Has to be updated after RunPars is finalized.
    """

    # Now, load/print logo!
    with open(Files.script_dir / "logo.txt") as lfile:
        logostr = lfile.read()

    # convert abbr to actual color markers
    colors = Printer().colors
    logostr = logostr.replace("P", colors.pink_hc)
    logostr = logostr.replace("G", colors.green_hc)
    logostr += colors.clear

    Printer().print(1, "\n\n" + logostr + "\n")
    Printer().print(
        1,
        "\nFor the most up-to-date version of GMAP, reporting bugs/issues, "
        "suggesting improvements for the program, questions, or any other "
        "kind of feedback, go to github.com/Kimvana/GMAP\n"
    )

    Printer().print(
        1,
        f"\nRunning the following job:\n{Files.callcommand}"
    )


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
        Contains all currently known paths and other file-related
        properties. Has to be updated after RunPars is finalized.
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
