
from pathlib import Path

import GMAP.src.tools.WarnSys as GM_WS


class RefPars:
    def __init__(self, fname):
        self.fname = fname
        self.add_groups()

        self.parse_refparfile(self.parse_line_type_protected)
        self.parse_refparfile(self.parse_line_choice_protected)

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
        try:
            self.parse_line_choice(self, linelist)
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
                options.append(bit)

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
