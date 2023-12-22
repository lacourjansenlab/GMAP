
import GMAP.src.tools.ParameterParser as GM_PP
from GMAP.src.tools.PrintTools import devprint as dpr
dpr("", end="")


class Map():
    """Contains all information regarding a single map.

    In this context, a map is as defined in the computational spectroscopy
    community - a way of estimating the properties of a functional group. It
    is not a python object.

    .. note ::
        Users of the program are probably looking for the
        :ref:`adding a new map<UserGuide_page_adding_map>` page.

    Parameters
    ----------
    mapdir : pathlib.Path
        The absolute path to the directory on the users system that
        contains the files for this specific map

    Attributes
    ----------
    directory : pathlib.Path
        The directory where the files defining this map can be found.
    name : str
        The name of this map. Often indicates the functional group modelled.
    RefPars : :class:`~GMAP.src.tools.ParameterParser.RefPars`
        The parameters defined and used by this map. Does not contain
        parameters used by this map, but defined elsewhere.

    Notes
    -----

    .. seealso ::
        :class:`~GMAP.src.tools.ParameterParser.RefPars`

    """

    def __init__(self, mapdir):
        self.directory = mapdir
        self.name = mapdir.name

    def find_refpars(self):
        """Creates a RefPars object for the map-specific parameters

        A map is not required to have any specific parameters. But if it
        has them, they are supposed to be in a reference parameter file
        of the same format as the one of GEM itself.

        Looks inside `self.directory` for a file of the name `parameters.ref`,
        If found, the resulting
        :class:`~GMAP.src.tools.ParameterParser.RefPars` object is stored as
        the `self.RefPars` attribute.

        """
        refparfilename = self.directory / "parameters.ref"
        if refparfilename.is_file():
            self.RefPars = GM_PP.RefPars(refparfilename)
        else:
            self.RefPars = None


def scan_mapdirs(mapdirs):
    """ gives a list of newly-generated Map objects

    Given a list of paths (each representing a map directory), create a Map
    object for each map found, which will be filled later.

    Parameters
    ----------
    mapdirs : list of pathlib.Path
        A list of directories which should be scanned for maps. This object
        is created by :func:`~GMAP.src.tools.ParameterParser.find_mapdir`.

    Returns
    -------
    all_maps : list of :class:`Map`

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
