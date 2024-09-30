
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
# import GMAP.src.tools.Plotter as GM_Pl
import GMAP.src.tools.StringClasses as GM_SC


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
        Initally, the user-specified log file path is not yet known.
        Until it is, all that should be printed is instead put into the
        backlog. In case the program quits before the log file is known,
        the backlog is printed to the crash file (and terminal).
    program_state : str
        In what phase/mode the program currently exists. This state
        influences the desired printing behaviour.
    color_mode : str
        How colors should be printed. 24bit, 4bit, or white.
    colors : :class:`~GMAP.src.tools.ColorSchemes.PrinterColors`
        Colors to be used/sampled by other functions. Contains unique
        color names.
    _colors : :class:`~GMAP.src.tools.ColorSchemes.PrinterColors`
        The actual colors to be used. Contains a dict to translate the
        unique color names of self.colors to ANSI escape codes.
    line_length : int
        The desired line length for both the command line and log files.
    dont_report_error : list of \
    :class:`~GMAP.src.tools.StringClasses.ErrCode`
        Any error codes in this list will not be reported on when
        encountered. Silenced fatal errors will still quit the program.
    Timer : :class:`~Timer`
        The timer that keeps track of calculation times.
    verbose : int
        How verbose the prints to the command line should be.
    verbose_logfile : int
        How verbose the prints to the log file should be.
    preline : list of (list of int, str pairs) or list of (list of int,\
     :class: `~GMAP.src.tools.StringClasses.ColStr` pairs)
        Short bits that should be printed at the beginning of every
        output line. The ints represent the verbose levels at which the
        companion string should be printed. These (short!) strings can
        either be lines/marks for pretty makeup of output, or a marker
        like those used for demo mode.
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
        sep : str
            The character that should be used to separate items in
            *toprint. See the argument 'sep' of the python function
            print for more information.
        **kwargs : any
            These kwargs are forwarded to the call to python's print.
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
            message = self._print_preparation(
                self.verbose, toprint, line_length, self.color_mode)
            print(message, **kwargs)

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
                message = self._print_preparation(
                    self.verbose_logfile, toprint, line_length, "white")
                print(message, file=fhand, **kwargs)

    def _print_preparation(self, verbose, message, line_length, color_mode):
        """Format prints so they can be shown.

        After self.print() has decided that something should indeed be
        printed, this function is called. It does all the formatting
        and makeup of the information that should be printed:

        - First, see if anything should (by default) come before the
          message to print (the preline). This could be a border,
          or demo-mode marker.
        - If so, figure out the length of this preline, and change its
          color to the desired print color ((2)4bit, or white)
        - Word wrap the message that should be printed, with the desired
          wrap distance adjusted for len(preline).
        - change the color of the message
        - make sure any color markers in the message are repeated (less
          and more automatically reset the color at linebreaks...)
        - add the preline to the front of each message line
        - return the finalized message.

        Parameters
        ----------
        verbose : int
            The verbose level at which the message will be printed
        message : str or :class:`GMAP.src.tools.StringClasses.ColStr`
            The message to format for printing
        line_length : int
            How many characters can at most be on a line.
        color_mode : str
            What color palette should be used. Can be '24bit', '4bit' or
            'white' (colorless).

        Returns
        -------
        outmessage : same type as message
            The input message, fully formatted.
        """

        # The color-repeat tool is much, much easier to write/create if the
        # input color format is fixed! So, that's why that step is earlier in
        # the process.

        # Figure out (the length of) printpreline, and change its color to
        # the desired color (so they can be returned directly).
        printpreline = GM_SC.ColStr("").join(
            [item[1] for item in self.preline if verbose in item[0]])
        printpreline = printpreline.change_color(color_mode)
        prelinelen = len(printpreline)

        # wordwrap the message to be printed (adjusted length for preline)
        message = GM_SC.ColStr(message).wrap(line_length - prelinelen)
        # change the message color (so color_repeater knows what to expect)
        # make sure color markers/codes are repeated after a line break
        message = message.change_color(color_mode).repeat_color()

        # add prelines
        message = printpreline + message.replace("\n", f"\n{printpreline}")

        return message

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
        GMAPerrclass : BaseException, default=None
            The exact exception that should be raised if the error is
            fatal. One should pick one from GMAP.src.tools.Exceptions.
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
        if GM_SC.ErrCode(error_code) not in self.dont_report_error:
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
                "user pages using the following error "
                f"code: {self.colors.clear} {error_code}"
            )
            self.print(
                0, self.colors.red_todef + msg,
                instruction=printinstruct)
            error_message += msg

        if exitbool:
            if self.backlog:
                self.print_backlog()
            # We want an empty line before the error
            self.print(0, f"\n{self.colors.red_hc}", instruction="p", end="")
            error_message = (
                self.colors.red_todef + error_message
            ).change_color(self.color_mode)
            raise GMAPerrclass(error_message, error_code, exception)

    def setenv(self, safe_mode, dark_mode):
        """Similar to set_state, set safe_mode and dark_mode

        The provided choices for safe mode and dark mode are stored in
        the Printer object for later use. These two have to be treated
        separate from those in self.set_state, as they have to be set
        at the very beginning of the program, so errors can be printed
        accordingly.

        Parameters
        ----------
        safe_mode : bool
            Whether the program should be run in safe mode.
        dark_mode : bool
            Whether the program should be run in dark mode, or light
            mode. Influences the color palette used.
        """

        self.safe_mode = safe_mode
        self.dark_mode = dark_mode

        if safe_mode:
            # in case some terminal cannot handle other colors
            self.color_mode = "white"
        if self.dark_mode:
            self._colors = GM_CS.DarkModeColors
        else:
            self._colors = GM_CS.LightModeColors

    def set_state(
        self, new_state, verbose=None, verbose_logfile=None, color_mode=None,
        line_length=None, new_logfile=None, new_dont_report_error=None
    ):
        """Change the current state of Printer

        Printer will always be initialized in startup mode, without a
        user-specified log file and verbose choices. This function allows
        to re-chose those three values, allowing 'importing' them after
        :class:`~GMAP.src.tools.ParameterParser.RunPars` finds them.

        If a parameter is not given, or explicitly given as None, then
        the existing value is kept.

        Parameters
        ----------
        new_state : str
            The new value for the attribute `program_state`.
        verbose : int, default=None
            The new value for the attribute `verbose`
        verbose_logfile : int, default=None
            The new value for the attribute `verbose_logfile`
        color_mode : str, default=None
            The desired color palette. 24bit, 4bit, or no colors (white)
        line_length : int, default=None
            How many characters lines may contain at most.
        new_logfile : str, default=None
            The name of a different logfile to start to use.
        new_dont_report_error : list of ErrCodes, default=None
            These error codes shouldn't be reported on in the future.
        """

        self.program_state = new_state
        if verbose is not None:
            self.verbose = verbose
        if verbose_logfile is not None:
            self.verbose_logfile = verbose_logfile
        if (color_mode is not None) and (not self.safe_mode):
            self.color_mode = color_mode
        if line_length is not None:
            self.line_length = line_length
        if new_dont_report_error is not None:
            self.dont_report_error = new_dont_report_error
        if new_logfile is not None:
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
        label : str
            The label used for storing the timestamp in the Timer class.
            It is also used for retrieving information later.
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
    times : dict of str: int pairs
        The different times that the timer was requested to save. The
        keys are the messages the times were accompanied by, the values
        are the actual (raw perf_counter_ns()) times.
    totals : dict of str: int pairs
        The cumulative times the timer was requested to save. Allow to
        see (over many frames) how long the program spent where.
    previous : list of str, int
        What the previous time stamp was. If we call the current, only
        then do we know how long we spent in the previous step (and we
        can save it to totals).

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


def color_test():  # run this one with word_wrap to 150 (8 colors per row)
    """Prints the color array to display a number of 24bit colors along
    with their 4bit counteparts.

    .. important::
        This function is no longer used, and just here for testing/
        development purposes. There is now a more fancy version:
        :func: `GMAP.src.tools.Plotter.plot_color_conv`.

        Only when pandas is an issue, or when the commandline
        specifically is desired to generate the output, this function
        should still be used.

    Due to the windows command line only going back so many lines, I
    used this function in a very manual way. There are two modii, one
    from 0 to 128, and one from 128 to 255. To run the first, make sure
    that 'range_' is defined starting at 0, and the loop ends with
    'if r == 128: break'. For the latter, expand that value (or comment
    those last lines), and adjust the 'range_' definition to start at
    128.
    """

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
                shortstr = GM_SC.ColStr(f"\033[38;2;{r};{g};{b}m███\033[0m")
                string += shortstr
                string += shortstr.change_color("4bit")
                string += " "
            Printer().print(0, string, instruction="p", line_length=130)
        if r == 128:
            break


def word_wrap(string, deslen=79):
    """Formats a given string to create soft-wrap-like behaviour.

    Parameters
    ----------
    string : str or :class:`~GMAP.src.tools.StringClasses.ColStr`
        The string to format.
    deslen : int, default=79
        The maximum amount of characters per line.

    Returns
    -------
    new_string : str or :class:`~GMAP.src.tools.StringClasses.ColStr`
        The original input `string`, but with newline characters added
        where necessary. Retains input type.
    """

    intype = type(string)
    colstr = GM_SC.ColStr(string)
    startlst = colstr.split("\n")
    endlst = []

    # We always take the length of the 'white' string, not the original;
    # color swaps don't take up space in the command line, but here they do
    # represent a length of up to 16!

    for item in startlst:  # each item is of type ColStr
        ilen = len(item)  # ColStrs take their colors into account for length
        if ilen > deslen:
            itemlst = item.split(" ")
            buildstr = ""
            for subitem in itemlst:
                slen = len(subitem)
                blen = len(buildstr)
                if blen + slen >= deslen:
                    endlst.append(buildstr)
                    buildstr = subitem
                else:
                    if blen == 0:
                        buildstr += subitem
                    else:
                        buildstr += " " + subitem
            endlst.append(buildstr)
        else:
            endlst.append(item)

    return intype("\n").join(endlst)


def devprint(*args, **kwargs):
    """python print for developers

    Developers should use this function to print instead of the python
    print function - it also prints where it was evoked, so any random
    prints can be easily retraced and removed after they're no longer
    useful.

    .. note::
        Calling this function goes **exactly** like the print from
        python

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

    A call to footer with the exact same parameters will generate the
    corresponding closing structure. The header is directly printed,
    not returned.

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
                title = GM_SC.Header(title, **kwargs).s
            head += title
            Printer().print(verbose, head, **kwargs)
            if preline is not None:
                Printer().preline.append([[*range(verbose, 5)], preline])
        case "doublebox" | "doublebox_bare":
            if preset == "doublebox":
                special = {"u": {"replace": {"╦": [[1]]}}}
            else:
                special = None
            head += GM_SC.Header(
                title, linemode="oulrc", padding=1, overline_char="═",
                underline_char="═", left_char="║", right_char="║",
                corner_char="╔╗╚╝", special=special
            ).s
            Printer().print(verbose, head, **kwargs)
            if preset != "doublebox_bare":
                Printer().preline.append([
                    [*range(verbose, 5)], cb + " ║ " + cc])
    if newlines[1] > 0:
        Printer().print(verbose, "\n" * (newlines[1] - 1), **kwargs)


def footer(
    verbose, title, preset, preline=None, newlines=None, **kwargs
):
    """Create a footer from the given text.

    A call to header with the exact same parameters will generate the
    corresponding opening structure. The footer is directly printed,
    not returned.

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
            The footer closes the dropped double line::
                 ╚═══ End of Section═══

            The matching header should be used too.
            Newlines default = (1, 1)

        doublebox_bare :
            No footer is required for this one, will just print the
            requested newlines.
            Newlines default = (0, 0)
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
        ct = Printer().colors.clear

    cc = Printer().colors.clear

    if newlines is None:
        match preset:
            case "nohead" | "custom" | "doublebox_bare":
                newlines = (0, 0)
            case "doublebox":
                newlines = (1, 1)

    if newlines[0] > 0:
        foot = "\n" * (newlines[0] - 1)
        Printer().print(verbose, foot, **kwargs)
    match preset:
        case "nohead" | "custom":
            if preset == "custom":
                title = GM_SC.Header(title, **kwargs).s
            else:
                title = ""
            if preline is not None:
                if Printer().preline[-1][1] == preline:
                    _ = Printer().preline.pop()
        case "doublebox_bare":
            title = ""
        case "doublebox":
            title = f" {cb}╚═══{ct} End of {title} {cb}═════{cc}"
            if preset != "doublebox_bare":
                if Printer().preline[-1][1] == cb + " ║ " + cc:
                    _ = Printer().preline.pop()
    if newlines[1] > 0:
        title += "\n" * (newlines[1])
    if title != "":
        Printer().print(verbose, title, **kwargs)


def intlist_to_rangelist(intlist, n_int, make_shadow=True):
    """Takes a list of integers and packs it into ranges.

    Parameters
    ----------
    intlist : list of int
        The list of integers to be packed.
    n_int : int
        The amount of integers that can at most be there. (The provided
        value itself will never appear!)
    make_shadow : bool, default=True
        Whether the opposite should also be built - a list of all
        indices that weren't in the intlist

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
    """Given a start and stop, return separate items or range.
    Inclusive.

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
