
# local imports
import GMAP.src.tools.ParameterParser as GM_PP
from GMAP.src.tools.PrintTools import devprint as dpr
dpr("", end="")  # to disable error of dpr unused


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
        self.type = mapdir.parent.name

    def find_refpars(self, Printer):
        """Creates a RefPars object for the map-specific parameters

        A map is not required to have any specific parameters. But if it
        has them, they are supposed to be in a reference parameter file
        of the same format as the one of GEM itself.

        Looks inside `self.directory` for a file of the name `parameters.ref`,
        If found, the resulting
        :class:`~GMAP.src.tools.ParameterParser.RefPars` object is stored as
        the `self.RefPars` attribute.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        refparfilename = self.directory / "parameters.ref"
        if refparfilename.is_file():
            self.RefPars = GM_PP.RefPars(Printer, refparfilename)
        else:
            self.RefPars = None

    def find_rawpars(self, Printer, CmdPars, InPars, DefPars):
        """Creates CmdPars, InPars and DefPars objects for this map instance.

        Searches through the provided CmdPars, InPars and DefPars to see
        whether there are any map-type parameters belonging to this map. If
        so, they are taken from there, put in the map-specific instances for
        CmdPars, InPars and DefPars, and then removed from the source (as the
        source will be checked for emtiness at the end).

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        CmdPars : :class:`~GMAP.src.tools.ParameterParser.RawPars`
            The object storing all parameters provided on the command line.
        InPars : :class:`~GMAP.src.tools.ParameterParser.RawPars`
            The object storing all parameters provided in the input parameter
            file.
        DefPars : :class:`~GMAP.src.tools.ParameterParser.RawPars`
            The object storing all parameters provided in the default parameter
            file. If no such file was provided, RefPars is used instead.
        """

        # for each parameter source, extract all choices belonging to this
        # map, and make a RawPars object with those choices. Make sure
        # to empty the not_found array, so each source can be checked to make
        # sure all parameters are understood.

        # first, CmdPars
        map_pars = self.extract_notfound(Printer, CmdPars)
        self.CmdPars = GM_PP.RawPars.from_dict(
            Printer, "Cmdline", map_pars, self.RefPars, False
        )
        for parname in map_pars.keys():
            del CmdPars.not_found[self.name + "." + parname]

        # InPars
        map_pars = self.extract_notfound(Printer, InPars)
        self.InPars = GM_PP.RawPars.from_dict(
            Printer, InPars.fname, map_pars, self.RefPars, False
        )
        for parname in map_pars.keys():
            del InPars.not_found[self.name + "." + parname]

        # DefPars
        if type(DefPars) is GM_PP.RawPars:
            map_pars = self.extract_notfound(Printer, DefPars)
            self.DefPars = GM_PP.RawPars.from_dict(
                Printer, DefPars.fname, map_pars, self.RefPars, True
            )
            for parname in map_pars.keys():
                del DefPars.not_found[self.name + "." + parname]
        else:
            self.DefPars = GM_PP.RawPars.create_empty()

    def extract_notfound(self, Printer, RawParInst):
        """Find all parameters of this map in the given RawPars instance.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        RawParInst : :class:`~GMAP.src.tools.ParameterParser.RawPars`
            The instance through which to look for parameters that belong
            to this map.

        Returns
        -------
        map_pars : dict
            The 'slice' of the RawParInst.not_found dict that contains
            parameters starting with 'self.name'.
        """
        map_pars = {}
        for parname, choice in RawParInst.not_found.items():
            parnamelist = parname.split(".")
            if len(parnamelist) != 2:
                Printer.warning(
                    "Names of map-specific parameters cannot contain a '.'.",
                    "SU_MR_1", True
                )
            if parnamelist[0] != self.name:
                continue
            map_pars[parnamelist[1]] = choice

        return map_pars

    def find_runpars(self, Files, Printer, RunPars):
        """Create a RunPars instance for this map.

        Just like the main code, a map has a RefPars, DefPars, Inpars and
        CmdPars instance, that all need to be combined into a RunPars
        instance to be used further in the code.

        Parameters
        ----------
        Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
            Contains all currently known paths and other file-related
            properties.
            Has to be updated after RunPars is finalized.
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        """

        if self.RefPars:
            self.RunPars = GM_PP.RunPars(
                Files, Printer, self.CmdPars, self.InPars, self.DefPars,
                self.RefPars, False, MainRunPars=RunPars
            )
        else:
            self.RunPars = None


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
