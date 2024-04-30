
# standard library imports
import inspect
import pathlib
import sys
import time
from traceback import TracebackException as TbEx


class Printer:
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

        self.Timer = Timer(start=Files.start)

        Files.set_exec_os(self)

    def print(self, verbose_level, toprint):
        """Called when something needs to be printed.

        Parameters
        ----------
        verbose_level : int
            The verbosity of the message to print. This will be compared with
            the requested verbose levels for printing - if `verbose_level` is
            smaller than or equal to the value set by the verbose parameters,
            the message will be printed/logged.
        toprint : str
            The message to print
        """

        if self.program_state == "startup":
            self.backlog.append([verbose_level, toprint])
            return

        if verbose_level <= self.verbose:
            print(prettifier(str(toprint)))
        if verbose_level <= self.verbose_logfile:
            print(prettifier(str(toprint)), file=open(self.logfile, "a"))

    def print_backlog(self):
        """Prints the backlog so the program can stop.

        When called in startup mode, verbose and verbose_log are set to 3,
        the crash logfile is used, and the entire backlog is worked through.
        """

        if self.program_state == "startup":
            self.verbose = 3
            self.verbose_logfile = 4
            self.program_state = "running"
        with open(self.logfile, "w") as _:
            pass

        for verbose_level, toprint in self.backlog:
            self.print(verbose_level, toprint)
        self.backlog = []

    def warning(self, message, error_code, exitbool=False, exception=None):
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

        self.print(0, message)

        # print the traceback in exactly the same way as it would be
        # thrown into the command line.
        if exception:
            traceprint = TbEx.from_exception(exception).format()
            self.print(4, "\n" + "".join(traceprint))

        self.print(
            0,
            "More information can be found in the documentation "
            f"user pages using the following error code: {error_code}"
        )
        if exitbool:
            if self.backlog:
                self.print_backlog()
            sys.exit()

    def set_state(
        self, new_state, verbose, verbose_logfile, new_logfile=None
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
        if new_logfile:
            self.logfile = new_logfile
            self.print_backlog()

    def add_time(self, verbose_level, msg, precision='s'):
        self.Timer.add_time(msg)
        self.print(
            verbose_level,
            f"{msg} at: {time_to_str(self.Timer.get_time(msg), precision)}"
        )


class Timer:
    def __init__(self, start=None):
        if start is None:
            self.zero = time.perf_counter_ns()
        else:
            self.zero = start

        self.times = {}

    def add_time(self, msg):
        self.times[msg] = time.perf_counter_ns()

    def get_time(self, msg):
        return self.times[msg] - self.zero


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

    for item in startlst:
        if len(item) > deslen:
            itemlst = item.split(" ")
            buildstr = ""
            for subitem in itemlst:
                if len(buildstr) + len(subitem) >= deslen:
                    endlst.append(buildstr)
                    buildstr = subitem
                else:
                    if len(buildstr) == 0:
                        buildstr = subitem
                    else:
                        buildstr += " " + subitem
            endlst.append(buildstr)
        else:
            endlst.append(item)

    return "\n".join(endlst)


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


def make_header(
    title, buffer_char, overline=True, underline=True, padding=0
):
    """Returns a pretty header for distinguishing prints

    The header will be under and/or overlined with the character
    buffer_char. These lines will have the same length as the title,
    plus extra padding if requested.

    Parameters
    ----------
    title : str
        The text that should be within the header.
    buffer_char : str
        The character that should be used for the over/underline.
    overline, underline : bool, default=True
        Whether there should be an over-, and/or underline.
    padding : int, default=0
        How much extra space there should be. Over and underlines will
        get longer by twice this amount, the title itself gets this
        amount of whitespaces before and after the text.

    Returns
    -------
    header : str
        The header, ready for printing.
    """

    length = len(title)

    header = buffer_char * (length + padding*2)
    header += "\n" + padding*" " + title + padding*" " + "\n"
    header += buffer_char * (length + padding*2)

    return header


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
        str_time += f".{us:03d}"

    if precision == "ns":
        str_time += f".{ns:03d}"

    return str_time
