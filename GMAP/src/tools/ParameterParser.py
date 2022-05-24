
import GMAP.src.tools.WarnSys as GM_WS


def parse_commandline(FILES, callcommand):
    """
    Given the input from the command line, finds out the meaning of each part.
    Returns the job, the path of the input parameter filename, and the
    parameters specified on the command line.
    Parameters specified on the command line must have the parameter name
    preceded with '@'.
    """
    job = callcommand[1]
    
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
            "The requested file "
            + str(in_parfile) +
            " could not be found, or is not a file. "
            "Please make sure you specified it correctly."
        )

    return job, in_parfile, cmd_pars


def get_pardict(iterable):
    outdict = {}
    for line in iterable:
        line = cleanline(line)
        if len(line) == 0:
            continue
        linelist = [term.strip() for term in line.split()]

        outdict[linelist[0]] = linelist[1:]
    return outdict


def cleanline(line):
    return line.split("#")[0].strip()
