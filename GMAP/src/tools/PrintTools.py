import sys
import inspect
import pathlib


class Printer:
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
        if self.program_state == "startup":
            self.backlog.append([verbose_level, toprint])

    def quit_early(self):
        if self.backlog:
            self.print_backlog()

    def print_backlog(self):
        if self.program_state == "startup":
            self.verbose = 3
            self.verbose_logfile = 3
        with open(self.logfile, "w") as loghand:
            for verbose_level, toprint in self.backlog:
                if verbose_level <= self.verbose:
                    print(prettifier(toprint))
                if verbose_level <= self.verbose_logfile:
                    loghand.write(prettifier(toprint))
        self.backlog = []

    def warning(self, message, exitbool=False):
        self.print(0, message)
        if exitbool:
            if self.backlog:
                self.print_backlog()
            sys.exit()

    def set_state(
        self, new_state, verbose, verbose_logfile, new_logfile=None
    ):
        self.program_state = new_state
        self.verbose = verbose
        self.verbose_logfile = verbose_logfile
        if new_logfile:
            self.logfile = new_logfile
            self.print_backlog()


def prettifier(str, deslen=79):
    startlst = str.split("\n")
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
