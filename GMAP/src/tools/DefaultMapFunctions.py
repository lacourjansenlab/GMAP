
# 3rd party imports
import numpy as np

# local imports
import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.PhysicsFunctions as GM_PF


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


def get_get_VEG_ref(Printer, map_):
    """Creates the function GM_get_VEG_ref.

    Recognizes requested method and finds relevant function.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    map_ : :class:`~GMAP.src.tools.MapReader.Map`
        The map instance which this function will belong to.

    Returns
    -------
    GM_get_VEG_ref : function
        The function that should be called to find the VEG centre for
        this oscillator.
    """

    instructions = map_.rawcore["VEG_reference"]
    method = instructions[0]
    details = instructions[1:]
    match method.lower():
        case "residues":
            GM_get_VEG_ref = VEG_from_residues(details)
        case "com":
            GM_get_VEG_ref = VEG_from_com(details)
        case "position":
            GM_get_VEG_ref = VEG_from_position(Printer, map_, details)
    return GM_get_VEG_ref


def VEG_from_residues(local_atoms):
    """Creates the function GM_get_VEG_ref for given residues.

    Each residue is defined by an atom that is part of it. All atoms of
    the given residues will count towards the centre of mass.

    Parameters
    ----------
    local_atoms : list of str
        All these strings must be convertable to ints using int(). Each
        of these atoms is assumed to be in a different residue.

    Returns
    -------
    GM_get_VEG_ref : function
        The function that should be called to find the VEG centre for
        this oscillator.
    """

    def GM_get_VEG_ref(Printer, Map, Syst, osc):
        atnums = []
        for atom in local_atoms:
            resnum = Syst.resnums[osc.used_atoms[atom]]
            atnums.extend([*range(
                Syst.residues.first_ix[resnum],
                Syst.residues.last_ix[resnum] + 1
            )])
        CoM = GM_PF.calc_CoM(Syst, atnums)
        return CoM

    local_atoms = [int(num) for num in local_atoms]
    return GM_get_VEG_ref


def VEG_from_com(local_atoms):
    """Creates the function GM_get_VEG_ref for given atoms.

    Each atom given will count towards the VEG centre.

    Parameters
    ----------
    local_atoms : list of str
        All these strings must be convertable to ints using int(). Each
        value corresponds to an atom (using local indices)

    Returns
    -------
    GM_get_VEG_ref : function
        The function that should be called to find the VEG centre for
        this oscillator.
    """

    def GM_get_VEG_ref(Printer, Map, Syst, osc):
        atnums = [osc.used_atoms[ix] for ix in local_atoms]
        CoM = GM_PF.calc_CoM(Syst, atnums)
        return CoM

    local_atoms = [int(num) for num in local_atoms]
    return GM_get_VEG_ref


def VEG_from_position(Printer, map_, details):
    """Creates the function GM_get_VEG_ref for given atoms.

    Each atom given will count towards the VEG centre.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    map_ : :class:`~GMAP.src.tools.MapReader.Map`
        The map instance which this function will belong to.
    details : list of str
        The string(s) explaining what to do. Ints will be converted to
        the box positions of the atoms with that int as used_ix.

    Returns
    -------
    GM_get_VEG_ref : function
        The function that should be called to find the VEG centre for
        this oscillator.
    """

    codestring = "\ndef GM_get_VEG_ref"
    codestring += "(Printer, Map, Syst, osc):\n"

    codestring += "    CoM = " + envelop_int(
        " ".join(details), "osc.positions_box[", "]"
    ) + "\n"
    codestring += "    CoM = (CoM - np.floor(CoM + 0.5)) @ Syst.boxvects\n"
    codestring += "    return CoM"

    try:
        exec(codestring)
    except Exception as ex:
        corefile = (map_.directory / 'core.txt').resolve()
        Printer.warning(
            f"\nThe file {corefile} does not contain a valid definition of "
            "VEG_reference.",
            "MI_MC_9", exception=ex
        )
        return None

    # return GM_get_VEG_ref
    return locals()["GM_get_VEG_ref"]


def get_get_dipole_dir(Printer, map_):
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
        The function that every oscillator can call to get its dipole
        moment direction (might not always get used), and the position
        of that dipole moment.
    """

    # based on the r_vec and r_pos lines in the map core, build a function.

    # find direction of dipole vector
    codestring = "\ndef GM_get_dipole_dir(Printer, Map, Syst, osc):\n"
    codestring += "    r_vec = " + envelop_int(
        " ".join(map_.rawcore["r_vec"]),
        "osc.positions_box[", "]"
    ) + "\n"
    # Move vector back into the box, and normalize
    codestring += "    r_vec = (r_vec - np.floor(r_vec + 0.5))\n"
    codestring += "    r_vec = r_vec @ Syst.boxvects\n"
    codestring += "    r_vec /= GM_MF.vec3_len(r_vec)\n\n"

    # find position of the dipole
    codestring += "    r_pos = " + envelop_int(
        " ".join(map_.rawcore["r_pos"]),
        "osc.positions_box[", "]"
    ) + "\n"
    codestring += "    r_pos = (r_pos - np.floor(r_pos + 0.5))\n"
    codestring += "    r_pos = r_pos @ Syst.boxvects\n"
    codestring += "    return r_vec, r_pos\n"

    try:
        exec(codestring)
    except Exception as ex:
        corefile = (map_.directory / 'core.txt').resolve()
        Printer.warning(
            f"\nThe file {corefile} does not contain a valid definition of "
            "r_vec and/or r_pos.",
            "MI_MC_9", exception=ex
        )
        return None

    return locals()["GM_get_dipole_dir"]


def get_get_dipole_mag():
    """Default for obtaining the dipole magnitude

    returns
    -------
    GM_get_dipole_mag : function
        The function that can be used to get the magnitude of a dipole moment.
    """

    def GM_get_dipole_mag(Printer, Map, Syst, osc):
        if Map.Core.dipole_data_array is not None:
            return uses_maps(
                Map.Core.dipole_gas_phase,
                osc.VEGout,
                Map.Core.dipole_data_array
            )
        else:
            return Map.Core.dipole_gas_phase

    return GM_get_dipole_mag


def get_get_dipole(map_):
    """Default for obtaining the dipole.

    If the size of the dipole does not depend on the electrostatics, or
    only a single dependence (through magnitude), the returned method
    just combines GM_get_dipole_dir with GM_get_dipole_mag.
    If each of the x, y and z components have their own dependency on
    the electrostatics, the r_vec from GM_get_dipole_dir is ignored.

    parameters
    ----------
    map_ : :class:`~GMAP.src.tools.MapReader.Map`
        The map instance which this function will belong to.

    returns
    -------
    GM_get_dipole : function
        The function that every oscillator will call to get its dipole
    """

    # the version when we are working with magnitude
    def GM_get_dipole_vmag(Printer, Map, Syst, osc):
        r_vec, r_pos = Map.code.GM_get_dipole_dir(Printer, Map, Syst, osc)
        r_vec *= Map.code.GM_get_dipole_mag(Printer, Map, Syst, osc)
        return r_vec, r_pos

    # the version when we are working with a separate x, y, z component
    # (this one ignores the earlier given r_vec)
    def GM_get_dipole_vxyz(Printer, Map, Syst, osc):
        _, r_pos = Map.code.GM_get_dipole_dir(Printer, Map, Syst, osc)
        xyz = [
            uses_maps(omega, osc.VEGout, arr) for omega, arr in zip(
                Map.Core.dipole_gas_phase, Map.Core.dipole_data_array)
        ]
        xyz_local = np.array(xyz, dtype="float32")
        xyz_cartesian = np.dot(xyz_local, osc.rotation_matrix)
        return xyz_cartesian, r_pos

    if map_.Core.dipole_data_array is None:
        return GM_get_dipole_vmag

    if len(map_.Core.dipole_data_array.shape) == 2:
        return GM_get_dipole_vmag

    # now, the array must be of shape 3 (xyz-style file)
    return GM_get_dipole_vxyz


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
    codestring += "(Printer, Map, Syst, osc):\n"

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


def uses_maps(gas_freq, VEG, mapconsts):
    return gas_freq + np.sum(np.multiply(VEG, mapconsts))

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
