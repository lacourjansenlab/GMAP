# standard lib imports
import sys

# my lib imports
import GMAP
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT


def _report_unknown_choice(Printer):
    Printer.warning(
        "\nChoice of program wasn't recognized. Please type the following "
        "for more\ninformation on how to use this package:\n\nGMP\n\n",
        True
    )


def main():
    Files = GM_FH.FileLocations()
    Printer = GM_PT.Printer(Files)
    with open(Files.script_dir / "logo.txt") as lfile:
        logostr = lfile.read()

    Printer.print(1, logostr)

    allhelps = ["help", "h", "-h"]
    callcommand = sys.argv
    if len(callcommand) == 1:
        callcommand.append(allhelps[0])
    if len(callcommand) == 2:
        callcommand.append(allhelps[0])

    choice = callcommand[1]
    subch = callcommand[2]

    if choice.lower() in allhelps:
        if subch.lower() in allhelps:
            Printer.print(GMAP.__doc__)
            Printer.quit_early()
        elif subch in GMAP.alltools:
            modch = getattr(GMAP, subch)
            Printer.print(modch.__doc__)
            Printer.quit_early()
        else:
            _report_unknown_choice(Printer)

    elif choice in GMAP.alltools:
        modch = getattr(GMAP, choice)
        if subch.lower() in allhelps:
            print(modch.__doc__)
        else:
            getattr(modch, choice)(callcommand[1:], Files, Printer)
            # modch.main(callcommand[1:], FILES)
    else:
        _report_unknown_choice(Printer)


if __name__ == "__main__":
    main()
