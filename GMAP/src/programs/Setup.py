import pathlib as Path
import sys
from GMAP.src.tools.PrintTools import devprint as dpr


def setup(target):
    """Copies the maps and src dirs and copies them to a new map.

    Setup copies the maps folder and the src folder and copies them to
    a new folder that is specified by the user with an absolute path.
    src and maps will both go into the same folder.

    Parameters:
    ----------
    target : str
             This is the folder to which the user copies the maps.
    """

    setup = Path(".")
    GMAP_dir = setup.parent[1]

    dpr(setup)


if __name__ == "__main__":
    # target = sys.argv[2]
    setup(target="")