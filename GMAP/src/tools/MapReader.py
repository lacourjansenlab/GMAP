
import GMAP.src.tools.ParameterParser as GM_PP
from GMAP.src.tools.PrintTools import devprint as dpr


class Map():
    def __init__(self, mapdir):
        self.directory = mapdir
        self.name = mapdir.name

    def find_refpars(self):
        refparfilename = self.directory / "parameters.ref"
        if refparfilename.is_file():
            self.RefPars = GM_PP.RefPars(refparfilename)
        else:
            self.RefPars = None


def scan_mapdirs(mapdirs):
    """
    Given a list of paths (each representing a map directory), create a Map
    object for each map, which will be filled later.
    """

    all_maps = {}
    for direc in mapdirs:
        subdirs = [item for item in [*direc.iterdir()] if item.is_dir()]
        lookfor = ("Singles", "Pairs")

        for subdir in subdirs:
            if subdir.name in lookfor:
                ssdirs = [
                    item for item in [*subdir.iterdir()] if item.is_dir()
                ]

            for ssdir in ssdirs:
                mapp = Map(ssdir)
                all_maps[mapp.name] = mapp
    return all_maps
