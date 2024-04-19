
# 3rd party imports
import numpy as np

# local imports
import GMAP.src.tools.MathFunctions as GM_MF
from GMAP.src.tools.PrintTools import devprint as dpr
dpr("", end="")  # to disable error of dpr unused


class NewModule:
    def __init__(self):
        pass


# ------------------------
# Getters for mapfunctions
# ------------------------


def get_adjust_RunPars():
    return does_nothing


def get_adjust_map_core_raw():
    return does_nothing


def get_adjust_oscillators():
    return returns_last


def get_post_init():
    return does_nothing


def get_pre_run():
    return does_nothing


def get_pre_frame():
    return does_nothing


def get_post_frame():
    return does_nothing


def get_post_run():
    return does_nothing


def get_get_dipole(Printer, map_):
    """Default for obtaining the dipole

    parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    map_ : :class:`~GMAP.src.tools.MapReader.Map`
        The map instance which this function will belong to.

    returns
    -------
    GM_get_dipole : function
        The function that every oscillator will call to get its dipole
    """

    # based on the r_vec and r_pos lines in the map core, build a function.
    codestring = "\ndef GM_get_dipole(Files, Printer, Map, Syst, osc):\n"
    codestring += "    r_vec = " + envelop_int(
        " ".join(map_.rawcore["r_vec"]),
        # "GM_MF.PBCvect(Syst.positions[osc.used_atoms[", "]])"
        "osc.positions_box[", "]"
    ) + "\n"
    codestring += "    r_pos = " + envelop_int(
        " ".join(map_.rawcore["r_pos"]),
        # "GM_MF.PBCvect(Syst.positions[osc.used_atoms[", "]])"
        "osc.positions_box[", "]"
    ) + "\n"
    codestring += "    return r_vec @ Syst.boxvects, r_pos @ Syst.boxvects\n"

    # dpr(envelop_int("1-0", "pos(", ")"))
    # dpr(envelop_int("np.cross(1, 0)", "pos(", ")"))
    # dpr(envelop_int("(1+0)/2.0", "pos(", ")"))
    # dpr(map_.rawcore["r_vec"])
    # dpr(codestring)

    try:
        # exec(codestring, globals(), locals())
        exec(codestring)
    except Exception as ex:
        corefile = (map_.directory / 'core.txt').resolve()
        Printer.warning(
            f"\nThe file {corefile} does not contain a valid definition of "
            "r_vec and/or r_pos.",
            "MI_MC_9", exception=ex
        )
        return None

    # return GM_get_dipole
    return locals()["GM_get_dipole"]


def get_get_rotation_matrix(Printer, map_):
    """Default for creating a rotation matrix

    parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    map_ : :class:`~GMAP.src.tools.MapReader.Map`
        The map instance which this function will belong to.

    returns
    -------
    GM_get_rotation_matrix : function
        The function that every oscillator will call to get its rotaion matrix
    """

    allparnames = ("x_uvec", "y_uvec", "z_uvec")
    # determine xyz order
    given_directions = [key for key in map_.rawcore if key in allparnames]

    codestring = "\ndef GM_get_rotation_matrix"
    codestring += "(Files, Printer, Map, Syst, osc):\n"

    # the first direction should be taken as is
    direc = given_directions[0]
    codestring += f"    {direc} = (" + envelop_int(
        " ".join(map_.rawcore[direc]),
        # "GM_MF.PBCvect(Syst.positions[osc.used_atoms[", "]])"
        "osc.positions_box[", "]"
    ) + ") @ Syst.boxvects\n"
    codestring += f"    {direc} /= GM_MF.vec3_len({direc})\n\n"

    # the second direction depends on the type
    olddir = direc
    if map_.Core.type == "standard":
        direc = given_directions[1]
        codestring += f"    {direc} = GM_MF.project({olddir}, ("
        codestring += envelop_int(
            " ".join(map_.rawcore[direc]),
            # "GM_MF.PBCvect(Syst.positions[osc.used_atoms[", "]])"
            "osc.positions_box[", "]"
        ) + ") @ Syst.boxvects)\n"
    elif map_.Core.type == "linear":
        # get the next item in the list
        direc = allparnames[(allparnames.index(olddir) + 1) % 3]

        # find the direction with smallest value of prev vector
        codestring += f"    smalldir = np.argmin(np.abs({olddir}))\n"
        codestring += f"    {direc} = np.zeros((3))\n"
        codestring += f"    {direc}[smalldir] = 1\n"
        codestring += f"    {direc} = GM_MF.project({olddir}, {direc})\n"

    codestring += f"    {direc} /= GM_MF.vec3_len({direc})\n\n"

    # the third direction is always the cross product
    lastdir = [x for x in allparnames if x not in (olddir, direc)][0]
    codestring += f"    {lastdir} = GM_MF.crossprod({olddir}, {direc})\n"
    codestring += f"    {lastdir} /= GM_MF.vec3_len({lastdir})\n\n"

    # now, combine into array to return
    codestring += "    return np.array([x_uvec, y_uvec, z_uvec])\n"

    # dpr(codestring)

    try:
        # exec(codestring, globals(), locals())
        exec(codestring)
    except Exception as ex:
        corefile = (map_.directory / 'core.txt').resolve()
        Printer.warning(
            f"\nThe file {corefile} does not contain a valid definition of "
            "x_uvec, y_uvec and/or z_uvec.",
            "MI_MC_9", exception=ex
        )
        return None

    # return GM_get_dipole
    return locals()["GM_get_rotation_matrix"]


# ------------------------
# Base functions
# ------------------------


def does_nothing(*args):
    pass


def returns_last(*args):
    return args[-1]


# ------------------------
# Useful tools
# ------------------------


def envelop_int(string, pre, post):
    """Envelops any integer (but not float) found in string with pre and post.

    Currently, python built-in and numpy functions are supported.

    Parameters
    ----------
    string : str
        The string in which all integers should be enveloped.
    pre : str
        The thing that should be prepended to every integer.
    post : str
        The thing that should be appended to every integer.

    Returns
    -------
    newstr : str
        The string with enveloped integers.

    Examples
    --------
    Each integer will be enveloped, operators are kept as-is.

    >>> string = "1-0"
    >>> envelop_int(string, "pos(", ")")
    pos(1)-pos(0)

    More complex operators are also supported:

    >>> string = "np.cross(1,0)"
    >>> envelop_int(string, "pos(", ")")
    np.cross(pos(1),pos(0))

    Floats are not affected:

    >>> string = "(1+0)/2.0"
    >>> envelop_int(string, "pos(", ")")
    (pos(1)+pos(0))/2.0
    """

    nums = "1234567890"
    newstr = ""
    intstr = ""
    float_found = False
    for char in string:
        if char in nums:
            if float_found:
                newstr += char
            else:
                intstr += char
        elif char == ".":
            float_found = True
            if intstr:
                newstr += intstr
                intstr = ""
            newstr += char
        else:
            # this is both float_found=True and False.
            if not intstr:
                float_found = False
            else:
                newstr += pre + intstr + post
                intstr = ""
            newstr += char
    else:
        if intstr:
            newstr += pre + intstr + post
            intstr = ""

    return newstr


# never called, just to remove the unused warnings for imports
def unused_user():
    _ = np.array([1, 2])
    _ = GM_MF.dotprod([1, 2, 3], [1, 2, 3])
