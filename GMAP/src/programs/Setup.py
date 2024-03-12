import shutil
import sys
from GMAP.src.tools.PrintTools import devprint as dpr
import GMAP.src.tools.FileHandler as GM_FH
from pathlib import Path


def main():
    """Copies the maps and src dirs and copies them to a new map.

    Setup copies the maps folder and the src folder and copies them to
    a new folder that is specified by the user with an absolute path.
    src and maps will both go into the same folder.

    Parameters:
    ----------
    target : str
             This is the folder to which the user copies the maps.
    """

    callcommand = sys.argv
    target = callcommand[1]
    # target_path = Path(target)

    Files = GM_FH.FileLocations()

    src_dir = Files.sourcedir_hc
    map_dir = Files.mapdir_hc

    dpr(src_dir)
    dpr(map_dir)

    # if not target_path.exists():
    #     target_path.mkdir()
    dpr("Hello!")
    shutil.copytree(src_dir, target)
    shutil.copytree(map_dir, target)


if __name__ == "__main__":
    main()
