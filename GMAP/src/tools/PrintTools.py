import sys
import inspect
import pathlib
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
