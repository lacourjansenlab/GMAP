"""
Generator of default functions for
:class:`~GMAP.src.tools.map_reader.Map` objects. 

A map has an asssociated code object that stores python functions which
can be used by map makers to trigger certain behaviour. When a map does
not make a choice, a default has to be inserted instead. Those defaults
are created here.

Classes
-------
NewModule
    Creates an empty class.

Functions
---------
get_adjust_run_pars
    Creates the default for the map function GM_adjust_run_pars
get_adjust_map_core_raw
    Creates the default for the map function GM_adjust_map_core_raw
get_adjust_oscillators
    Creates the default for the map function GM_adjust_oscillators
get_filter_oscillators
    Creates the default for the map function GM_filter_oscillators
filter_single_line
    Defines how to apply a filter to a given list of oscillators
get_post_init
    Creates the default for the map function GM_post_init
get_pre_run
    Creates the default for the map function GM_pre_run
get_pre_frame
    Creates the default for the map function GM_pre_frame
get_post_frame
    Creates the default for the map function GM_post_frame
get_post_run
    Creates the default for the map function GM_post_run
get_change_coup_type
    Creates the default for the map function GM_change_coup_type
get_prep_coupling
    Creates the default for the map function GM_prep_coupling
get_calc_coupling
    Creates the default for the map function GM_calc_coupling
get_str_osc
    Creates the default for the map function GM_str_osc
get_report_system
    Creates the default for the map function GM_report_system
get_get_VEG_ref
    Creates the default for the map function GM_get_VEG_ref
VEG_from_residues
    Stores a default for the map function GM_get_VEG_ref, based on
    residues
VEG_from_CoM
    Stores a default for the map function GM_get_VEG_ref, based on
    center of mass
interpret_position
    Converts integers in a simple math expression to atoms of that
    index. Resulting math obeys PBC.
get_get_dipole_dir
    Creates the default for the map function GM_get_dipole_dir
get_get_dipole_mag
    Creates the default for the map function GM_get_dipole_mag
get_get_rotation_matrix
    Creates the default for the map function GM_get_rotation_matrix
get_calculate_dipole
    Creates the default for the map function GM_calculate_dipole
get_calculate_frequency
    Creates the default for the map function GM_calculate_frequency
get_get_position
    Creates the default for the map function GM_get_position
get_get_doublepos
    Creates the default for the map function GM_get_doublepos
get_report_references
    Creates the default for the map function GM_report_references
does_nothing
    Does nothing.
returns_last
    Returns the last argument
returns_input
    Returns a function which always returns the input to this function
uses_maps
    A simple element-wise multiplication of arrays. These must be of
    correct size (not checked)
envelop_int
    Envelops any integer (but not float) found in given string with the
    given pre and post.
"""


# 3rd party imports
import numpy as np

# local imports
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.math_functions as GM_mf
import GMAP.src.tools.physics_functions as GM_pf
import GMAP.src.tools.print_tools as GM_pt


class NewModule:
    def __init__(self):
        pass


# ------------------------
# Getters for mapfunctions
# ------------------------


def get_adjust_run_pars():
    """provides the default for the function GM_adjust_run_pars.

    For more details on GM_adjust_run_pars, see
    :ref:`MapFiles_SingMainPy_adjust_run_pars` (Single) or
    :ref:`MapFiles_SingMainPy_adjust_run_pars` (Pair).

    Returns
    -------
    GM_adjust_run_pars : function
        The function that should be called to make changes to requested
        run parameters.
    """

    return does_nothing


def get_adjust_map_core_raw():
    """provides the default for the function GM_adjust_map_core_raw.

    For more details on GM_adjust_map_core_raw, see
    :ref:`MapFiles_SingMainPy_adjust_map_core_raw` (Single) or
    :ref:`MapFiles_PairMainPy_adjust_map_core_raw` (Pair).

    Returns
    -------
    GM_adjust_map_core_raw : function
        The function that should be called to make changes to the
        contents of the core.txt file.
    """

    return does_nothing


def get_adjust_oscillators():
    """provides the default for the function GM_adjust_oscillators.

    For more details on GM_adjust_map_core_raw, see
    :ref:`MapFiles_SingMainPy_adjust_oscillators` (Single).

    Returns
    -------
    GM_adjust_oscillators : function
        The function that should be called to make changes to the
        found oscillators.
    """

    return returns_last


def get_filter_oscillators():
    """provides the default for the function GM_filter_oscillators.

    For more details on GM_filter_oscillators, see
    :ref:`MapFiles_SingMainPy_filter_oscillators` (Single).

    Returns
    -------
    GM_filter_oscillators : function
        The function that should be called to apply user-requested,
        run-specific oscillator black/whitelists to the oscillators
        found in the system.
    """

    def filter_oscillators(map_, system, oscillators):
        """The default function for applying black/whitelist filters.

        Options supported by default:
        - :All and :None
        - resnums - these indicate the residue number of the first atom
        - resnames - assumed a residue name.
        """

        runpars = map_.run_pars.main_run_pars
        wl_rules = runpars.singles_whitelist_dict.get(map_.name, [[":All"]])
        bl_rules = runpars.singles_blacklist_dict.get(map_.name, [[":None"]])

        # the 'rules' are lists of lists. Each sublist corresponds to a line
        # from the input file, each item within the sublist is a 'word'

        # first, select all in whitelist from oscillators
        filtered = set()
        oscset = set(oscillators)
        for rule in wl_rules:
            success, filtered = filter_single_line(
                rule, "white", filtered, oscset, map_, system)
            if not success:
                GM_pt.Printer.warning(
                    "\nUsing the parameter 'singles_whitelist', the map "
                    f"{map_.name} "
                    "requestested a specific selection, but it was not "
                    "recognized. ",
                    "SU_NP_8", True, GMAPerrclass=GM_ex.GmapFileSyntaxError
                )

        # from the whitelisted, remove all those in blacklist.
        for rule in bl_rules:
            success, filtered = filter_single_line(
                rule, "black", filtered, oscset, map_, system
            )
            if not success:
                GM_pt.Printer.warning(
                    "\nUsing the parameter 'singles_whitelist', the map "
                    f"{map_.name} "
                    "requestested a specific selection, but it was not "
                    "recognized. ",
                    "SU_NP_8", True, GMAPerrclass=GM_ex.GmapFileSyntaxError
                )

        # sort the oscillators in correct order (same as before)
        filtered_list = [osc for osc in oscillators if osc in filtered]
        return filtered_list
    return filter_oscillators


def filter_single_line(line, BW, found, avail, map_, system):
    """Apply the filter rule on a single line to the current list of
    found oscillators.

    This function has been designed with the assumption that the
    whitelist should be applied first, then the blacklist.

    Parameters
    ----------
    line : list
        The contents of a single line from an input file. This contains
        the instructions only - the 'singles_BWlist' label and map name
        have already been stripped off.
    BW : string
        Should either be "black" or "white". Anything that does not
        exactly match "white" (case sensitive) is taken to be "black".
        Indicates whether we're blacklisting or whitelisting currently.
    found : set of :class:`~GMAP.src.tools.system_reader.Oscillator`
        The oscillators that should be kept, (i.e. have already been
        found) considering the black/whitelist lines so far.
    avail : set of :class:`~GMAP.src.tools.system_reader.Oscillator`
        The oscillators that are available in the system.
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about the map the oscillators belong to.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)

    Returns
    -------
    success : bool
        Whether the contents of the line were recognized correctly. This
        allows maps writing a custom GM_filter_oscillators to still use
        this function first to give the same support as GMAP, and then
        also apply their own rules.
    found : set of :class:`~GMAP.src.tools.system_reader.Oscillator`
        The oscillators that should be used given the already processed
        black/whitelist rules.
    """

    match line[0].lower():
        case ":all":
            if BW == "white":
                return True, avail.copy()
            else:
                return True, set()
        case ":none":
            if BW == "white":
                return True, set()
            else:
                return True, found.copy()
        case "resnums":
            # Check whether the choice is alphanumeric
            # we can use/support hyphens, too, but not commas/periods.
            if not set("".join(line[1:])).issubset("1234567890-"):
                GM_pt.Printer.warning(
                    f"\nUsing the parameter 'singles_{BW}list', the map "
                    f"{map_.name}"
                    "was requestested certain residue numbers, but this "
                    "specification used non-numeric characters. Please make "
                    "sure to only use numbers and hyphens. ",
                    "SU_NP_8", True, GMAPerrclass=GM_ex.GmapFileSyntaxError
                )
            # find all allowed numbers
            try:
                resnums = set(map_.core.allow_ranges(line[1:], system.nres))
            except IndexError as ierr:
                GM_pt.Printer.warning(
                    f"\nUsing the parameter 'singles_{BW}list', the map "
                    f"{map_.name}"
                    "was requestested certain residue numbers, but the "
                    "specific residue numbers requested do not exist in the "
                    "provided MD system. ",
                    "SU_NP_8", True, exception=ierr,
                    GMAPerrclass=GM_ex.GmapIndexError
                )
            except Exception as ex:
                GM_pt.Printer.warning(
                    f"\nUsing the parameter 'singles_{BW}list', the map "
                    f"{map_.name}"
                    "was requestested certain residue numbers, but the "
                    "specific choice provided could not be interpreted. "
                    "Please make sure the choice consists of nothing but "
                    "numbers separated by spaces "
                    "and/or ranges of integers separated by a hyphen.",
                    "SU_NP_8", True, exception=ex,
                    GMAPerrclass=GM_ex.GmapFileSyntaxError
                )

            # only keep an oscillator if its number is expected.
            filtered = {
                osc for osc in avail
                if system.resnums[osc.used_atoms[0]] in resnums
            }
            if BW == "white":
                found |= filtered
            else:
                found -= filtered
            return True, found
        case "resnames":
            resnames = set(line[1:])
            filtered = {
                osc for osc in avail
                if system.resnames[osc.used_atoms[0]] in resnames
            }
            if BW == "white":
                found |= filtered
            else:
                found -= filtered
            return True, found
        case _:
            return False, found


def get_post_init():
    """provides the default for the function GM_post_init.

    For more details on GM_post_init, see
    :ref:`MapFiles_SingMainPy_post_init` (Single) or
    :ref:`MapFiles_PairMainPy_post_init` (Pair).

    Returns
    -------
    GM_post_init : function
        The function that should be called to perform any further map
        initialization.
    """

    return does_nothing


def get_pre_run():
    """provides the default for the function GM_pre_run.
    
    For more details on GM_pre_run, see
    :ref:`MapFiles_SingMainPy_pre_run` (Single) or
    :ref:`MapFiles_PairMainPy_pre_run` (Pair).

    Returns
    -------
    GM_pre_run : function
        The function that should be called to do prep work that needs
        to happen before the calculation.
    """

    return does_nothing


def get_pre_frame():
    """provides the default for the function GM_pre_frame.
    
    For more details on GM_pre_frame, see
    :ref:`MapFiles_SingMainPy_pre_frame` (Single) or
    :ref:`MapFiles_PairMainPy_pre_frame` (Pair).

    Returns
    -------
    GM_pre_frame : function
        The function that should be called to do prep work that needs to
        be repeated for every frame.
    """

    return does_nothing


def get_post_frame():
    """provides the default for the function GM_post_frame.
    
    For more details on GM_post_frame, see
    :ref:`MapFiles_SingMainPy_post_frame` (Single) or
    :ref:`MapFiles_PairMainPy_post_frame` (Pair).

    Returns
    -------
    GM_post_frame : function
        The function that should be called to round up any
        frame-specific tasks.
    """

    return does_nothing


def get_post_run():
    """provides the default for the function GM_post_run.
    
    For more details on GM_post_run, see
    :ref:`MapFiles_SingMainPy_post_run` (Single) or
    :ref:`MapFiles_PairMainPy_post_run` (Pair).

    Returns
    -------
    GM_post_run : function
        The function that should be called to round up any tasks before
        the calculation/GMAP stops.
    """

    return does_nothing


def get_change_coup_type(name):
    """provides the default for the function GM_change_coup_type.
    
    For more details on GM_change_coup_type, see
    :ref:`MapFiles_PairMainPy_change_coup_type` (Pair).

    Parameters
    ----------
    name : str
        The mapname that the function should return.

    Returns
    -------
    GM_change_coup_type : function
        The function that should be called to assign the correct
        coupling map to a provided oscillator pair.
    """

    # yes, here we have call - there's a def inside returns_input.
    return returns_input(name)


def get_prep_coupling():
    """provides the default for the function GM_prep_coupling.
    
    For more details on GM_prep_coupling, see
    :ref:`MapFiles_PairMainPy_prep_coupling` (Pair).

    Returns
    -------
    GM_prep_coupling : function
        The function that should be called to do any prep work for the
        couplings of this frame.
    """

    return does_nothing


def get_calc_coupling():
    """provides the default for the function GM_calc_coupling.
    
    For more details on GM_calc_coupling, see
    :ref:`MapFiles_PairMainPy_calc_coupling` (Pair).

    Returns
    -------
    GM_calc_coupling : function
        The function that should be called to calculate the couplings
        for this map, this frame.
    """

    return does_nothing


def get_str_osc():
    """provides the default for the function GM_str_osc.
    
    For more details on GM_str_osc, see
    :ref:`MapFiles_SingMainPy_str_osc` (Single).

    Returns
    -------
    GM_str_osc : function
        The function that should be called to determine the
        representative string of this oscillator.
    """

    def base_str_getter(map_, system, osc):
        return f"living on residue number {system.resnums[osc.used_atoms[0]]}"
    return base_str_getter


def get_report_system():
    """provides the default for the function GM_report_system.
    
    For more details on GM_report_system, see
    :ref:`MapFiles_SingMainPy_report_system` (Single).

    Returns
    -------
    GM_report_system : function
        The function that should be called to determine how this map
        should be listed when GMAP reports on the MD system.
    """

    def base_str_getter(map_, system):
        name = map_.name + ":"
        amount = len(system.oscillators_ordered.get(map_.name, []))
        return f"{name: <21} {amount: >4}"
    return base_str_getter


def get_get_VEG_ref(map_):
    """Creates the function GM_get_VEG_ref.

    Recognizes requested method and finds relevant function.

    For more details on GM_get_VEG_ref, see
    :ref:`MapFiles_SingMainPy_get_VEG_ref` (Single).

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
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
            GM_get_VEG_ref = VEG_from_CoM(details)
        case "position":
            GM_get_VEG_ref = interpret_position(map_, details, "VEG_reference")
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

    def GM_get_VEG_ref(map_, system, osc):
        atnums = []
        for atom in local_atoms:
            resnum = system.resnums[osc.used_atoms[atom]]
            atnums.extend([*range(
                system.residues.first_ix[resnum],
                system.residues.last_ix[resnum] + 1
            )])
        CoM = GM_pf.calc_CoM(system, atnums)
        return CoM

    local_atoms = [int(num) for num in local_atoms]
    return GM_get_VEG_ref


def VEG_from_CoM(local_atoms):
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

    def GM_get_VEG_ref(map_, system, osc):
        atnums = [osc.used_atoms[ix] for ix in local_atoms]
        CoM = GM_pf.calc_CoM(system, atnums)
        return CoM

    local_atoms = [int(num) for num in local_atoms]
    return GM_get_VEG_ref


def interpret_position(map_, details, parname, center=None):
    """Creates a function that finds a requested position.

    This position could be the definition of the VEG-sphere-centre
    (VEG reference), but it could also be the position or doublepos
    output.

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map instance which this function will belong to.
    details : list of str
        The string(s) explaining what to do. Ints will be converted to
        the box positions of the atoms with that int as used_ix.
    parname : str
        The name of the parameter which specified the position currently
        being analyzed.
    center : list or `np.ndarray`, default = [0, 0, 0]
        The center of the output positions. If the box coordinate
        representation of the difference from any point to this center
        exceeds 0.5, that point is wrapped around the box.

    Returns
    -------
    GM_get_position : function
        The function that should be called to find the requested
        position for this oscillator.
    """

    if center is None:
        center = [0, 0, 0]

    centerstring = [str(item) for item in center]
    centerstring = ", ".join(centerstring)
    centerstring = f"np.array([{centerstring}], dtype='float32')"

    codestring = "\ndef GM_get_position"
    codestring += "(map_, system, osc):\n"

    codestring += "    CoM = " + envelop_int(
        " ".join(details), "osc.positions_box[", "]"
    ) + "\n"
    codestring += f"    CoM = (CoM - np.floor(CoM - {centerstring}"
    codestring += "+ 0.5)) @ system.boxvects\n"
    codestring += "    return CoM"

    try:
        locs = locals()
        exec(codestring, globals(), locs)
    except Exception as ex:
        corefile = (map_.directory / 'core.txt').resolve()
        GM_pt.Printer.warning(
            f"\nThe file {corefile} does not contain a valid definition of "
            f"{parname}.",
            "MI_MC_9", exception=ex
        )
        return None

    # return GM_get_VEG_ref
    return locs["GM_get_position"]


def get_get_rotation_matrix(map_):
    """provides the default for the function GM_get_rotation_matrix.
    
    For more details on GM_get_rotation_matrix, see
    :ref:`MapFiles_SingMainPy_get_rotation_matrix` (Single).

    parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map instance which this function will belong to.

    returns
    -------
    GM_get_rotation_matrix : function
        The function that every oscillator will call to get its rotaion
        matrix
    """

    allparnames = ("x_uvec", "y_uvec", "z_uvec")
    # determine xyz order
    given_directions = [key for key in map_.rawcore if key in allparnames]

    codestring = "\ndef GM_get_rotation_matrix"
    codestring += "(map_, system, osc):\n"

    # the first direction should be taken as is
    direc = given_directions[0]
    codestring += f"    {direc} = (" + envelop_int(
        " ".join(map_.rawcore[direc]),
        # "GM_mf.PBCvect(system.positions[osc.used_atoms[", "]])"
        "osc.positions_box[", "]"
    ) + ") @ system.boxvects\n"
    codestring += f"    {direc} /= GM_mf.vec3_len({direc})\n\n"

    # the second direction depends on the type
    olddir = direc
    if map_.core.type == "standard":
        direc = given_directions[1]
        codestring += f"    {direc} = GM_mf.project({olddir}, ("
        codestring += envelop_int(
            " ".join(map_.rawcore[direc]),
            # "GM_mf.PBCvect(system.positions[osc.used_atoms[", "]])"
            "osc.positions_box[", "]"
        ) + ") @ system.boxvects)\n"
    elif map_.core.type == "linear":
        # get the next item in the list
        direc = allparnames[(allparnames.index(olddir) + 1) % 3]

        # find the direction with smallest value of prev vector
        codestring += f"    smalldir = np.argmin(np.abs({olddir}))\n"
        codestring += f"    {direc} = np.zeros((3))\n"
        codestring += f"    {direc}[smalldir] = 1\n"
        codestring += f"    {direc} = GM_mf.project({olddir}, {direc})\n"

    codestring += f"    {direc} /= GM_mf.vec3_len({direc})\n\n"

    # the third direction is always the cross product
    lastdir = [x for x in allparnames if x not in (olddir, direc)][0]
    codestring += f"    {lastdir} = GM_mf.crossprod({olddir}, {direc})\n"
    codestring += f"    {lastdir} /= GM_mf.vec3_len({lastdir})\n\n"

    # now, combine into array to return
    codestring += "    return np.array([x_uvec, y_uvec, z_uvec])\n"

    try:
        # exec(codestring, globals(), locals())
        locs = locals()
        exec(codestring, globals(), locs)
    except Exception as ex:
        corefile = (map_.directory / 'core.txt').resolve()
        GM_pt.Printer.warning(
            f"\nThe file {corefile} does not contain a valid definition of "
            "x_uvec, y_uvec and/or z_uvec.",
            "MI_MC_9", exception=ex
        )
        return None

    # return GM_get_dipole
    return locs["GM_get_rotation_matrix"]


def get_get_dipole_dir(map_):
    """provides the default for the function GM_get_dipole_dir.
    
    For more details on GM_get_dipole_dir, see
    :ref:`MapFiles_SingMainPy_get_dipole_dir` (Single).

    parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map instance which this function will belong to.

    returns
    -------
    GM_get_dipole_dir : function
        The function that every oscillator can call to get its dipole
        moment direction (might not always get used), and the position
        of that dipole moment.
    """

    # based on the r_vec and r_pos lines in the map core, build a function.

    # find direction of dipole vector
    codestring = "\ndef GM_get_dipole_dir(map_, system, osc):\n"
    codestring += "    r_vec = " + envelop_int(
        " ".join(map_.rawcore["r_vec"]),
        "osc.positions_box[", "]"
    ) + "\n"
    # Move vector back into the box, and normalize
    codestring += "    r_vec = (r_vec - np.floor(r_vec + 0.5))\n"
    codestring += "    r_vec = r_vec @ system.boxvects\n"
    codestring += "    r_vec /= GM_mf.vec3_len(r_vec)\n"
    codestring += "    r_vec = r_vec.astype('float32')\n\n"

    # find position of the dipole
    codestring += "    r_pos = " + envelop_int(
        " ".join(map_.rawcore["r_pos"]),
        "osc.positions_box[", "]"
    ) + "\n"
    codestring += "    r_pos = (r_pos - np.floor(r_pos + 0.5))\n"
    codestring += "    r_pos = r_pos @ system.boxvects\n"
    codestring += "    r_pos = r_pos.astype('float32')\n\n"
    codestring += "    return r_vec, r_pos\n"

    try:
        locs = locals()
        exec(codestring, globals(), locs)
    except Exception as ex:
        corefile = (map_.directory / 'core.txt').resolve()
        GM_pt.Printer.warning(
            f"\nThe file {corefile} does not contain a valid definition of "
            "r_vec and/or r_pos.",
            "MI_MC_9", exception=ex
        )
        return None

    return locs["GM_get_dipole_dir"]


def get_get_dipole_mag():
    """provides the default for the function GM_get_dipole_mag.
    
    For more details on GM_get_dipole_mag, see
    :ref:`MapFiles_SingMainPy_get_dipole_mag` (Single).

    Returns
    -------
    GM_get_dipole_mag : function
        The function that can be used to get the magnitude of a dipole
        moment.
    """

    def GM_get_dipole_mag(map_, system, osc):
        if map_.core.dipole_data_array is not None:
            return uses_maps(
                map_.core.dipole_gas_phase,
                [osc.VEGout],
                [map_.core.dipole_data_array]
            )
        else:
            return map_.core.dipole_gas_phase

    return GM_get_dipole_mag


def get_calculate_dipole(map_):
    """Default for obtaining the dipole.

    If the size of the dipole does not depend on the electrostatics, or
    only a single dependence (through magnitude), the returned method
    just combines GM_get_dipole_dir with GM_get_dipole_mag.
    If each of the x, y and z components have their own dependency on
    the electrostatics, the r_vec from GM_get_dipole_dir is ignored.

    For more details on GM_get_dipole, see
    :ref:`MapFiles_SingMainPy_calculate_dipole` (Single).

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map instance which this function will belong to.

    Returns
    -------
    GM_get_dipole : function
        The function that every oscillator will call to get its dipole
    """

    # the version when we are working with magnitude
    def GM_get_dipole_vmag(map_, system, osc):
        r_vec, r_pos = map_.code.GM_get_dipole_dir(map_, system, osc)
        r_vec *= map_.code.GM_get_dipole_mag(map_, system, osc)
        r_vec = r_vec.astype("float32")
        return r_vec, r_pos

    # the version when we are working with a separate x, y, z component
    # (this one ignores the earlier given r_vec)
    def GM_get_dipole_vxyz(map_, system, osc):
        _, r_pos = map_.code.GM_get_dipole_dir(map_, system, osc)
        # xyz = [
        #     uses_maps(omega, [osc.VEGout], [arr]) for omega, arr in zip(
        #         map_.core.dipole_gas_phase, map_.core.dipole_data_array)
        # ]
        # xyz_local = np.array(xyz, dtype="float32")
        xyz_local = map_.core.dipole_gas_phase_array + np.sum(
            np.multiply(osc.VEGout[None, :, :], map_.core.dipole_data_array),
            axis=(1, 2)
        )
        xyz_cartesian = np.dot(xyz_local, osc.rotation_matrix)
        return xyz_cartesian, r_pos

    if map_.core.dipole_data_array is None:
        return GM_get_dipole_vmag

    if len(map_.core.dipole_data_array.shape) == 2:
        return GM_get_dipole_vmag

    # now, the array must be of shape 3 (xyz-style file)
    return GM_get_dipole_vxyz


def get_calculate_frequency(map_):
    """Default for obtaining the frequency.

    If frequency does not depend on the electrostatics, the returned
    frequency simply equals the gas phase value. If there is a
    dependency, the VEGout array will be combined with the mapping
    coeffients to obtain the frequency.

    For more details on GM_calculate_frequency, see
    :ref:`MapFiles_SingMainPy_calculate_frequency` (Single).

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map instance which this function will belong to.

    Returns
    -------
    GM_calculate_frequency : function
        The function that every oscillator will call to get its
        frequency
    """

    def GM_calculate_freq_base(map_, system, osc):
        return map_.core.frequency_gas_phase

    def GM_calculate_freq_VEG_lin(map_, system, osc):
        freq = uses_maps(
            map_.core.frequency_gas_phase, [osc.VEGout],
            [map_.core.frequency_data_array_linear]
        )
        return freq

    def GM_calculate_freq_VEG_quad(map_, system, osc):
        freq = uses_maps(
            map_.core.frequency_gas_phase, [osc.VEGout**2],
            [map_.core.frequency_data_array_quadratic]
        )
        return freq

    def GM_calculate_freq_VEG_both(map_, system, osc):
        freq = uses_maps(
            map_.core.frequency_gas_phase,
            [osc.VEGout, osc.VEGout**2],
            [
                map_.core.frequency_data_array_linear,
                map_.core.frequency_data_array_quadratic]
        )
        return freq

    if map_.core.frequency_data_array_linear is None:
        if map_.core.frequency_data_array_quadratic is None:
            return GM_calculate_freq_base
        else:
            return GM_calculate_freq_VEG_quad
    elif map_.core.frequency_data_array_quadratic is None:
        return GM_calculate_freq_VEG_lin
    else:
        return GM_calculate_freq_VEG_both


def get_get_position(map_):
    """Default for obtaining the position.

    By default, the author of a map uses the oscillator-indices to
    indicate what position (e.g. just an atom index) should be returned.
    Those instructions are interpreted here and converted to a function
    that can be used during runs.
    
    For more details on GM_get_position, see
    :ref:`MapFiles_SingMainPy_get_position` (Single).

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map instance which this function will belong to.

    Returns
    -------
    GM_get_position : function
        The function that every oscillator will call to get its
        position
    """

    instructions = map_.rawcore["position"]
    position_center_choice = map_.run_pars.main_run_pars.positions_center
    GM_get_positions = interpret_position(
        map_, instructions, "position", center=position_center_choice)
    return GM_get_positions


def get_get_doublepos(map_):
    """Default for obtaining the double positions.

    By default, the author of a map uses the oscillator-indices to
    indicate what positions (e.g. just an atom index) should be
    returned.
    Those instructions are interpreted here and converted to a function
    that can be used during runs.
    
    For more details on GM_get_doublepos, see
    :ref:`MapFiles_SingMainPy_get_doublepos` (Single).

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map instance which this function will belong to.

    Returns
    -------
    GM_get_doublepos : function
        The function that every oscillator will call to get its
        doublepos (two positions)
    """

    def GM_get_doublepos(map_, system, osc):
        pos0 = GM_get_doublepos0(map_, system, osc)
        pos1 = GM_get_doublepos1(map_, system, osc)
        return pos0, pos1

    instructions = map_.rawcore["doublepos_0"]
    GM_get_doublepos0 = interpret_position(map_, instructions, "doublepos_0")
    instructions = map_.rawcore["doublepos_1"]
    GM_get_doublepos1 = interpret_position(map_, instructions, "doublepos_1")

    return GM_get_doublepos


def get_report_references():
    """Default for obtaining the correct references of a map.

    By default, all references should be considered.
    
    For more details on GM_report_references, see
    :ref:`MapFiles_SingMainPy_report_references` (Single).

    Returns
    -------
    GM_report_references : function
        The function that can be used to get the magnitude of a dipole
        moment.
    """

    def GM_report_references(map_, system):
        return map_.references
    return GM_report_references


# ------------------------
# Base functions
# ------------------------


def does_nothing(*args):
    pass


def returns_last(*args):
    return args[-1]


def returns_input(input_):
    def returner(*args):
        return input_
    return returner


def uses_maps(gas_freq, VEGs, mapconsts_list):
    freq = gas_freq
    for VEG, mapconsts in zip(VEGs, mapconsts_list):
        freq += np.sum(np.multiply(VEG, mapconsts))
    return freq

# ------------------------
# Useful tools
# ------------------------


def envelop_int(string, pre, post):
    """Envelops any integer (but not float) found in string with pre and
    post.

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


def _unused_user():
    """never called, just to remove the unused warnings for imports"""

    _ = np.array([1, 2])
    _ = GM_mf.dotprod(np.array([1, 2, 3]), np.array([1, 2, 3]))
