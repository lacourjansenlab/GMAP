# Standard library imports
import sys
# Local imports
from GMAP import mainy


def main():
    callcommand = sys.argv
    mainy.cmd_interface(callcommand)


if __name__ == "__main__":
    callcommand = sys.argv
    mainy.cmd_interface(callcommand)
