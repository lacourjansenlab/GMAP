
# standard library imports
from pathlib import Path

# local imports
import GMAP.src.tools.FileHandler as GM_FH
from GMAP.src.tools.PrintTools import devprint as dpr
dpr("", end="")  # to disable error of dpr unused


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
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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

    def __init__(self, Printer, fname, is_main=True):
        self.is_main = is_main
        self.fname = fname.resolve()
        self.add_groups()
        self.nondefcount = 0

        self.parse_refparfile(Printer, self.parse_line_type_protected)
        self.parse_refparfile(Printer, self.parse_line_choice_protected)

        # path-type parameters cannot also request a choice.
        for parname in self.allfilepars:
            if parname in self.options:
                Printer.warning(
                    "\nDue to path conflicts, reference files may not "
                    "contain options for path-type parameters. "
                    f"The affected file is {self.fname}",
                    "SU_FP_9", True
                )

        # for fixing intertwined / more convoluted parameters (main file only)
        if is_main:
            self.resolve(Printer)

    @classmethod
    def add_reffile(cls, Printer, fname, base_RefPars):
        """
        When the default parameter file given by the user is of .ref format
        instead of .txt, it ends up here. How are .ref files treated different?
            - most importantly: format! A .ref file is formatted differently
              from a .txt.
            - While a .txt only stores the choice for each parameter, the .ref
              also stores the allowed options. This would allow users to impose
              stricter limits. Is this actually useful???
        """
        Printer.warning(
            "\nNot implemented yet!",
            "SU_FP_1", True
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

    def parse_refparfile(self, Printer, func):
        """ Apply provided function on each line of the file

        Loops through lines of given file. Each line is stripped of comments,
        and empty lines are ignored. For each remaining line, the function
        func is called.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                    Printer.warning(
                        "\nThe following problem occured when reading the "
                        f"reference parameter file {self.fname}"
                        "\n\nOne of the lines contains only one item, while "
                        "key-value pairs are expected. Quitting!",
                        "SU_FP_2", True
                    )

                # now, line must have at least length 2. Start interpreting!
                func(Printer, line, linelist)

    def parse_line_type_protected(self, Printer, line, linelist):
        """Wrapper for parse_line_type

        Also triggers any errors stopping the program when needed.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
            Printer.warning(
                "\nCould not interpret the parameter name on the following "
                f"line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_3", True, exception=ex
            )
        except Exception as ex:
            Printer.warning(
                "\nEncountered an error while parsing the parameter name "
                "on the "
                f"following line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_4", True, exception=ex
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

    def parse_line_choice_protected(self, Printer, line, linelist):
        """Wrapper for parse_line_choice

        Also triggers any errors stopping the program when needed.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
            Printer.warning(
                "\nCould not interpret the parameter choice on the following "
                f"line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_5", True, exception=ex
            )
        except IndexError as ex:
            Printer.warning(
                "\nDetected a wrong amount of choices for the parameter "
                "choice "
                f"on the following line:\n{line}"
                "\nWhile reading the following file as a reference file:\n"
                f"{self.fname}\nQuitting!",
                "SU_FP_6", True, exception=ex
            )
        except Exception as ex:
            Printer.warning(
                "\nEncountered an error while parsing the parameter choice on "
                f"the following line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                "SU_FP_7", True, exception=ex
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

    def resolve(self, Printer):
        """Fixes intertwined/special parameters the standard parser can't fix

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        # influencers - we need some defaults, but they should not clash in any
        # way.... in the default file, top one takes precedence.
        for parameter in self.maybe_list:
            if parameter in ("influencers_whitelist", "influencers_blacklist"):
                break
        else:
            Printer.warning(
                "Encountered an issue with the following reference parameter "
                f"file: {self.fname}. The file should contain the parameters "
                "'influencers_whitelist' and 'influencers_blacklist', but "
                "contains neither.",
                "SU_FP_8", True
            )

        self.maybe_list.append("influencers")
        if parameter == "influencers_whitelist":
            self.choices["influencers"] = self.choices[parameter]
        elif parameter == "influencers_blacklist":
            # invert the choice by subtracting the blacklist choice from all
            self.choices["influencers"] = [":All", "-", "("] + self.choices[
                parameter
            ] + [")"]

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

    def __init__(self, Printer, fname, is_default, given_dict, RefPars):
        self.fname = fname
        self.is_default = is_default

        self.extract_choices(Printer, given_dict, RefPars)
        if is_default:
            self.check_completeness(Printer, RefPars)

        # if the class isn't empty
        if given_dict:
            self.resolve(Printer)

    @classmethod
    def create_empty(cls, Printer):
        """Create an instance of this class without any data

        .. seealso ::
            :meth:`from_dict`, :meth:`from_file`, :meth:`from_cmdline`

        Returns
        -------
        instance : :class:`RawPars`
            A newly generated instance.
        """

        return cls(Printer, None, False, {}, {})

    @classmethod
    def from_dict(cls, Printer, fname, given_dict, RefPars, is_default):
        """Create an instance of this class for parameters stored in a dict.

        .. seealso ::
            :meth:`create_empty`, :meth:`from_file`, :meth:`from_cmdline`

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
            instance = cls.create_empty(Printer)
            return instance

        return cls(Printer, fname, is_default, given_dict, RefPars)

    @classmethod
    def from_file(cls, Printer, fname, RefPars, is_default):
        """Create an instance of this class for parameters stored in a file.

        First obtains a dict from the file, then uses :meth:`from_dict`

        .. seealso ::
            :meth:`create_empty`, :meth:`from_dict`, :meth:`from_cmdline`

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
            given_dict = get_pardict(file)

        instance = cls.from_dict(
            Printer, fname, given_dict, RefPars, is_default
        )
        return instance

    @classmethod
    def from_cmdline(
        cls, Printer, cmdargs, RefPars, maprefpars_dict, is_default
    ):
        """Create an instance of this class for parameters in the command line

        A method more different from the others, as it has to do some parsing,
        too. Also immediately deals with map-specific parameters, while
        instances created from other sources need an extra pass for those.

        .. seealso ::
            :meth:`create_empty`, :meth:`from_dict`, :meth:`from_file`

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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

        temp_instance = cls(Printer, Path("command line"), False, {}, {})
        pardict = {}

        while len(cmdargs) > 0:
            # Step 1: Figure out what the parameter name is, and where its from

            #   - hyphens
            if not cmdargs[0].startswith("-"):
                Printer.warning(
                    "\nThe name of a parameter specified on the command line "
                    "should be preceeded with '-'.",
                    "SU_WP_1", True
                )
            curparraw = cmdargs.pop(0)
            curpar, curpar_tocheck, refpars_to_use = cls.parse_cmd_parname(
                Printer, curparraw, RefPars, maprefpars_dict
            )

            # Step 2: See if it actually exists
            found = temp_instance.check_par_existence(
                Printer, curpar, curpar_tocheck, refpars_to_use, None, False
            )[1]
            if not found:
                Printer.warning(
                    f"\nThe parameter {curpar} as specified on the command "
                    "line is not recognised. Please make sure you spelled "
                    "it correctly.",
                    "SU_WP_3", True
                )

            # Step 3: extract num of expected arguments, and also:
            # Step 4: extract actual arguments
            choice = cls.parse_cmd_choice(
                Printer, cmdargs, curpar, curpar_tocheck, refpars_to_use
            )

            pardict[curpar] = choice

        instance = cls.from_dict(
            Printer, Path("command line"), pardict, RefPars, is_default
        )

        return instance

    @staticmethod
    def parse_cmd_parname(Printer, curparraw, RefPars, maprefpars_dict):
        """Identifies a parameter name specified on the command line

        Removes hyphens, figures out whether the name is shorthand or not,
        whether it belongs to the base program, or one of the maps, and
        whether (in the case of bools) the parameter is inverted using the
        nobool format. If it is, this invertion is not cancelled, the 'no'
        part is left in place.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                Printer.warning(warntext, "SU_WP_2", True, exception=ex)

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
                Printer.warning(warntext, warncode, True, exception=ex)

            if "." in curpar:
                curpar = curpar_list[0] + "." + curpar_tocheck
            else:
                curpar = curpar_tocheck

        return curpar, curpar_tocheck, RefParsToUse

    @staticmethod
    def parse_cmd_choice(
        Printer, cmdargs, curpar, curpar_tocheck, RefParsToUse
    ):
        """Extracts the choice from the command line

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                Printer.warning(
                    f"\nThe parameter {curpar} specified in the command "
                    "line requires a choice to be given.",
                    "SU_WP_4", True, exception=ex
                )

            warntext = (
                f"\nThe parameter {curpar} specified in the command line "
                "requires the last choice to be appended with '\\;'."
            )
            while not choice[-1].endswith("\\;"):
                try:
                    choice.append(cmdargs.pop(0))
                except IndexError:
                    Printer.warning(warntext, "SU_WP_5", True)

                if choice[-1].startswith("-"):
                    Printer.warning(warntext, "SU_WP_5", True)
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

    def extract_choices(self, Printer, given_dict, RefPars):
        """Takes each parameter and their choice from the dict for parsing

        Each pair is forwarded to the correct location for further parsing.
        Does not deal in-depth with map-specific parameters, unless the
        :class:`RawPars` instance is created specifically for that map.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                Printer, parname, parname, RefPars, choice
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
                Printer.warning(
                    f"\nUnknown parameter {parname} found in the file "
                    f"{self.fname}. "
                    "Please make sure you spelled it correctly.",
                    "SU_WP_6", True
                )

    def verify_choice(self, Printer, parname, choice, RefPars):
        """Check if the supplied choice is valid

        Checks performed:
            - Are there exactly enough choices given?
            - Can all choices be converted into the correct datatype?
            - If there is a limited set of options to chose from - is the
              provided choice allowed?

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                Printer.warning(
                    f"\nNo choice detected for the parameter {printname} "
                    f"specified in the file {self.fname}. "
                    "All parameters must be specified for the file to be "
                    "used.",
                    "SU_WP_7", True
                )
            # This is a bool-type par - presence means 'True'
            elif parname in RefPars.boolpars:
                choice.append("true")
            else:
                Printer.warning(
                    f"\nNo choice detected for the parameter {printname} "
                    f"specified in the file {self.fname}. "
                    "Either remove the parameter line, or make a choice.",
                    "SU_WP_8", True
                )

        # if we expect a single choice, but multiple were given
        elif len(choice) > 1 and parname not in RefPars.maybe_list:
            Printer.warning(
                f"\nToo many choices given for the parameter {printname} "
                f"specified in the file {self.fname}. "
                "Please only specify one.",
                "SU_WP_9", True
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
            raise TypeError

        if parname in RefPars.boolpars:  # bools need special care
            trueicators = ("true", "t")
            falseicators = ("false", "f")
            if any(
                x.lower() not in trueicators and x.lower() not in falseicators
                for x in choice
            ):
                Printer.warning(errortext1, "SU_WP_10", True)
            choice = [1 if x.lower() in trueicators else 0 for x in choice]

        try:
            choice = [usetype(x) for x in choice]
        except Exception:
            Printer.warning(errortext2, "SU_WP_12", True)

        if parname not in RefPars.options:
            return choice

        if any(
            opt not in RefPars.options[parname] for opt in choice
        ):
            Printer.warning(errortext1, "SU_WP_11", True)
        else:
            return choice

    def check_par_existence(
        self, Printer, parname_full, parname_refpars, RefPars, choice,
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
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                choice = self.verify_choice(
                    Printer, parname_refpars, choice, RefPars
                )
            if not do_verify or choice is None:
                return None, found, parname_refpars

        elif parname_refpars in RefPars.not_expected_in_deffile:
            found = True
            if self.is_default and len(choice) != 0:
                Printer.warning(
                    f"\nA choice for the parameter {parname_full} is "
                    "specified "
                    f"in the default parameter file {self.fname}. "
                    "However, default files cannot contain a choice for "
                    "this parameter. Please remove the parameter from the "
                    "file.",
                    "SU_WP_13", True
                )
            elif self.is_default:
                return None, found, parname_refpars
            else:
                if do_verify:
                    choice = self.verify_choice(
                        Printer, parname_refpars, choice, RefPars
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
                Printer, parname_full[2:], parname_refpars[2:], RefPars,
                newchoice, do_verify
            )

        return choice, found, parname_refpars

    def check_completeness(self, Printer, RefPars):
        """Check if all required parameters are present

        When the file is marked as being default, this method makes sure that
        all parameters are present.

        If a default parameter file contains any map-related choices, then
        this function is called with the RefPars of that specific map, as it
        then must contain all choices for that map.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                Printer.warning(
                    f"\nNo entry found for the parameter {parname} in the "
                    f"default parameter file {self.fname}. "
                    "All parameters must be specified for default files to "
                    "be used.",
                    "SU_WP_14", True
                )

    def resolve(self, Printer):
        """Fixes intertwined/special parameters the standard parser can't fix

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        # see how many influencer parameters are present - only one can be!
        n_present = sum([parameter in (
            "influencers_whitelist",
            "influencers_blacklist",
            "influencers_file",
            "influencers_select_atoms"
        ) for parameter in self.choices])

        if n_present > 1 and not self.is_default:
            Printer.warning(
                "Encountered an issue with the following parameter source: "
                f" {self.fname}. The source should contain only one of the "
                "parameters 'influencers_whitelist', 'influencers_blacklist', "
                "'influencers_file' and influencers_select_atoms, but "
                "contains more than one.",
                "SU_WP_16", True
            )

        if "influencers_whitelist" in self.choices:
            self.choices["influencers"] = self.choices["influencers_whitelist"]
        elif "influencers_blacklist" in self.choices:
            # invert the choice by subtracting the blacklist choice from all
            self.choices["influencers"] = [":All", "-", "("] + self.choices[
                "influencers_blacklist"
            ] + [")"]
        elif "influencers_file" in self.choices:
            self.choices["influencers"] = self.choices["influencers_file"]
        elif "influencers_select_atoms" in self.choices:
            self.choices["influencers"] = " ".join(
                self.choices["influencers_select_atoms"]
            )

    def finalize_map_pars(self, Printer):
        """Check whether `not_found` is empty

        This method is called after
        :meth:`~GMAP.src.tools.MapReader.Map.find_rawpars` is run for
        every available instance of
        :class:`~GMAP.src.tools.MapReader.Map`. Any parameters
        recognised there were removed from
        the `not_found` dictionary, so it should be empty, if all parameters
        were understood. Here we check if that is indeed the case.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """
        if len(self.not_found.keys()) != 0:
            Printer.warning(
                f"\nUnknown parameter {list(self.not_found.keys())[0]} "
                "found in "
                "the "
                f"file {self.fname}. "
                "Please make sure you spelled it correctly.",
                "SU_WP_15", True
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
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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
    requested_mapdict : dict of str: :class:`~GMAP.src.tools.MapReader.Map`
        The maps that should be applied during the calculation.

    """

    def __init__(
        self, Files, Printer, CmdPars, InPars, DefPars, RefPars, is_main,
        MainRunPars=None
    ):
        self.is_main = is_main
        if not is_main:
            self.MainRunPars = MainRunPars
        else:
            self.MainRunPars = self

        # Extract all 'normal' parameters
        self.get_pars(Printer, CmdPars, InPars, DefPars, RefPars)

        # Extract all parameters that are a file
        self.get_files(Files, Printer, CmdPars, InPars, DefPars, RefPars)

        if self.is_main:
            Printer.set_state(
                "running", self.verbose, self.verbose_logfile,
                self.log_filename
            )

        # Resolve conflicts due to choices, change any settings that need to
        # be changed, due to parameters

    def get_pars(self, Printer, CmdPars, InPars, DefPars, RefPars):
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
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
                Printer.warning(
                    f"\nNo choice for the parameter {parname} could be found. "
                    "Please specify a choice on either the command line, or "
                    "in the input file. ",
                    "SU_NP_1", True
                )
            if parname not in RefPars.maybe_list:
                choice = choice[0]

            setattr(self, parname, choice)

    def get_files(self, Files, Printer, CmdPars, InPars, DefPars, RefPars):
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
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
            Files, Printer, CmdPars, InPars, DefPars, RefPars
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
                Printer.warning(
                    f"\nThe directory {', '.join(names)} was requested for "
                    "the "
                    f"parameter map_directory, but could not be found, or is "
                    "not a directory. Please make sure you specified it "
                    "correctly.",
                    "SU_NP_3", True
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
                Printer.warning(
                    f"\nNo choice for the parameter {parname} could be found. "
                    "Please specify a choice on either the command line, or "
                    "in the input file. ",
                    "SU_NP_1", True, exception=ex
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
                    Printer.warning(
                        f"\nThe file(s) {', '.join(names)} was requested for "
                        "the "
                        f"parameter {parname}, "
                        "but could not be found, or is not a "
                        "file. Please make sure you specified it correctly.\n",
                        "SU_NP_2", True
                    )
                else:
                    Printer.warning(
                        f"\nThe file(s) {', '.join(names)} was requested for "
                        "the "
                        f"parameter {parname}, for the map "
                        f"{RefPars.fname.parent.name}, "
                        "but could not be found, or is not a "
                        "file. Please make sure you specified it correctly.\n",
                        "SU_NP_2", True
                    )

            if parname in RefPars.maybe_list:
                setattr(self, parname, files_found)
            else:
                setattr(self, parname, files_found[0])

    def get_ordered_files(
        self, Files, Printer, CmdPars, InPars, DefPars, RefPars
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
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
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
        if not DefPars.fname == RefPars.fname:
            dirlist.append(DefPars.choices)
            fnamelist.append(DefPars.fname)

        for dir_parname, file_parnames in RefPars.organized_filepars.items():
            try:
                dir_hc = RefPars.choices[dir_parname][0]
            except Exception:
                dir_hc = Files.cwd

            dir_hc = GM_FH.get_bare_file(
                Files, dir_parname, [dir_hc], RefPars.fname.parent,
                CmdPars.choices, dirlist, fnamelist
            )
            name = dir_hc[0]
            if name.is_dir():
                setattr(self, dir_parname, name.resolve())
            else:
                if self.is_main:
                    Printer.warning(
                        f"\nThe directory {name.resolve()} was requested for "
                        "the "
                        f"parameter {dir_parname}, but could not be found, or "
                        "is "
                        "not a directory. Please make sure you specified it "
                        "correctly.",
                        "SU_NP_3", True
                    )
                else:
                    Printer.warning(
                        f"\nThe directory {name.resolve()} was requested for "
                        "the "
                        f"parameter {dir_parname}, for the map "
                        f"{RefPars.fname.parent.name}, "
                        "but could not be found, or is "
                        "not a directory. Please make sure you specified it "
                        "correctly.",
                        "SU_NP_3", True
                    )

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
                    # directory exists.
                    files_found = [file.resolve() for file in files_found]
                    names = files_found
                    file_found = files_found[0]
                    for file in files_found:
                        par_dir = file.parent
                        if not par_dir.is_dir():
                            file_found = None

                if not file_found:
                    names = [str(file) for file in names]
                    Printer.warning(
                        f"\nThe file(s) {'.'.join(names)} was requested "
                        "for the parameter "
                        f"{file_parname}, but could not be found, or is not a "
                        "file. Please make sure you specified it correctly. "
                        "This error could also be triggered by a mistake in "
                        f"the choice for {dir_parname}.\n", "SU_NP_2", True
                    )

                if (
                    file_parname in RefPars.filepars_create
                    and self.MainRunPars.prevent_overwrite
                    and file_found.is_file()
                ):
                    # A new file should be made, but if a file of the same
                    # name already exists, it shouldn't be replaced.
                    # We already know that the parent directory of the
                    # requested path exists.
                    for file in files_found:
                        rawname = file.name
                        backup_path = file.resolve()

                        addnum = 0
                        while backup_path.is_file():
                            addnum += 1
                            backup_path = file.parent.resolve()
                            backup_path /= f"#{rawname}.{addnum}#"

                        file.rename(backup_path)

                if file_parname in RefPars.maybe_list:
                    setattr(self, file_parname, files_found)
                else:
                    setattr(self, file_parname, files_found[0])


def parse_commandline(
    Files, Printer, callcommand, alljobs, helpcall, expect_inputfile=False,
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
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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
        Printer.warning(
            f"\nChoice '{job}' was not recognized. "
            "Please type the following to see all available options:"
            f"\n\n{helpcall}\n",
            "SU_PP_1", True
        )

    if expect_inputfile:
        # if we expect an input filename, but it isn't there, error!
        if len(callcommand) < 3:
            Printer.warning(
                f"\n{job} requires an input file. Quitting!", "SU_PP_2", True
            )

        in_parfile = (Files.cwd / callcommand[2]).resolve()
        if not (in_parfile.exists() and in_parfile.is_file()):
            Printer.warning(
                f"\nThe requested input parameter file {in_parfile} could not "
                "be found, or is not a file. "
                "Please make sure you specified it correctly.\n",
                "SU_PP_3", True
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


def find_defparfile_in_cmd(Printer, argslist):
    """Finds any parameters pertaining to default parfile in command line

    Given an argslist (the part of sys.argv that should/could contain
    arguments), see if there is anything hinting at a default parameter
    file there.

    Parameters:
    -----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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
        Printer, argslist, srcdir_names, "source_directory"
    )
    if srcdir:
        pardict["source_directory"] = srcdir

    defparfile_names = ("--default_parameter_filename", "-dpf")
    defparfile = find_par_in_cmd(
        Printer, argslist, defparfile_names, "default_parameter_filename"
    )
    if defparfile:
        pardict["default_parameter_filename"] = defparfile

    return pardict


def find_par_in_cmd(Printer, argslist, flags, parname, is_list=False):
    """Searches for a given parameter in the command line

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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
            Printer.warning(
                "\nThe program was called with more than one setting "
                f"for {parname}. "
                "Please make sure your command contains this parameter at "
                "most once.",
                "SU_PP_4", True
            )

        warntext = f"\n{used_flag} requires a file name to be specified.",
        try:
            choice = [argslist[ix + 1]]
        except IndexError:
            Printer.warning(warntext, "SU_WP_4", True)
        if choice[0].startswith("-"):
            Printer.warning(warntext, "SU_WP_4", True)

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
                    Printer.warning(warntext, "SU_WP_5", True)
                if choice[-1].startswith("-"):
                    Printer.warning(warntext, "SU_WP_5", True)
            choice[-1] = choice[-1][:-2]

        return choice


def find_mapdir(Files, Printer, argslist, InPars, DefPars):
    """Extracts choice for the parameter map_directory from the command line.

    If the choice has been found, checks whether it exists. If it does not,
    triggers warning and stops the program.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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
        Printer, argslist, map_flags, "map_directory", is_list=True
    )
    # if cmd supplied, check if exists
    if cmd_mapdir:
        mapdirs = directory_list_checker(
            Printer, Files.cwd, cmd_mapdir, "map_directory", "the command line"
        )

    elif InPars and "map_directory" in InPars.choices:
        mapdirs = directory_list_checker(
            Printer,
            InPars.fname.parent,
            InPars.choices["map_directory"],
            "map_directory",
            InPars.fname
        )

    else:
        mapdirs = directory_list_checker(
            Printer,
            DefPars.fname.parent,
            DefPars.choices["map_directory"],
            "map_directory",
            DefPars.fname
        )

    return mapdirs


def directory_list_checker(Printer, parent, direclist, parname, source):
    """Checks whether each of the given paths exists, and is a directory.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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
        Printer.warning(
            f"\nThe following choice(s) for {parname} found in {source} "
            "either "
            "do not exist, or are not directories:\n"
            + "\n".join(failed),
            "SU_PP_3", True
        )
    dirs = [loc.resolve() for loc in dirs]
    return dirs


def get_pardict(iterable):
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

    Returns
    -------
    outdict : dict
        The new information. Keys are the zeroeth item, values are lists of the
        remaining items.

    """
    outdict = {}
    for line in iterable:
        line = cleanline(line).strip()
        if len(line) == 0:
            continue
        linelist = [term.strip() for term in line.split()]
        linelist = [term for term in linelist if term]

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


def parse_influencerfile(Printer, fname, groupdict):
    """Parses an entire influencer file. A collection of influencers.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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
                Printer, " ".join(line[1:]), groupdict, fname
            )
    return groupdict


def parse_influencerfile_line(Printer, line, groupdict, fname):
    """Parse a single influencer definition.

    Influencers are groups of residue names. A group can contain many,
    a single, or no items. This function deals with the definition of
    one of those groups. The resulting set is returned so it can be
    used/assigned.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
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

    dpr(line)
    dpr(allowed_chars)
    problem_chars = [char for char in line if char not in allowed_chars]
    dpr(problem_chars)

    if problem_chars:
        Printer.warning(
            f"The influencers file {fname} contains one or more invalid "
            "characters. Make sure the following characters are not present: "
            f"{''.join(problem_chars)}.",
            "SU_NP_4", True
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
    else:
        if is_name:
            if fromdict:
                final_choice += "groupdict['" + curname + "']"
                fromdict = False
            else:
                final_choice += "set(['" + curname + "'])"

    dpr(final_choice)

    try:
        exec(final_choice)
    except Exception as ex:
        Printer.warning(
            f"\nThe file {fname} has a problem with one of the definitions "
            "of parameters. See the error for more information.",
            "SU_NP_5", True, exception=ex
        )

    # return GM_get_dipole
    try:
        newset = locals()["build_set"](groupdict)
    except Exception as ex:
        Printer.warning(
            f"\nThe file {fname} has a problem with one of the definitions "
            "of parameters. See the error for more information.",
            "SU_NP_5", True, exception=ex
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
