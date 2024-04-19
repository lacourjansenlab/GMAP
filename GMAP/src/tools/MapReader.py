
# standard library imports
import importlib
import sys

# local imports
import GMAP.src.tools.DefaultMapFunctions as GM_DMF
import GMAP.src.tools.FileHandler as GM_FH
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
        else:
            self.RunPars = None

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
          GM_get_dipole and GM_get_rotation matrix based on core.

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

        self.Core = Core(Printer, self)
        if not self.Core.success:
            self.success = False
            return

        # adding GM_get_dipole and GM_get_rotation_matrix to self.code.
        self.code_add_builds(Printer)
        if not self.success:
            return

        self.complete_code(("get_VEG_ref",), ({
            "map_": self,
            "Printer": Printer
        },))

        # Add in the remaining code
        self.complete_code((
            "post_init",
            "pre_run",
            "pre_frame",
            "post_frame",
            "post_run"
        ))

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
            all_to_add = all_to_add = [
                file for files in self.rawcore.get("add_corefile", [])
                for file in files
            ]
            self.rawcore["add_corefile"] = []

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
            suffix)
        """

        if not kwargslist:
            kwargslist = [{}] * len(funcnames)

        for funcname, kwargs in zip(funcnames, kwargslist):
            if not hasattr(self.code, "GM_" + funcname):
                setattr(
                    self.code, "GM_" + funcname,
                    getattr(GM_DMF, "get_" + funcname)(**kwargs)
                )

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
            "get_dipole"
        ]
        kwargs_for_build = [{
            "map_": self,
            "Printer": Printer
        }]

        # If the code doesn't contain a function for getting the dipole, make
        # sure the two necessary keywords are there.
        if not hasattr(self.code, "GM_get_dipole"):
            if not all(
                keyword in self.rawcore for keyword in ("r_vec", "r_pos")
            ):
                Printer.warning(
                    f"\nThe file {self.corepath} does not contain a "
                    "definition of "
                    "r_vec and/or r_pos. These two variables have to be "
                    "present if the map's main.py file does not contain "
                    "the function 'GM_get_dipole'.",
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
            Printer.warning(
                f"\nCould not find the file {filepath}. This file is "
                "required for the map to function. Please consult the "
                "information of this map, or contact the developer of "
                "this map.",
                "MI_MR_2", False
            )
            self.success = False
            return None

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

        Returns
        -------
        core_contents : dict of str - list of str pairs
            The contents of the file, not yet analyzed for validity.
        """

        if file_contents is None:
            file_contents = {}

        with open(filepath) as fhand:
            for line in fhand:
                line = Map.cleanline(line)
                if line:
                    file_contents = Map.parse_core_line(
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
        if keyword in ("functional_group", "add_corefile", "influencer_group"):
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


class Core():
    """Contains all information regarding a single core.txt file.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
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
            else:
                self.requires_bonds = False
        else:
            self.requires_bonds = False

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
        # dpr(struct)
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
        # dpr(resnums)
        for bond in self.bonds:
            res1 = self.indices[bond[0]][0]
            res2 = self.indices[bond[1]][0]
            newset = resnums[res1] | resnums[res2]
            resnums[res1] = newset
            resnums[res2] = newset
            # dpr(resnums)
        # dpr(len(resnums), len(resnums[0]))
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


def manage_maps(Files, Printer, RunPars, mapdict):
    for map_ in mapdict.values():
        map_.initialize(Files, Printer)

    for map_ in mapdict:
        dpr(map_)
    mapdict = {map_.name: map_ for map_ in mapdict.values() if map_.success}

    # dpr("successful:")
    # for map_ in mapdict.values():
    #     dpr(map_.name)
    #     dpr(map_.Core.functional_group)

    for map_choice in RunPars.maps_to_use:
        if map_choice not in mapdict:
            Printer.warning(
                f"The map {map_choice} was requested for use. However, it "
                "either does not exist, or the map was loaded unsuccessfully "
                "due to issues with its definition.",
                "MI_GEM_1", True
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


def scan_mapdirs(mapdirs):
    """Gives a list of newly-generated Map objects

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

        available_files = [
            item for item in [*direc.iterdir()]
            if item.is_file()
            and GM_FH.check_file_readability(None, item)
        ]

        for subdir in subdirs:
            if subdir.name in lookfor:
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
                map_ = Map(ssdir, available_files_sub + available_files)
                all_maps[map_.name] = map_
    return all_maps
