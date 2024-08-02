
# standard library imports
from pathlib import Path

# 3rd party imports
import numpy as np

# local imports
import GMAP.src.tools.constants as GM_con
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.MapReader as GM_MR
import GMAP.src.tools.PrintTools as GM_PT


class RefPars:
    """Deals with reference parameters

    To allow for easier use of the program, users are not required to specify
    a choice for
    each separate parameter. However, the program needs a default choice for
    each parameter. Instead of hard-coding these choices (or parameters in
    general), they are specified in a file. The reference file not only
    contains default choices, but also defines what the expected datatype
    for each choice is.

    Each map (see :ref:`adding a new map<UserGuide_page_adding_map>`) can
    also have it's own selection of parameters, stored in its own parameter
    file. See :ref:`parameters.ref<UserGuide_page_map_parameters>` for
    an explanation of the expected format.

    .. note ::
        Users of the program are probably looking for the
        :ref:`parameters.ref<UserGuide_page_map_parameters>` page.

    Parameters
    ----------
    fname : pathlib.Path
        The absolute path to the file that contains all desired parameters
    is_main : bool, default=True
        Whether this refpars object is the main one.

    See Also
    --------
    RawPars
        The class containing parameter choices from other sources
    RunPars
        The class containing the final parameter choices after combining all
        input sources.

    Attributes
    ----------
    fname : pathlib.Path
        The absolute path to the file that contains all desired parameters
    nondefcount : int
        The amount of path-type parameters encountered that have no choice
        determined in the reference parameter file. Every time one is found,
        this number is used to generate a temporary filename so the run can
        continue. Then, the number is incremented by one to prevent duplicate
        file names.
    options : dict
        Some parameters don't allow free choice, but instead require you
        to pick from a certain list. `options` contains that list. Its
        keys are the parameter names, the values are the choices available
        for that specific parameter.
    choices : dict
        Each parameter requires a choice. Default choices are stored in here.
        The keys are the parameter names, the values are the default choice(s)
        for each parameter. Note that for some parameters, it doesn't make
        sense for there to be a default choice, these are excluded from this
        dict, and can be found in the attribute `not_expected_in_deffile`.
    shorthands : dict
        Some parameters have very long names, which makes them annoying to
        specify on the command line. In the reffile a shorthand version of
        their name can be supplied, which the user can use instead. This dict
        stores the given shorthands as keys, the corresponding parameters they
        belong to are stored as values.
    organized_filepars : dict
        Some file paths are expected relative to their corresponding directory
        (although this behaviour can always be omitted by using absolute
        paths for the files). This dict stores for each directory-specifying
        parameter (keys) which file-specifying paramters are expected relative
        to it (values)
    organized_filepars_id : dict
        The behaviour described under the attribute `organized_filepars` is
        made possible by supplying each directory (and its files) an
        identifying shorthand. This dict stores the ids as keys, and their
        respective directory-specifying parameter as values.
    allfilepars : list of str
        contains all parameters of type path.
    filepars_create : list of str
        Contains the parameters which have a path/filename that is not
        expected to exist when first starting the program, but rather will be
        created during runtime
    intpars : list of str
        contains all parameters with a choice of type int.
    floatpars : list of str
        contains all parameters with a choice of type float.
    boolpars : list of str
        contains all parameters with a choice of type bool.
    strpars : list of str
        contains all parameters with a choice of type str.
    not_expected_in_deffile : list of str
        A list of parameters which are not expected (and allowed) to define a
        choice in reference (or default) parameter files.
    maybe_list : list of str
        Some parameters allow more than one choice to be given. All these
        parameters are stored in this list, but must also be stored depending
        on the expected type of the items in the list.

    """

    def __init__(self, fname, is_main=True):
        self.is_main = is_main
        self.fname = fname.resolve()
        self.add_groups()
        self.nondefcount = 0

        if self.is_main:
            self.compounds = ("couplings_to_use",)
        else:
            self.compounds = tuple()

        self.parse_refparfile(self.parse_line_type_protected)
        self.parse_refparfile(self.parse_line_choice_protected)

        # path-type parameters cannot also request a choice.
        for parname in self.allfilepars:
            if parname in self.options:
                GM_PT.Printer().warning(
                    "\nDue to path conflicts, reference files may not "
                    "contain options for path-type parameters. "
                    f"The affected file is {self.fname}",
                    "SU_FP_9", True, GMAPerrclass=GM_Ex.GmapTypeError
                )

        # for fixing intertwined / more convoluted parameters (main file only)
        if is_main:
            self.resolve()

    @classmethod
    def add_reffile(cls, fname, base_RefPars):
        """
        When the default parameter file given by the user is of .ref format
        instead of .txt, it ends up here. How are .ref files treated different?
            - most importantly: format! A .ref file is formatted differently
              from a .txt.
            - While a .txt only stores the choice for each parameter, the .ref
              also stores the allowed options. This would allow users to impose
              stricter limits. Is this actually useful???
        """
        GM_PT.Printer().warning(
            "\nNot implemented yet!",
            "SU_FP_1", True, GMAPerrclass=GM_Ex.GmapNotImplementedError
        )

    def add_groups(self):
        """ Initializes all attributes collecting parameter names

        This method is called by self.__init__. For explanation/list of the
        generated attributes, see :class:`RefPars`

        """

        self.options = {}  # key = parname, val = possible options
        self.choices = {}  # key = parname, val = actual choice
        self.shorthands = {}  # key = shorthand, val = actual parname

        # -----
        # Path-type parameters
        # -----

        # a dictionary where the key is a directory, the value is a list of
        # files expected in that directory
        self.organized_filepars = {}  # contains parameter names only
        self.organized_filepars_id = {}  # contains the translation key
        self.allfilepars = []  # a list of all parameters dealing with files

        # When testing if requested files exist, runpar needs to treat these
        # differently
        self.filepars_create = []  # a list of all pars that will create a file

        # -----
        # other-type parameters
        # -----
        self.intpars = []
        self.floatpars = []
        self.boolpars = []
        self.strpars = []

        # -----
        # special parameter-type groups
        # Any parameter in here should also be in some other place - this is
        # an extra grouping of things.
        # -----
        self.not_expected_in_deffile = []
        self.maybe_list = []

    def parse_refparfile(self, func):
        """ Apply provided function on each line of the file

        Loops through lines of given file. Each line is stripped of comments,
        and empty lines are ignored. For each remaining line, the function
        func is called.

        Parameters
        ----------
        func : function or method
            The function that is applied on each line of the file (after
            cleaning that line)
        """

        with open(self.fname) as file:
            for line in file:
                line = cleanline(line).strip()  # remove all comments
                if len(line) == 0:  # ignore all empty lines
                    continue

                linelist = line.split()
                if len(linelist) == 1:
                    GM_PT.Printer().warning(
                        "\nThe following problem occured when reading the "
                        f"reference parameter file {self.fname}"
                        "\n\nOne of the lines contains only one item, while "
                        "key-value pairs are expected. Quitting!",
                        "SU_FP_2", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
                    )

                # now, line must have at least length 2. Start interpreting!
                func(line, linelist)

    def parse_line_type_protected(self, line, linelist):
        """Wrapper for parse_line_type

        Also triggers any errors stopping the program when needed.

        Parameters
        ----------
        line : str
            The line of text that must be parsed - just here for printing
            purposes.
        linelist : list of str
            same contents as line, but processed and split into a format
            usable for :meth:`parse_line_type`.
        """

        try:
            self.parse_line_type(linelist)
        except (TypeError, KeyError) as ex:
            if isinstance(ex, TypeError):
                GMAPerr = GM_Ex.GmapTypeError
            else:
                GMAPerr = GM_Ex.GmapKeyError
            GM_PT.Printer().warning(
                "\nCould not interpret the parameter name on the following "
                f"line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_3", True, exception=ex, GMAPerrclass=GMAPerr
            )
        except Exception as ex:
            GM_PT.Printer().warning(
                "\nEncountered an error while parsing the parameter name "
                "on the "
                f"following line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_4", True, exception=ex,
                GMAPerrclass=GM_Ex.GmapFileSyntaxError
            )

    def parse_line_type(self, linelist):
        """Extracts the type of the parameter specified on the given line

        By analyzing the type-code specified in the parameter.ref file,
        figures out what type is expected, and adds the (also extracted)
        parameter name to the correct list/dict attributes of this class
        for later use.

        Parameters
        ----------
        linelist : list of str
            The contents of a single line in the parameters.ref file, but
            processed and split into a usable format.
        """

        parname_raw = linelist[0]
        parchoice_raw = linelist[1:]

        parname, shorthand, partype = self.parse_key(parname_raw)
        if shorthand:
            self.shorthands[shorthand] = parname

        if parchoice_raw[0] == "[N/A]":
            self.not_expected_in_deffile.append(parname)

        # see if parameter might accept choice as list

        if partype[0] == "list":
            self.maybe_list.append(parname)
            del partype[0]

        match partype[0]:
            case "path":
                self.allfilepars.append(parname)
                match partype[1]:
                    case  "dir":
                        self.organized_filepars_id[partype[2]] = parname
                        self.organized_filepars[parname] = []
                    case "rel":
                        parent_dir = self.organized_filepars_id[partype[2]]
                        if len(partype) > 3 and partype[3] == "c":
                            self.filepars_create.append(parname)
                        self.organized_filepars[parent_dir].append(parname)
                    case "sep":
                        if len(partype) > 2 and partype[2] == "c":
                            self.filepars_create.append(parname)
                    case _:
                        raise KeyError
            case "int":
                self.intpars.append(parname)
            case "float":
                self.floatpars.append(parname)
            case "bool":
                self.boolpars.append(parname)
            case "str":
                self.strpars.append(parname)
            case _:
                raise TypeError

    def parse_line_choice_protected(self, line, linelist):
        """Wrapper for parse_line_choice

        Also triggers any errors stopping the program when needed.

        Parameters
        ----------
        line : str
            The line of text that must be parsed - just here for printing
            purposes.
        linelist : list of str
            same contents as line, but processed and split into a format
            usable for :meth:`parse_line_choice`.
        """

        try:
            self.parse_line_choice(linelist)
        except ValueError as ex:
            GM_PT.Printer().warning(
                "\nCould not interpret the parameter choice on the following "
                f"line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_5", True, exception=ex,
                GMAPerrclass=GM_Ex.GmapValueError
            )
        except IndexError as ex:
            GM_PT.Printer().warning(
                "\nDetected a wrong amount of choices for the parameter "
                "choice "
                f"on the following line:\n{line}"
                "\nWhile reading the following file as a reference file:\n"
                f"{self.fname}\nQuitting!",
                "SU_FP_6", True, exception=ex,
                GMAPerrclass=GM_Ex.GmapIndexError
            )
        except Exception as ex:
            GM_PT.Printer().warning(
                "\nEncountered an error while parsing the parameter choice on "
                f"the following line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_7", True, exception=ex,
                GMAPerrclass=GM_Ex.GmapFileSyntaxError
            )

    def parse_line_choice(self, linelist):
        """Extract the choice for a parameter specified on the given line

        Analizes all information regarding the choice and options. Also
        converts any choice/option into the datatype recognized by
        :meth:`parse_line_type`. Stores found information in self.options
        and self.choices.

        Parameters
        ----------
        linelist : list of str
            The contents of a single line in the parameters.ref file, but
            processed and split into a usable format.
        """

        # extract the parameter name we're looking at
        parname_raw = linelist[0]
        parchoice_raw = linelist[1:]
        parname = self.parse_key(parname_raw)[0]

        # if this parameter shouldn't be defined in a default file, there
        # will not be any useful information on this line.
        if parname in self.not_expected_in_deffile:
            return

        options = []
        choices = []

        # extract all bits of information, and store them in options (always),
        # and choices (if the option was surrounded by '[]').
        for bit_raw in parchoice_raw:
            if bit_raw[0] == "[" and bit_raw[-1] == "]":
                bit = bit_raw[1:-1]
                options.append(bit)
                choices.append(bit)
            else:
                options.append(bit_raw)

        # type swap!
        if parname in self.allfilepars:
            usetype = Path
        elif parname in self.intpars:
            usetype = int
        elif parname in self.floatpars:
            usetype = float
        elif parname in self.boolpars:
            usetype = bool
        elif parname in self.strpars:
            usetype = str
        else:
            raise TypeError

        # bools need special care
        trueicators = ("true", "t")
        falseicators = ("false", "f")
        if usetype is bool:
            if any(
                x.lower() not in trueicators and x.lower() not in falseicators
                for x in options+choices
            ):
                raise ValueError
            options = [1 if x.lower() in trueicators else 0 for x in options]
            choices = [1 if x.lower() in trueicators else 0 for x in choices]

        options = [usetype(x) for x in options]
        choices = [usetype(x) for x in choices]

        # if at least one pair of square brackets (selected items), that
        # indicates that there are only limited choices, instead of general
        if len(choices) != 0:
            if (parname not in self.maybe_list) and (len(choices) != 1):
                raise IndexError
            else:
                self.options[parname] = options
                self.choices[parname] = choices
        # if there is no square brackets (selected items), that indicates that
        # there is free parameter choice, so no need to save allowed options
        else:
            self.choices[parname] = options

    def resolve(self):
        """Fixes intertwined/special parameters the standard parser can't fix
        """

        # influencers - we need some defaults, but they should not clash in any
        # way.... in the default file, top one takes precedence.
        for parameter in self.maybe_list:
            if parameter in ("influencers_whitelist", "influencers_blacklist"):
                break
        else:
            GM_PT.Printer().warning(
                "Encountered an issue with the following reference parameter "
                f"file: {self.fname}. The file should contain the parameters "
                "'influencers_whitelist' and 'influencers_blacklist', but "
                "contains neither.",
                "SU_FP_8", True, GMAPerrclass=GM_Ex.GmapParameterError
            )

        self.maybe_list.append("influencers")
        if parameter == "influencers_whitelist":
            self.choices["influencers"] = self.choices[parameter]
        elif parameter == "influencers_blacklist":
            # invert the choice by subtracting the blacklist choice from all
            self.choices["influencers"] = [":All", "-", "("] + self.choices[
                parameter
            ] + [")"]

        # Checking radii for estatic sphere
        estatic_range = self.choices.get("estatic_range", [1])[0]
        if estatic_range < 0:
            GM_PT.Printer().warning(
                "\nEncountered an issue with the following parameter source: "
                f"{self.fname}. The parameter estatic_range can only take a "
                "positive value, but a negative one was detected. Please make "
                "sure it has a positive value.",
                "SU_FP_7", True, GMAPerrclass=GM_Ex.GmapValueError
            )
        estatic_smooth_range = self.choices.get("estatic_smooth_range", [1])[0]
        if estatic_smooth_range < 0:
            GM_PT.Printer().warning(
                "\nEncountered an issue with the following parameter source: "
                f"{self.fname}. The parameter estatic_smooth_range can only "
                "take a positive value, but a negative one was detected. "
                "Please make sure it has a positive value.",
                "SU_FP_7", True, GMAPerrclass=GM_Ex.GmapValueError
            )

        if self.choices["hamiltonian_units"][0] == "cm-1":
            self.choices["hamiltonian_multiplier"] = [1]
        else:  # eV
            self.choices["hamiltonian_multiplier"] = [GM_con.cm2eV]

        if self.choices["energies_units"][0] == "cm-1":
            self.choices["energies_multiplier"] = [1]
        else:  # eV
            self.choices["energies_multiplier"] = [GM_con.cm2eV]

        if self.choices["dipoles_units"][0] == "Debye":
            self.choices["dipoles_multiplier"] = [1]
        else:  # ea0
            self.choices["dipoles_multiplier"] = [GM_con.Debye2ea0]

        if self.choices["raman_units"][0] == "none":
            self.choices["raman_multiplier"] = [1]
        # else:
        # There is only one unit option for raman at the moment, as the
        # units used in raman are a bit (very) confusing. If we ever want
        # to add more, this is where they go!

        match self.choices["positions_units"][0]:
            case "Ang":
                self.choices["positions_multiplier"] = [1]
            case "Bohr":
                self.choices["positions_multiplier"] = [GM_con.ang2bohr]
            case "nm":
                self.choices["positions_multiplier"] = [0.1]

        match self.choices["doublepos_units"][0]:
            case "Ang":
                self.choices["doublepos_multiplier"] = [1]
            case "Bohr":
                self.choices["doublepos_multiplier"] = [GM_con.ang2bohr]
            case "nm":
                self.choices["doublepos_multiplier"] = [0.1]

    @staticmethod
    def parse_key(string):
        """Extracts parameter name, shorthand and type from key in file

        The key (first part of a line) in the file storing the reference
        parameters has a more complex shape, so it can also encode a shorthand
        if needed, and the type the choice for this parameter is expected to
        have. This method extracts those parts.

        Parameters
        ----------
        string : str
            The text to extract a name, shorthand and type from

        Returns
        -------
        key_name : str
            The actual parameter name (the one users will provide when
            providing inputs)
        key_shorthand : str
            The shorthand that can be used on the command line for providing
            a choice for this parameter
        key_dtype : list of str
            The datatype expected for this parameter. See
            :ref:`parameters.ref<UserGuide_page_map_parameters>` for more
            explanation on datatypes.
        """

        if "(" in string:
            key_name, temp = string.split("(")
            key_shorthand, key_dtype = temp.split(")")
            key_dtype = key_dtype[1:]
        else:
            key_name, key_dtype = string.split("[")
            key_shorthand = ""
        key_dtype = key_dtype.strip("]").split("_")
        return key_name, key_shorthand, key_dtype


class RawPars:
    """Stores a set of choices from a single source

    Choices can be specified in multiple places. Command line, input parameter
    file, or a default parameter file. Each of those sources gets its own
    instance of this class, storing the choices specified in that source.

    .. warning ::
        The basic __init__ of this class is not meant to be used standalone.
        Instead, this class is supposed to be used through any of the following
        constructing classmethods:
        :meth:`from_dict`, :meth:`from_file`, :meth:`from_cmdline`

    Parameters
    ----------
    fname : str
        The name of the file whose contents are stored
    is_default : bool
        Whether the file is a default parameter file. In other words, the file
        is expected to be complete.

            Note that 'Complete' can mean multiple things. Here, we expect
            only that all
            parameters given in the GMAP reference parameter file are present
            (except those marked as not being allowed to be in there).
            However, if even a single parameter from a certain map is included
            in the file, *all* parameters from that specific map must be
            present.
    given_dict : dict
        The parameters (keys) and their choices (values).
    RefPars : :class:`RefPars`
        Contains all parameters that might be found in `given_dict`.

    See Also
    --------
    RefPars
        The class containing all available parameters, and extra information
        about them
    RunPars
        The class containing the final parameters choices after combining all
        input sources.

    Attributes
    ----------
    fname : pathlib.Path or str
        The absolute path to the file that contains the parameter choices. In
        case the source is not a file but the command line, the path is the
        string 'command line' instead.
    is_default : bool
        Whether the set of parameter choices is supposed to be complete.
    choices : dict
        Stores parameter names as keys, and the choice for the parameter as
        values. Beware the exact typing: **all** parameters (not only
        list-type ones) have their choice stored as a list. The items in the
        list are of the correct type.
    not_found : dict
        When a source is first analyzed for parameters, only the GMAP-based
        parameters are known. Therefore, inherently, any map-specific
        parameters cannot be recognized/identified, and parsed. During the
        first pass, any map-specific-looking parameters are stored in here,
        so they can be analyzed during a second pass. Keys in this dictionary
        are the full parameter names (including the map-name), values are the
        not-so-parsed choices.

    """

    def __init__(self, fname, is_default, given_dict, RefPars):
        self.fname = fname
        self.is_default = is_default

        self.extract_choices(given_dict, RefPars)
        if is_default:
            self.check_completeness(RefPars)

        # if the class isn't empty
        if given_dict:
            self.resolve()

    @classmethod
    def create_empty(cls):
        """Create an instance of this class without any data

        .. seealso ::
            :meth:`from_dict`, :meth:`from_file`, :meth:`from_cmdline`

        Returns
        -------
        instance : :class:`RawPars`
            A newly generated instance.
        """

        return cls(None, False, {}, {})

    @classmethod
    def from_dict(cls, fname, given_dict, RefPars, is_default):
        """Create an instance of this class for parameters stored in a dict.

        .. seealso ::
            :meth:`create_empty`, :meth:`from_file`, :meth:`from_cmdline`

        Parameters
        ----------
        fname : pathlib.Path
            The name of the file from which the data in `given_dict` was
            obtained
        given_dict : dict
            Contains parameter choices. Keys are the parameter names (str),
            values are lists containing all choices (str). Lists are still
            expected when there are 0 or 1 choices.
        RefPars : :class:`RefPars`
            Contains all parameters that might be found in `given_dict`.
        is_default : bool
            Whether this is a default file (i.e. complete, see
            :class:`RawPars`)

        Returns
        -------
        instance : :class:`RawPars`
            A newly generated instance with all choices parsed and stored.
        """

        if len(given_dict) == 0:
            instance = cls.create_empty()
            return instance

        return cls(fname, is_default, given_dict, RefPars)

    @classmethod
    def from_file(cls, fname, RefPars, is_default):
        """Create an instance of this class for parameters stored in a file.

        First obtains a dict from the file, then uses :meth:`from_dict`

        .. seealso ::
            :meth:`create_empty`, :meth:`from_dict`, :meth:`from_cmdline`

        Parameters
        ----------
        fname : pathlib.Path
            The name of the file from which to obtain the parameters
        RefPars : :class:`RefPars`
            Contains all parameters that might be found in `given_dict`.
        is_default : bool
            Whether this is a default file (i.e. complete, see
            :class:`RawPars`)

        Returns
        -------
        instance : :class:`RawPars`
            A newly generated instance with all choices parsed and stored.
        """

        with open(fname) as file:
            given_dict = get_pardict(file, RefPars.compounds)

        instance = cls.from_dict(
            fname, given_dict, RefPars, is_default
        )
        return instance

    @classmethod
    def from_cmdline(
        cls, cmdargs, RefPars, maprefpars_dict, is_default
    ):
        """Create an instance of this class for parameters in the command line

        A method more different from the others, as it has to do some parsing,
        too. Also immediately deals with map-specific parameters, while
        instances created from other sources need an extra pass for those.

        .. seealso ::
            :meth:`create_empty`, :meth:`from_dict`, :meth:`from_file`

        Parameters
        ----------
        cmdargs : list of str
            A slice from the list generated using sys.argv
        RefPars : :class:`RefPars`
            Contains all parameters that might be found in `given_dict`.
        maprefpars_dict : dict
            A dictionary containing the RefPars objects for all recognized
            maps. Keys are the map names, values are their RefPars object.
        is_default : bool
            Whether this is a default file (i.e. complete, see
            :class:`RawPars`)

        Returns
        -------
        instance : :class:`RawPars`
            A newly generated instance with all choices parsed and stored.
        """

        # In order to read the command line, we need to know whether a
        # parameter takes arguments, and if so, how many. steps needed:
        # - Figure out what the parameter name is, and where it's from
        # - See if it actually exists
        # - extract num of expected arguments
        # - extract actual arguments

        temp_instance = cls(Path("command line"), False, {}, {})
        parfile_mock = []

        while len(cmdargs) > 0:
            # Step 1: Figure out what the parameter name is, and where its from

            #   - hyphens
            if not cmdargs[0].startswith("-"):
                GM_PT.Printer().warning(
                    "\nThe name of a parameter specified on the command line "
                    "should be preceeded with '-'.",
                    "SU_WP_1", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
                )
            curparraw = cmdargs.pop(0)
            curpar, curpar_tocheck, refpars_to_use = cls.parse_cmd_parname(
                curparraw, RefPars, maprefpars_dict
            )

            # Step 2: See if it actually exists
            found = temp_instance.check_par_existence(
                curpar, curpar_tocheck, refpars_to_use, None, False
            )[1]
            if not found:
                GM_PT.Printer().warning(
                    f"\nThe parameter {curpar} as specified on the command "
                    "line is not recognised. Please make sure you spelled "
                    "it correctly.",
                    "SU_WP_3", True, GMAPerrclass=GM_Ex.GmapKeyError
                )

            # Step 3: extract num of expected arguments, and also:
            # Step 4: extract actual arguments
            choice = cls.parse_cmd_choice(
                cmdargs, curpar, curpar_tocheck, refpars_to_use
            )

            parfile_mock.append(curpar + " " + " ".join(choice))
        pardict = get_pardict(parfile_mock, RefPars.compounds)

        instance = cls.from_dict(
            Path("command line"), pardict, RefPars, is_default
        )

        return instance

    @staticmethod
    def parse_cmd_parname(curparraw, RefPars, maprefpars_dict):
        """Identifies a parameter name specified on the command line

        Removes hyphens, figures out whether the name is shorthand or not,
        whether it belongs to the base program, or one of the maps, and
        whether (in the case of bools) the parameter is inverted using the
        nobool format. If it is, this invertion is not cancelled, the 'no'
        part is left in place.

        Parameters
        ----------
        curparraw : str
            The parameter name as specified on the command line
        RefPars : :class:`RefPars`
            Contains all parameters that might be found in `given_dict`.
        maprefpars_dict : dict
            A dictionary containing the RefPars objects for all recognized
            maps. Keys are the map names, values are their RefPars object.

        Returns
        -------
        curpar : str
            The full name of the parameter. Basically mapname.parname. If
            the parameter belongs to the main program, this is just parname.
        curpar_to_check : str
            The name of the parameter, without the map prefix - as it should
            be looked up in the refpars object.
        RefParsToUse : :class:`RefPars`
            The RefPars object to which the recognized parameter belongs.
        """

        curpar = curparraw.lstrip("-")
        hyphno = len(curparraw) - len(curpar)
        if hyphno == 1:
            expect_shorthand = True
        else:
            expect_shorthand = False

        warntext = (
            f"\nThe parameter {curpar} as specified on the command "
            "line is not recognised. Please make sure you spelled "
            "it correctly."
        )

        #   - maps (see what map this parameter belongs to)
        if '.' in curpar:
            curpar_list = curpar.split('.')
            try:
                RefParsToUse = maprefpars_dict[curpar_list[0]]
                curpar_tocheck = curpar_list[1]
            except KeyError as ex:
                GM_PT.Printer().warning(
                    warntext, "SU_WP_2", True, exception=ex,
                    GMAPerrclass=GM_Ex.GmapKeyError
                )

        #   - base program - expect its from here.
        else:
            RefParsToUse = RefPars
            curpar_tocheck = curpar

        #   - expand shorthands
        if expect_shorthand:
            found = False
            try:
                curpar_tocheck = RefParsToUse.shorthands[curpar_tocheck]
                found = True
                ex = None
            except Exception as excep:
                ex = excep

            if not found and curpar_tocheck[:2].lower().startswith("no"):
                try:
                    curpar_tocheck = "no" + RefParsToUse.shorthands[
                        curpar_tocheck[2:]
                    ]
                    found = True
                except Exception:
                    pass

            if not found:
                if "." in curpar:
                    warncode = "SU_WP_2"
                else:
                    warncode = "SU_WP_3"
                GM_PT.Printer().warning(
                    warntext, warncode, True, exception=ex,
                    GMAPerrclass=GM_Ex.GmapKeyError
                )

            if "." in curpar:
                curpar = curpar_list[0] + "." + curpar_tocheck
            else:
                curpar = curpar_tocheck

        return curpar, curpar_tocheck, RefParsToUse

    @staticmethod
    def parse_cmd_choice(
        cmdargs, curpar, curpar_tocheck, RefParsToUse
    ):
        """Extracts the choice from the command line

        Parameters
        ----------
        cmdargs : list of str
            A slice from the list generated using sys.argv
        curpar : str
            The full name of the parameter. Basically mapname.parname. If
            the parameter belongs to the main program, this is just parname.
        curpar_to_check : str
            The name of the parameter, without the map prefix - as it should
            be looked up in the refpars object.
        RefParsToUse : :class:`RefPars`
            The RefPars object to which the recognized parameter belongs.

        Returns
        -------
        choice : list of str
            The choice that was submitted on the command line, parsed to the
            same format as the values in the dict from a parameter file.
        """

        if curpar_tocheck in RefParsToUse.maybe_list:
            # Lists MUST always come with at least one choice.
            try:
                choice = [cmdargs.pop(0)]
            except IndexError as ex:
                GM_PT.Printer().warning(
                    f"\nThe parameter {curpar} specified in the command "
                    "line requires a choice to be given.",
                    "SU_WP_4", True, exception=ex,
                    GMAPerrclass=GM_Ex.GmapIndexError
                )

            warntext = (
                f"\nThe parameter {curpar} specified in the command line "
                "requires the last choice to be appended with '\\;'."
            )
            while not choice[-1].endswith("\\;"):
                try:
                    choice.append(cmdargs.pop(0))
                except IndexError:
                    GM_PT.Printer().warning(
                        warntext, "SU_WP_5", True,
                        GMAPerrclass=GM_Ex.GmapIndexError
                    )

                if choice[-1].startswith("-"):
                    GM_PT.Printer().warning(
                        warntext, "SU_WP_5", True,
                        GMAPerrclass=GM_Ex.GmapFileSyntaxError
                    )
            choice[-1] = choice[-1][:-2]

        else:
            # Here, we blindly assume that the user gave the correct
            # amount of choices (bools don't require them). Whether they
            # did will be verified at 'extract choices', a few lines down.
            try:
                if not cmdargs[0].startswith("-"):
                    choice = [cmdargs.pop(0)]
                else:
                    choice = []
            except Exception:
                choice = []

        return choice

    def extract_choices(self, given_dict, RefPars):
        """Takes each parameter and their choice from the dict for parsing

        Each pair is forwarded to the correct location for further parsing.
        Does not deal in-depth with map-specific parameters, unless the
        :class:`RawPars` instance is created specifically for that map.

        Parameters
        ----------
        given_dict : dict
            Contains parameter choices. Keys are the parameter names (str),
            values are lists containing all choices (str). Lists are still
            expected when there are 0 or 1 choices.
        RefPars : :class:`RefPars`
            Contains all parameters that might be found in `given_dict`.
        """

        self.choices = {}
        self.not_found = {}

        # lets find out about each parameter!
        for parname, choice in given_dict.items():
            choice, found, parname = self.check_par_existence(
                parname, parname, RefPars, choice
            )
            if found:
                if choice is not None:
                    self.choices[parname] = choice

            # anything that's left, is not part of base program

            # if parameter is expected to not belong to core, but mapping
            elif "." in parname:
                self.not_found[parname] = choice

            # parameter should belong to core, but isn't recognized
            else:
                if not RefPars.is_main:
                    # if for a map, re-find map name!
                    mapname = RefPars.fname.parent.name
                    parname = mapname + "." + parname
                GM_PT.Printer().warning(
                    f"\nUnknown parameter {parname} found in the file "
                    f"{self.fname}. "
                    "Please make sure you spelled it correctly.",
                    "SU_WP_6", True, GMAPerrclass=GM_Ex.GmapKeyError
                )

    def verify_choice(self, parname, choice, RefPars):
        """Check if the supplied choice is valid

        Checks performed:
            - Are there exactly enough choices given?
            - Can all choices be converted into the correct datatype?
            - If there is a limited set of options to chose from - is the
              provided choice allowed?

        Parameters
        ----------
        parname : str
            The name of the parameter whose choice is verified.
        choice : list of str
            The given choice.
        RefPars : :class:`RefPars`
            If the parameter has any available options, they are stored
            in here.

        Returns
        -------
        choice : list of any
            A homogenous list, containing the same information as supplied
            as the parameter `choice`, but converted to the correct datatype.
        """

        if RefPars.is_main:
            printname = parname
        else:
            printname = RefPars.fname.parent.name + "." + parname
        if len(choice) == 0:
            if self.is_default:
                GM_PT.Printer().warning(
                    f"\nNo choice detected for the parameter {printname} "
                    f"specified in the file {self.fname}. "
                    "All parameters must be specified for the file to be "
                    "used.",
                    "SU_WP_7", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
                )
            # This is a bool-type par - presence means 'True'
            elif parname in RefPars.boolpars:
                choice.append("true")
            else:
                GM_PT.Printer().warning(
                    f"\nNo choice detected for the parameter {printname} "
                    f"specified in the file {self.fname}. "
                    "Either remove the parameter line, or make a choice.",
                    "SU_WP_8", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
                )

        # if we expect a single choice, but multiple were given
        elif len(choice) > 1 and parname not in RefPars.maybe_list:
            GM_PT.Printer().warning(
                f"\nToo many choices given for the parameter {printname} "
                f"specified in the file {self.fname}. "
                "Please only specify one.",
                "SU_WP_9", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
            )

        # now, correct amount of arguments.
        errortext1 = (
            f"\nInvalid choice given for the parameter {printname} "
            f"specified in the file {self.fname}. "
            "Please refer to the manual for the allowed options."
        )
        errortext2 = (
            f"\nChoice given for the parameter {printname} specified in "
            "the file "
            f"{self.fname} is of the wrong type. "
            "Please refer to the manual for the expected type."
        )

        # type swap!
        if parname in RefPars.intpars:
            usetype = int
        elif parname in RefPars.floatpars:
            usetype = float
        elif parname in RefPars.allfilepars:
            usetype = Path
        elif parname in RefPars.boolpars:
            usetype = bool
        elif parname in RefPars.strpars:
            usetype = str
        else:
            # This should not be reached - the parameter type parser already
            # caught this.
            raise TypeError

        if parname in RefPars.boolpars:  # bools need special care
            trueicators = ("true", "t")
            falseicators = ("false", "f")
            if any(
                x.lower() not in trueicators and x.lower() not in falseicators
                for x in choice
            ):
                GM_PT.Printer().warning(
                    errortext1, "SU_WP_10", True,
                    GMAPerrclass=GM_Ex.GmapValueError
                )
            choice = [1 if x.lower() in trueicators else 0 for x in choice]

        try:
            choice = [usetype(x) for x in choice]
        except Exception:
            GM_PT.Printer().warning(
                errortext2, "SU_WP_12", True,
                GMAPerrclass=GM_Ex.GmapTypeError
            )

        if parname not in RefPars.options:
            return choice

        if any(
            opt not in RefPars.options[parname] for opt in choice
        ):
            GM_PT.Printer().warning(
                errortext1, "SU_WP_11", True,
                GMAPerrclass=GM_Ex.GmapValueError
            )
        else:
            return choice

    def check_par_existence(
        self, parname_full, parname_refpars, RefPars, choice,
        do_verify=True
    ):
        """See if the given parameter exists within the supplied RefPars.

        After :meth:`extract_choices` found a
        parameter/choice pair that says it should be present in the supplied
        RefPars, it is given to this function to see whether it actually does.
        If so (and if requested), :meth:`verify_choice` is called to see if
        the supplied choice is valid, too.

        Parameters
        ----------
        parname_full : str
            The complete parameter name, needed for reporting errors.
        parname_refpars : str
            The parameter name as we expect to find it within RefPars
        RefPars : :class:`RefPars`
            The reference parameters in which the given parameter should occur
        choice : list
            The choice supplied as input
        do_verify : bool, default=True
            Whether the supplied choice should be verified.

        Returns
        -------
        choice : list
            The choice as returned by :meth:`verify_choice` if requested,
            otherwise as supplied
        found : bool
            Whether the requested parameter was found to exist.
        parname_refpars : str
            The name that we should look for in refpars. Most notably, if
            the supplied parameter was of nobool, the no is removed in this
            output.
        """

        found = False
        if parname_refpars in RefPars.choices:
            found = True
            if do_verify:
                # if the parameter name is in RefPars.compounds, this
                # parameter contains the information from multiple lines.
                if parname_refpars in RefPars.compounds:
                    choice = [self.verify_choice(
                        parname_refpars, subchoice, RefPars
                    ) for subchoice in choice]
                else:
                    choice = self.verify_choice(
                        parname_refpars, choice, RefPars
                    )
            if not do_verify or choice is None:
                return None, found, parname_refpars

        elif parname_refpars in RefPars.not_expected_in_deffile:
            found = True
            if self.is_default and len(choice) != 0:
                GM_PT.Printer().warning(
                    f"\nA choice for the parameter {parname_full} is "
                    "specified "
                    f"in the default parameter file {self.fname}. "
                    "However, default files cannot contain a choice for "
                    "this parameter. Please remove the parameter from the "
                    "file.",
                    "SU_WP_13", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            elif self.is_default:
                return None, found, parname_refpars
            else:
                if do_verify:
                    # if the parameter name is in RefPars.compounds, this
                    # parameter contains the information from multiple lines.
                    if parname_refpars in RefPars.compounds:
                        choice = [self.verify_choice(
                            parname_refpars, subchoice, RefPars
                        ) for subchoice in choice]
                    else:
                        choice = self.verify_choice(
                            parname_refpars, choice, RefPars
                        )
                if not do_verify or choice is None:
                    return None, found, parname_refpars

        # nobool format?
        elif (
            parname_refpars[:2].lower() == "no"
            and parname_refpars[2:] in RefPars.boolpars
        ):
            if not choice:
                newchoice = ["false"]
            else:
                trueicators = ("true", "t")
                newchoice = [
                    "false" if x.lower() in trueicators else "true"
                    for x in choice
                ]
            choice, found, parname_refpars = self.check_par_existence(
                parname_full[2:], parname_refpars[2:], RefPars,
                newchoice, do_verify
            )

        return choice, found, parname_refpars

    def check_completeness(self, RefPars):
        """Check if all required parameters are present

        When the file is marked as being default, this method makes sure that
        all parameters are present.

        If a default parameter file contains any map-related choices, then
        this function is called with the RefPars of that specific map, as it
        then must contain all choices for that map.

        Parameters
        ----------
        RefPars : :class:`RefPars`
            Contains all parameters that should be present here.
        """

        for parname in RefPars.choices.keys():
            if parname not in self.choices:
                if self.is_default and parname in ("influencers"):
                    continue
                if not RefPars.is_main:
                    # if for a map, re-find map name!
                    mapname = RefPars.fname.parent.name
                    parname = mapname + "." + parname
                GM_PT.Printer().warning(
                    f"\nNo entry found for the parameter {parname} in the "
                    f"default parameter file {self.fname}. "
                    "All parameters must be specified for default files to "
                    "be used.",
                    "SU_WP_14", True, GMAPerrclass=GM_Ex.GmapParameterError
                )

    def resolve(self):
        """Fixes intertwined/special parameters the standard parser can't fix
        """

        # first - influencers!

        # see how many influencer parameters are present - only one can be!
        n_present = sum([parameter in (
            "influencers_whitelist",
            "influencers_blacklist",
            "influencers_file",
            "influencers_select_atoms"
        ) for parameter in self.choices])

        if n_present > 1 and not self.is_default:
            GM_PT.Printer().warning(
                "\nEncountered an issue with the following parameter source: "
                f"{self.fname}. The source should contain only one of the "
                "parameters 'influencers_whitelist', 'influencers_blacklist', "
                "'influencers_file' and influencers_select_atoms, but "
                "contains more than one.",
                "SU_WP_16", True, GMAPerrclass=GM_Ex.GmapParameterError
            )

        if "influencers_whitelist" in self.choices:
            self.choices["influencers"] = self.choices["influencers_whitelist"]
        elif "influencers_blacklist" in self.choices:
            # invert the choice by subtracting the blacklist choice from all
            self.choices["influencers"] = [":All", "-", "("] + self.choices[
                "influencers_blacklist"
            ] + [")"]
        elif "influencers_file" in self.choices:
            self.choices["influencers"] = self.choices["influencers_file"][0]
        elif "influencers_select_atoms" in self.choices:
            self.choices["influencers"] = " ".join(
                self.choices["influencers_select_atoms"]
            )

        # Checking radii for estatic sphere
        estatic_range = self.choices.get("estatic_range", [1])[0]
        if estatic_range < 0:
            GM_PT.Printer().warning(
                "\nEncountered an issue with the following parameter source: "
                f"{self.fname}. The parameter estatic_range can only take a "
                "positive value, but a negative one was detected. Please make "
                "sure it has a positive value.",
                "SU_WP_11", True, GMAPerrclass=GM_Ex.GmapValueError
            )
        estatic_smooth_range = self.choices.get("estatic_smooth_range", [1])[0]
        if estatic_smooth_range < 0:
            GM_PT.Printer().warning(
                "\nEncountered an issue with the following parameter source: "
                f"{self.fname}. The parameter estatic_smooth_range can only "
                "take a positive value, but a negative one was detected. "
                "Please make sure it has a positive value.",
                "SU_WP_11", True, GMAPerrclass=GM_Ex.GmapValueError
            )

        # next - frame numbers!
        start_frame = self.choices.get("start_frame", [None])[0]
        number_frames = self.choices.get("number_frames", [None])[0]
        stop_frame = self.choices.get("stop_frame", [None])[0]
        n_pars = len([
            x for x in (start_frame, number_frames, stop_frame)
            if x is not None
        ])

        msg = (
            "\nEncountered an issue with the following parameter source: "
            f"{self.fname}. This source can contain any combination of the "
            "parameters start_frame, number_frames and stop_frame, but the "
            "values should make sense: the value for stop_frame (if present) "
            "should always be bigger than both start_frame and number_frames, "
            "and if all three are present, the following equation should hold "
            "true: start_frame + number_frames = stop_frame"
        )

        if n_pars == 3:
            if start_frame + number_frames != stop_frame:
                GM_PT.Printer().warning(
                    msg, "SU_WP_17", True,
                    GMAPerrclass=GM_Ex.GmapParameterError
                )
        elif n_pars == 2:
            if start_frame is None and stop_frame < number_frames:
                GM_PT.Printer().warning(
                    msg, "SU_WP_17", True,
                    GMAPerrclass=GM_Ex.GmapParameterError
                )
            elif number_frames is None and stop_frame < start_frame:
                GM_PT.Printer().warning(
                    msg, "SU_WP_17", True,
                    GMAPerrclass=GM_Ex.GmapParameterError
                )

        # output units
        # if the multiplier is defined using set units, make the conversion.
        # if both, error. If none, also fine.
        if "hamiltonian_units" in self.choices:
            if self.is_default:  # for default, use multiplier
                pass
            elif "hamiltonian_multiplier" in self.choices:
                GM_PT.Printer().warning(
                    "\nEncountered an issue with the following parameter "
                    f"source: {self.fname}. The source should contain only "
                    "one of the parameters 'hamiltonian_units' and "
                    "'hamiltonian_multiplier', but contains both.",
                    "SU_WP_16", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            else:
                if self.choices["hamiltonian_units"][0] == "cm-1":
                    self.choices["hamiltonian_multiplier"] = [1]
                else:  # eV
                    self.choices["hamiltonian_multiplier"] = [GM_con.cm2eV]

        if "energies_units" in self.choices:
            if self.is_default:  # for default, use multiplier
                pass
            elif "energies_multiplier" in self.choices:
                GM_PT.Printer().warning(
                    "\nEncountered an issue with the following parameter "
                    f"source: {self.fname}. The source should contain only "
                    "one of the parameters 'energies_units' and "
                    "'energies_multiplier', but contains both.",
                    "SU_WP_16", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            else:
                if self.choices["energies_units"][0] == "cm-1":
                    self.choices["energies_multiplier"] = [1]
                else:  # eV
                    self.choices["energies_multiplier"] = [GM_con.cm2eV]

        if "dipoles_units" in self.choices:
            if self.is_default:  # for default, use multiplier
                pass
            elif "dipoles_multiplier" in self.choices:
                GM_PT.Printer().warning(
                    "\nEncountered an issue with the following parameter "
                    f"source: {self.fname}. The source should contain only "
                    "one of the parameters 'dipoles_units' and "
                    "'dipoles_multiplier', but contains both.",
                    "SU_WP_16", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            else:
                if self.choices["dipoles_units"][0] == "Debye":
                    self.choices["dipoles_multiplier"] = [1]
                else:  # eV
                    self.choices["dipoles_multiplier"] = [GM_con.Debye2ea0]

        if "raman_units" in self.choices:
            if self.is_default:  # for default, use multiplier
                pass
            elif "raman_multiplier" in self.choices:
                GM_PT.Printer().warning(
                    "\nEncountered an issue with the following parameter "
                    f"source: {self.fname}. The source should contain only "
                    "one of the parameters 'raman_units' and "
                    "'raman_multiplier', but contains both.",
                    "SU_WP_16", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            else:
                if self.choices["raman_units"][0] == "none":
                    self.choices["raman_multiplier"] = [1]
                # no else needed, only one option available.

        if "positions_units" in self.choices:
            if self.is_default:  # for default, use multiplier
                pass
            elif "positions_multiplier" in self.choices:
                GM_PT.Printer().warning(
                    "\nEncountered an issue with the following parameter "
                    f"source: {self.fname}. The source should contain only "
                    "one of the parameters 'positions_units' and "
                    "'positions_multiplier', but contains both.",
                    "SU_WP_16", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            else:
                match self.choices["positions_units"][0]:
                    case "Ang":
                        self.choices["positions_multiplier"] = [1]
                    case "Bohr":
                        self.choices["positions_multiplier"] = [
                            GM_con.ang2bohr]
                    case "nm":
                        self.choices["positions_multiplier"] = [0.1]

        if "doublepos_units" in self.choices:
            if self.is_default:  # for default, use multiplier
                pass
            elif "doublepos_multiplier" in self.choices:
                GM_PT.Printer().warning(
                    "\nEncountered an issue with the following parameter "
                    f"source: {self.fname}. The source should contain only "
                    "one of the parameters 'doublepos_units' and "
                    "'doublepos_multiplier', but contains both.",
                    "SU_WP_16", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            else:
                match self.choices["doublepos_units"][0]:
                    case "Ang":
                        self.choices["doublepos_multiplier"] = [1]
                    case "Bohr":
                        self.choices["doublepos_multiplier"] = [
                            GM_con.ang2bohr]
                    case "nm":
                        self.choices["doublepos_multiplier"] = [0.1]

    def finalize_map_pars(self):
        """Check whether `not_found` is empty

        This method is called after
        :meth:`~GMAP.src.tools.MapReader.Map.find_rawpars` is run for
        every available instance of
        :class:`~GMAP.src.tools.MapReader.Map`. Any parameters
        recognised there were removed from
        the `not_found` dictionary, so it should be empty, if all parameters
        were understood. Here we check if that is indeed the case.
        """
        if len(self.not_found.keys()) != 0:
            GM_PT.Printer().warning(
                f"\nUnknown parameter {list(self.not_found.keys())[0]} "
                "found in "
                "the "
                f"file {self.fname}. "
                "Please make sure you spelled it correctly.",
                "SU_WP_15", True, GMAPerrclass=GM_Ex.GmapKeyError
            )


class RunPars:
    """Stores the final choices used for the calculation

    Choices can be specified in multiple places. In the end, they have to be
    combined into a single set containing all parameters. This might mean
    that a single parameter is defined multiple times, each different. This
    is the intended order of places to look for choices: choices from the
    command line go first. Anything not specified there will be attempted to
    be retrieved from the input parameter file. Anything that is still missing
    will be retrieved from the default parameter file, and the final missing
    values will be retrieved from the reference parameter file.

    But shouldn't the default file contain all parameters, making the choices
    in the reference file redundant? Yes, for GMAP parameters, but no, not
    necessarily for map parameters. The default file doesn't have to contain
    any of those, so those still have to be retrieved from the (map specific)
    reference parameter file.

    .. note::
        This class has many attributes, all variable: each parameter in RefPars
        becomes an attribute. Same name, same capitalization, same everything.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    CmdPars : :class:`RawPars`
        Contains any parameter choices made on the command line
    InPars : :class:`RawPars`
        Contains any parameter choices made in the input parameter file
    DefPars : :class:`RawPars` or :class:`RefPars`
        Contains all default parameter choices. Might be RefPars, might be
        from a separate default parameters file.
    RefPars : :class:`RefPars`
        Contains all available parameters from GMAP itself (not map-specific)
    is_main : bool
        Whether this instance of RunPar belongs to the main program (and thus
        contains parameters about the runtime itself) - indicated by 'True',
        or if it belongs to an instance of
        :class:`~GMAP.src.tools.MapReader.Map` - indicated by 'False'.
    MainRunPars : :class:`RunPars` or None, default=None
        The instance of RunPars that is the main (and thus contains the
        main parameters). If the main instance is still being created,
        None will be passed (or assumed) instead, and 'self' will be used.


    See Also
    --------
    RefPars
        The class containing all available parameters, and extra information
        about them
    RawPars
        The class containing parameter choices from other sources


    Attributes
    ----------
    is_main : bool
        Whether this instance of RunPar belongs to the main program (and thus
        contains parameters about the runtime itself) - indicated by 'True',
        or if it belongs to an instance of
        :class:`~GMAP.src.tools.MapReader.Map` - indicated by 'False'.
    MainRunPars : :class:`RunPars`
        The instance of RunPars that is the main (and thus contains the
        main parameters). When assigning this attribute to the 'main' instance,
        'self' will be used.
    detected_requires_bonds : bool
        Whether (one of) the maps requested for use require(s) bonds
    available_maps_singles : dict of str: \
        :class:`~GMAP.src.tools.MapReader.SingleMap` pairs
        The maps that are available during the calculation. These are
        available for any other maps that might want to know something
        from these.
    requested_mapdict : dict of str: \
        :class:`~GMAP.src.tools.MapReader.SingleMap` pairs
        The maps that should be applied during the calculation. This
        must be a subset of available_maps_singles
    available_maps_pairs : dict of str: \
        :class:`~GMAP.src.tools.MapReader.PairMap` pairs
        The pairmaps that are available during the calculation. If any
        pairmap requires another, it must be present in at least this list.
    requested_pairmapdict : dict of str: \
        :class:`~GMAP.src.tools.MapReader.PairMap` pairs
        The pair maps that should be applied during the calculation. This
        must be a subset of available_maps_pairs.
    pair_v_coupling_dict : dict of (tuple of str): str pairs
        For each possible pair of oscillator(types), get the coupling map name
    coupling_v_pair_dict : dict of str: tuple of str pairs
        For each requested coupling map, get the pairs of oscillators it
        couples
    available_outputs : tuple of str
        What kinds of output the user can request the program to generate.
        Is a copy of RefPars.options["output_data"].
    """

    def __init__(
        self, Files, CmdPars, InPars, DefPars, RefPars, is_main,
        MainRunPars=None
    ):
        self.is_main = is_main
        if not is_main:
            self.MainRunPars = MainRunPars
        else:
            self.MainRunPars = self
            self.available_outputs = tuple(RefPars.options["output_data"])

        # Extract all 'normal' parameters
        self.get_pars(CmdPars, InPars, DefPars, RefPars)

        # Extract all parameters that are a file
        self.get_files(Files, CmdPars, InPars, DefPars, RefPars)

        if self.is_main:
            GM_PT.Printer().set_state(
                "running", self.verbose, self.verbose_logfile,
                self.log_filename
            )

            # Resolve conflicts due to choices, change any settings that need
            # to be changed, due to parameters that interlock.
            self.resolve(CmdPars, InPars, DefPars, RefPars)

    def get_pars(self, CmdPars, InPars, DefPars, RefPars):
        """Sets attribute for each non-path parameter.

        Following the order mentioned in `RunPars`, extracts the choice for
        each non-path type parameter found in RefPars. For each of these
        parameters which is not allowed to have multiple choices, the choice
        is extracted from the list and stored without that list.

        .. seealso::
            :meth:`get_files`
                does the same, but for path type parameters

        Parameters
        ----------
        CmdPars : :class:`RawPars`
            Contains any parameter choices made on the command line
        InPars : :class:`RawPars`
            Contains any parameter choices made in the input parameter file
        DefPars : :class:`RawPars` or :class:`RefPars`
            Contains all default parameter choices. Might be RefPars, might be
            from a separate default parameters file.
        RefPars : :class:`RefPars`
            Contains all available parameters from GMAP itself (not
            map-specific)
        """

        # This should be all parameters except path-type ones
        allpars = (
            RefPars.intpars + RefPars.floatpars + RefPars.boolpars
            + RefPars.strpars
        )
        if self.is_main:
            allpars.append("influencers")

        sources = [CmdPars, InPars, DefPars, RefPars]
        for parname in allpars:
            choice = None
            for source in sources[::-1]:
                if parname in source.choices:
                    choice = source.choices[parname]
            if choice is None:
                GM_PT.Printer().warning(
                    f"\nNo choice for the parameter {parname} could be found. "
                    "Please specify a choice on either the command line, or "
                    "in the input file. ",
                    "SU_NP_1", True, GMAPerrclass=GM_Ex.GmapParameterError
                )
            if parname not in RefPars.maybe_list:
                choice = choice[0]

            setattr(self, parname, choice)

    def get_files(self, Files, CmdPars, InPars, DefPars, RefPars):
        """Sets attribute for each path parameter

        Following the order mentioned in `RunPars`, extracts the choice for
        each path type parameter found in RefPars.

        .. seealso::
            :meth:`get_pars`
                does the same, but for non-path type parameters

        Parameters
        ----------
        Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
            Contains all currently known paths and other file-related
            properties.
            Has to be updated after RunPars is finalized.
        CmdPars : :class:`RawPars`
            Contains any parameter choices made on the command line
        InPars : :class:`RawPars`
            Contains any parameter choices made in the input parameter file
        DefPars : :class:`RawPars` or :class:`RefPars`
            Contains all default parameter choices. Might be RefPars, might be
            from a separate default parameters file.
        RefPars : :class:`RefPars`
            Contains all available parameters from GMAP itself (not
            map-specific)
        """

        # deal with all files that are organized
        self.get_ordered_files(
            Files, CmdPars, InPars, DefPars, RefPars
        )

        if self.is_main:
            # deal with map_directory separately
            file_hc = RefPars.choices["map_directory"]
            names = GM_FH.get_bare_file(
                Files, "map_directory", file_hc, RefPars.fname.parent,
                CmdPars.choices,
                [InPars.choices, DefPars.choices],
                [InPars.fname, DefPars.fname]
            )
            names = [file.resolve() for file in names]
            exists = [dir_.is_dir() for dir_ in names]
            if False not in exists:
                setattr(self, "map_directory", names)
            else:
                names = [str(file) for file in names]
                GM_PT.Printer().warning(
                    f"\nThe directory {', '.join(names)} was requested for "
                    "the "
                    f"parameter map_directory, but could not be found, or is "
                    "not a directory. Please make sure you specified it "
                    "correctly.",
                    "SU_NP_3", True, GMAPerrclass=GM_Ex.GmapFileNotFoundError
                )

        # deal with all other files
        for parname in RefPars.allfilepars:
            if hasattr(self, parname):  # This filepar was ordered (or mapdir)
                continue
            try:
                file_hc = RefPars.choices[parname]
            except Exception:
                file_hc = None
            try:
                names = GM_FH.get_bare_file(
                    Files, parname, file_hc, RefPars.fname.parent,
                    CmdPars.choices,
                    [InPars.choices, DefPars.choices],
                    [InPars.fname, DefPars.fname]
                )
            except Exception as ex:
                GM_PT.Printer().warning(
                    f"\nNo choice for the parameter {parname} could be found. "
                    "Please specify a choice on either the command line, or "
                    "in the input file. ",
                    "SU_NP_1", True, exception=ex,
                    GMAPerrclass=GM_Ex.GmapParameterError
                )

            if parname not in RefPars.filepars_create:
                # if name doesnt exist, returns None
                files_found = [GM_FH.try_file(name) for name in names]
                file_found = (None not in files_found)
            else:
                files_found = [name.resolve() for name in names]
                file_found = files_found[0]
                for file in files_found:
                    par_dir = file.parent
                    if not par_dir.is_dir():
                        file_found = None

            if not file_found:
                names = [str(file) for file in names]
                if self.is_main:
                    GM_PT.Printer().warning(
                        f"\nThe file(s) {', '.join(names)} was requested for "
                        "the "
                        f"parameter {parname}, "
                        "but could not be found, or is not a "
                        "file. Please make sure you specified it correctly.\n",
                        "SU_NP_2", True,
                        GMAPerrclass=GM_Ex.GmapFileNotFoundError
                    )
                else:
                    GM_PT.Printer().warning(
                        f"\nThe file(s) {', '.join(names)} was requested for "
                        "the "
                        f"parameter {parname}, for the map "
                        f"{RefPars.fname.parent.name}, "
                        "but could not be found, or is not a "
                        "file. Please make sure you specified it correctly.\n",
                        "SU_NP_2", True,
                        GMAPerrclass=GM_Ex.GmapFileNotFoundError
                    )

            if parname in RefPars.maybe_list:
                setattr(self, parname, files_found)
            else:
                setattr(self, parname, files_found[0])

    def get_ordered_files(
        self, Files, CmdPars, InPars, DefPars, RefPars
    ):
        """Sets attribute for each ordered-path parameter

        The paths to these files are more complicated, as they are relative
        to a directory, but it is not required for both the directory-, and
        file-specifying parameters to be present. For an overview how the
        files are selected, see the development-notes file.

        .. seealso::
            :meth:`get_files`
                does the same for non-ordered path type parameters

        Parameters
        ----------
        Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
            Contains all currently known paths and other file-related
            properties.
            Has to be updated after RunPars is finalized.
        CmdPars : :class:`RawPars`
            Contains any parameter choices made on the command line
        InPars : :class:`RawPars`
            Contains any parameter choices made in the input parameter file
        DefPars : :class:`RawPars` or :class:`RefPars`
            Contains all default parameter choices. Might be RefPars, might be
            from a separate default parameters file.
        RefPars : :class:`RefPars`
            Contains all available parameters from GMAP itself (not
            map-specific)
        """

        dirlist = [InPars.choices]
        fnamelist = [InPars.fname]

        # Dedicated defparfile
        if not DefPars.fname == RefPars.fname:
            dirlist.append(DefPars.choices)
            fnamelist.append(DefPars.fname)

        # all ordered file parameters are sorted by the directory the files
        # should be based in
        for dir_parname, file_parnames in RefPars.organized_filepars.items():
            try:
                dir_hc = RefPars.choices[dir_parname][0]
            except Exception:
                dir_hc = Files.cwd

            # What directory are we based on?
            dir_hc = GM_FH.get_bare_file(
                Files, dir_parname, [dir_hc], RefPars.fname.parent,
                CmdPars.choices, dirlist, fnamelist
            )
            name = dir_hc[0].resolve()

            # check if directory exists
            if name.is_dir():
                setattr(self, dir_parname, name)
            else:
                if self.is_main:
                    GM_PT.Printer().warning(
                        f"\nThe directory {name.resolve()} was requested for "
                        "the "
                        f"parameter {dir_parname}, but could not be found, or "
                        "is "
                        "not a directory. Please make sure you specified it "
                        "correctly.",
                        "SU_NP_3", True,
                        GMAPerrclass=GM_Ex.GmapNotADirectoryError
                    )
                else:
                    GM_PT.Printer().warning(
                        f"\nThe directory {name.resolve()} was requested for "
                        "the "
                        f"parameter {dir_parname}, for the map "
                        f"{RefPars.fname.parent.name}, "
                        "but could not be found, or is "
                        "not a directory. Please make sure you specified it "
                        "correctly.",
                        "SU_NP_3", True,
                        GMAPerrclass=GM_Ex.GmapNotADirectoryError
                    )

            # now, consider each file that should live in this directory
            for file_parname in file_parnames:
                if (
                    self.is_main
                    and file_parname == "default_parameter_filename"
                ):
                    setattr(self, file_parname, DefPars.fname)
                    continue  # This parameter has been dealt with separately

                try:
                    files_hc = RefPars.choices[file_parname]
                except Exception:
                    files_hc = [Path(
                        f"name_not_defined_{str(RefPars.nondefcount)}.txt"
                    )]
                    RefPars.nondefcount += 1

                files_found = GM_FH.get_file(
                    Files, dir_parname, file_parname, dir_hc[0], files_hc,
                    CmdPars.choices, dirlist, fnamelist
                )[0]

                if file_parname not in RefPars.filepars_create:
                    # if name doesnt exist, returns None
                    names = [file.resolve() for file in files_found]
                    files_found = [
                        GM_FH.try_file(name) for name in files_found
                    ]
                    file_found = (None not in files_found)
                else:
                    # If a new file is made, we only have to see if the parent
                    # directory exists. (yes, we still have to do this, as the
                    # file name a user provides could contain further folders)
                    files_found = [file.resolve() for file in files_found]
                    names = files_found
                    file_found = files_found[0]  # start at value of first
                    for file in files_found:
                        par_dir = file.parent
                        if not par_dir.is_dir():
                            file_found = None  # mark that some is missing!

                # if any of the files for this parameter are missing
                if not file_found:
                    names = [str(file) for file in names]
                    GM_PT.Printer().warning(
                        f"\nThe file(s) {'.'.join(names)} was requested "
                        "for the parameter "
                        f"{file_parname}, but could not be found, or is not a "
                        "file. Please make sure you specified it correctly. "
                        "This error could also be triggered by a mistake in "
                        f"the choice for {dir_parname}.\n", "SU_NP_2", True,
                        GMAPerrclass=GM_Ex.GmapFileNotFoundError
                    )

                # If the filename already exists, and we don't want to
                # overwrite, rename existing files!
                self.rename_outfiles(RefPars, file_parname, files_found, True)

                # Some output parameters add file extensions later!

                # if not all files provided have suffixed:
                if not all(file.suffix for file in files_found):
                    if 'txt' in self.output_format:
                        files_tocheck = [
                            file.with_suffix('.txt') for file in files_found]
                        self.rename_outfiles(
                            RefPars, file_parname, files_tocheck)
                    if 'bin' in self.output_format:
                        files_tocheck = [
                            file.with_suffix('.bin') for file in files_found]
                        self.rename_outfiles(
                            RefPars, file_parname, files_tocheck)

    def rename_outfiles(
        self, RefPars, file_parname, files_found, do_setattr=False
    ):
        """Renames files that would otherwise be overwritten

        The program will create all kinds of files during runtime. But
        if a file of that name already exists, it will be overwritten.
        To prevent this, we seek out if such an overwrite will take
        place, and rename the targeted file.

        Parameters
        ----------
        RefPars : :class:`RefPars`
            Contains all available parameters from GMAP itself (not
            map-specific)
        file_parname : str
            The name of the parameter which' files we're taking care of
        files_found : list of `pathlib.Path`
            The requested file locations. If the user provided multiple
            filenames in the input file, this list will have more than
            one item.
        do_setattr : bool
            Whether the provided filepaths should also be saved as the
            choice for this parameter.
        """

        for file in files_found:
            if (
                file_parname in RefPars.filepars_create
                and self.MainRunPars.prevent_overwrite
                and file.is_file()
            ):
                # A new file should be made, but if a file of the same
                # name already exists, it shouldn't be replaced.
                # We already know that the parent directory of the
                # requested path exists.
                rawname = file.name
                backup_path = file.resolve()

                addnum = 0
                while backup_path.is_file():
                    addnum += 1
                    backup_path = file.parent.resolve()
                    backup_path /= f"#{rawname}.{addnum}#"

                file.rename(backup_path)

        if do_setattr:
            if file_parname in RefPars.maybe_list:
                setattr(self, file_parname, files_found)
            else:
                setattr(self, file_parname, files_found[0])

    def resolve(self, CmdPars, InPars, DefPars, RefPars):
        """Fix any issues that may arise from the combination of sources.

        This either means checking if there are no invalid combinations
        (where a choice for a parameter doesn't make sense given the one
        for a different one), or it means combining choices from
        different sources when their values are interdependent.

        CmdPars : :class:`RawPars`
            Contains any parameter choices made on the command line
        InPars : :class:`RawPars`
            Contains any parameter choices made in the input parameter file
        DefPars : :class:`RawPars` or :class:`RefPars`
            Contains all default parameter choices. Might be RefPars, might be
            from a separate default parameters file.
        RefPars : :class:`RefPars`
            Contains all available parameters from GMAP itself (not
            map-specific)
        """

        self.resolve_framenums(CmdPars, InPars, DefPars, RefPars)
        self.resolve_couplings(CmdPars, InPars, DefPars)

    def resolve_framenums(self, CmdPars, InPars, DefPars, RefPars):
        """Make sure the combination of frame numbers makes sense.

        This means making sure that after all sources are combined,
        there are no inconsistencies - start + num must equal stop.

        If a source doesn't give all three parameters, this requirement
        is relaxed, and the combination of sources is interpreted
        somewhat more intelligently.

        CmdPars : :class:`RawPars`
            Contains any parameter choices made on the command line
        InPars : :class:`RawPars`
            Contains any parameter choices made in the input parameter file
        DefPars : :class:`RawPars` or :class:`RefPars`
            Contains all default parameter choices. Might be RefPars, might be
            from a separate default parameters file.
        RefPars : :class:`RefPars`
            Contains all available parameters from GMAP itself (not
            map-specific)
        """

        # The smoothing should start sooner than we start calculating the
        # electrostatics to begin with....
        if self.estatic_smooth_range > (self.estatic_range * 2):
            GM_PT.Printer().warning(
                "\nEncountered an issue with the combined choices of "
                "parameters. The parameter estatic_smooth_range can not "
                "take a value larger than twice that of estatic_range. "
                "Please make sure it does not exceed that.",
                "SU_NP_7", True, GMAPerrclass=GM_Ex.GmapValueError
            )

        # An inconsistency with frame parameters?
        all_parameter_names = ("start_frame", "stop_frame", "number_frames")
        found = {}
        for source in (CmdPars, InPars, DefPars, RefPars):
            newdict = {
                parameter: choice[0]
                for parameter, choice in source.choices.items()
                if parameter in all_parameter_names
            }

            # how many did we find before looking at this source?
            match len(found):
                # if we didn't have anything yet, just go to next.
                case 0:
                    found.update(newdict)
                    continue

                # if we find three at once, it's easy!
                case 3:
                    for parameter, choice in found.items():
                        setattr(self, parameter, choice)
                    break

                # if we find two at once, finding third is easy!
                case 2:
                    found = add_missing_frame_parameter(found)
                    for parameter, choice in found.items():
                        setattr(self, parameter, choice)
                    break

            # now, only the case of 1 parameter in found remains.

            # skip if the new source doesn't have anything
            if len(newdict) == 0:
                continue

            # skip if the new source doesn't have anything new
            foundpar = [*found.keys()][0]
            if len(newdict) == 1 and foundpar in newdict:
                continue

            # now, merging the second source with the first.

            # add the most important secondary parameter
            for parameter in all_parameter_names:
                if parameter not in found and parameter in newdict:
                    found[parameter] = newdict[parameter]
                    break

            # find third
            found = add_missing_frame_parameter(found)
            for parameter, choice in found.items():
                setattr(self, parameter, choice)
            break

    def resolve_couplings(self, CmdPars, InPars, DefPars):
        """Interprets the requested coupling choices

        The coupling choices are provided on multiple lines, possibly
        from multiple sources (so a single choice can be changed without
        having to re-specify all). Combining is simple: the sources are
        read in increasing order of importance, from beginning to end.
        every next/new line can overwrite any previous lines.

        Parameters
        ----------
        CmdPars : :class:`RawPars`
            Contains any parameter choices made on the command line
        InPars : :class:`RawPars`
            Contains any parameter choices made in the input parameter file
        DefPars : :class:`RawPars` or :class:`RefPars`
            Contains all default parameter choices. Might be RefPars, might be
            from a separate default parameters file.
        """

        couplist = []

        # Later sources modify the choices from earlier!
        for source in (DefPars, InPars, CmdPars):
            if "couplings_to_use" in source.choices:
                if isinstance(source, RefPars):
                    couplist.extend([source.choices["couplings_to_use"]])
                else:
                    couplist.extend(source.choices["couplings_to_use"])

        # now, find all pairs of couplings, and assign the correct
        # coupling choice to them.
        coupdict = {}
        for oscname1 in self.maps_to_use:
            for oscname2 in self.maps_to_use:
                coupdict[(oscname1, oscname2)] = None
        self.pair_v_coupling_dict = coupdict

        failed_couppairs = []

        # coupline corresponds to a single line from RawPars files, and
        # contains information about a single coupling map.
        for coupline in couplist:
            if len(coupline) < 2:
                GM_PT.Printer().warning(
                    "\nThe parameter couplings_to_use must always take 2 or "
                    "more "
                    "arguments, but only one was provided. Please make sure "
                    "you specify this parameter correctly.",
                    "SU_NP_8", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
                )
            if coupline[0].lower() == "none":
                coupmap = None
            else:
                coupmap = coupline[0]
            # each coupline can contain multiple pairs of oscillators. Loop
            # over each mentioned pair, and process it.
            for pairstr in coupline[1:]:
                failed_couppairs = self.interpret_coupling_pairstr(
                    pairstr, failed_couppairs, coupmap)

        if failed_couppairs:
            joined = '\n'.join(failed_couppairs)
            GM_PT.Printer().warning(
                "\nAll arguments for the parameter couplings_to_use "
                "(EXCEPT the first one) represent a pair of groups to "
                "couple. The following groups received coupling instructions, "
                "but weren't requested for use by 'maps_to_use':\n"
                f"{joined}\n"
                "This might indicate a mistake in the indication, please stop "
                "the program if this is the case.",
                "SU_NP_8", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
            )

        self.coupling_v_pair_dict = {}
        for key, value in self.pair_v_coupling_dict.items():
            if value in self.coupling_v_pair_dict:
                self.coupling_v_pair_dict[value].append(key)
            else:
                self.coupling_v_pair_dict[value] = [key]

    def interpret_coupling_pairstr(
        self, pairstr, failed_couppairs, coupmap
    ):
        """Helper for self.resolve_couplings - processes a single pair.

        Edits the coupling dictionary directly in place.

        Parameters
        ----------
        pairstr : str
            the string from the rawpars files indicating the single pair to
            be processed here. Might take a few formats:

            - oscname:oscname  indicates a specific pair of oscillators
            - oscname: indicates any pair containing that oscillator
            - :all indicates all pairs
            - :same indicates all pairs of oscillators of the same type
            - :diff indicates all pairs of oscillators of a different type
        failed_couppairs : list of str
            All pairs that contain an oscillator type not requested by
            the parameter maps_to_use. These are not added to the dict.
        coupmap : str or None
            The coupling map that should be used for the pairs denoted using
            pairstr

        returns
        -------
        failed_couppairs : list of str
            All pairs that contain an oscillator type not requested by
            the parameter maps_to_use. These are not added to the dict.
        """

        coupdict = self.pair_v_coupling_dict

        if pairstr.lower() == ":all":
            for key in coupdict.keys():
                coupdict[key] = coupmap
            return failed_couppairs
        elif pairstr.lower() == ":same":
            for key in coupdict.keys():
                if key[0] == key[1]:
                    coupdict[key] = coupmap
            return failed_couppairs
        elif pairstr.lower() == ":diff":
            for key in coupdict.keys():
                if key[0] != key[1]:
                    coupdict[key] = coupmap
            return failed_couppairs

        pair = pairstr.split(":")
        if len(pair) != 2:
            GM_PT.Printer().warning(
                "\nAll arguments for the parameter couplings_to_use "
                "(EXCEPT the first one) must contain one ':'. This "
                "is not the case. Please make sure to have exactly "
                "one.", "SU_NP_8", True,
                GMAPerrclass=GM_Ex.GmapFileSyntaxError
            )
        if len(pair[0]) == 0:
            GM_PT.Printer().warning(
                "\nAll arguments for the parameter couplings_to_use "
                "(EXCEPT the first one) represent a pair of groups to "
                "couple. While the second group is optional, the "
                "first one is not. Make sure to give at least the "
                "first one.", "SU_NP_8", True,
                GMAPerrclass=GM_Ex.GmapFileSyntaxError
            )

        # if either of the group names in the pair has not been
        # requested as a group to use, error!
        if (
            pair[0] not in self.maps_to_use
            or (pair[1] not in self.maps_to_use and pair[1] != "")
        ):
            failed_couppairs.append(pairstr)
            return failed_couppairs

        if pair[1] == "":
            for key in coupdict.keys():
                if pair[0] in key:
                    coupdict[key] = coupmap
            return failed_couppairs

        for key in coupdict.keys():
            if key in ((pair[0], pair[1]), (pair[1], pair[0])):
                coupdict[key] = coupmap
        return failed_couppairs

    # Called by GEM.trj_loop()
    def manage_dtypes(self):
        """Convert any values that might need it to the correct datatype.

        This is mostly in preparation for numba and/or c algorithms that
        are not capable of dealing with the uncertain (system-dependent)
        choice of datatype that python and numpy have.
        """

        self.estatic_range = np.float32(self.estatic_range)
        self.estatic_smooth_range = np.float32(self.estatic_smooth_range)


def get_parameters(Files, in_parfile, argslist):
    """Collect all provided parameters, and store them.

    Parameters are defined (along with default choices) in the reference
    parameter file. Users can have a different set of defaults defined
    in the default parameter file, and specific choices for this (set of)
    runs in the input parameter file and the command line. This function
    uses the functionality in src/tools/ParameterParser.py to collect
    all choices, and construct a final set of choices from them. All
    generated options are then returned.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    in_parfile : `pathlib.Path`
        The path to the requested input parameter file.
    argslist : list of str
        The slice of sys.argv containing all parameter choices given on
        the command line.

    Returns
    -------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    Singles_mapdict : dict of str: \
        :class:`~GMAP.src.tools.MapReader.SingleMap` pairs
        Stores all the :class:`~GMAP.src.tools.MapReader.SingleMap` objects for
        each map supplied. The keys are the Map.name attributes corresponding
        to the maps stored as values.
    Pairs_mapdict : dict of str: \
        :class:`~GMAP.src.tools.MapReader.PairMap` pairs
        Stores all the :class:`~GMAP.src.tools.MapReader.PairMap` objects for
        each map supplied. The keys are the Map.name attributes corresponding
        to the maps stored as values.
    CmdPars : :class:`RawPars`
        Contains any parameter choices made on the command line
    InPars : :class:`RawPars`
        Contains any parameter choices made in the input parameter file
    DefPars : :class:`RawPars` or :class:`RefPars`
        Contains all default parameter choices. Might be RefPars, might be
        from a separate default parameters file.
    RefPars : :class:`RefPars`
        Contains all available parameters from GMAP itself (not map-specific)
    """

    # very basic parsing of cmd

    # before we can parse the command line, or the input parameter file,
    # we have to know what parameter names to expect. However, to know
    # this, we need to open the default parameter file, but we don't
    # know where it is, before parsing command line and input parameter
    # file.

    # solution: only look for sourcedir and defparfilename in command
    # line and input parameter file, do further parsing later.

    # step 3 (See if the arg from cmdline have anything on srcdir or defpar)
    temp_cmd_pardict = find_defparfile_in_cmd(argslist)

    if in_parfile:
        # step 4 (very basic inpar file parser)

        # check if file is UTF8
        GM_FH.check_file_readability(in_parfile)
        with open(in_parfile) as file:
            in_pardict = get_pardict(file)
        # step 5 (find which defpar to use)
        def_parfile = GM_FH.get_def_parfile(
            Files, temp_cmd_pardict, in_parfile, in_pardict
        )
    else:
        # step 5 (find which defpar to use)
        def_parfile = GM_FH.get_def_parfile(Files, temp_cmd_pardict)

    # as get_def_parfile also checks for the presence of the hard-coded
    # reference parameter file (regardless of program flow), no need to do
    # it again.
    # step 6 (find refparfile)
    ref_parfile = Files.sourcedir_hc / Files.refparfilename_hc
    # step 7 (parse refparfile)
    GM_FH.check_file_readability(ref_parfile)  # check if file is UTF8
    RefPars_ = RefPars(ref_parfile, True)

    # step 8 (parse defparfile)
    if def_parfile.suffix == ".txt":
        # check if file is UTF8
        GM_FH.check_file_readability(def_parfile)
        DefPars = RawPars.from_file(
            def_parfile, RefPars_, True
        )
    elif def_parfile == ref_parfile:
        DefPars = RefPars_
        setattr(DefPars, "not_found", {})
    elif def_parfile.suffix == ".ref":
        DefPars = RefPars.add_reffile(def_parfile, RefPars_)
    else:
        GM_PT.Printer().warning(
            f"The requested default parameter file {def_parfile} is of the "
            "wrong file format. "
            "Please refer to the manual to see what file types are supported.",
            "SU_GEM_1", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
        )

    # step 9 (parse inparfile, not map part)
    if in_parfile:
        InPars = RawPars.from_file(
            in_parfile, RefPars_, False)
    else:
        InPars = RawPars.create_empty()

    # step 10 (find mapdir in cmdline > inparfile > defparfile)
    mapdirs = find_mapdir(Files, argslist, InPars, DefPars)

    # step 11 (for each map, parse parameters.ref, if present)
    singles_mapdict = GM_MR.scan_mapdirs(mapdirs, "Singles")
    pairs_mapdict = GM_MR.scan_mapdirs(mapdirs, "Pairs")
    all_mapdict = singles_mapdict | pairs_mapdict
    for map_ in all_mapdict.values():
        map_.find_refpars()

    # step 12 (finish parsing cmdline, inparfile, defparfile)

    # cmdline
    CmdPars = RawPars.from_cmdline(
        argslist, RefPars_,
        {name: map_.RefPars for name, map_ in all_mapdict.items()},
        False
    )

    for map_ in all_mapdict.values():
        map_.find_rawpars(CmdPars, InPars, DefPars)

    CmdPars.finalize_map_pars()
    InPars.finalize_map_pars()
    if def_parfile != ref_parfile:
        DefPars.finalize_map_pars()

    RunPars_ = RunPars(
        Files, CmdPars, InPars, DefPars, RefPars_, True
    )

    for map_ in all_mapdict.values():
        map_.find_runpars(Files, RunPars_)

    return (
        RunPars_, singles_mapdict, pairs_mapdict, CmdPars, InPars, DefPars,
        RefPars_
    )


def add_missing_frame_parameter(pardict):
    """Adds in the missing frame number parameter with a sensible value.

    Expects that the other two are present, and we only need the third.
    All values in the dictionary are expected to be integers (so no
    lists of a single int, like RawPars.choices).

    Returns the same dict, but with the missing item added in.

    Parameters
    ----------
    pardict : dict
        The dictionary containing two of the three frame parameters.

    Returns
    -------
    pardict : dict
        The input dictionary, with the third item added in.
    """

    if "start_frame" not in pardict:
        pardict["start_frame"] = (
            pardict["stop_frame"] - pardict["number_frames"])
    elif "number_frames" not in pardict:
        pardict["number_frames"] = (
            pardict["stop_frame"] - pardict["start_frame"])
    else:
        pardict["stop_frame"] = (
            pardict["number_frames"] + pardict["start_frame"])

    return pardict


def parse_commandline(
    Files, callcommand, alljobs, helpcall, expect_inputfile=False,
    expect_parameters=False
):
    """Extracts the groups of information from the command line.

    Parses a command stored in a list, to return and check different
    parts. Expects the following items:
    [0] should contain the name of the tool used. eg. GEM, AIM.
    [1] should contain the requested job from the tool. eg. run, demo.
    (if expect_inputfile == True) the filename of the input file to use
    (if expect_parameters == True) the further parameters to use. Optional
    Parameters specified on the command line must have the parameter name
    preceded with '-'.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    callcommand : list
        A slice from the output of sys.argv
    alljobs : list of str
        The kind of jobs the program is able to do
    helpcall : str
        Example of how to call the program to get the help, to help the user
        getting the command parsed here correct.
    expect_inputfile : bool, default=False
        Whether the supplied command will contain the path to an input file,
        too.
    expect_parameters : bool, default=False
        Whether the supplied command is allowed to have extra parameters. If
        it is not, any that might be present will just be ignored. If it is,
        it is not required to have any.

    Returns
    -------
    job : str
        The type of job the user requested.
    in_parfile : pathlib.Path
        The path to the input file given.
    cmd_pars : list of str
        The part of the command that should contain information on
        parameter choices - to be parsed later.
    """

    job = callcommand[1]

    if job.lower() not in alljobs:
        GM_PT.Printer().warning(
            f"\nChoice '{job}' was not recognized. "
            "Please type the following to see all available options:"
            f"\n\n{helpcall}\n",
            "SU_PP_1", True, GMAPerrclass=GM_Ex.GmapKeyError
        )

    if expect_inputfile:
        # if we expect an input filename, but it isn't there, error!
        if len(callcommand) < 3:
            GM_PT.Printer().warning(
                f"\n{job} requires an input file. Quitting!", "SU_PP_2", True,
                GMAPerrclass=GM_Ex.GmapParameterError
            )

        in_parfile = (Files.cwd / callcommand[2]).resolve()
        if not (in_parfile.exists() and in_parfile.is_file()):
            GM_PT.Printer().warning(
                f"\nThe requested input parameter file {in_parfile} could not "
                "be found, or is not a file. "
                "Please make sure you specified it correctly.\n",
                "SU_PP_3", True, GMAPerrclass=GM_Ex.GmapFileNotFoundError
            )
        args_list = callcommand[3:]
    else:
        in_parfile = None
        args_list = callcommand[2:]

    if expect_parameters:
        cmd_pars = args_list
    else:
        cmd_pars = []

    return job, in_parfile, cmd_pars


def find_defparfile_in_cmd(argslist):
    """Finds any parameters pertaining to default parfile in command line

    Given an argslist (the part of sys.argv that should/could contain
    arguments), see if there is anything hinting at a default parameter
    file there.

    Parameters:
    -----------
    argslist : list of str
        The part of the output of sys.argv that contains parameter choices

    Returns
    -------
    pardict : dict
        The dictionary containing all relevant parameter choices. Keys are the
        parameter names, values are their choices.
    """
    pardict = {}

    srcdir_names = ("--source_directory", "-sd")
    srcdir = find_par_in_cmd(
        argslist, srcdir_names, "source_directory"
    )
    if srcdir:
        pardict["source_directory"] = srcdir

    defparfile_names = ("--default_parameter_filename", "-dpf")
    defparfile = find_par_in_cmd(
        argslist, defparfile_names, "default_parameter_filename"
    )
    if defparfile:
        pardict["default_parameter_filename"] = defparfile

    return pardict


def find_par_in_cmd(argslist, flags, parname, is_list=False):
    """Searches for a given parameter in the command line

    Parameters
    ----------
    argslist : list of str
        The part of the output of sys.argv that contains parameter choices
    flags : tup of str
        The parameter names that might be used for this parameter
    parname : str
        The parameter name to be used in the rest of the program
    is_list : bool, default=False
        Whether the desired parameter might accept multiple choices.

    Returns
    -------
    choice : list
        The found choice for the parameter.
    """

    if any(item in argslist for item in flags):
        totalcount = 0
        for item in flags:
            totalcount += argslist.count(item)
            try:
                ix = argslist.index(item)
                used_flag = item
            except ValueError:
                pass

        if totalcount > 1:
            GM_PT.Printer().warning(
                "\nThe program was called with more than one setting "
                f"for {parname}. "
                "Please make sure your command contains this parameter at "
                "most once.",
                "SU_PP_4", True, GMAPerrclass=GM_Ex.GmapParameterError
            )

        warntext = f"\n{used_flag} requires a file name to be specified."
        try:
            choice = [argslist[ix + 1]]
        except IndexError:
            GM_PT.Printer().warning(
                warntext, "SU_WP_4", True, GMAPerrclass=GM_Ex.GmapIndexError)
        if choice[0].startswith("-"):
            GM_PT.Printer().warning(
                warntext, "SU_WP_4", True,
                GMAPerrclass=GM_Ex.GmapFileSyntaxError
            )

        if is_list:
            adder = 2
            warntext = (
                f"\n{used_flag} requires the last choice to be appended with "
                "'\\;'."
            )
            while not choice[-1].endswith("\\;"):
                try:
                    choice.append(argslist[ix + adder])
                    adder += 1
                except IndexError:
                    GM_PT.Printer().warning(
                        warntext, "SU_WP_5", True,
                        GMAPerrclass=GM_Ex.GmapIndexError
                    )
                if choice[-1].startswith("-"):
                    GM_PT.Printer().warning(
                        warntext, "SU_WP_5", True,
                        GMAPerrclass=GM_Ex.GmapFileSyntaxError
                    )
            choice[-1] = choice[-1][:-2]

        return choice


def find_mapdir(Files, argslist, InPars, DefPars):
    """Extracts choice for the parameter map_directory from the command line.

    If the choice has been found, checks whether it exists. If it does not,
    triggers warning and stops the program.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    argslist : list of str
        The part of the output of sys.argv that contains parameter choices.
    InPars : :class:`RawPars`
        Contains any parameter choices made in the input parameter file
    DefPars : :class:`RawPars` or :class:`RefPars`
        Contains all default parameter choices. Might be RefPars, might be
        from a separate default parameters file.

    Returns
    -------
    map_dirs : list of pathlib.Path
        All locations that were requested.
    """
    map_flags = ("--map_directory", "-md")
    cmd_mapdir = find_par_in_cmd(
        argslist, map_flags, "map_directory", is_list=True
    )
    # if cmd supplied, check if exists
    if cmd_mapdir:
        mapdirs = directory_list_checker(
            Files.cwd, cmd_mapdir, "map_directory", "the command line"
        )

    elif InPars and "map_directory" in InPars.choices:
        mapdirs = directory_list_checker(
            InPars.fname.parent,
            InPars.choices["map_directory"],
            "map_directory",
            InPars.fname
        )

    else:
        mapdirs = directory_list_checker(
            DefPars.fname.parent,
            DefPars.choices["map_directory"],
            "map_directory",
            DefPars.fname
        )

    return mapdirs


def directory_list_checker(parent, direclist, parname, source):
    """Checks whether each of the given paths exists, and is a directory.

    Parameters
    ----------
    parent : pathlib.Path
        The location to which the provided paths are relative.
    direclist : list of pathlib.Path
        The locations provided
    parname : str
        The parameter for which the locations were provided.
    source : str
        Where this choice for parameter was made.

    Returns
    -------
    dirs : list of pathlib.Path
        The same paths as provided using the parameter `direclist`, but now
        absolute.
    """
    dirs = [parent / direc for direc in direclist]
    failed = [str(direc.resolve()) for direc in dirs if not direc.is_dir()]
    if len(failed) > 0:
        # not using fstrings here, as backslashes arent supported in
        # fstrings before python 3.12.
        GM_PT.Printer().warning(
            f"\nThe following choice(s) for {parname} found in {source} "
            "either "
            "do not exist, or are not directories:\n"
            + "\n".join(failed),
            "SU_PP_3", True, GMAPerrclass=GM_Ex.GmapNotADirectoryError
        )
    dirs = [loc.resolve() for loc in dirs]
    return dirs


def get_pardict(iterable, compounds=None):
    """Takes an iterable, and returns it in dict form.

    Each iteration of the iterable is subjected to .split(); the zeroeth item
    becomes the key, the list of the remaining items (or empty list) becomes
    the value.
    All keys and items in value lists are strings - the contents are NOT
    interpreted, and converted to correct datatypes.

    Parameters
    ----------
    iterable : any iterable
        Contains the information to be converted to a dict.
    compounds : tuple of str
        These keys are allowed to occur more than once.

    Returns
    -------
    outdict : dict
        The new information. Keys are the zeroeth item, values are lists of the
        remaining items.

    """

    if compounds is None:
        compounds = tuple()

    outdict = {}
    for line in iterable:
        line = cleanline(line).strip()
        if len(line) == 0:
            continue
        linelist = [term.strip() for term in line.split()]

        if linelist[0] in compounds:
            if linelist[0] in outdict:
                outdict[linelist[0]].append(linelist[1:])
            else:
                outdict[linelist[0]] = [linelist[1:]]
        else:
            outdict[linelist[0]] = linelist[1:]
    return outdict


def cleanline(line, escape_char="#"):
    """Removes any escape character and text following it

    In other words, get rid of comments.
    Default escape character is '#'

    Parameters
    ----------
    line : str
        The line to remove any comments from
    escape_char : str, default="#"
        The character that indicates that a comment started.
    """
    return line.split(escape_char)[0]


def parse_influencerfile(fname, groupdict):
    """Parses an entire influencer file. A collection of influencers.

    Parameters
    ----------
    fname : pathlib.Path
        The file that contains the line. Used for printing warnings.
    groupdict : dict of str: set pairs
        Previously defined groups

    Returns
    -------
    groupdict : dict of str: set pairs
        All currently known groups - both previously defined and newly
        found in the supplied file.
    """

    with open(fname) as fhand:
        for line in fhand:
            line = cleanline(line).strip()
            if not line:
                continue

            # reduce many spaces to a single one
            line = [word for word in line.split() if word]
            groupdict[line[0]] = parse_influencerfile_line(
                " ".join(line[1:]), groupdict, fname
            )
    return groupdict


def parse_influencerfile_line(line, groupdict, fname):
    """Parse a single influencer definition.

    Influencers are groups of residue names. A group can contain many,
    a single, or no items. This function deals with the definition of
    one of those groups. The resulting set is returned so it can be
    used/assigned.

    Parameters
    ----------
    line : str
        The definition of the influencer group.
    groupdict : dict of str: set pairs
        Previously defined groups
    fname : pathlib.Path
        The file that contains the line. Used for printing warnings.

    Returns
    -------
    newset : set
        The set as was requested.
    """

    letters = "abcdefghijklmnopqrstuvwxyz"
    numbers = "1234567890"
    namechars = letters + letters.upper() + numbers + "_"
    specialchars = "-&|^()"
    allowed_chars = " :" + namechars + specialchars

    problem_chars = [char for char in line if char not in allowed_chars]

    if problem_chars:
        GM_PT.Printer().warning(
            f"The influencers file {fname} contains one or more invalid "
            "characters. Make sure the following characters are not present: "
            f"{''.join(problem_chars)}.",
            "SU_NP_4", True, GMAPerrclass=GM_Ex.GmapFileSyntaxError
        )

    # go through the line, character by character
    final_choice = "def build_set(groupdict):\n"
    final_choice += "    return "
    is_name = False
    fromdict = False
    curname = ""

    for char in line:
        if char == ":":
            fromdict = True
        elif char in namechars:
            is_name = True
            curname += char
        elif char in (specialchars + " "):
            if is_name:
                if fromdict:
                    final_choice += "groupdict['" + curname + "']"
                    fromdict = False
                else:
                    final_choice += "set(['" + curname + "'])"
                curname = ""
                is_name = False
            final_choice += char
    else:  # after we're done, flush out the last bit.
        if is_name:
            if fromdict:
                final_choice += "groupdict['" + curname + "']"
                fromdict = False
            else:
                final_choice += "set(['" + curname + "'])"

    try:
        exec(final_choice)
    except Exception as ex:
        GM_PT.Printer().warning(
            f"\nThe file {fname} has a problem with one of the definitions "
            "of parameters. See the error for more information.",
            "SU_NP_5", True, exception=ex,
            GMAPerrclass=GM_Ex.GmapFileSyntaxError
        )

    try:
        newset = locals()["build_set"](groupdict)
    except Exception as ex:
        GM_PT.Printer().warning(
            f"\nThe file {fname} has a problem with one of the definitions "
            "of parameters. See the error for more information.",
            "SU_NP_5", True, exception=ex,
            GMAPerrclass=GM_Ex.GmapFileSyntaxError
        )

    return newset


def parse_influencer_par(string):
    """Allows different selection language for influencers given as parameter.

    Influencers can be given as a separate file, where, using the python
    set syntax, all kinds of groups can be defined. However, when the
    influencers are defined within the parameter file, this syntax is
    less intuitive, because the selection for multiple maps, for
    example, only has spaces separating the items.

    If no set operators are used, but there are multiple items, assume
    they should be 'added' together (union).

    Parameters
    ----------
    string : str
        The choice provided for the parameter

    Returns
    -------
    string : str
        The same choice as provided, but translated into set language.
    """

    specialchars = "-&|^()"

    # there are spaces in between items, but there's not a single
    # set-operator character to be found.
    # In this case, assume that the user doesn't know/use set operators,
    # and that all given objects should just be added together.
    if (
        not any(char in specialchars for char in string)
        and any(char in " " for char in string)
    ):
        string = string.replace(" ", " | ")

    return string
