# standard lib imports
import sys

# my lib imports
import GMAP
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.WarnSys as GM_WS


def _report_unknown_choice():
    GM_WS.Warning(
        "\nChoice of program wasn't recognized. Please type the following "
        "for more\ninformation on how to use this package:\n\nGMP\n\n",
        True
    )


def main():
    FILES = GM_FH.FileLocations()
    with open(FILES.script_dir / "logo.txt") as lfile:
        logostr = lfile.read()

    print(logostr)

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
            print(GMAP.__doc__)
        elif subch in GMAP.alltools:
            modch = getattr(GMAP, subch)
            print(modch.__doc__)
        else:
            _report_unknown_choice()

    elif choice in GMAP.alltools:
        modch = getattr(GMAP, choice)
        if subch.lower() in allhelps:
            print(modch.__doc__)
        else:
            getattr(modch, choice)(callcommand[1:], FILES)
            # modch.main(callcommand[1:], FILES)
    else:
        _report_unknown_choice()


if __name__ == "__main__":
    main()
