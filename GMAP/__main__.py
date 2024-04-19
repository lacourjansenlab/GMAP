# Standard library imports
import sys
# Local imports
from GMAP.src.tools import CmdInterface as CM_IF


def main():
    callcommand = sys.argv
    CM_IF.cmd_interface(callcommand)


if __name__ == "__main__":
    callcommand = sys.argv
    CM_IF.cmd_interface(callcommand)
