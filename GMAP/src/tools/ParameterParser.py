
from pathlib import Path

import GMAP.src.tools.WarnSys as GM_WS


class RefPars:
    def __init__(self, fname):
        self.fname = fname
        self.add_groups()

        self.parse_refparfile(self.parse_line_type_protected)
        self.parse_refparfile(self.parse_line_choice_protected)

    @classmethod
    def add_reffile(cls, fname, base_refpars):
        """
        When the default parameter file given by the user is of .ref format
        instead of .txt, it ends up here. How are .ref files treated different?
         - most importantly: format! A .ref file is formatted differently from
           a .txt.
         - While a .txt only stores the choice for each parameter, the .ref
           also stores the allowed options. This would allow users to impose
           stricter limits. Is this actually useful???
        """
        GM_WS.Warning(
            "Not implemented yet!",
            True
        )

    def add_groups(self):
        self.options = {}  # key = parname, val = possible options
        self.choices = {}  # key = parname, val = choice
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
        """
        Loops through lines of given file. Each line is stripped of comments,
        and empty lines are ignored. For each remaining line, the function
        func is called.
        """
        with open(self.fname) as file:
            for line in file:
                line = cleanline(line).strip()  # remove all comments
                if len(line) == 0:  # ignore all empty lines
                    continue

                linelist = line.split()
                if len(linelist) == 1:
                    GM_WS.Warning(
                        "The following problem occured when reading the "
                        "default parameter file " + str(self.fname) +
                        "\n\nOne of the lines contains only one item, while "
                        "pairs are expected. Quitting!",
                        True
                    )

                # now, line must have at least length 2. Start interpreting!
                func(line, linelist)

    def parse_line_type_protected(self, line, linelist):
        try:
            self.parse_line_type(linelist)
        except (TypeError, KeyError):
            GM_WS.Warning(
                "Could not interpret the parameter name on the following "
                "line:\n" + line +
                "\nwhile reading the following file as reference "
                "file:\n" + str(self.fname) +
                "\nQuitting!",
                True
            )
        except Exception:
            GM_WS.Warning(
                "Encountered an error while parsing the parameter name on the "
                "following line:\n" + line +
                "\nwhile reading the following file as reference "
                "file:\n" + str(self.fname) +
                "\nQuitting!",
                True
            )

    def parse_line_type(self, linelist):
        parname_raw = linelist[0]
        parchoice_raw = linelist[1:]

        parname, partype = self.parse_key(parname_raw)

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
        # self.parse_line_choice(linelist)
        try:
            self.parse_line_choice(linelist)
        except (TypeError, IndexError):
            GM_WS.Warning(
                "Could not interpret the parameter choice on the following "
                "line:\n" + line +
                "\nwhile reading the following file as reference "
                "file:\n" + str(self.fname) +
                "\nQuitting!",
                True
            )
        except Exception:
            GM_WS.Warning(
                "Encountered an error while parsing the parameter choice on "
                "the following line:\n" + line +
                "\nwhile reading the following file as reference "
                "file:\n" + str(self.fname) +
                "\nQuitting!",
                True
            )

    def parse_line_choice(self, linelist):
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
        key_name, key_dtype = string.split("[")
        key_dtype = key_dtype.strip("]").split("_")
        return key_name, key_dtype


class RawPars:
    def __init__(self, fname, given_dict, refpars, is_default):
        """
        Takes a dictionary from the format created by get_pardict, and parses
        it:
        For each parameter, see if it is in the refpars object. if not, it is
        either a typo, or a map-specific parameter. If former, raise error,
        if latter, save for later (2nd pass done by the .... function).
        If it is in refpars, see if choice is valid (one of the allowed choices
        and/or of correct datatype).
        All choices are saved in self.choices, in the same format as the
        refpars object.

        If is_default is True, the file is assumed a default file, and must
        contain a choice for each and every parameter (except for those flagged
        as not expected in default file).
        If it is False, the file is assumed an input file, and may miss some.
        """

        self.fname = fname
        self.is_default = is_default
        self.extract_choices(given_dict, refpars)
        if is_default:
            self.check_completeness(refpars)

    @classmethod
    def from_dict(cls, fname, given_dict, refpars, is_default):
        return cls(fname, given_dict, refpars, is_default)

    @classmethod
    def from_file(cls, fname, refpars, is_default):
        with open(fname) as file:
            given_dict = get_pardict(file)

        return cls.__init__(fname, given_dict, refpars, is_default)

    def extract_choices(self, given_dict, refpars):
        self.choices = {}
        self.not_found = {}

        # lets find out about each parameter!
        for parname, choice in given_dict.items():

            # if parameter is known
            if parname in refpars.choices:
                choice = self.verify_choice(parname, choice, refpars)
                if choice is None:
                    continue
                self.choices[parname] = choice

            # if parameter is known, but shouldn't be in default parfiles
            elif parname in refpars.not_expected_in_deffile:
                if self.is_default and len(choice) != 0:
                    GM_WS.Warning(
                        "A choice for the parameter " + parname +
                        " is specified in the default parameter file "
                        + str(self.fname) +
                        ". However, default files cannot contain a choice for "
                        "this parameter. Please remove the parameter from the "
                        "file.", True
                    )
                elif self.is_default:
                    continue
                else:
                    choice = self.verify_choice(parname, choice, refpars)
                    if choice is None:
                        continue
                    self.choices[parname] = choice

            # anything that's left, is not part of base program

            # if parameter is expected to not belong to core, but mapping
            elif "." in parname:
                self.not_found[parname] = choice

            # parameter should belong to core, but isn't recognized
            else:
                GM_WS.Warning(
                    "Unknown parameter " + parname +
                    " found in the file " + str(self.fname) +
                    ". Please make sure you spelled it correctly.",
                    True
                )

    def verify_choice(self, parname, choice, refpars):
        # currently, all parameters must take an argument (no bools yet)
        if len(choice) == 0:
            if self.is_default:
                GM_WS.Warning(
                    "No choice detected for the parameter " + parname +
                    " specified in the file " + str(self.fname) +
                    ". All parameters must be specified for the file to be "
                    "used.",
                    True
                )
            else:
                GM_WS.Warning(
                    "No choice detected for the parameter " + parname +
                    " specified in the file " + str(self.fname) +
                    ". Either remove the parameter line, or make a choice.",
                    True
                )
                return

        # if we expect a single choice, but multiple were given
        elif len(choice) > 1 and parname not in refpars.maybe_list:
            GM_WS.Warning(
                "Too many choices given for the parameter " + parname +
                " specified in the file " + str(self.fname) +
                ". Please only specify one.",
                True
            )

        # now, correct amount of arguments.
        errortext1 = (
            "Invalid choice given for the parameter " + parname +
            " specified in the file " + str(self.fname) +
            ". Please refer to the manual for the allowed options."
        )
        errortext2 = (
            "Choice given for the parameter " + parname +
            " specified in the file " + str(self.fname) +
            " is of the wrong type. Please refer to the manual for the "
            "expected type."
        )

        if parname in refpars.intpars:
            try:
                choice = [int(x) for x in choice]
            except Exception:
                GM_WS.Warning(errortext2, True)

        if parname not in refpars.options:
            return choice

        if any(
            opt not in refpars.options[parname] for opt in choice
        ):
            GM_WS.Warning(errortext1, True)
        else:
            return choice

    def check_completeness(self, refpars):
        for parname in refpars.choices.keys():
            if parname not in self.choices:
                GM_WS.Warning(
                    "No entry found for the parameter " + parname +
                    " in the default parameter file " + str(self.fname) +
                    ". All parameters must be specified for default files to "
                    "be used.",
                    True
                )


class RunPars:
    def __init__(self, FILES, ref_pars, def_pars, in_pars):
        pass

        # first, find logfile location (so we can swith to that for output
        # quickly instead of sticking with temporary file...)

        # then, find verbose setting, and print all that should've been printed
        # to log earlier. But of course, with the verbose filter.

        # after, extract the mapdir parameter, so we know where to look for
        # those

        # then (finally!), search through mapdir to find any maps to apply.


def parse_commandline(FILES, callcommand, alljobs, helpcall):
    """
    Given the input from the command line, finds out the meaning of each part.
    Returns the job, the path of the input parameter filename, and the
    parameters specified on the command line.
    Parameters specified on the command line must have the parameter name
    preceded with '@'.
    """
    job = callcommand[1]

    if job not in alljobs:
        GM_WS.Warning(
            "\nChoice '" + str(job) +
            "' was not recognized. Please type the following to see all "
            "available options:\n\n" + helpcall + "\n", True
        )

    args = callcommand[2:]

    # interpret the command line. parameters specified on the command line
    in_parfile = None
    cmd_pars = ""
    if len(args) != 0:
        if args[0][0] == "@":
            cmd_pars = " ".join(args[0:])
        else:
            in_parfile = (FILES.cwd / args[0]).resolve()
            if len(args) > 1 and args[1][0] == "@":
                cmd_pars = " ".join(args[1:])

    if cmd_pars:
        # now, cmd_pars is iter (list) of strings, just like for line in file
        cmd_pars = cmd_pars.split("@")[1:]

    if in_parfile and (not in_parfile.exists() or not in_parfile.is_file()):
        GM_WS.Warning(
            "\nThe requested input parameter file "
            + str(in_parfile) +
            " could not be found, or is not a file. "
            "Please make sure you specified it correctly.\n",
            True
        )

    return job, in_parfile, cmd_pars


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


def cleanline(line):
    """
    Removes any '#' and text following it (i.e., get rid of comments)
    """
    return line.split("#")[0]
