# standard lib imports
import sys

# my lib imports
import GMAP


def _report_unknown_choice():
    print(
            "Choice of program wasn't recognized. Please type the following "
            "for more information on how to use this package:\nGMP"
        )


def main():
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
            modch.main(callcommand[1:])
    
    else:
        _report_unknown_choice()


if __name__ == "__main__":
    main()
