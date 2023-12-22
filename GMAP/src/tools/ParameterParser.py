
from pathlib import Path

import GMAP.src.tools.PrintTools as GM_PT
from GMAP.src.tools.PrintTools import devprint as dpr


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
    intpars : list of str
        contains all parameters of type int.
    not_expected_in_deffile : list of str
        A list of parameters which are not expected (and allowed) to define a
        choice in reference (or default) parameter files.
    maybe_list : list of str
        Some parameters allow more than one choice to be given. All these
        parameters are stored in this list, but must also be stored depending
        on the expected type of the items in the list.

    """

    def __init__(self, fname):
        self.fname = fname
        self.add_groups()

        self.parse_refparfile(self.parse_line_type_protected)
        self.parse_refparfile(self.parse_line_choice_protected)

    @classmethod
    def add_reffile(cls, fname, base_refpars):
        """
        When the default parameter file given by the user is of .ref format\
        instead of .txt, it ends up here. How are .ref files treated different?
            - most importantly: format! A .ref file is formatted differently
              from a .txt.
            - While a .txt only stores the choice for each parameter, the .ref
              also stores the allowed options. This would allow users to impose
              stricter limits. Is this actually useful???
        """
        GM_PT.Warning(
            "Not implemented yet!",
            True
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

        # -----
        # other-type parameters
        # -----
        self.intpars = []

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
                    GM_PT.Warning(
                        "The following problem occured when reading the "
                        f"default parameter file {self.fname}"
                        "\n\nOne of the lines contains only one item, while "
                        "pairs are expected. Quitting!",
                        True
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
        except (TypeError, KeyError):
            GM_PT.Warning(
                "Could not interpret the parameter name on the following "
                f"line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                True
            )
        except Exception:
            GM_PT.Warning(
                "Encountered an error while parsing the parameter name on the "
                f"following line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                True
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

        if partype[0] == "path":
            self.allfilepars.append(parname)
            if partype[1] == "dir":
                self.organized_filepars_id[partype[2]] = parname
                self.organized_filepars[parname] = []
            elif partype[1] == "rel":
                parent_dir = self.organized_filepars_id[partype[2]]
                self.organized_filepars[parent_dir].append(parname)
            else:
                raise KeyError

        elif partype[0] == "int":
            self.intpars.append(parname)

        else:
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

        # self.parse_line_choice(linelist)
        try:
            self.parse_line_choice(linelist)
        except (TypeError, IndexError):
            GM_PT.Warning(
                "Could not interpret the parameter choice on the following "
                f"line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                True
            )
        except Exception:
            GM_PT.Warning(
                "Encountered an error while parsing the parameter choice on "
                f"the following line:\n{line}"
                "\nwhile reading the following file as reference "
                f"file:\n{self.fname}"
                "\nQuitting!",
                True
            )

    def parse_line_choice(self, linelist):
        """Extract the choice for a parameter specified on the given line

        Analizes all information regarding the choice and options. Also
        converts any choice/option into the datatype recognized by
        :meth:`parse_line_type`

        Parameters
        ----------
        linelist : list of str
            The contents of a single line in the parameters.ref file, but
            processed and split into a usable format.
        """
        parname_raw = linelist[0]
        parchoice_raw = linelist[1:]

        parname = self.parse_key(parname_raw)[0]

        if parname in self.not_expected_in_deffile:
            return

        options = []
        choices = []

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
        else:
            raise TypeError

        options = [usetype(x) for x in options]
        choices = [usetype(x) for x in choices]

        # if at least one pair of square brackets (selected items), that
        # indicates that there are only limited choices, instead of general
        if len(choices) != 0:
            if parname not in self.maybe_list and len(choices) != 1:
                raise IndexError
            else:
                self.options[parname] = options
                self.choices[parname] = choices
        # if there is no square brackets (selected items), that indicates that
        # there is free parameter choice, so no need to save allowed options
        else:
            self.choices[parname] = options

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

    def __init__(self, fname, is_default):
        self.fname = fname
        self.is_default = is_default

    @classmethod
    def from_dict(cls, fname, given_dict, refpars, is_default):
        """Create an instance of this class for parameters stored in a dict.

        .. seealso ::
            :meth:`from_file`, :meth:`from_cmdline`

        Parameters
        ----------
        fname : pathlib.Path
            The name of the file from which the data in `given_dict` was
            obtained
        given_dict : dict
            Contains parameter choices. Keys are the parameter names (str),
            values are lists containing all choices (str). Lists are still
            expected when there are 0 or 1 choices.
        refpars : `RefPars`
            Contains all parameters that might be found in `given_dict`.
        is_default : bool
            Whether this is a default file (i.e. complete, see
            :class:`RawPars`)

        Returns
        -------
        instance : `RawPars`
            A newly generated instance with all choices parsed and stored.
        """

        instance = cls(fname, is_default)

        instance.extract_choices(given_dict, refpars)
        if is_default:
            instance.check_completeness(refpars)
        return instance

    @classmethod
    def from_file(cls, fname, refpars, is_default):
        """Create an instance of this class for parameters stored in a file.

        First obtains a dict from the file, then uses :meth:`from_dict`

        .. seealso ::
            :meth:`from_dict`, :meth:`from_cmdline`

        Parameters
        ----------
        fname : pathlib.Path
            The name of the file from which to obtain the parameters
        refpars : `RefPars`
            Contains all parameters that might be found in `given_dict`.
        is_default : bool
            Whether this is a default file (i.e. complete, see
            :class:`RawPars`)

        Returns
        -------
        instance : `RawPars`
            A newly generated instance with all choices parsed and stored.
        """
        with open(fname) as file:
            given_dict = get_pardict(file)

        instance = cls(fname, is_default)

        instance.extract_choices(given_dict, refpars)
        if is_default:
            instance.check_completeness(refpars)
        return instance

    @classmethod
    def from_cmdline(cls, cmdargs, refpars, maprefpars_dict, is_default):
        """Create an instance of this class for parameters in the command line

        A method more different from the others, as it has to do some parsing,
        too. Also immediately deals with map-specific parameters, while
        instances created from other sources need an extra pass for those.

        .. seealso ::
            :meth:`from_dict`, :meth:`from_file`

        Parameters
        ----------
        cmdargs : list of str
            A slice from the list generated using sys.argv
        refpars : `RefPars`
            Contains all parameters that might be found in `given_dict`.
        maprefpars_dict : dict
            A dictionary containing the RefPars objects for all recognized
            maps. Keys are the map names, values are their RefPars object.
        is_default : bool
            Whether this is a default file (i.e. complete, see
            :class:`RawPars`)

        Returns
        -------
        instance : `RawPars`
            A newly generated instance with all choices parsed and stored.
        """

        instance = cls("command line", is_default)
        pardict = {}

        while len(cmdargs) > 0:
            if not cmdargs[0].startswith("-"):
                GM_PT.Warning(
                    "The name of a parameter specified on the command line "
                    "should be preceeded with '-'.",
                    True
                )
            curparraw = cmdargs.pop(0)
            curpar = curparraw.strip("-")
            hyphno = len(curparraw) - len(curpar)
            if hyphno == 1:
                expect_shorthand = True
            else:
                expect_shorthand = False

            if '.' in curpar:
                warntext = (
                    f"The parameter {curpar} as specified on the command "
                    "line is not recognised. Please make sure you spelled "
                    "it correctly."
                )
                curpar_list = curpar.split('.')
                try:
                    refpars_to_use = maprefpars_dict[curpar_list[0]]
                    curpar_tocheck = curpar_list[1]
                except KeyError:
                    GM_PT.Warning(warntext, True)

            else:
                refpars_to_use = refpars
                curpar_tocheck = curpar

            if expect_shorthand:
                curpar_tocheck = refpars_to_use.shorthands[curpar_tocheck]
                if "." in curpar:
                    curpar = curpar_list[0] + "." + curpar_tocheck
                else:
                    curpar = curpar_tocheck
            dpr(curpar_tocheck)

            found = instance.check_par_existence(
                curpar, curpar_tocheck, refpars_to_use, None, False
            )[1]

            if not found:
                GM_PT.Warning(warntext, True)

            # now, we know the parameter exists. Next is to see how many
            # choices to look for!
            if curpar_tocheck in refpars_to_use.maybe_list:
                try:
                    choice = [cmdargs.pop(0)]
                except IndexError:
                    GM_PT.Warning(
                        f"The parameter {curpar} specified in the command "
                        "line requires a choice to be given.",
                        True
                    )
                warntext = (
                    f"The parameter {curpar} specified in the command line "
                    "requires the last choice to be appended with '\\;'."
                )
                while not choice[-1].endswith("\\;"):
                    try:
                        choice.append[cmdargs.pop(0)]
                    except IndexError:
                        GM_PT.Warning(warntext, True)

                    if choice[-1].startswith("-"):
                        GM_PT.Warning(warntext, True)
                choice[-1] = choice[-1][:-2]
            else:
                try:
                    choice = [cmdargs.pop(0)]
                except IndexError:
                    GM_PT.Warning(
                        f"The parameter {curpar} specified in the command "
                        "line requires a choice to be given.",
                        True
                    )

            pardict[curpar] = choice

        instance.extract_choices(pardict, refpars)
        if is_default:
            instance.check_completeness(refpars)

        for name, maprefpar in maprefpars_dict.items():
            instance.extract_choices_map(name, maprefpar)
        instance.finalize_map_pars()

        return instance

    def extract_choices(self, given_dict, refpars):
        """Takes each parameter and their choice from the dict for parsing

        Each pair is forwarded to the correct location for further parsing.
        Does not deal in-depth with map-specific parameters.
        :meth:`extract_choices_map` does.

        Parameters
        ----------
        given_dict : dict
            Contains parameter choices. Keys are the parameter names (str),
            values are lists containing all choices (str). Lists are still
            expected when there are 0 or 1 choices.
        refpars : `RefPars`
            Contains all parameters that might be found in `given_dict`.
        """
        self.choices = {}
        self.not_found = {}

        # lets find out about each parameter!
        for parname, choice in given_dict.items():

            # # if parameter is known
            # if parname in refpars.choices:
            #     choice = self.verify_choice(parname, choice, refpars)
            #     if choice is None:
            #         continue
            #     self.choices[parname] = choice

            # # if parameter is known, but shouldn't be in default parfiles
            # elif parname in refpars.not_expected_in_deffile:
            #     if self.is_default and len(choice) != 0:
            #         GM_PT.Warning(
            #             f"A choice for the parameter {parname} is specified "
            #             f"in the default parameter file {self.fname}. "
            #             "However, default files cannot contain a choice for "
            #           "this parameter. Please remove the parameter from the "
            #             "file.",
            #             True
            #         )
            #     elif self.is_default:
            #         continue
            #     else:
            #         choice = self.verify_choice(parname, choice, refpars)
            #         if choice is None:
            #             continue
            #         self.choices[parname] = choice
            choice, found = self.check_par_existence(
                parname, parname, refpars, choice
            )
            if found:
                continue

            # anything that's left, is not part of base program

            # if parameter is expected to not belong to core, but mapping
            elif "." in parname:
                self.not_found[parname] = choice

            # parameter should belong to core, but isn't recognized
            else:
                GM_PT.Warning(
                    f"Unknown parameter {parname} found in the file "
                    f"{self.fname}. "
                    "Please make sure you spelled it correctly.",
                    True
                )

    def verify_choice(self, parname, choice, refpars):
        # currently, all parameters must take an argument (no bools yet)
        if len(choice) == 0:
            if self.is_default:
                GM_PT.Warning(
                    f"No choice detected for the parameter {parname} "
                    f"specified in the file {self.fname}. "
                    "All parameters must be specified for the file to be "
                    "used.",
                    True
                )
            else:
                GM_PT.Warning(
                    f"No choice detected for the parameter {parname} "
                    f"specified in the file {self.fname}. "
                    "Either remove the parameter line, or make a choice.",
                    True
                )
                return

        # if we expect a single choice, but multiple were given
        elif len(choice) > 1 and parname not in refpars.maybe_list:
            GM_PT.Warning(
                f"Too many choices given for the parameter {parname} "
                f"specified in the file {self.fname}. "
                "Please only specify one.",
                True
            )

        # now, correct amount of arguments.
        errortext1 = (
            f"Invalid choice given for the parameter {parname} "
            f"specified in the file {self.fname}. "
            "Please refer to the manual for the allowed options."
        )
        errortext2 = (
            f"Choice given for the parameter {parname} specified in the file "
            f"{self.fname} is of the wrong type. "
            "Please refer to the manual for the expected type."
        )

        if parname in refpars.intpars:
            try:
                choice = [int(x) for x in choice]
            except Exception:
                GM_PT.Warning(errortext2, True)

        if parname not in refpars.options:
            return choice

        if any(
            opt not in refpars.options[parname] for opt in choice
        ):
            GM_PT.Warning(errortext1, True)
        else:
            return choice

    def extract_choices_map(self, mapname, maprefpars):
        to_del = []
        for parname, choice in self.not_found.items():
            parnamelist = parname.split(".")
            if len(parnamelist) != 2:
                GM_PT.Warning(
                    "Names of map-specific parameters cannot contain a '.'.",
                    True
                )
            if parnamelist[0] != mapname:
                continue

            # now, we know that this parameter (supposedly) belongs to this map
            # if parnamelist[1] in maprefpars.choices:
            #   choice = self.verify_choice(parnamelist[1], choice, maprefpars)
            #     if choice is None:
            #         continue
            #     self.choices[parname] = choice

            # elif parnamelist[1] in maprefpars.not_expected_in_deffile:
            #     if self.is_default and len(choice) != 0:
            #         GM_PT.Warning(
            #             f"A choice for the parameter {parname} is specified "
            #             f"in the default parameter file {self.fname}. "
            #             "However, default files cannot contain a choice for "
            #           "this parameter. Please remove the parameter from the "
            #             "file.",
            #             True
            #         )
            #     elif self.is_default:
            #         continue
            #     else:
            #         choice = self.verify_choice(
            #             parnamelist[1], choice, maprefpars
            #         )
            #         if choice is None:
            #             continue
            #         self.choices[parname] = choice
            choice, found = self.check_par_existence(
                parname, parnamelist[1], maprefpars, choice
            )

            # parameter is not recognized
            if not found:
                GM_PT.Warning(
                    f"Unknown parameter {parname} found in the file "
                    f"{self.fname}. "
                    "Please make sure you spelled it correctly.",
                    True
                )

            to_del.append(parname)

        for parname in to_del:
            del self.not_found[parname]

    def check_par_existence(
        self, parname_full, parname_refpars, refpars, choice, do_verify=True
    ):
        found = False
        if parname_refpars in refpars.choices:
            found = True
            if do_verify:
                choice = self.verify_choice(parname_refpars, choice, refpars)
            if not do_verify or choice is None:
                return None, found
            else:
                self.choices[parname_full] = choice

        elif parname_refpars in refpars.not_expected_in_deffile:
            found = True
            if self.is_default and len(choice) != 0:
                GM_PT.Warning(
                    f"A choice for the parameter {parname_full} is specified "
                    f"in the default parameter file {self.fname}. "
                    "However, default files cannot contain a choice for "
                    "this parameter. Please remove the parameter from the "
                    "file.",
                    True
                )
            elif self.is_default:
                return None, found
            else:
                if do_verify:
                    choice = self.verify_choice(
                        parname_refpars, choice, refpars
                    )
                if not do_verify or choice is None:
                    return None, found
                else:
                    self.choices[parname_full] = choice

        return choice, found

    def check_completeness(self, refpars):
        for parname in refpars.choices.keys():
            if parname not in self.choices:
                GM_PT.Warning(
                    f"No entry found for the parameter {parname} in the "
                    f"default parameter file {self.fname}. "
                    "All parameters must be specified for default files to "
                    "be used.",
                    True
                )

    def finalize_map_pars(self):
        if len(self.not_found.keys()) != 0:
            GM_PT.Warning(
                f"Unknown parameter {self.not_found.keys()[0]} found in the "
                f"file {self.fname}. "
                "Please make sure you spelled it correctly.",
                True
            )


class RunPars:
    def __init__(self, FILES, cmd_pars, in_pars, def_pars, ref_pars):
        pass

        # first, find logfile location (so we can swith to that for output
        # quickly instead of sticking with temporary file...)

        # then, find verbose setting, and print all that should've been printed
        # to log earlier. But of course, with the verbose filter.

        # after, extract the mapdir parameter, so we know where to look for
        # those

        # then (finally!), search through mapdir to find any maps to apply.


def parse_commandline(
    FILES, callcommand, alljobs, helpcall, expect_inputfile=False,
    expect_parameters=False
):
    """
    Parses a command stored in a list, to return and check different
    parts. Expects the following items:
    [0] should contain the name of the tool used. eg. GEM, AIM.
    [1] should contain the requested job from the tool. eg. run, demo.
    (if expect_inputfile == True) the filename of the input file to use
    (if expect_parameters == True) the further parameters to use. Optional

    Parameters specified on the command line must have the parameter name
    preceded with '-'.
    """

    job = callcommand[1]

    if job.lower() not in alljobs:
        GM_PT.Warning(
            f"\nChoice '{job}' was not recognized. "
            "Please type the following to see all available options:"
            f"\n\n{helpcall}\n",
            True
        )

    if expect_inputfile:
        # if we expect an input filename, but it isn't there, error!
        if len(callcommand) < 3:
            GM_PT.Warning(f"{job} requires an input file. Quitting!", True)

        in_parfile = (FILES.cwd / callcommand[2]).resolve()
        if not (in_parfile.exists() and in_parfile.is_file()):
            GM_PT.Warning(
                f"\nThe requested input parameter file {in_parfile} could not "
                "be found, or is not a file. "
                "Please make sure you specified it correctly.\n",
                True
            )
        args_list = callcommand[3:]
    else:
        in_parfile = None
        args_list = callcommand[2:]

    if expect_parameters:
        cmd_pars = args_list
    else:
        cmd_pars = None

    return job, in_parfile, cmd_pars


def find_defparfile_in_cmd(argslist):
    """
    Given an argslist (the part of sys.argv that should/could contain
    arguments), see if there is anything hinting at a default parameter
    file there.
    """
    pardict = {}

    srcdir_names = ("--source_directory", "-sd")
    srcdir = find_par_in_cmd(argslist, srcdir_names, "source_directory")
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
            GM_PT.Warning(
                "The program was called with more than one setting "
                f"for {parname}. "
                "Please make sure your command contains this parameter at "
                "most once.",
                True
            )

        warntext = f"{used_flag} requires a file name to be specified.",
        try:
            choice = [argslist[ix + 1]]
        except IndexError:
            GM_PT.Warning(warntext, True)
        if choice[0].startswith("-"):
            GM_PT.Warning(warntext, True)

        if is_list:
            adder = 2
            warntext = (
                f"{used_flag} requires the last choice to be appended with "
                "'\\;'."
            )
            while not choice[-1].endswith("\\;"):
                try:
                    choice.append(argslist[ix + adder])
                    adder += 1
                except IndexError:
                    GM_PT.Warning(warntext, True)
                if choice[-1].startswith("-"):
                    GM_PT.Warning(warntext, True)
            choice[-1] = choice[-1][:-2]

        return choice


def find_mapdir(argslist, FILES, in_pars, def_pars):
    map_flags = ("--map_directory", "-md")
    cmd_mapdir = find_par_in_cmd(
        argslist, map_flags, "map_directory", is_list=True
    )
    # if cmd supplied, check if exists
    if cmd_mapdir:
        mapdirs = directory_list_checker(
            FILES.cwd, cmd_mapdir, "map_directory", "the command line"
        )

    elif in_pars and "map_directory" in in_pars.choices:
        mapdirs = directory_list_checker(
            in_pars.fname.parent,
            in_pars.choices["map_directory"],
            "map_directory",
            in_pars.fname
        )

    else:
        mapdirs = directory_list_checker(
            def_pars.fname.parent,
            def_pars.choices["map_directory"],
            "map_directory",
            def_pars.fname
        )

    return mapdirs


def directory_list_checker(parent, direclist, parname, source):
    """This function does something.

    Parameters
    ----------
    var1 : array_like
        This is a type.
    var2 : int
        This is another var.
    Long_variable_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    describe : type
        Explanation
    """
    dirs = [parent / direc for direc in direclist]
    failed = [str(direc.resolve()) for direc in dirs if not direc.is_dir()]
    if len(failed) > 0:
        # not using fstrings here, as backslashes arent supported in
        # fstrings before python 3.12.
        GM_PT.Warning(
            f"The following choice(s) for {parname} found in {source} either "
            "do not exist, or are not directories:\n"
            + "\n".join(failed),
            True
        )
    dirs = [loc.resolve() for loc in dirs]
    return dirs


def get_pardict(iterable):
    """
    Takes an iterable, and returns it as dict form.
    Each iteration of the iterable is subjected to .split(); the zeroeth item
    becomes the key, the list of the remaining items (or empty list) becomes
    the value.
    All keys and items in value lists are strings - the contents are NOT
    interpreted, and converted to correct datatypes.

    """
    outdict = {}
    for line in iterable:
        line = cleanline(line).strip()
        if len(line) == 0:
            continue
        linelist = [term.strip() for term in line.split()]

        outdict[linelist[0]] = linelist[1:]
    return outdict


def cleanline(line, escape_char="#"):
    """
    Removes any escape character and text following it (i.e., get rid of
    comments).
    Default escape character is '#'
    """
    return line.split(escape_char)[0]
