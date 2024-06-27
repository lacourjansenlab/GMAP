
# standard library imports
import importlib
import sys

# 3rd party lib imports
import numpy as np

# local imports
import GMAP.src.tools.DefaultMapFunctions as GM_DMF
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.ParameterParser as GM_PP


class Map():
    """Contains all information regarding a single map. Base to build upon.

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
    corepath : pathlib.Path
        The path to the core.txt file within self.directory.
    name : str
        The name of this map. Often indicates the functional group
        modelled.
    RefPars : :class:`~GMAP.src.tools.ParameterParser.RefPars`
        The parameters defined and used by this map. Does not contain
        parameters used by this map, but defined elsewhere.
    success : bool
        Whether the map has (thusfar) been read successfully. If a
        problem occurs, a warning is in order, but the program does not
        have to quit - if the map isn't used, we don't care. Later, when
        looking at the requested maps, if an unsuccessful map is
        requested, we can throw an error and quit!
    avail_files : list of `pathlib.Path`
        All files that are in the same map directory as this map. These
        are the files available for appending using 'add_corefile'
    type : str
        The type of this map. Either 'Singles' or 'Doubles'
    CmdPars : :class:`~GMAP.src.tools.ParameterParser.RawPars`
        The object storing all parameters provided on the command line
        that belong to this map.
    InPars : :class:`~GMAP.src.tools.ParameterParser.RawPars`
        The object storing all parameters provided in the input parameter
        file that belong to this map.
    DefPars : :class:`~GMAP.src.tools.ParameterParser.RawPars`
        The object storing all parameters provided in the default parameter
        file that belong to this map. If no such file was provided, an
        empty instance is used instead.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The RunPars instance containing all the basic run-defining
        parameters that belong to this map.
    code : module
        The code that goes along with this map, if present. If not, an
        empty module will be filled with default functions. If it is
        present, any missing functions will be added from the default
        functions.
    rawcore : dict of str: list of str pairs
        The contents of core.txt, after very simple parsing
    Core : :class:`Core`
        The contents of core.txt, fully parsed and ready to use.

    Notes
    -----

    .. seealso ::
        :class:`~GMAP.src.tools.ParameterParser.RefPars`

    """

    def __init__(self, mapdir, avail_files):
        self.directory = mapdir
        self.name = mapdir.name
        self.type = mapdir.parent.name
        self.success = True
        self.avail_files = avail_files

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
            self.RefPars = GM_PP.RefPars(Printer, refparfilename, False)
        else:
            # self.RefPars = None
            with open(refparfilename, "w") as _:
                pass
            self.RefPars = GM_PP.RefPars(Printer, refparfilename, False)

    def find_rawpars(self, Printer, CmdPars, InPars, DefPars):
        """Creates CmdPars, InPars and DefPars objects for this map instance.

        Searches through the provided CmdPars, InPars and DefPars to see
        whether there are any map-type parameters belonging to this map. If
        so, they are taken from there, put in the map-specific instances for
        CmdPars, InPars and DefPars, and then removed from the source (as the
        source will be checked for emptiness at the end).

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
            self.DefPars = GM_PP.RawPars.create_empty(Printer)

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
                    "\nNames of map-specific parameters cannot contain a '.'.",
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

    def extract_code(self, Printer):
        """Imports the main.py file and returns its module instance.

        Taking ``import numpy as np`` as example, ``np`` is the module
        instance.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.

        Returns
        -------
        module : module
            The contents of the file as a module.
        """
        modpath = self.directory / "main.py"
        if not modpath.is_file():
            return None

        modname = self.name + "_code"

        try:
            spec = importlib.util.spec_from_file_location(modname, modpath)
            module = importlib.util.module_from_spec(spec)
            sys.modules[modname] = module
            spec.loader.exec_module(module)
        except Exception as ex:
            Printer.warning(
                "\nA problem occured while reading in the code for the map "
                f"{self.name}, defined at "
                f"{str(self.directory.resolve())}. "
                "Please consult the information of this map, or contact the "
                "developer of this map.",
                "MI_MR_1", False, ex
            )
            return None
        return module

    def complete_code(self, funcnames, kwargslist=None):
        r"""Adds missing functions to the code of this map.

        A map can have many different funtions called by the program to
        allow for fully custom behaviour. To make it easier to call them
        later, any that do not exist yet, will have a default function
        added in. For some, that may be a useless shell (just pass),
        for others, there will be an actual default calculation.

        Parameters
        ----------
        funcnames : tuple of str
            The functions that should be added in (without the GM\_
            prefix)
        kwargslist : tuple of dicts or NoneType, default=None
            If any of the requested functions (in funcnames) require
            arguments, they should be supplied as kwargs in a dict.
            If any function needs them, the kwargs for all must be
            provided, this tuple must have the same length as funcnames.
        """

        if not kwargslist:
            kwargslist = [{}] * len(funcnames)

        for funcname, kwargs in zip(funcnames, kwargslist):
            if not hasattr(self.code, "GM_" + funcname):
                setattr(
                    self.code, "GM_" + funcname,
                    getattr(GM_DMF, "get_" + funcname)(**kwargs)
                )

    def append_core(self, Printer):
        """Interprets the choice in core.txt for add_corefile.

        Appends the contents of the requested file(s). If added files
        rely on files themselves, those dependencies are also added.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        all_to_add = [
            file for files in self.rawcore.get("add_corefile", [])
            for file in files
        ]
        self.rawcore["add_corefile"] = []
        # as long as things should be added - this allows imports to rely
        # on imports themselves.
        while all_to_add:
            for name in all_to_add:
                # we only want the first occurence of this file
                fpaths = [
                    file for file in self.avail_files if file.name == name
                ]

                try:
                    self.rawcore = self.parse_core(
                        Printer, fpaths[0], self.rawcore
                    )
                    if not self.rawcore:
                        self.success = False
                        return
                except IndexError as ex:
                    Printer.warning(
                        f"\nA file of the name {name} was requested to be "
                        "added "
                        f"to the file {self.corepath}. However, no file of "
                        "that name could be found",
                        "MI_MR_6", False, exception=ex
                    )
                    self.success = False
                    return
                except Exception as ex:
                    Printer.warning(
                        f"\nThe file {fpaths[0]} was requested to be added to "
                        f"the file {self.corepath}. However, an issue "
                        "occured, so it cannot be added.",
                        "MI_MR_5", False, exception=ex
                    )
                    self.success = False
                    return
            all_to_add = [
                file for files in self.rawcore.get("add_corefile", [])
                for file in files
            ]
            self.rawcore["add_corefile"] = []

    def find_core(self, Printer):
        """Sees if the map core exists, and extracts all its information.

        The validity is not confirmed in any way - that will come later.
        First, just extracting it, so that the GM_adjust_map_core_raw
        function of the map may change it.

        The returned dict contains the first word of a line as the key,
        and the rest of the line split into a list as the value.
        Parameters that are allowed to occur on multiple lines have
        a list of all lines split into lists as their value instead.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.

        Returns
        -------
        core_contents : dict of str - list of str pairs
            The contents of the file, not yet analyzed for validity.
        """

        filepath = (self.directory / "core.txt").resolve()
        if not filepath.is_file():
            # This file is mandatory for singles maps
            if isinstance(self, SingleMap):
                Printer.warning(
                    f"\nCould not find the file {filepath}. This file is "
                    "required for the map to function. Please consult the "
                    "information of this map, or contact the developer of "
                    "this map.",
                    "MI_MR_2", False
                )
                self.success = False
                return None

            # This file is optional for pairs maps
            elif isinstance(self, PairMap):
                return {}

        if not GM_FH.check_file_readability(Printer, filepath, doquit=False):
            self.success = False
            return None

        self.corepath = filepath

        core_contents = self.parse_core(Printer, filepath)
        if not core_contents:
            self.success = False
            return None

        return core_contents

    @staticmethod
    def parse_core(Printer, filepath, file_contents=None):
        """Actually retrieves the information from core.txt.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        filepath : pathlib.Path
            The location at which the file is stored.
        file_contents : dict or NoneType, default=None
            Any contents belonging to core.txt that have already been
            found. This is applicable when using the 'append_core'
            keyword, which in spirit concatenates file contents.

        Returns
        -------
        core_contents : dict of str - list of str pairs
            The contents of the file, not yet analyzed for validity.
        """

        if file_contents is None:
            file_contents = {}

        with open(filepath) as fhand:
            for line in fhand:
                line = SingleMap.cleanline(line)
                if line:
                    file_contents = SingleMap.parse_core_line(
                        Printer, line, file_contents, filepath
                    )
                    if not file_contents:
                        return None
        return file_contents

    @staticmethod
    def cleanline(line):
        """Cleans up a line from core.txt for parsing

        If there is a '#' on the line, ignore it and everything after it.
        Interpret multiple whitespaces back-to-back as a single one.

        Parameters
        ----------
        line : str
            The line as directly read from the file.

        Returns
        -------
        line : list of str
            The 'words' on the line. Each item is anything but whitespace.
        """
        line = GM_PP.cleanline(line)
        line = line.strip().split()
        line = [x for x in line if x]
        return line

    @staticmethod
    def parse_core_line(Printer, line, file_contents, filepath):
        """Parses a single line from core.txt

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        line : list of str
            A cleaned version of the line. Already split into a list, all
            whitespaces removed.
        file_contents : dict of str - list of str pairs
            The contents of the file, not yet analyzed for validity.
            Here, it is still incomplete, being built by this function
            each iteration.
        filepath : pathlib.Path
            The location at which the file is stored.

        Returns
        -------
        file_contents : dict of str - list of str pairs
            The contents of the file, not yet analyzed for validity.
            Here, it is still incomplete, being built by this function
            each iteration.
        """

        keyword = line[0]
        choice = line[1:]

        if not choice:
            Printer.warning(
                f"\nNo choice detected for parameter {keyword} in the file "
                f"{filepath}. This issue must be fixed before this map can "
                "be used.",
                "MI_MR_3", False
            )
            return None
        if keyword in (
            "functional_group", "add_corefile", "influencer_group",
            "valid_combinations"
        ):
            if keyword in file_contents:
                file_contents[keyword].append(choice)
            else:
                file_contents[keyword] = [choice]
            return file_contents
        elif keyword not in file_contents:
            file_contents[keyword] = choice
            return file_contents
        else:
            Printer.warning(
                f"\nThe parameter {keyword} appeared more than once in "
                "the file "
                f"{filepath}. It may only occur once. This issue must be "
                "fixed before this map can be used.",
                "MI_MR_4", False
            )
            return None


class SingleMap(Map):
    def initialize(self, Files, Printer):
        """Initializes the map.

        Initializing is a multi-step process:

        - If there is a main.py file, read/extract it.
        - If any of GM_adjust_[RunPars/map_core_raw/oscillators] are
          missing, add the default for them.
        - Run GM_adjust_RunPars
        - Find the core.txt file, parse to rawcore. Supplement any
          files, if requested.
        - Run GM_adjust_map_core_raw
        - Parse the final choice of rawcore to Core
        - If not present in self.code, create functions for
          GM_calculate_dipole and GM_get_rotation matrix based on core.

        Parameters
        ----------
        Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
            Contains all currently known paths and other file-related
            properties.
            Has to be updated after RunPars is finalized.
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        self.code = self.extract_code(Printer)
        if not self.code:
            self.code = GM_DMF.NewModule()

        # not all code can be added in yet - we need to make sure that
        # we have adjust_RunPars and adjust_map_core_raw, as they might
        # influence core.txt in ways that influence the functions
        # defined later.
        self.complete_code((
            "adjust_RunPars",
            "adjust_map_core_raw",
            "adjust_oscillators"
        ))
        self.code.GM_adjust_RunPars(Files, Printer, self)

        # simple parse of core.txt
        self.rawcore = self.find_core(Printer)
        if not self.success:
            return

        # add extra corefiles to the main core
        self.append_core(Printer)
        if not self.success:
            return

        # allow the contents of core.txt to be changed
        self.code.GM_adjust_map_core_raw(Files, Printer, self)

        self.Core = SingleCore(Printer, self)
        if not self.Core.success:
            self.success = False
            return

        # adding GM_get_dipole_dir and GM_get_rotation_matrix to self.code.
        self.code_add_builds(Printer)
        if not self.success:
            return

        self.complete_code(("get_VEG_ref",), ({
            "map_": self,
            "Printer": Printer
        },))

        self.complete_code(
            ("calculate_dipole", "calculate_frequency"),
            ({"map_": self}, {"map_": self})
        )

        # Add in the remaining code
        self.complete_code((
            "get_dipole_mag",
            "str_osc",
            "post_init",
            "pre_run",
            "pre_frame",
            "post_frame",
            "post_run"
        ))

    def code_add_builds(self, Printer):
        """Add functions that depend on lines in core.txt.

        These functions require that core.txt is checked for certain
        keywords. If they are not present, self.success is set to false,
        and this function is left prematurely.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        # build remaining functions (i.e. do something with the contents
        # of core.txt)
        functs_to_build = [
            "get_dipole_dir"
        ]
        kwargs_for_build = [{
            "map_": self,
            "Printer": Printer
        }]

        # If the code doesn't contain a function for getting the dipole, make
        # sure the two necessary keywords are there.
        if not hasattr(self.code, "get_dipole_dir"):
            if not all(
                keyword in self.rawcore for keyword in ("r_vec", "r_pos")
            ):
                Printer.warning(
                    f"\nThe file {self.corepath} does not contain a "
                    "definition of "
                    "r_vec and/or r_pos. These two variables have to be "
                    "present if the map's main.py file does not contain "
                    "the function 'GM_calculate_dipole'.",
                    "MI_MC_6"
                )
                self.success = False
                return

        # check for existence of xyz_uvec

        # they're not expected if 'type' isn't expected, either (they go
        # together)
        # (type is set to None if not in file)
        if self.Core.type:
            msg = (
                f"\nThe file {self.corepath} does not contain the right "
                "amount of "
                "definitions for x_uvec, y_uvec, and z_uvec. Depending on "
                "the choice for type, only one or two of these is allowed "
                "to be specified."
            )
            nvars = sum([vec + "_uvec" in self.rawcore for vec in "xyz"])
            if self.Core.type == 'standard' and nvars != 2:
                Printer.warning(msg, "MI_MC_10")
                self.success = False
                return
            elif self.Core.type == 'linear' and nvars != 1:
                Printer.warning(msg, "MI_MC_10")
                self.success = False
                return
            functs_to_build.append("get_rotation_matrix")
            kwargs_for_build.append({"map_": self, "Printer": Printer})

        self.complete_code(functs_to_build, kwargs_for_build)


class PairMap(Map):
    """The Pair-specialized version of Map.

    Any attributes listed for Map are not separately listed here.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.

    Attributes
    ----------
    allpairs : list of tuple of 2 ints
        A list of all pairs that should be coupled by this map. A pair
        is indicated by the oscix of each oscillator involved. Maps can
        (and probably should) change the data type of this attribute -
        this can severely impact calculation times.
    """

    def initialize(self, Files, Printer):
        """Initializes the map.

        Initializing is a multi-step process:

        - If there is a main.py file, read/extract it.
        - If any of GM_adjust_[RunPars/map_core_raw] are
          missing, add the default for them.
        - Run GM_adjust_RunPars
        - Find the core.txt file, parse to rawcore. Supplement any
          files, if requested.
        - Run GM_adjust_map_core_raw
        - Parse the final choice of rawcore to Core
        - If not present in self.code, create functions for all missing
          behaviour

        Parameters
        ----------
        Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
            Contains all currently known paths and other file-related
            properties.
            Has to be updated after RunPars is finalized.
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        self.code = self.extract_code(Printer)
        if not self.code:
            self.code = GM_DMF.NewModule()

        self.complete_code((
            "adjust_RunPars",
            "adjust_map_core_raw"
        ))
        self.code.GM_adjust_RunPars(Files, Printer, self)

        # simple parse of core.txt
        self.rawcore = self.find_core(Printer)
        if not self.success:
            return

        # add extra corefiles to the main core
        self.append_core(Printer)
        if not self.success:
            return

        # allow the contents of core.txt to be changed
        self.code.GM_adjust_map_core_raw(Files, Printer, self)

        self.Core = PairCore(Printer, self)
        if not self.Core.success:
            self.success = False
            return

        # self.complete_code(("needs_mapfunc",))
        # self.required_functions = self.code.GM_needs_mapfunc(
        #     Files, Printer, self)

        # self.complete_code(("needs_keyword",))
        # self.required_keywords = self.code.GM_needs_keyword(
        #     Files, Printer, self)

        # Add in the remaining code
        self.complete_code((
            "change_coup_type",
            "prep_coupling",
            "post_init",
            "pre_run",
            "pre_frame",
            "post_frame",
            "post_run"
        ), [{"name": self.name}] + [{}] * 6)

    def check_singles(self, main_runpars, Printer, requester=None):
        """Sees if all indicated requirements of the map are met.

        Some pair-wise maps require other content to be present. For
        example, a specialized coupling could need additional
        information about an oscillator, such as TRESP needing the delQ.
        Such mappings can list certain keywords or functions that they
        can interpret which singles must have before they can be
        coupled.
        This function makes sure that any oscillator coupled by this map
        meets these requirements, or else quit the program.

        Parameters
        ----------
        main_runpars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        requester : str or NoneType, default=None
            The map requesting the map we're checking. This is needed
            to avoid the confusion of a map not directly requested by the
            user throwing errors.
        """

        # this map might have some requirements, see if they are present
        if requester:
            basestr = (
                f"\nThe map {self.name} (requested by the map {requester}) ")
        else:
            basestr = f"\nThe map {self.name} "

        # if any required single is not present
        missing_maps = [
            map_ for map_ in self.Core.require_singles
            if map_ not in main_runpars.available_maps_singles
        ]
        if missing_maps:
            Printer.warning(
                basestr + "requires the map(s) "
                f"{', '.join(missing_maps)}, but these are not available to "
                "the program. Either they are not present, or an error was "
                "encountered when loading them in. This map will not be "
                "available for use until this is fixed. ", "MI_MC_2", True
            )

        # We don't yet know what singles each map will deal with in the end.
        # Therefore, we should wait with these checks until after this has
        # been determined.
        if requester is not None:
            return

        requested_singles = set()
        for pair in main_runpars.coupling_v_pair_dict[self.name]:
            requested_singles.add(pair[0])
            requested_singles.add(pair[1])

        # if any required single does not have keyword - stop this map
        self.check_singles_keyword(
            Printer, main_runpars, requested_singles, basestr)

        # if any required single does not have map function - stop this map
        self.check_singles_mapfunc(
            Printer, main_runpars, requested_singles, basestr)

    def check_singles_2(self, Printer, main_runpars, oscillators):
        """Checks if actually assigned singles fit the requirements.

        Very similar to check_singles(), with the slight difference that
        that one is meant for checking whether the initally assigned
        maps have all their requirements met. But they can request other
        pairmaps to do their job. In that case, a map might have a
        specific reference for a specific case, so it does not make sense
        to have all pairs (or, singles within them) to conform to all
        rules for all pairs. That is why we do those checks again here,
        on a per-oscillator basis (after sorting everything out).

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        main_runpars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        oscillators : list of :class:`~GMAP.src.tools.SystemReader.Oscillator`
            The map requesting the map we're checking. This is needed
            to avoid the confusion of a map not directly requested by the
            user throwing errors.
        """

        all_singles_used = set()
        for osc in oscillators:
            all_singles_used.add(osc.Map.name)

        basestr = f"\nThe map {self.name} "

        # if any required single does not have keyword - stop this map
        self.check_singles_keyword(
            Printer, main_runpars, all_singles_used, basestr)

        # if any required single does not have map function - stop this map
        self.check_singles_mapfunc(
            Printer, main_runpars, all_singles_used, basestr)

    def check_singles_keyword(
        self, Printer, main_runpars, singles_to_check, printstr
    ):
        """Checks whether all given maps have all required keywords.

        This map might depend on more information about singles. To
        obtain that information, it can require them to have a specific
        keyword. This method checks whether each type of single provided
        has this keyword.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        main_runpars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        singles_to_check : iterable of str
            The names of the singles that should be checked for validity.
        printstr : str
            What should be shown as the name of this coupling map.
        """

        missing_maps = [
            (map_, f"{self.name}.{keyword}")
            for map_ in singles_to_check
            for keyword in self.Core.require_keywords
            if f"{self.name}.{keyword}"
            not in main_runpars.requested_mapdict[map_].rawcore
        ]
        if missing_maps:
            basestrings = [
                f"the map {pair[0]} is missing the keyword {pair[1]}"
                for pair in missing_maps
            ]
            basestrings = '\n'.join(basestrings)
            Printer.warning(
                printstr + "was requested for use in calculating "
                "couplings. It requires any singles maps it couples to contain"
                " (a) certain keyword(s), but the following maps are missing "
                f"the following keywords:\n{basestrings}\n"
                "Please contact the creators of both maps to fix the issue. "
                "In the meantime, please use a different coupling method for "
                "these maps.", "MI_MM_2", True
            )

    def check_singles_mapfunc(
        self, Printer, main_runpars, singles_to_check, printstr
    ):
        """Checks whether all given maps have all required keywords.

        This map might depend on more information about singles. To
        obtain that information, it can require them to have a specific
        function defined in their main.py. This method checks whether
        each type of single provided has this function.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        main_runpars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        singles_to_check : iterable of str
            The names of the singles that should be checked for validity.
        printstr : str
            What should be shown as the name of this coupling map.
        """

        missing_maps = [
            (map_, f"CP_{self.name}_{func}")
            for map_ in singles_to_check
            for func in self.Core.require_mapfuncs
            if not hasattr(
                main_runpars.requested_mapdict[map_].code,
                f"CP_{self.name}_{func}")
        ]
        if missing_maps:
            basestrings = [
                f"the map {pair[0]} is missing the function {pair[1]}"
                for pair in missing_maps
            ]
            basestrings = '\n'.join(basestrings)
            Printer.warning(
                printstr + "was requested for use in calculating "
                "couplings. It requires any singles maps it couples to contain"
                " (a) certain function(s) in the main.py file, but the "
                "following maps are missing "
                f"the following functions:\n{basestrings}\n"
                "Please contact the creators of both maps to fix the issue. "
                "In the meantime, please use a different coupling method for "
                "these maps.", "MI_MM_2", True
            )

    def check_pairs(self, main_runpars, Printer):
        """Sees if all pair-map requirements of the map are met.

        Some pair-wise maps require other content to be present. For
        example, a specialized coupling could need to be able to fall
        back to a more generic coupling map, like the dipole-dipole
        (DipDip) coupling map. These fallbacks should be prepared as
        well, so we must check if they are known (or not present),
        complete, and valid.
        This function makes sure that any oscillator coupled by this map
        meets these requirements, or else quit the program.

        Parameters
        ----------
        main_runpars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        # we need these maps, but they weren't directly requested by the user
        maybe_missing_maps = [
            map_ for map_ in self.Core.require_pairs
            if map_ not in main_runpars.requested_pairmapdict
        ]

        if maybe_missing_maps:
            # we need these maps, but they are not available at all.
            missing_maps = [
                map_ for map_ in self.Core.require_pairs
                if map_ not in main_runpars.available_maps_pairs
            ]
            if missing_maps:
                Printer.warning(
                    f"\nThe map {self.name} requires the map(s) "
                    f"{', '.join(missing_maps)}, but these are not available "
                    "to the program. Either they are not present, or an error "
                    "was encountered when loading them in. This map will not "
                    "be available for use until this is fixed. ",
                    "MI_MC_2", True
                )

            # The maps are available, but not requested - before we know
            # whether we can use them, we first have to check them, too.
            for mapname in maybe_missing_maps:
                map_ = main_runpars.available_maps_pairs[mapname]
                # if this check fails, the program is quit automatically.
                map_.check_singles(main_runpars, Printer, requester=mapname)
            # add them to the requested - they have to be screened, too.
            main_runpars.requested_pairmapdict[mapname] = map_


class SingleCore():
    """Contains all information regarding a single core.txt file.

    Such a core.txt file is assumed to belong to a singles map.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.SingleMap`
        The object that stores the map which this core.txt file belongs to.

    Attributes
    ----------
    success : bool
        Whether the core has (thusfar) been read successfully. If a
        problem occurs, a warning is in order, but the program does not
        have to quit - if the map isn't used, we don't care. Later, when
        looking at the requested maps, if an unsuccessful map is
        requested, we can throw an error and quit!
    functional_group : list of list of list of list of list of str
        The more structured version of what functional group(s) this
        map operates on.
    bonds : list of list of list of int
        All bonds that are indicative of the functional group(s)
        this map operates on. This list doesn't have to be complete,
        these bonds are those that make the difference. If there
        are multiple residues in a single functional group, there
        must at least be a single bond for each extra residue to
        'bind' them all to a single structure.
    requires_bonds : bool
        Whether this map requires atombond information.
    used_atoms : list of int
        The indices of the atoms in functional_group that should actually
        be stored for later use. The indices are the positions of the
        atoms in functional_group, starting counting at 0.
    electrostatic_atoms : list of int
        The indices of the atoms in used_atoms that should actually
        be used in electrostatic calculations. The indices are the
        positions of the atoms in used_atoms, starting counting at 0.
    """

    def __init__(self, Printer, Map):
        rawcore = Map.rawcore
        self.success = True

        self.parse_functional_group(Printer, rawcore, Map.directory)
        if not self.success:
            return

        self.used_atoms = self.parse_used_atoms(
            Printer, rawcore, Map.directory)
        if not self.success:
            return

        self.electrostatic_atoms = self.parse_estatic_atoms(
            Printer, rawcore, Map.directory)
        if not self.success:
            return

        if self.electrostatic_atoms:
            self.electrostatic_choice = self.parse_estatic_choice(
                Printer, rawcore, Map.directory)
        else:
            self.electrostatic_choice = None
        if not self.success:
            return

        self.local_atoms = self.parse_local_atoms(
            Printer, rawcore, Map.directory)
        if not self.success:
            return

        self.type = self.parse_type(Printer, rawcore, Map.directory)
        if not self.success:
            return

        # If there is no custom function for defining an oscillators VEG
        # reference point, a default is needed. Make sure core.txt is valid.
        if not hasattr(Map.code, "GM_get_VEG_ref"):
            self.check_VEG_reference(Printer, rawcore, Map.directory)
            if not self.success:
                return

        self.dipole_gas_phase, self.dipole_data_array = self.parse_dipoles(
            Printer, rawcore, Map.directory)
        if not self.success:
            return

        (
            self.frequency_gas_phase, self.frequency_data_array_linear,
            self.frequency_data_array_quadratic,
        ) = self.parse_frequency(Printer, rawcore, Map.directory)
        if not self.success:
            return

    def parse_functional_group(self, Printer, rawcore, mapdir):
        """Parses the input for keywords functional_group(_file) in core.txt

        Choice for the functional group is stored in self.functional_group.
        This attribute is a list(1) of lists(2) of lists(3) of strings.
        Each of the lists numbered 2 corresponds to a possible defnition -
        either a line in core.txt, or a section (labelled newstruct) in
        the functgroup file.
        Each of the lists numbered 3 corresponds to a residue (in
        case it is the first) or atom to be named.
        Each of the items in the lists numbered 3 corresponds to a
        possible name for that object.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str: list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.
        """

        funcgroup_par = "functional_group"
        fgfile_par = "functional_group_file"
        corefile = (mapdir / 'core.txt').resolve()

        # step 1: make sure the functional group is defined unambiguously.
        if funcgroup_par in rawcore and fgfile_par in rawcore:
            Printer.warning(
                f"\nFound both the parameters '{funcgroup_par}' and "
                f"'{fgfile_par}' in the file {corefile}. Only one "
                "of these two is allowed.",
                "MI_MC_1"
            )
            self.success = False
            return

        if funcgroup_par not in rawcore and fgfile_par not in rawcore:
            Printer.warning(
                f"\nFound neither the parameter '{funcgroup_par}' nor the "
                f"parameter '{fgfile_par}' in the file {corefile}. However, "
                "at least one of them is necessary for the map to function.",
                "MI_MC_2"
            )
            self.success = False
            return

        # step 2: if the 'separate-file' method is used for the definition,
        #         translate it to the in-file method, and store it as such.
        if fgfile_par in rawcore:
            fname = (mapdir / rawcore[fgfile_par][0]).resolve()
            if not fname.is_file():
                Printer.warning(
                    f"\nThe file {corefile} wants to use the file {fname}"
                    " to define the functional groups for that map. "
                    "However, this file does not exist.",
                    "MI_MC_3"
                )
                self.success = False
                return

            # we've got a file, now we need to parse its contents - but
            # only such that they look the same as what would've been
            # obtained from the file itself.
            rawcore[funcgroup_par] = self.funcgroupfile_to_infile(fname)

        # step 3: now there must definitely be an in-file (lookalike)
        #         definition. Parse and store it as such.
        (
            self.functional_group, self.bonds, error_code
        ) = self.funcgroup_parse_infile(rawcore[funcgroup_par])
        if error_code[0] != 0:
            self.success = False
            errstring = "-".join([str(num) for num in error_code])
            Printer.warning(
                f"\nThe file {corefile} contains a definition of "
                "functional_group that cannot be interpreted. A hint of what "
                f"went wrong is this extra code: {errstring}. Please see the "
                "manual for more information.",
                "MI_MC_4"
            )
            self.success = False
            return
        n_bonds = sum([len(bonds) for bonds in self.bonds])
        if n_bonds == 0:
            self.requires_bonds = True
        else:
            self.requires_bonds = False

        if "functional_group_bonds" in rawcore:
            self.parse_fg_bonds(
                Printer, corefile, rawcore["functional_group_bonds"]
            )
            if not self.success:
                return

            self.check_bonds(Printer, corefile)
            if not self.success:
                return

        if "requires_bonds" in rawcore:
            if rawcore["requires_bonds"][0].lower() in ("t", "true"):
                self.requires_bonds = True

        self.functional_group = [
            Structure(struct, bonds) for struct, bonds in zip(
                self.functional_group, self.bonds
            )
        ]

        if any(not item.success for item in self.functional_group):
            Printer.warning(
                f"\nThe file {corefile} contains an invalid definition of "
                "functional_group. At least one of the definitions consists "
                "of multiple residues, but not all residues are bonded to "
                "each other. Please make sure all residues are bonded!",
                "MI_MC_9"
            )
            self.success = False
            return

    @staticmethod
    def funcgroupfile_to_infile(fname):
        """Parses the functional_group_file from a map into infile format.

        Parameters
        ----------
        fname : pathlib.Path
            The name of the file to parse.

        Returns
        -------
        file_contents : list of list of str
            The contents of the file parsed into the same format as would
            have been obtained when the molecule would have been defined in
            the file itself
        """

        file_contents = []
        templist = []
        with open(fname) as fhand:
            for line in fhand:
                line = GM_PP.cleanline(line).strip()
                if not line:
                    continue

                if line == "newstruct":
                    if templist:
                        file_contents.append(templist)
                        templist = []
                else:
                    templist.append(line)

            if templist:
                file_contents.append(templist)

        return file_contents

    @staticmethod
    def funcgroup_parse_infile(funcgroup):
        """Parse the choice made for functional_groups

        This is the core of the parser. After catching blatant issues
        and enforcing a single format independent of source, this
        function is the next step in the process to store whats on these
        lines.

        output formats:

        - all_opts is a list(1).

          - Each item in list(1) corresponds to a single line/newstruct
            (depends of source) and is itself a list(2).
          - Each item in list(2) corresponds to a single residue, and is
            itself a list of 2 items. The first item contains the residue
            name (is a list of str), the second item contains the atom
            names. The second item is itself a list(3).
          - Each item in list(3) corresponds to an atom and is itself a
            list of str.

        - all_bonds is a list(1).

          - Each item in list(1) corresponds to a single line/newstruct
            (depends of source) and is itself a list(2).
          - Each item in list(2) corresponds to a bond and is a list of
            two items. These are the indices of the two atoms that form
            the bond.

        Parameters
        ----------
        funcgroup : list of list of str
            The choice for functional_group as stored in rawcore.

        Returns
        -------
        all_opts : list of list of list of list of list of str
            The more structured version of what functional group(s) this
            map operates on. See explanation above for more details
            about the datatype.
        all_bonds : list of list of list of int
            All bonds that are indicative of the functional group(s)
            this map operates on. This list doesn't have to be complete,
            these bonds are those that make the difference. If there
            are multiple residues in a single functional group, there
            must at least be a single bond for each extra residue to
            'bind' them all to a single structure.
        error_code : tup of int
            More information on whether and why the structure was read
            unsuccessfully. See
            :ref:`Warning overview<UserGuide_page_warning_overview>`
            for more information - look for code MI_MC_4.
        """

        # funcgroup is a list, each item of which corresponds to a different
        # 'option' of what the group could look like. In core.txt, each
        # 'option' is defined on a separate line, in the separate file, each
        # 'option' is marked with the label 'newstruct'.
        all_opts = []
        all_bonds = []
        for opt in funcgroup:
            # each opt is a list of strings. Each string is a 'word' in the
            # file.
            ix_count = 0
            residues = []
            resname = ""
            atoms = []
            bonds = {}
            for word in opt:
                # if a new residue starts
                if word.startswith("[") and word.endswith("]"):
                    # if this is not the first residue
                    if resname and atoms:
                        atoms = [item.split(",") for item in atoms]
                        residues.append([resname.split(","), atoms])
                        atoms = []
                        resname = word[1:-1]
                    elif resname or atoms:
                        return None, None, (1, len(all_opts), ix_count)
                    # if this is the first residue
                    else:
                        resname = word[1:-1]
                elif word.startswith("[") or word.endswith("]"):
                    return None, None, (2, len(all_opts), ix_count)
                # if this is an atom
                else:
                    if "(" in word and ")" in word:
                        word = word.split("(")
                        atnames = word[0]
                        word = word[1].split(")")
                        numlist = word[0].split(",")
                        try:
                            bondnums = [int(item) for item in numlist]
                        except Exception:
                            return None, None, (3, len(all_opts), ix_count)
                        for bondnum in bondnums:
                            if bondnum in bonds:
                                bonds[bondnum].append(ix_count)
                            else:
                                bonds[bondnum] = [ix_count]
                    elif "(" in word or ")" in word:
                        return None, None, (4, len(all_opts), ix_count)
                    else:
                        atnames = word

                    atoms.append(atnames)
                    ix_count += 1
            # end of line
            if resname and atoms:
                atoms = [item.split(",") for item in atoms]
                residues.append([resname.split(","), atoms])
            elif resname or atoms:
                return None, None, (5, len(all_opts), ix_count)

            bondslist = []

            for id, bond in bonds.items():
                if len(bond) != 2:
                    return None, None, (6, len(all_opts), id)
                bondslist.append(bond)

            # append found info to main lists.
            if residues:
                all_opts.append(residues)
                all_bonds.append(bondslist)

        return all_opts, all_bonds, (0,)

    def parse_fg_bonds(self, Printer, corefile, bonds):
        """Parses the choice for functional_group_bonds in core.txt.

        The bonds found this way will be applied to all definitions
        found for functional_group for this map. If this behaviour is
        not desired and only some maps should get these bonds, they
        should be defined using parentheses in the definition for
        functional_group.

        This function does not return anything - instead, it adds the
        bonds found directly to each sublist of self.bonds.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        corefile : pathlib.Path
            The name + path of the core.txt file.
        bonds : list of str
            The choice for functional_group_bonds as stored in rawcore.
        """

        # each item is already a bond
        for bond in bonds:
            if "-" not in bond:
                Printer.warning(
                    f"\nThe file {corefile} contains a definition of "
                    "functional_group_bonds that cannot be interpreted. "
                    "Please make sure that the bond is defined using a "
                    "hyphen.",
                    "MI_MC_5"
                )
                self.success = False
                return
            bond = bond.split("-")
            if len(bond) != 2:
                Printer.warning(
                    f"\nThe file {corefile} contains a definition of "
                    "functional_group_bonds that cannot be interpreted. "
                    "Please make sure that the bond consists of exactly "
                    "two atoms.",
                    "MI_MC_5"
                )
                self.success = False
                return

            try:
                bond = [int(num) for num in bond]
            except Exception as ex:
                Printer.warning(
                    f"\nThe file {corefile} contains a definition of "
                    "functional_group_bonds that cannot be interpreted. "
                    "Please make sure that the definition contains only "
                    "integers and a single hyphen.",
                    "MI_MC_5", exception=ex
                )
                self.success = False
                return

            for newstruct in self.bonds:
                newstruct.append(bond)

    def check_bonds(self, Printer, corefile):
        """Checks whether the indices supplied for bonds actually exist.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        corefile : pathlib.Path
            The name + path of the core.txt file.
        """

        n_bonds = sum([len(bonds) for bonds in self.bonds])
        if n_bonds:
            self.requires_bonds = True
        else:
            self.requires_bonds = False

        for struct, bonds in zip(self.functional_group, self.bonds):
            number_atoms = sum([len(res[1]) for res in struct])
            for bond in bonds:
                if any(ix >= number_atoms for ix in bond):
                    Printer.warning(
                        f"\nThe file {corefile} contains a definition of "
                        "functional_group_bonds that cannot be interpreted. "
                        "Please make sure that the indices point to atoms "
                        "within functional_group.",
                        "MI_MC_5"
                    )
                    self.success = False
                    return

    def parse_used_atoms(self, Printer, rawcore, mapdir):
        """Parse the choice for the parameter used_atoms

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        used_atoms : list of int
            The indices of the atoms in functional_group that should actually
            be stored for later use. The indices are the positions of the
            atoms in functional_group, starting counting at 0.
        """

        # see if it exists
        if "used_atoms" not in rawcore:
            Printer.warning(
                "\nCould not find the parameter 'used_atoms' in the file "
                f"{mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return

        # convert to ints
        try:
            used_atoms = [int(num) for num in rawcore["used_atoms"]]
        except Exception as ex:
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'used_atoms'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "choice consists of nothing but numbers separated by spaces.",
                "MI_MC_7", exception=ex
            )
            self.success = False
            return

        if any(
            not all(ix in struct.indices for struct in self.functional_group)
            for ix in used_atoms
        ):
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'used_atoms'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "indices don't exceed the amount of atoms given for the "
                "parameter functional_group.",
                "MI_MC_8"
            )
            self.success = False
            return

        return used_atoms

    def parse_estatic_atoms(self, Printer, rawcore, mapdir):
        """Parse the choice for the parameter electrostatic_atoms

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        estatic_atoms : list of int
            The indices of the atoms in used_atoms that should actually
            be used in electrostatic calculations. The indices are the
            positions of the atoms in used_atoms, starting counting at 0.
        """

        # see if it exists
        if "electrostatic_atoms" not in rawcore:
            Printer.warning(
                "\nCould not find the parameter 'electrostatic_atoms' in the "
                f"file {mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return

        # convert to ints
        try:
            estatic_atoms = [
                int(num) for num in rawcore["electrostatic_atoms"]
            ]
        except Exception as ex:
            if rawcore["electrostatic_atoms"][0].lower() == "none":
                estatic_atoms = []
            else:
                Printer.warning(
                    "\nCould not interpret the choice for the parameter "
                    "'electrostatic_atoms'"
                    f" in the file {mapdir / 'core.txt'}. Please make sure "
                    "the choice consists of nothing but numbers separated by "
                    "spaces.",
                    "MI_MC_7", exception=ex
                )
                self.success = False
                return

        # now, see if choice is valid
        maxlen = len(self.used_atoms)
        if any(ix >= maxlen for ix in estatic_atoms):
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'electrostatic_atoms'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "indices don't exceed the amount of atoms given for the "
                "parameter used_atoms.",
                "MI_MC_8"
            )
            self.success = False
            return

        return estatic_atoms

    def parse_estatic_choice(self, Printer, rawcore, mapdir):
        """Parse the choice for the parameter electrostatic_choice

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        estatic_choice : str
            What electrostatic properties should be calculated for the
            atoms given for the parameter electrostatic_atoms.
        """

        # see if it exists
        if "electrostatic_choice" not in rawcore:
            # if there are no atoms for which to calculate estatic properties,
            # it is okay if this parameter is missing.
            if not self.electrostatic_atoms:
                return None

            # If there are such atoms, this parameter is required.
            Printer.warning(
                "\nCould not find the parameter 'electrostatic_choice' in the "
                f"file {mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return

        choice = rawcore["electrostatic_choice"][0]
        if choice.upper() not in ("V", "E", "G"):
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'electrostatic_choice'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "choice is either 'V', 'E', or 'G'.",
                "MI_MC_8"
            )
            self.success = False
            return
        return choice.upper()

    def parse_local_atoms(self, Printer, rawcore, mapdir):
        """Parse the choice for the parameter electrostatic_atoms

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        local_atoms : list of int
            The indices of the atoms in used_atoms that should actually
            be used in electrostatic calculations. The indices are the
            positions of the atoms in used_atoms, starting counting at 0.
        """

        # see if it exists
        if "local_atoms" not in rawcore:
            Printer.warning(
                "\nCould not find the parameter 'local_atoms' in the "
                f"file {mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return

        # convert to ints
        try:
            local_atoms = [
                int(num) for num in rawcore["local_atoms"]
            ]
        except Exception as ex:
            if rawcore["local_atoms"][0].lower() == "none":
                local_atoms = []
            else:
                Printer.warning(
                    "\nCould not interpret the choice for the parameter "
                    "'local_atoms'"
                    f" in the file {mapdir / 'core.txt'}. Please make sure "
                    "the choice consists of nothing but numbers separated by "
                    "spaces.",
                    "MI_MC_7", exception=ex
                )
                self.success = False
                return

        # now, see if choice is valid
        maxlen = len(self.used_atoms)
        if any(ix >= maxlen for ix in local_atoms):
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'local_atoms'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "indices don't exceed the amount of atoms given for the "
                "parameter used_atoms.",
                "MI_MC_8"
            )
            self.success = False
            return

        return local_atoms

    def parse_type(self, Printer, rawcore, mapdir):
        """Parse the choice for the parameter type

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        choice : str
            What the type of the oscillator is.
        """

        if "type" not in rawcore:
            # type is only used for rotating VEG matrix (actualy, only
            # the EG part of it)
            if not self.electrostatic_atoms:
                return None
            if self.electrostatic_choice == "V":
                return None

            Printer.warning(
                "\nCould not find the parameter 'type' in the "
                f"file {mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return

        choice = rawcore["type"][0]
        if choice.lower() not in ("standard", "linear"):
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'type'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "choice is either 'standard', or 'linear'.",
                "MI_MC_8"
            )
            self.success = False
            return
        return choice.lower()

    def check_VEG_reference(self, Printer, rawcore, mapdir):
        """Check the choice for the parameter VEG_reference.

        Confirms the validity of the choice for VEG_reference. Does the
        chosen method exist? Is the type of the rest of the arguments
        correct?

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.
        """

        def tryint(x):
            try:
                int(x)
            except Exception:
                return False
            else:
                return True

        if "VEG_reference" not in rawcore:
            Printer.warning(
                "\nCould not find the parameter 'VEG_reference' in the "
                f"file {mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return

        # We need a valid keyword
        choice = rawcore["VEG_reference"][0]
        if choice.lower() not in ("residues", "position", "com"):
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'VEG_reference'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "choice is 'residues', 'position', or 'CoM'.",
                "MI_MC_8"
            )
            self.success = False
            return

        # we need a valid definition after. Firstly, it must be present.
        # For residues and CoM, we also need just integers.
        if (
            len(rawcore["VEG_reference"]) < 2
            or
            (choice.lower() in ("residues", "com") and not all(
                tryint(val) for val in rawcore["VEG_reference"][1:]
            ))
        ):
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'VEG_reference'"
                f" in the file {mapdir / 'core.txt'}. Please make sure the "
                "choice of method 'residues', 'position', or 'CoM' is also "
                "followed with a choice for this method. ",
                "MI_MC_8"
            )
            self.success = False
            return

    def parse_dipoles(self, Printer, rawcore, mapdir):
        """Parse the information for dipole magnitude.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        dipole_gas_phase : `np.float32`
            What the base magnitude for the dipole should be. The program
            can either use this as-is, or in combination with the contents
            from a given file.
        fdata : `np.ndarray` or None
            An array of shape (n_estatic_ats, 10) or (3, n_estatic_ats, 10),
            with padded zeros for any columns that are not required.
            The 2D array is returned when the file is for magnitude, the 3D
            when the file is for xyz separately.
            If the parameter 'dipole_data_file' does not occur in the file
            core.txt, None is returned instead.
        """

        # First, get the (gas phase) magnitude of the dipole, this must
        # always be given.

        if "dipole_gas_phase" not in rawcore:
            Printer.warning(
                "\nCould not find the parameter 'dipole_gas_phase' in the "
                f"file {mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return None, None

        try:
            dipole_gas_phase = [
                np.float32(num) for num in rawcore["dipole_gas_phase"]
            ]
        except Exception as ex:  # no 0th entry, not floatable
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'dipole_gas_phase'"
                f" in the file {mapdir / 'core.txt'}. Please make sure "
                "the choice consists of a single decimal number.",
                "MI_MC_7", exception=ex
            )
            self.success = False
            return None, None

        # how many we need, depends on the other parameter, dipole_data_file.
        # it can either give a single VEG matrix (for magnitude), or three,
        # one for each of the XYZ components.
        if "dipole_data_file" not in rawcore:
            # This is actually completely fine. The dipole moment does not
            # need to depend on the electrostatics, even if the frequency
            # does. In that case, we only need a single value.
            return dipole_gas_phase[0], None

        # ---------------------------------------------------------------------

        # Then, look for the optional dependency of the dipole on the
        # electrostatics from the environment.

        warntext = (
            f"\nThe file {mapdir / 'core.txt'} contains an invalid choice for "
            "the parameter 'dipole_data_file'. The expected format requires "
            "both a specification of type of file (magnitude or xyz), and the "
            "file name."
        )

        # now, the parameter  "dipole_data_file" exists.
        match rawcore["dipole_data_file"][0]:
            case "[N/A]":
                return dipole_gas_phase[0], None
            case "magnitude":
                dipole_gas_phase = dipole_gas_phase[0]
                choice = "mag"
            case "xyz":
                if len(dipole_gas_phase) != 3:
                    Printer.warning(
                        "\nInvalid choice for the parameter 'dipole_gas_phase'"
                        f" in the file {mapdir / 'core.txt'}. Please make "
                        "sure the choice consists of three decimal numbers.",
                        "MI_MC_8"
                    )
                    self.success = False
                    return None, None
                choice = "xyz"
            case _:
                Printer.warning(warntext, "MI_MC_8")
                self.success = False
                return None, None

        if len(rawcore["dipole_data_file"]) != 2:
            Printer.warning(warntext, "MI_MC_8")
            self.success = False
            return None, None

        # if the parameter exists, but the specified file does not:
        fname = (mapdir / rawcore["dipole_data_file"][1]).resolve()
        if not fname.is_file():
            Printer.warning(
                f"\nThe file {mapdir / 'core.txt'} wants to use the file "
                f"{fname}"
                " to define the dependency of the dipole moment on the "
                "electrostatics. "
                "However, this file does not exist.",
                "MI_MC_3"
            )
            self.success = False
            return None, None

        try:
            fdata = np.genfromtxt(
                fname, "float32", missing_values=0, ndmin=2)
        except Exception as ex:  # numpy had some issue
            Printer.warning(
                "\nNumpy could not interpret the contents of the file "
                f"{fname}. Please make sure the file contains only decimal "
                "numbers in a grid.",
                "MI_MC_7", exception=ex
            )
            self.success = False
            return dipole_gas_phase, None

        # numpy read was succesfull, now to see whether the dimensions of the
        # array from the file are correct.

        # required (minimum) width of array:
        deswidth = 1
        if self.electrostatic_choice == "E":
            deswidth = 4
        elif self.electrostatic_choice == "G":
            deswidth = 10

        if choice == "mag":
            desheight = len(self.electrostatic_atoms)
        elif choice == "xyz":
            desheight = len(self.electrostatic_atoms) * 3

        array = self.confirm_array_size(
            Printer, fdata, deswidth, desheight, fname)
        if not self.success:
            return dipole_gas_phase, None

        if choice == "xyz":
            array = array.reshape((3, -1, 10))

        return dipole_gas_phase, array

    def parse_frequency(self, Printer, rawcore, mapdir):
        """Parse the information for frequency determination.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        frequency_gas_phase : `np.float32`
            What the base value for the frequency should be. The program
            can either use this as-is, or in combination with the contents
            from a given file.
        linear_array : `np.ndarray` or None
            An array of shape (n_estatic_ats, 10),
            with padded zeros for any columns that are not required.
            If the parameter 'frequency_data_file_linear' does not occur
            in the file core.txt, None is returned instead.
        quadratic_array : `np.ndarray` or None
            An array of shape (n_estatic_ats, 10),
            with padded zeros for any columns that are not required.
            If the parameter 'frequency_data_file_quadratic' does not occur
            in the file core.txt, None is returned instead.
        """

        frequency_gas_phase = self.parse_frequency_gas_phase(
            Printer, rawcore, mapdir)
        if not self.success:
            return frequency_gas_phase, None, None

        linear_array = self.parse_frequency_data_file(
            Printer, rawcore, mapdir, "frequency_data_file_linear")
        if not self.success:
            return frequency_gas_phase, linear_array, None

        quadratic_array = self.parse_frequency_data_file(
            Printer, rawcore, mapdir, "frequency_data_file_quadratic")

        return frequency_gas_phase, linear_array, quadratic_array

    def parse_frequency_gas_phase(self, Printer, rawcore, mapdir):
        """Parse the choice for the gas phase frequency

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.

        Returns
        -------
        frequency_gas_phase : `np.float32`
            What the base value for the frequency should be. The program
            can either use this as-is, or in combination with the contents
            from a given file.
        """

        if "frequency_gas_phase" not in rawcore:
            Printer.warning(
                "\nCould not find the parameter 'frequency_gas_phase' in the "
                f"file {mapdir / 'core.txt'}. Without it, the map cannot "
                "function. Please make sure it is present.",
                "MI_MC_6"
            )
            self.success = False
            return None

        try:
            frequency_gas_phase = np.float32(rawcore["frequency_gas_phase"][0])
        except Exception as ex:  # no 0th entry, not floatable
            Printer.warning(
                "\nCould not interpret the choice for the parameter "
                "'frequency_gas_phase'"
                f" in the file {mapdir / 'core.txt'}. Please make sure "
                "the choice consists of a single decimal number.",
                "MI_MC_7", exception=ex
            )
            self.success = False
            return None
        return frequency_gas_phase

    def parse_frequency_data_file(self, Printer, rawcore, mapdir, parname):
        """Parse the choice for the gas phase frequency

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory in which the map is defined.
        parname : str
            The name of the parameter used for referring to the file
            with constants.

        Returns
        -------
        array : `np.ndarray` or None
            An array of shape (n_estatic_ats, 10),
            with padded zeros for any columns that are not required.
            If the parameter `parname` does not occur
            in the file core.txt, None is returned instead.
        """

        # dependence on electrostatics is given by the other parameter,
        # frequency_data_file.
        # it can give a single VEG matrix (for magnitude).
        if parname not in rawcore:
            # This is actually completely fine. The frequency does not
            # need to depend on the electrostatics. In that case, we only need
            # a single value.
            return None

        # ---------------------------------------------------------------------

        # Then, look for the optional dependency of the frequency on the
        # electrostatics from the environment.

        # now, the parameter  "frequency_data_file" exists.
        if rawcore[parname][0] == "[N/A]":
            return None

        # if the parameter exists, but the specified file does not:
        fname = (mapdir / rawcore[parname][0]).resolve()
        if not fname.is_file():
            Printer.warning(
                f"\nThe file {mapdir / 'core.txt'} wants to use the file "
                f"{fname}"
                " to define the dependency of the frequency on the "
                "electrostatics. However, this file does not exist.",
                "MI_MC_3"
            )
            self.success = False
            return None

        try:
            fdata = np.genfromtxt(
                fname, "float32", missing_values=0, ndmin=2)
        except Exception as ex:  # numpy had some issue
            Printer.warning(
                "\nNumpy could not interpret the contents of the file "
                f"{fname}. Please make sure the file contains only decimal "
                "numbers in a grid.",
                "MI_MC_7", exception=ex
            )
            self.success = False
            return None

        # numpy read was succesfull, now to see whether the dimensions of the
        # array from the file are correct.

        # required (minimum) width of array:
        deswidth = 1
        if self.electrostatic_choice == "E":
            deswidth = 4
        elif self.electrostatic_choice == "G":
            deswidth = 10

        desheight = len(self.electrostatic_atoms)

        array = self.confirm_array_size(
            Printer, fdata, deswidth, desheight, fname)
        if not self.success:
            return None

        return array

    def confirm_array_size(self, Printer, array, deswidth, desheight, fname):
        """Makes sure that the array from the file is of the correct shape.

        If not, self.success is set to false and None is immediately
        returned, kicking of the abortion all the way up the call chain.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        array : `np.ndarray`
            The array that was read from file, and whose shape/size must
            be confirmed.
        deswidth : int
            The desired amount of columns in the array.
        desheight : int
            The desired amount of rows in the array
        fname : `pathlib.Path`
            The filename of the file the array is from.

        Returns
        -------
        array : `np.ndarray` or None
            None is returned if the input array was too small along at
            least one dimension. If the array is larger in any dimension,
            it is cropped to fit the dimensions exactly.
            Finally, if the desired width was smaller than 10, the width
            (after any possible cropping) is extended to 10, by padding
            extra zeros.
        """

        # actual dimensions of array
        foundheight, foundwidth = array.shape

        success, array = self.report_array_size(
            Printer, foundwidth, deswidth, "columns", fname, array)
        success2, array = self.report_array_size(
            Printer, foundheight, desheight, "rows", fname, array)
        if not success or not success2:
            self.success = False
            return None

        if foundwidth != 10:
            toadd = np.zeros(
                (array.shape[0], 10-array.shape[1]), dtype="float32")
            array = np.concatenate((array, toadd), axis=1)
        return array

    @staticmethod
    def report_array_size(Printer, foundlen, deslen, dir_, fname, fdata):
        """Reports on the size of the array, and cuts when necessary.

        This is a helper function for the method :meth:`confirm_array_size`.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        foundlen : int
            The actual size in a single dimension.
        deslen : int
            The desired size in that same dimension.
        dir_ : str
            What dimension we are looking at, in a human-readable format.
            Must be either 'rows' or 'columns'.
        fname : `pathlib.Path`
            The filename of the file the array is from.
        fdata : `np.ndarray`
            The array that was read from file, and whose shape/size must
            be confirmed.

        Returns
        -------
        success : bool
            False if foundlen < deslen, True otherwise.
        fdata : `np.ndarray`
            The input fdata array, but cropped in case foundlen > deslen.
        """

        if foundlen < deslen:
            Printer.warning(
                f"\nThere was a problem with the contents of the file {fname}"
                ". Please make sure the file has the correct amount of "
                f"{dir_}.\n"
                f"Amount of {dir_} found: {foundlen}\n"
                f"Amount of {dir_} needed: {deslen}\n",
                "MI_MC_8"
            )
            return False, fdata

        elif foundlen > deslen:
            Printer.warning(
                f"\nFound unexpected contents for the file {fname}. There "
                f"were {foundlen} {dir_} found, but only {deslen} {dir_} are "
                f"needed. The first {deslen} {dir_} will be used for the "
                "calculation. If this is not what you want, please terminate "
                "the process manually.",
                "MI_MC_8"
            )
            if dir_ == "columns":
                return True, fdata[:, :deslen]
            elif dir_ == "rows":
                return True, fdata[:deslen, :]

        else:
            return True, fdata


class PairCore():
    """Contains all information regarding a single core.txt file.

    Such a core.txt file is assumed to belong to a pairs map.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.SingleMap`
        The object that stores the map which this core.txt file belongs to.

    Attributes
    ----------
    success : bool
        Whether the core has (thusfar) been read successfully. If a
        problem occurs, a warning is in order, but the program does not
        have to quit - if the map isn't used, we don't care. Later, when
        looking at the requested maps, if an unsuccessful map is
        requested, we can throw an error and quit!
    allowed_singels : list of str
        The names of singles maps that are allowed to be coupled by this
        map. This list is built by combining the black-/whitelist
        requirements from this map with all requested singles maps.
    valid_combinations : list of tuple of str
        Each tuple has two strings, the names of two kinds (could both
        be equal) of oscillator. It corresponds to a certain type of
        pair that can be coupled using this map.
    """
    def __init__(self, Printer, Map):
        rawcore = Map.rawcore
        self.success = True

        # These can't fail
        for keyword in (
            "require_singles",
            "require_pairs",
            "require_keywords",
            "require_mapfuncs"
        ):
            setattr(self, keyword, self.parse_optional_string_list(
                rawcore, keyword))

        self.allowed_singles = self.parse_singles_BWlist(
            Map.RunPars.MainRunPars, rawcore)

        self.valid_combinations = self.parse_valid_combinations(
            Printer, rawcore, Map.directory)

        if not self.success:
            return

    def parse_optional_string_list(self, rawcore, keyword):
        """A base function for reading an optional list_str keyword choice.

        The core.txt file for pairmaps contains quite some keywords for
        which the choice will be one or more strings. This function
        retrieves the choice for that keyword from rawpars.

        If the keyword doesn't exist in rawcore (it is optional after
        all), or if the only detected choices are 'none', an empty list
        is returned instead.

        Parameters
        ----------
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        keyword : str
            The keyword whose choice to obtain.

        Returns
        -------
        choice : list of str
            The choice for the keyword found in rawcore. If rawcore
            doesn't contain a choice for the keyword, an empty list is
            returned instead.
        """

        # this keyword is not required
        # if it is present, and all(choice) == None, ignore that choice.
        choice = rawcore.get(keyword, [])
        if all(item.lower() == "none" for item in choice):
            choice = []
        return choice

    def parse_singles_BWlist(self, main_runpars, rawcore):
        """Finds what kinds of singles may be treated with this map.

        Not all maps can deal with all singles. Using either a blacklist
        or a whitelist, a map can indicate what kind of singles may be
        treated. This function starts with all requested singles (so,
        ones that will be searched for in the MD data), then only keeps
        those given in the whitelist and/or discards those given in the
        blacklist.

        Parameters
        ----------
        main_runpars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt

        Returns
        -------
        chosen_groups : list of str
            The names of singles maps that are allowed to be coupled by
            this map. This list is built by combining the black-/whitelist
            requirements from this map with all requested singles maps.
        """

        whitelist = self.parse_optional_string_list(
            rawcore, "singles_whitelist")
        blacklist = self.parse_optional_string_list(
            rawcore, "singles_blacklist")

        # All groups the map could couple if it'd like. (present groups)
        chosen_groups = [*main_runpars.requested_mapdict.keys()]

        # --------------------------------------------------------------
        # deal with whitelist:

        # no special whitelist
        if len(whitelist) == 0:
            pass
        # everything in whitelist
        elif ":all" in [item.lower() for item in whitelist]:
            pass
        else:  # only those that are both in whitelist and chosen_groups
            chosen_groups = [
                item for item in chosen_groups if item in whitelist]

        # --------------------------------------------------------------
        # deal with blacklist:

        # no special blacklist
        if len(blacklist) == 0:
            pass
        # nothing in blacklist
        elif all(item.lower() in (":none", "none") for item in blacklist):
            pass
        else:
            chosen_groups = [
                item for item in chosen_groups if item not in blacklist]

        return chosen_groups

    def parse_valid_combinations(self, Printer, rawcore, mapdir):
        """Finds what oscillator pairs may be treated with this map.

        Not all maps can deal with all kinds of pairs. On a case-by-case
        basis, a map can say what kinds of oscillator pairs it can
        couple.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during
            runtime, and handle errors.
        rawcore : dict of str - list of str pairs
            The raw contents of the file core.txt
        mapdir : pathlib.Path
            The path to the directory where this map is stored.

        Returns
        -------
        chosen_combinations : list of tuple of str
            Each tuple has two strings, the names of two kinds (could both
            be equal) of oscillator. It corresponds to a certain type of
            pair that can be coupled using this map.
        """

        possible_combinations = []
        for osc1 in self.allowed_singles:
            for osc2 in self.allowed_singles:
                possible_combinations.append((osc1, osc2))

        chosen_combinations = set()
        if "valid_combinations" not in rawcore:
            return possible_combinations

        for line in rawcore["valid_combinations"]:
            for word in line:
                if word.lower() == ":all":
                    for pair in possible_combinations:
                        chosen_combinations.add(pair)
                    continue
                elif word.lower() == ":same":
                    for pair in possible_combinations:
                        if pair[0] == pair[1]:
                            chosen_combinations.add(pair)
                    continue
                elif word.lower() == ":diff":
                    for pair in possible_combinations:
                        if pair[0] != pair[1]:
                            chosen_combinations.add(pair)
                    continue

                splitted = word.split(":")
                if len(splitted) != 2:
                    Printer.warning(
                        "\nAll arguments for the keyword 'valid_combinations' "
                        f"for the pairs map {mapdir.name} must contain "
                        "exactly one ':'. This is, however, not the case. "
                        "Please make sure to have exactly one.",
                        "MI_MC_11", False
                    )
                    self.success = False
                    return
                if len(splitted[0]) == 0:
                    Printer.warning(
                        "\nEach argument for the keyword 'valid_combinations' "
                        f"for the pairs map {mapdir.name} represents a pair "
                        "of groups to couple. While the second group is "
                        "optional, the first one is not. Please make sure to "
                        "give at least the first one.",
                        "MI_MC_11", False
                    )
                    self.success = False
                    return

                if splitted[1] == "":
                    for pair in possible_combinations:
                        if splitted[0] in pair:
                            chosen_combinations.add(pair)
                for pair in (
                    (splitted[0], splitted[1]), (splitted[1], splitted[0])
                ):
                    if pair in possible_combinations:
                        chosen_combinations.add(pair)

        return list(chosen_combinations)


class Structure():
    """What an oscillator looks like

    output formats:

    - struct corresponds to a single line/newstruct
      (depends of source) and is itself a list(1).

      - Each item in list(1) corresponds to a single residue, and is
        itself a list of 2 items. The first item contains the residue
        name (is a list of str), the second item contains the atom
        names. The second item is itself a list(2).
      - Each item in list(2) corresponds to an atom and is itself a
        list of str.

    - bonds corresponds to a single line/newstruct
      (depends of source) and is itself a list(1).

      - Each item in list(1) corresponds to a bond and is a list of
        two items. These are the indices of the two atoms that form
        the bond.


    Parameters
    ----------
    struct : list of list of list of list of str
        Describes the names of all parts of this oscillator, see above
        for further explanation of the format.
    bonds : list of list of ints
        Gives all pairs of atom indices that should be bound together.

    Attributes
    ----------
    residues : list of :class:`~GMAP.src.tools.MapReader.Residue`
        What atom/residue names go into each of the residues.
    bonds : list of list of ints
        What bonds make up the oscillator.
    indices : dict of int: tuple of int pairs
        The keys are the indices of atoms in the entire oscillator, the
        values show where that atom is located. The first int in the
        value is the index of the residue, the second int is the index
        of the atom, within that residue.
    indices_per_residue : dict of int: list of int pairs
        The keys are the indices of the residue, the values are all
        oscillator-indices of the atoms (like the keys in self.indices).
    indices_inv : dict of typle of int: int pairs
        Same as self.indices, but the keys and values have been
        switched.
    success : bool
        Whether there were any problems encountered - a problem means
        that the map the instance belongs to cannot be used.
    """

    def __init__(self, struct, bonds):
        self.residues = [Residue(res) for res in struct]
        self.bonds = bonds

        self.indices = {}
        self.indices_per_residue = {}
        ix = 0
        for res_ix, residue in enumerate(self.residues):
            local_ix = 0
            self.indices_per_residue[res_ix] = []
            for _ in residue.atoms:
                self.indices[ix] = (res_ix, local_ix)
                self.indices_per_residue[res_ix].append(ix)
                local_ix += 1
                ix += 1
        self.indices_inv = {val: key for key, val in self.indices.items()}

        if len(self.residues) > 1:
            self.check_bonds()
        else:
            self.success = True

    def __str__(self):
        return f"{self.__class__.__name__}({str(self.residues)})"

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.residues)})"

    def check_bonds(self):
        """Confirms whether supplied bonds link all residues

        A multi-residue oscillator can only be properly defined and
        found using the existing syntax if the parts within different
        residues are bonded together. This function checks whether
        the supplied bonds are enough to confirm that the different
        residues actually lock together.
        """

        # It's already been checked/confirmed that all indices in bonds exist.
        # now, see if the bonds couple the multiple residues.

        resnums = [set([ix]) for ix in range(len(self.residues))]
        for bond in self.bonds:
            res1 = self.indices[bond[0]][0]
            res2 = self.indices[bond[1]][0]
            newset = resnums[res1] | resnums[res2]
            resnums[res1] = newset
            resnums[res2] = newset
        if len(resnums) != len(resnums[0]):
            self.success = False
        else:
            self.success = True


class Residue():
    """What a single residue of a structure (template) looks like.

    Parameters
    ----------
    residue : list of lists of str
        The names of the residue and atoms making up this residue

    Attributes
    ----------
    resnames : list of str
        The different names this residue is allowed to have.
    atoms : list of list of str
        The different names each of the atoms in this residue is allowed
        to have.
    """

    def __init__(self, residue):
        self.resnames = residue[0]
        self.atoms = residue[1]

    def __str__(self):
        return f"{self.__class__.__name__}({str([self.resnames, self.atoms])})"

    def __repr__(self):
        mylist = [self.resnames, self.atoms]
        return f"{self.__class__.__name__}({repr(mylist)})"


def manage_maps_singles(Files, Printer, RunPars, mapdict):
    """Initializes and manages the detected maps in singles.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    mapdict : dict of str: :class:`~GMAP.src.tools.MapReader.SingleMap` pairs
        Stores all the :class:`~GMAP.src.tools.MapReader.SingleMap` objects for
        each map supplied. The keys are the Map.name attributes corresponding
        to the maps stored as values.
    """

    for map_ in mapdict.values():
        map_.initialize(Files, Printer)

    mapdict = {map_.name: map_ for map_ in mapdict.values() if map_.success}
    RunPars.available_maps_singles = mapdict

    for map_choice in RunPars.maps_to_use:
        if map_choice not in mapdict:
            Printer.warning(
                f"\nThe map {map_choice} was requested for use. However, it "
                "either does not exist, or the map was loaded unsuccessfully "
                "due to issues with its definition.",
                "MI_MM_1", True
            )

    requested_mapdict = {
        map_.name: map_ for map_ in mapdict.values()
        if map_.name in RunPars.maps_to_use
    }
    RunPars.requested_mapdict = requested_mapdict
    if any(map_.Core.requires_bonds for map_ in requested_mapdict.values()):
        RunPars.detected_requires_bonds = True
    else:
        RunPars.detected_requires_bonds = False


def manage_maps_pairs(Files, Printer, RunPars, mapdict):
    """Initializes and manages the detected maps in singles.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    mapdict : dict of str: :class:`~GMAP.src.tools.MapReader.PairMap` pairs
        Stores all the :class:`~GMAP.src.tools.MapReader.PairMap` objects for
        each map supplied. The keys are the Map.name attributes corresponding
        to the maps stored as values.
    """

    for map_ in mapdict.values():
        map_.initialize(Files, Printer)

    mapdict = {map_.name: map_ for map_ in mapdict.values() if map_.success}
    RunPars.available_maps_pairs = mapdict

    for coupmapname, pairs in RunPars.coupling_v_pair_dict.items():
        # check if the requested map exists
        if coupmapname not in mapdict and coupmapname is not None:
            Printer.warning(
                f"\nThe map {coupmapname} was requested for use in "
                "couplings. However, it "
                "either does not exist, or the map was loaded unsuccessfully "
                "due to issues with its definition.",
                "MI_MM_1", True
            )
        elif coupmapname is None:
            continue

        coupmap = mapdict[coupmapname]

        for pair in pairs:
            # check if the map can deal with these kinds of singles
            wrong_singles = [
                osc for osc in pair if osc not in coupmap.Core.allowed_singles]
            if wrong_singles:
                printstr = " and ".join(pair)
                Printer.warning(
                    f"\nThe map {coupmapname} was requested for use in "
                    "couplings. "
                    f"However, it cannot deal with singles of type {printstr}"
                    ", which were requested. Please use a different map for "
                    "these.", "MI_MM_3", True
                )

            # check if the map can deal with this exact coupling
            if pair not in coupmap.Core.valid_combinations:
                printstr = " and ".join(pair)
                Printer.warning(
                    f"\nThe map {coupmapname} was requested for use in "
                    "couplings. "
                    f"However, it cannot couple oscillators of type {printstr}"
                    " together, which was requested. Please use a different "
                    "map for this.", "MI_MM_4", True
                )

    # just have to check if all requested coupling maps have indeed been
    # read/loaded in successfully.
    # Due to how the coupling-pair dict was built, we only consider maps
    # that couple oscillators that were requested by maps_to_use.
    requested_mapdict = {
        map_.name: map_ for map_ in mapdict.values()
        if map_.name in RunPars.coupling_v_pair_dict.keys()
    }
    RunPars.requested_pairmapdict = requested_mapdict

    # first check if all requested maps are valid till here
    for coupmap in requested_mapdict.values():
        coupmap.check_singles(RunPars, Printer)

    # then, check if all requested maps are also still valid after paircheck.
    # new checks need to be done as long as new maps are found as dependencies.
    # any found dependencies are added to the dict.
    requested_maps = set()
    new_requested_maps = set(requested_mapdict.keys())
    while requested_maps != new_requested_maps:
        requested_maps = new_requested_maps  # save old one
        # we can't loop over the dict, as it might change size.
        for coupmapname in requested_maps:
            coupmap = requested_mapdict[coupmapname]
            coupmap.check_pairs(RunPars, Printer)
        new_requested_maps = set(requested_mapdict.keys())

    # loop is quit after no new maps were found. This means the last mapcheck
    # did not find any new ones - all present ones were checked for pair-map
    # dependencies -> if any were missing anything, the program would have
    # quit by now -> all desired maps are there!

    # --------------------------------------------------------------

    # next: check if all required pairs exist
    # If a map requires a pair, that pair should also be able to treat
    # all oscillators that the initial coupmap was supposed to treat

    # is it? Maybe not - maybe a map knows only a certain subset will be
    # passed on to certain maps - alternative is to just allow a map if
    # it passed before without issue. Then, when all oscillators have been
    # found, feed all maps their oscillator pairs, have them shove some
    # onto others, and after that shoving passed, see if the new matches are
    # valid. If they are, let all maps see their oscillator pairs again, and
    # allow them to shove again. Repeat until shoving does not result in
    # changes anymore -> thats the configuration we'll use.


def scan_mapdirs(mapdirs, maptype):
    """Gives a list of newly-generated Map objects

    Given a list of paths (each representing a map directory), create a Map
    object for each map found, which will be filled later.

    Parameters
    ----------
    mapdirs : list of pathlib.Path
        A list of directories which should be scanned for maps. This object
        is created by :func:`~GMAP.src.tools.ParameterParser.find_mapdir`.
    maptype : str
        Either 'Singles' for getting singles maps, or 'Pairs' for getting
        pairs maps.

    Returns
    -------
    all_maps : dict of str: :class:`Map` pairs
        Depending on the choice for the parameter maptype, these are
        either of type :class:`SingleMap` or :class:`PairMap`
    """

    match maptype:
        case "Singles":
            useclass = SingleMap
        case "Pairs":
            useclass = PairMap
        case _:
            return {}

    all_maps = {}
    for direc in mapdirs:
        subdirs = [item for item in [*direc.iterdir()] if item.is_dir()]

        available_files = [
            item for item in [*direc.iterdir()]
            if item.is_file()
            and GM_FH.check_file_readability(None, item)
        ]

        for subdir in subdirs:
            if subdir.name == maptype:
                available_files_sub = [
                    item for item in [*subdir.iterdir()]
                    if item.is_file()
                    and GM_FH.check_file_readability(None, item)
                ]
                ssdirs = [
                    item.resolve() for item in [*subdir.iterdir()]
                    if item.is_dir()
                ]

                for ssdir in ssdirs:
                    map_ = useclass(
                        ssdir, available_files_sub + available_files)
                    all_maps[map_.name] = map_
    return all_maps
