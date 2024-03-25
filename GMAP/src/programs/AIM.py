r"""

Usage:

    GMAP AIM
    GMAP AIM help
prints this help

    GMAP AIM demo
Launches AIM in demo-mode. Performs a basic calculation to demonstrate basic
use and to verify the program is installed correctly.

    GMAP AIM run [name of input file]
Performs a run of AIM using the parameters specified in the included file.


The purpose of AIM is to take an MD trajectory and compute the time-dependent
Hamiltonian to be used in infrared spectral calculations. Natively, only
(protein) amide groups are supported, but AIM allows the user to specify their
own oscillating groups.

For more information, check the manual on github.com/Kimvana/AIM.
"""


# standard lib imports
import sys

# imports from this package
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT


def AIM(callcommand, Files, Printer):
    GM_PT.devprint("entered main of AIM - yet to be constructed")


def main(callcommand):
    if len(callcommand) == 1:
        print(__doc__)
    else:
        Files = GM_FH.FileLocations()
        Printer = GM_PT.Printer(Files)
        AIM(callcommand, Files, Printer)


if __name__ == "__main__":
    callcommand = sys.argv
    main(callcommand)
