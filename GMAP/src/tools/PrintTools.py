
# standard library imports
import datetime
import inspect
import pathlib
# import sys
import time
from traceback import TracebackException as TbEx

# local imports
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.ColorSchemes as GM_CS
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.MathFunctions as GM_MF
# import GMAP.src.tools.Plotter as GM_Pl


class Printer(metaclass=GM_CT.Singleton):
    """Manages prints and logs during runtime.

    During runtime, the program can communicate many things, but the user
    might not be interested in all of them. That's why verbose printing
    is desired. Besides that, having the prints saved in a log file is
    greatly desired, especially on clusters. This class allows many kinds
    of print functionality.

    .. seealso::
        :func:`devprint`
            Meant for printing during development.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related properties.

    Attributes
    ----------
    logfile : `pathlib.path`
        The path to the logfile
    backlog : list
        Initally, the user-specified log file path is not yet known. Until
        it is, all that should be printed is instead put into the backlog.
        In case the program quits before the log file is known, the backlog
        is printed to the crash file (and terminal).
    program_state : str
        In what phase/mode the program currently exists. This state influences
        the desired printing behaviour.
    verbose : int
        How verbose the prints to the command line should be.
    verbose_logfile : int
        How verbose the prints to the log file should be.
    """

    def __init__(self, Files):
        # The requested log file name/location is not immediately known, but
        # we still want to log information of the run. As long as the logfile
        # isn't found (/known), put info in the backlog instead of immediately
        # into the file. In case of a crash, write the entire backlog to the
        # crash logfile.

        # this can be done through self.program_state
        # self.logfilefound = False
        self.logfile = Files.cwd / f"crash_{Files.now_str}.log"
        self.backlog = []

        # 'startup' for initial part of code
        # 'demo' for when running in demo mode
        # 'running' for when running normally
        self.program_state = "startup"
        self.color_mode = "24bit"  # safe mode will overwrite this!
        self.colors = GM_CS.StandInColors  # should be used by callers
        self._colors = GM_CS.DarkModeColors  # default colors for early prints
        self.line_length = 79

        # error codes which shouldn't be printed by warning.
        self.dont_report_error = []

        self.Timer = Timer(start=Files.start)

        Files.set_exec_os()

        # to have some kind of default - will be changed as soon as parameter
        # choices are known.
        self.verbose = 3
        self.verbose_logfile = 4
        self.preline = []

    def print(
        self, verbose_level, *toprint, instruction="pf", line_length=None,
        detailed_instructions=None, sep=" ", **kwargs
    ):
        """Called when something needs to be printed.

        Parameters
        ----------
        verbose_level : int
            The verbosity of the message to print. This will be compared with
            the requested verbose levels for printing - if `verbose_level` is
            smaller than or equal to the value set by the verbose parameters,
            the message will be printed/logged.
        *toprint : str
            The message to print. Can be multiple arguments, like with
            python print
        instruction : str, default="pf"
            Where to print to. If the string contains a 'p', the message
            will be printed to the terminal, if the string contains an
            "f", the message will be written to the logfile.
        line_length : int or None, default=None
            At what length the program should wrap lines. Lines printed
            to the terminal or logfile will not exceed this length. If
            provided, RunPars.command_line_length will be ignored. If
            the default None is provided, RunPars.command_line_length
            will be used.
        detailed instructions : list of int or None, default=None
            Any extra instructions. If None, an empty list will be
            assumed. Currently supported::

                If any of the digits 0-4 are present in the list (each a
                separate item), only at EXACTLY that verbose level the
                message will be printed.
        """

        # This means that RunPars hasn't been completed yet, and many print
        # settings are still unknown. So if we don't have to print, don't!
        if self.program_state == "startup":
            self.backlog.append([
                verbose_level, toprint, kwargs | {
                    "instruction": instruction,
                    "line_length": line_length,
                    "detailed_instructions": detailed_instructions,
                    "sep": sep}
            ])
            return

        if line_length is None:
            line_length = self.line_length
        if detailed_instructions is None:
            detailed_instructions = []
        toprint = [str(item) for item in toprint]
        toprint = sep.join(toprint)
        all_verbose = {0, 1, 2, 3, 4}

        # print to command line
        if (
            "p" in instruction
            and verbose_level <= self.verbose
            and (  # no specific verbose instr, or our specific one is in there
                (self.verbose in detailed_instructions)
                is not all_verbose.isdisjoint(detailed_instructions))
        ):
            printpreline = "".join(
                [item[1] for item in self.preline if self.verbose in item[0]])
            printpreline = change_color(printpreline, self.color_mode)
            prelinelen = len(change_color(printpreline, "white"))
            out = prettifier(
                change_color(toprint, self.color_mode), line_length-prelinelen)
            print(
                printpreline + out.replace("\n", f"\n{printpreline}"),
                **kwargs)

        # print to file
        if (
            "f" in instruction
            and verbose_level <= self.verbose_logfile
            and (  # no specific verbose instr, or our specific one is in there
                (self.verbose_logfile in detailed_instructions)
                is not all_verbose.isdisjoint(detailed_instructions))
        ):
            with open(self.logfile, "a", encoding="utf-8") as fhand:
                # change color to white here so color codes/markers are not
                # present in the log files
                printpreline = "".join([
                    item[1] for item in self.preline
                    if self.verbose_logfile in item[0]])
                printpreline = change_color(printpreline, "white")
                prelinelen = len(printpreline)
                out = prettifier(
                    change_color(toprint, "white"), line_length-prelinelen)
                print(
                    printpreline + out.replace("\n", f"\n{printpreline}"),
                    file=fhand, **kwargs)

    def quit_early(self):
        """Called when the program is quitted early

        Prints the backlog if there is any.
        """

        if self.backlog:
            self.print_backlog()

    def print_backlog(self):
        """Prints the backlog so the program can stop.

        When called in startup mode, verbose and verbose_log are set to 3,
        the crash logfile is used, and the entire backlog is worked through.
        """

        if self.program_state == "startup":
            self.program_state = "running"

        # create the file (clear it if it exists). File equivalent of
        # creating an empty list.
        with open(self.logfile, "w") as _:
            pass

        for print_instructions in self.backlog:
            args = (print_instructions[0],) + print_instructions[1]
            self.print(*args, **print_instructions[2])
        self.backlog = []

    def warning(
        self, message, error_code, exitbool=False, exception=None,
        GMAPerrclass=None
    ):
        """Warning system. Prints the message, and allows to force-quit after.

        Parameters
        ----------
        message : str
            The warning/error message to print.
        error_code : str
            The error code belonging to the warning that is raised - to be
            reported to the user. See the
            :ref:`warning overview<UserGuide_page_warning_overview>` page.
        exitbool : bool, default=False
            Whether the program should stop due to this error.
        exception : BaseException, default=None
            If the warning corresponds to a 'basic' python error,
            that error can be caught and fed into this function.
        """

        # if this default is set directly in the function signature, a circular
        # reference problem occurs, and this module MUST be imported before
        # the exceptions module is imported. This way, the import order does
        # not matter.
        if GMAPerrclass is None:
            GMAPerrclass = GM_Ex.GMAPexception

        if not message.startswith("\n"):
            message = "\n" + message

        # might seem backwards, but we should report if the error wasn't
        # silenced.
        if GM_CT.ErrCode(error_code) not in self.dont_report_error:
            if exitbool:
                printinstruct = "f"
            else:
                message = (
                    f"\n{self.colors.red_hc}WARNING:" + self.colors.red_todef
                    + message + self.colors.clear)
                printinstruct = "pf"

            error_message = message
            self.print(0, message, instruction=printinstruct)

            # print the traceback in exactly the same way as it would be
            # thrown into the command line.
            if exception:
                traceprint = TbEx.from_exception(exception).format()
                msg = (
                    "\n" + self.colors.red_todef + "".join(traceprint)
                    + self.colors.clear)
                self.print(4, msg, instruction=printinstruct)
                if self.verbose == 4:
                    error_message += msg

            msg = (
                " More information can be found in the documentation "
                f"user pages using the following error code: {error_code}"
            )
            self.print(
                0, self.colors.red_todef + msg + self.colors.clear,
                instruction=printinstruct)
            error_message += msg

        if exitbool:
            if self.backlog:
                self.print_backlog()
            # We want an empty line before the error
            self.print(0, f"\n{self.colors.red_hc}", instruction="p", end="")
            error_message = change_color(
                self.colors.red_todef + error_message + self.colors.clear,
                self.color_mode)
            raise GMAPerrclass(error_message, error_code, exception)

    def setenv(self, safe_mode, dark_mode):
        self.safe_mode = safe_mode
        self.dark_mode = dark_mode

        if safe_mode:
            # in case some terminal cannot handle others
            self.color_mode = "white"
        if self.dark_mode:
            self._colors = GM_CS.DarkModeColors
        else:
            self._colors = GM_CS.LightModeColors

    def set_state(
        self, new_state, verbose, verbose_logfile, color_mode, line_length,
        new_logfile=None, new_dont_report_error=None
    ):
        """Change the current state of Printer

        Printer will always be initialized in startup mode, without a
        user-specified log file and verbose choices. This function allows
        to re-chose those three values, allowing 'importing' them after
        :class:`~GMAP.src.tools.ParameterParser.RunPars` finds them.

        Parameters
        ----------
        new_state : str
            The new value for the attribute `program_state`.
        verbose : int
            The new value for the attribute `verbose`
        verbose_logfile : int
            The new value for the attribute `verbose_logfile`
        """

        self.program_state = new_state
        self.verbose = verbose
        self.verbose_logfile = verbose_logfile
        if not self.safe_mode:
            self.color_mode = color_mode
        self.line_length = line_length
        if new_dont_report_error is not None:
            self.dont_report_error = new_dont_report_error
        if new_logfile:
            self.logfile = new_logfile
            self.print_backlog()
        # color_test()
        # GM_Pl.plot_color_conv()

    def add_time(self, verbose_level, msg, label, precision='s'):
        """Adds a timestamp to the program output to track speed.

        Parameters
        ----------
        verbose_level : int
            At what verbose setting (or higher) used by the user this
            message should be reported.
        msg : str
            The text that should be reported along with the timestamp.
        precision : str, default="s"
            To what precision the time should be reported.
        """

        self.Timer.add_time(label)
        now = datetime.datetime.now().strftime("%a %d %H:%M")
        runtime = time_to_str(self.Timer.get_time(label), precision)
        self.print(
            verbose_level,
            f"{self.colors.blue_hc}[{now}] {self.colors.clear}{runtime}:  "
            f"{msg}"
        )


class Timer:
    """Manages the timekeeping during runtime.

    Times can be either added, or read from here.

    Parameters
    ----------
    start : int, default=None
        If provided, this is used as the reference time, instead of the
        time at which the class was created. This new starting time
        should be created using time.perf_counter_ns()

    Attributes
    ----------
    zero : int
        The reference point to which all times should be compared.
    times : dict of str: int pairs.
        The different times that the timer was requested to save. The
        keys are the messages the times were accompanied by, the values
        are the actual (raw perf_counter_ns()) times.

    Notes
    -----
    All labels in use (refers to what'll be done next)::

        (start)
        ParParse      (3)
        AddMaps       (3)
        MDinit        (2)
        MapInit       (3)
        ClibLoad      (3)
        PrepLoop      (3)
        StartLoop     (3)
          FrameUpdate (4)
            PosBox    (4)
            COM       (4)
          OscUpdate   (4)
          StructInit  (4)
          MapFInit    (4)
          Calc        (4)
            VEGprop   (4)
            VEGcalc   (5)
            VEGuse    (5)
            PrepCoup  (4)
            CalcCoup  (4)
          MapFPost    (4)
          FrameWrite  (4)
          LoadFrame   (4)
        MapPost       (3)
    """

    def __init__(self, start=None):
        if start is None:
            self.zero = time.perf_counter_ns()
        else:
            self.zero = start

        self.times = {}
        self.totals = {}
        self.previous = ["start", self.zero]

    def add_time(self, msg):
        """Add another time to the dict.

        Parameters
        ----------
        msg : str
            The key with which the time is stored.
        """

        now = time.perf_counter_ns()

        if self.previous[0] not in self.totals:
            self.totals[self.previous[0]] = now - self.previous[1]
        else:
            self.totals[self.previous[0]] += now - self.previous[1]
        self.times[msg] = now
        self.previous = [msg, now]

    def get_time(self, msg):
        """Retrieve a time from the dict.

        Times retrieved have self.zero subtracted first, so they become
        useful/meaningful.

        Parameters
        ----------
        msg : str
            The key from which the time should be retrieved.
        """

        return self.times[msg] - self.zero

    def get_total_ns(self, *args):
        """Get sum of total calculation times.

        Each label listed in args is retrieved from totals, which is
        subsequently summed.

        Parameters
        ----------
        *args : str
            Each argument is a string and represents a label of which
            the time should be retrieved.
        """

        total_time = 0
        for label in args:
            total_time += self.totals[label]
        return total_time

    def get_total_format(self, *args):
        """Get a nicely formatted representation of total calculation times.

        Each label listed in args is retrieved from totals, and they
        are summed before conversion to a human-readable format.

        Parameters
        ----------
        *args : str
            Each argument is a string and represents a label of which
            the time should be retrieved.
        """

        total_time = self.get_total_ns(*args)
        return time_to_str(total_time)


def color_test():  # run this one with prettifier to 150 (8 colors per row)
    def doprint(string):
        convstring = change_color(string, "4bit")
        Printer().print(0, string + convstring, line_length=130)

    step = 16
    range_ = [*range(0, 255, step)] + [255]
    for r in range_:
        Printer().print(
            0, f"\nRed value: {r}", instruction="p", line_length=130)
        Printer().print(
            0, " Blue -> " + "".join(
                [f"{ix:<7}" for ix in range_])
            + "\nGreen", instruction="p", line_length=130)
        for g in range_:
            string = f"{g:>4}   "
            # manual: either do (0, 127, 16), or (128, 255, 16)
            for b in range_:
                shortstr = f"\033[38;2;{r};{g};{b}m███\033[0m"
                string += shortstr
                string += change_color(shortstr, "4bit")
                string += " "
            Printer().print(0, string, instruction="p", line_length=130)
        if r == 128:
            break


def prettifier(string, deslen=79):
    """Formats a given string to create soft-wrap-like behaviour.

    Parameters
    ----------
    string : str
        The string to format.
    deslen : int, default=79
        The maximum amount of characters per line.

    Returns
    -------
    new_string : str
        The original input `string`, but with newline characters added where
        necessary.
    """
    startlst = string.split("\n")
    endlst = []

    # We always take the length of the 'white' string, not the original;
    # color swaps don't take up space in the command line, but here they do
    # represent a length of up to 16!

    for item in startlst:
        ilen = len(change_color(item, "white"))
        if ilen > deslen:
            itemlst = item.split(" ")
            buildstr = ""
            for subitem in itemlst:
                slen = len(change_color(subitem, "white"))
                blen = len(change_color(buildstr, "white"))
                if blen + slen >= deslen:
                    endlst.append(buildstr)
                    buildstr = subitem
                else:
                    if blen == 0:
                        if len(buildstr) == 0:  # stripping whitespaces
                            buildstr = subitem
                        else:  # There's nothing but color marker -> preserve
                            buildstr += subitem
                    else:
                        buildstr += " " + subitem
            endlst.append(buildstr)
        else:
            endlst.append(item)

    return "\n".join(endlst)


def change_color(string, target_mode):
    """GMAP defaults to 24-bit color. Change this to 4-bit or white.
    """

    # The code should be able to choose colors last-minute, so there are
    # internal codes, too! Here, we switch from internal to ANSI
    # Even if there are no custom markers, don't quit, there might be ANSI
    # markers still!
    string_split = string.split("\033<")
    if len(string_split) != 1:  # custom color marker!
        string_list = [item.split(">", 1) for item in string_split]
        newlist = [">".join(string_list[0])]
        for item in string_list[1:]:
            newlist.append(getattr(Printer()._colors, item[0]) + item[1])
        string = "".join(newlist)

    # If we want 24bit, we can stay with the current ANSI codes.
    if target_mode == "24bit":
        return string

    # make sure the beginning text has a color, too (just for code
    # simplification, not actually in output)
    string_split = string.split("\033[")
    if len(string_split) == 1:  # no color marker!
        return string

    # prepare the string - split it up into a list in which each item
    # represents a monocolor segment. The item is a list of length 2, first
    # the ansi color string, then the actual string.
    newstr = "0m" + string
    string_split = newstr.split("\033[")
    # cut only at first m as thats the end of the color marker
    string_list = [item.split("m", 1) for item in string_split]

    # now, change the color of each monocolor substring
    if target_mode == "4bit":  # 8 colors + their bright varieties
        for item in string_list:
            item[0] = ANSI24_to_ANSI4(item[0])
        outputlist = [string_list[0][1]]  # don't keep color of first item
        outputlist += [f"\033[{item[0]}m{item[1]}" for item in string_list[1:]]
        return "".join(outputlist)
    else:
        # just delete any color markers
        output = "".join([item[1] for item in string_list])
        return output


def ANSI24_to_ANSI4(colorstr):
    """input colorstr in ANSI format (e.g. 38;2;45;61;32)"""

    warning_msg = "\nInvalid color specification."

    color_split = colorstr.split(";")  # get all useful values
    color_new = []
    while len(color_split) > 0:
        match color_split[0]:
            case "0":  # reset command - no extra's expected
                color_new.append("0")
                color_split = color_split[1:]

            case "38":  # foreground - 5 items including this one
                curr_color = color_split[:5]
                if len(curr_color) != 5:  # premature end of list
                    Printer().warning(warning_msg, "PT_CC_1", True)

                new_col, bright = GM_MF.convert_color_24_4(*curr_color[2:])
                if bright:
                    color_new.append("1")
                color_new.append(str(30 + new_col))
                color_split = color_split[5:]

            case "48":  # background - 5 items including this one
                curr_color = color_split[:5]
                if len(curr_color) != 5:  # premature end of list
                    Printer().warning(warning_msg, "PT_CC_1", True)

                # no bright - a bright background is not possible
                new_col = GM_MF.convert_color_24_4(*curr_color[2:])[0]
                color_new.append(str(40 + new_col))
                color_split = color_split[5:]

            case _:
                Printer().warning(warning_msg, "PT_CC_1", True)

    return ";".join(color_new)


def devprint(*args, **kwargs):
    """python print for developers

    Developers should use this function to print instead of the python print
    function - it also prints where it was evoked, so any random prints can
    be easily retraced and removed after they're no longer useful.

    .. note::
        Calling this function goes **exactly** like the print from python

    Parameters
    ----------
    *args : tuple
        All the things to print
    **kwargs : tuple
        The keyword arguments to pass to python print.
    """

    cf = inspect.currentframe().f_back
    lineno = cf.f_lineno
    cf_i = inspect.getframeinfo(cf)
    filename = pathlib.Path(cf_i.filename).name
    funcname = cf_i.function
    print(
        f"(line {lineno:4d})",
        *args,
        f"(from {funcname} in {filename})",
        **kwargs
    )


def header(
    verbose, title, preset, preline=None, newlines=None, **kwargs
):
    """Create a header from the given text.

    Parameters
    ----------
    verbose : int
        The verbose level on which the header should be printed. Is
        directly passed to the :func:`Printer.print` call.
    tile : str
        The text that should be within the header
    preset : str
        What style header should be used. Current options:

        custom :
            The caller fully decides. Any additional kwargs to this
            function are passed to :func:`_make_header`. See the
            documentation of that function for available kwargs.
            newlines default = (0, 0)
        nohead :
            No special header is made - title is taken as-is.
        doublebox :
            The header receives a border of the ascii double-line box
            character set, with a double-line dropping down to mark all
            output belonging to the section::
                ╔═════════════╗
                ║ input_title ║
                ╚╦════════════╝
                 ║ text with the new set preline

            The matching footer should be used too.
            Newlines default = (2, 1)

        doublebox_bare :
            The header receives a border of the ascii double-line box
            character set. There is no line dropped::
                ╔═════════════╗
                ║ input_title ║
                ╚═════════════╝
                text will be printed with no set preline

            No footer is required.
            Newlines default = (2, 1)
    preline : str, default=None
        Only used if preset set to "custom" or "nohead". If the text
        following the header should have a preline, this will be
        arranged.
    newlines : tuple of two ints, default=None
        The amount of empty lines that should be printed before and
        after the header, respectively. If set to None, the
        preset-specific default will be used.
    **kwargs : any
        Any kwargs that should be passed to either
        :func:`Printer.print` or :func:`_make_header`.
    """

    if "color_border" not in kwargs or kwargs["color_border"] is None:
        cb = Printer().colors.green_lc

    if "color_text" not in kwargs or kwargs["color_text"] is None:
        _ = Printer().colors.clear

    cc = Printer().colors.clear

    if newlines is None:
        match preset:
            case "nohead" | "custom":
                newlines = (0, 0)
            case "doublebox" | "doublebox_bare":
                newlines = (2, 1)

    head = "\n" * newlines[0]
    match preset:
        case "nohead" | "custom":
            if preset == "custom":
                title = _make_header(title, **kwargs)
            head += title
            Printer().print(verbose, head, **kwargs)
            if preline is not None:
                Printer().preline.append(preline)
        case "doublebox" | "doublebox_bare":
            if preset == "doublebox":
                special = {"u": {"replace": {"╦": [[1]]}}}
            else:
                special = None
            head += _make_header(
                title, linemode="oulrc", padding=1, overline_char="═",
                underline_char="═", left_char="║", right_char="║",
                corner_char="╔╗╚╝", special=special
            )
            Printer().print(verbose, head, **kwargs)
            if preset != "doublebox_bare":
                Printer().preline.append([
                    [*range(verbose, 5)], cb + " ║ " + cc])
    if newlines[1] > 0:
        Printer().print(verbose, "\n" * (newlines[1] - 1), **kwargs)


def footer(
    verbose, title, preset, preline=None, newlines=None, **kwargs
):
    """Create a footer from the given text
    """

    if "color_border" not in kwargs or kwargs["color_border"] is None:
        cb = Printer().colors.green_lc

    if "color_text" not in kwargs or kwargs["color_text"] is None:
        ct = Printer().colors.clear

    cc = Printer().colors.clear

    if newlines is None:
        match preset:
            case "nohead" | "custom" | "doublebox_bare":
                newlines = (0, 0)
            case "doublebox":
                newlines = (1, 1)

    foot = "\n" * (newlines[0]-1)
    match preset:
        case "nohead" | "custom":
            if preset == "custom":
                title = _make_header(title, **kwargs)
            Printer().print(verbose, foot, **kwargs)
            if preline is not None:
                if Printer().preline[-1][1] == preline:
                    _ = Printer().preline.pop()
        case "doublebox_bare":
            Printer().print(verbose, foot, **kwargs)
            title = ""
        case "doublebox":
            title = f" {cb}╚═══{ct} End of {title} {cb}═════{cc}"
            Printer().print(verbose, foot, **kwargs)
            if preset != "doublebox_bare":
                if Printer().preline[-1][1] == cb + " ║ " + cc:
                    _ = Printer().preline.pop()
    if newlines[1] > 0:
        Printer().print(verbose, title + "\n" * (newlines[1]), **kwargs)


def _make_header(
    title, padding_char=" ", linemode="ou", padding=0,
    overline_char="-", underline_char="-", left_char="|", right_char="|",
    corner_char="+", alignment="centered", maxwidth=79,
    color_border=None, color_text=None, special=None
):
    """Returns a pretty header for distinguishing prints

    The header will be under and/or overlined with the character
    buffer_char. These lines will have the same length as the title,
    plus extra padding if requested.

    Parameters
    ----------
    title : str
        The text that should be within the header.
    padding_char : str
        The character that should be used for padding around the title
    linemode : str, default="ou"
        which lines should(n't) be displayed. Add the letters for the
        elements you do want to display::

            o: A line above the text
            u: A line below the text
            l: A line left of the text
            r: A line right of the text
            c: Corners

    padding : int, default=0
        How much extra space there should be. Over and underlines will
        get longer by twice this amount, the title itself gets this
        amount of whitespaces before and after the text.
    overline_char, underline_car, left_char, right_char : str, \
    default="-"
        The character that should be used for the respective segment
    corner_char : str, default="+"
        The character that should be used for the corners. If a single
        character is provided, all corners get that character. If
        different characters are desired, there must be 4 characters
        in the string: one for the upleft, upright, downleft, downright
        corner respectively.
    alignment : str, default="centered"
        If the title text consists of multiple lines of unequal length,
        decide how these should be aligned. Regardless of choice, the
        character specified using padding_char will be used to increase
        the lengths of shorter lines. The amount of characters specified
        using padding will be added to the lines after they are made of
        equal length.
        "centered" aligns their midpoints, "leftadj" will align their
        left edges, and "rightadj" will align their right ones.
    maxwidth : int, default=79
        How wide the end result is allowed to be, max. If the title
        text is too wide to fit the requirements, it is line-wrapped to
        fit.
    special : dict, default={}
        Any special rules to apply after the header has been generated.
        Thakes the form of a nested dictionary structure:
        special={"u": {"command": {"|": [[2]]}}}

        - The outermost dict has as the key a string indicating what
          line should be altered. Same shorthands as linemode. The value
          of the dictionary is what should be changed about the line
          (here referred to as the 'rules')
        - The rules dict has the commands as keys, and specific
          instructions (another dict) as the values:

          - replace will put the character saved as key in the
            instructions dict at the positions saved in its values:
            if the line is "abcdefg", {"replace": ["V", [[3]]]} will
            result in "abcVefg". Similarly, {"replace": ["VR",
            [[1, 2], [4, 5]]]} will turn "abcdefg" into "aVRdVRg"

    Returns
    -------
    header : str
        The header, ready for printing.
    """

    if color_border is None:
        color_border = Printer().colors.green_lc

    if color_text is None:
        color_text = Printer().colors.clear

    # -----------  Inside text:  ----------------------

    # line wrapping at the correct places.
    title_width = maxwidth - 2 - (padding * 2)  # leave space for header
    title = prettifier(title, title_width)
    title, longest_length = _header_textwrap(title, alignment, padding_char)
    n_lines = len(title)

    # -----------  Outside border:  ----------------------

    ou_length = longest_length + padding * 2
    corner_char = corner_char * 4  # automatically solves all!
    lines = {}

    # overline
    lines["over"] = _header_overunder(
        overline_char, corner_char[:2], linemode, ou_length, "o")

    # sidelines
    lines["left"] = _header_sideline(left_char, linemode, n_lines, "l")
    lines["right"] = _header_sideline(left_char, linemode, n_lines, "r")

    # underline
    lines["under"] = _header_overunder(
        underline_char, corner_char[2:4], linemode, ou_length, "u")

    # -----------  Special instructions:  ----------------------

    if special is None:
        special = {}
    lines = _header_specials(special, lines)

    # -----------  Building the final product  ----------------------

    # overline
    header = ""
    over = lines["over"]
    if len(over) != 0:  # If we have an upper line, add a line break, too
        over += "\n"
    header += color_border + over

    # sidelines
    pad = padding_char[0] * padding
    for lft, txt, rght in zip(lines["left"], title, lines["right"]):
        header += (
            color_border + lft +
            color_text + pad + txt + pad +
            color_border + rght + "\n")

    # underline
    header += color_border + lines["under"] + Printer().colors.clear

    return header


def _header_overunder(line_char, corner_chars, linemode, length, dir):
    # Get middle portion (if no overline, but corners, we need whitespace)
    if dir in linemode:
        upper = line_char * length
    elif "c" in linemode:
        upper = " " * length
    else:
        upper = ""

    # add corners!
    if "c" in linemode:
        upper = corner_chars[0] + upper + corner_chars[1]

    return upper


def _header_sideline(line_char, linemode, length, dir):
    if dir in linemode:
        left = [line_char[0]] * length
    elif "c" in linemode:
        left = [" "] * length
    else:
        left = [""] * length
    return left


def _header_specials(special, lines):
    shorts = {"o": "over", "u": "under", "l": "left", "r": "right"}

    for lineshort, rules in special.items():
        line = lines[shorts[lineshort]]
        for command, instructions in rules.items():
            if command == "replace":
                if lineshort in "ou":
                    conv = GM_CT.return_first
                elif lineshort in "lr":
                    conv = GM_CT.return_list
                for char, positions in instructions.items():
                    char = conv(char)
                    for pos in positions:
                        line = line[:pos[0]] + char + line[pos[-1]+1:]
        lines[shorts[lineshort]] = line
    return lines


def _header_textwrap(title, alignment, padding_char):
    # padding and adjusting the lines
    title = title.split("\n")
    n_lines = len(title)
    if n_lines == 1:
        longest_length = len(change_color(title[0], "white"))
    else:
        longest_length = max([
            len(change_color(item, "white")) for item in title])
        new_title = []
        for line in title:
            linelength = len(change_color(line, "white"))
            diff = longest_length - linelength
            match alignment:
                case "centered":
                    pre = diff // 2
                    post = diff - pre
                case "leftadj":
                    pre = 0
                    post = diff
                case "rightadj":
                    pre = diff
                    post = 0
            new_title.append(pre * padding_char + line + post * padding_char)
        title = new_title
    return title, longest_length


def intlist_to_rangelist(intlist, n_int, make_shadow=True):
    """Takes a list of integers and packs it into ranges.

    Parameters
    ----------
    intlist : list of int
        The list of integers to be packed.
    n_int : int
        The amount of integers that can at most be there. (The provided value
        itself will never appear!)
    make_shadow : bool, default=True
        Whether the opposite should also be built - a list of all indices
        that weren't in the intlist

    Returns
    -------
    result : list of str
        All indices (grouped in ranges) that were in intlist.
    shadow : list of str or None
        All indices (grouped in ranges) that weren't in intlist.

    Examples
    --------
    Groups of 3 integers or larger will be grouped

    >>> intlist = [*range(10)]
    >>> intlist.remove(5)
    >>> intlist_to_rangelist(intlist, 10)
    (["0-4", "6-9"], ["5"])

    Groups of 2 integers are left as is

    >>> intlist = [0, 1, 5, 8, 9, 10]
    >>> intlist_to_rangelist(intlist, 11)
    (["0", "1", "5", "8-10"], ["2-4", "6", "7"])
    """

    result = []
    prevnum = intlist[0]  # loop will go over [1:]
    range_start = intlist[0]
    # so we don't need for-else to deal with last item
    intlist = intlist + [None]

    if make_shadow:
        if prevnum != 0:
            shadow = rangestrlist(0, prevnum)  # all numbers not in intlist
        else:
            shadow = []
    else:
        shadow = None

    for num in intlist[1:]:
        # if we don't logically count to the next one
        if num != prevnum + 1:

            # put missing numbers in the shadow list
            if make_shadow:
                if num is None:
                    end = n_int
                else:
                    end = num
                if prevnum + 1 != end:
                    shadow += rangestrlist(prevnum + 1, end - 1)

            # the last number was 'alone'
            result += rangestrlist(range_start, prevnum)

            range_start = num

        prevnum = num

    return result, shadow


def rangestrlist(start, stop):
    """Given a start and stop, return separate items or range. Inclusive.

    Meant as a helper function for :func"`intlist_to_rangelist`, not
    intended for separate use.

    Parameters
    ----------
    start : int
        The first int to be included.
    stop : int
        The last int to be included.

    Returns
    -------
    out : list of str
        The grouped ints.

    Examples
    --------
    Groups are shortened:

    >>> rangestrlist(3, 60)
    ["3-60"]

    >>> rangestrlist(3, 5)
    ["3-5"]

    Pairs are left as-is

    >>> rangestrlist(3, 4)
    ["3", "4"]

    Single values are left alone

    >>> rangestrlist(3, 3)
    ["3"]
    """
    if start == stop:
        return [str(start)]
    elif start == stop - 1:
        return [str(start), str(stop)]
    else:
        return [f"{start}-{stop}"]


def time_to_str(ns_time, precision="s"):
    """Converts an amount of ns into a formatted string.

    Parameters
    ----------
    ns_time : int
        An amount of nanoseconds
    precision : str, default=s
        To what precision the string should be printed. 's' for seconds,
        'ms' for milliseconds, 'us' for microseconds or 'ns' for
        nanoseconds.

    Returns
    -------
    str_time : str
        The input time formatted into a string.
    """

    ns = ns_time % 1000
    remainder = ns_time // 1000  # this is now in units of us

    us = remainder % 1000
    remainder //= 1000  # this is now in units of ms

    ms = remainder % 1000
    remainder //= 1000  # this is now in units of s

    s = remainder % 60
    remainder //= 60   # this is now in units of m

    m = remainder % 60
    remainder //= 60  # this is now in units of h

    h = remainder % 24
    d = remainder // 24

    str_time = f"{d}-{h:02d}:{m:02d}:{s:02d}"

    if precision in ("ms", "us", "ns"):
        str_time += f".{ms:03d}"

    if precision in {"us", "ns"}:
        str_time += f"{us:03d}"

    if precision == "ns":
        str_time += f"{ns:03d}"

    return str_time
