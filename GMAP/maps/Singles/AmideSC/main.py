"""Main code file for AmideSC map.

Also is the template/explanation for all that a map can hand directly to
GMAP. Of course, more functions are allowed, and these files can import
other custom python files stored in the same directory (or a directory
therein) as this file.

how about adding these?
 - post_init()
 - pre_run()  # just before per-frame loop
 - pre_frame()
 - post_frame()
 - post_run()

 - calculate_freq()
 - calculate_dipole()
"""

import numpy as np

import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.PhysicsFunctions as GM_PF


# A function to adjust the parameters of the map. For some kinds of
# parameter (especially if theres multiple that are linked), the way
# RunPar is built might not be correct. In this function, the user can
# fix that.
def GM_adjust_RunPars(Files, Printer, Map):
    """Makes the necessary changes to Map.RunPar.

    Is expected to not return anything - return value is not caught.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass


# A function to adjust the choices made in core.txt. Perhaps, based on
# a detected parameter, a different choice is preferred. This function
# allows to make a different choice, **in the same format as the file**.
# if more complex behaviour is desired, a separate function is needed.
def GM_adjust_map_core_raw(Files, Printer, Map):
    """Makes the necessary changes to the 'raw' input read from core.txt.

    Is expected to not return anything - return value is not caught.

    The core.txt file is stored in Map.rawcore. It has not yet been
    parsed, just loaded into a dictionary. In this dictionary, each
    keyword is its own dictionary key. Most keywords can only occur once
    in the file - those have a list of the 'words' on the line as
    their value. The parameters that are allowed to occur more than once
    have a list as value, in which other lists appear - one for each
    line.

    The purpose of this function is to change this dictionary. Perhaps,
    a rule in core.txt is dependent on a parameter of the map. This
    function can make a decision based on those parameters (stored in
    Map.RunPars).

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass


# A function to adjust the oscillators found for this map. Gets a list
# of oscillators, and is supposed to return a list of oscillators.
# For example, this function could remove some of the oscillators for
# some reason, and return the rest.
def GM_adjust_oscillators(Files, Printer, Map, Syst, oscillator_list):
    """Makes the necessary changes to the list of oscillators.

    The program finds all oscillators mathing the instructions from
    core.txt. However, there is no way for the program to avoid double
    counting symmetrical groups (like the cystbridge mockup example).
    If a map knows its group is symmetrical, this function can be
    designed to only return half of the inputs.

    Another possible use is for the code of the map to get to know its
    oscillators. When all oscillators are passed through this function,
    the (global) atom number of the first atom of this group (for
    example) can be linked to a specific property the group might need
    to know. This might be useful if a map needs to cover two very
    similar oscillators.

    .. note::
        This function is called separately for each struct that the map
        defines. So take into account that the function could be called
        multiple times within a single simulation!

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    Syst : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator_list : list of :class:`~GMAP.src.tools.SystemReader.Oscillator`
        All oscillators belonging to a single struct of this map.

    Returns
    -------
    oscillator_list : list of :class:`~GMAP.src.tools.SystemReader.Oscillator`
        All oscillators belonging to a single struct of this map.
    """

    return oscillator_list


# A place to do further initialization if a map requires it. Think of
# things like building further lookup tables, for instance.
# (for AmideBB - find neighbours!)
def GM_post_init(Files, Printer, Map, Syst):
    pass


# A place to do things before the main loop starts (create datastructures
# to be filled in, for example). GEM itself builds the coupling table at
# this point in time. Any preparation stuff that only requires constant
# properties (masses, charges, bonds, for example) should be done here.
def GM_pre_run(Printer, Map, Syst):
    pass


# A place to do things before the properties for this frame are being
# calculated. Any preparation stuff that requires frame-dependent
# data should be done here. AIM calculated the CoMs here, GEM also
# builds hamiltonian (as its contents change per frame)
def GM_pre_frame(Printer, Map, Syst):
    pass


# A place to do things with the results from this frame. GEM itself
# writes information like the hamiltonian to files at this point in time.
def GM_post_frame(Printer, Map, Syst):
    pass


# A place to wrap up the entire calculation. GEM itself reports on
# calculation time and treated frames at this point in time.
def GM_post_run(Printer, Map, Syst):
    pass


# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_rotation_matrix` - see the manual
# for more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_get_rotation_matrix(
    Printer, Map, Syst, osc
):
    """Finds the rotation matrix for a given oscillator.

    Most maps are encoded in local cartesian coordinates (a rotation
    and/or translation of the global cartesian coordinates - not sheared
    or box coordinates). So in order to be able to apply the map, the
    transformation must be performed.

    .. note::
        This function is called by the program every time it needs to
        know how
        to rotate for this group. This rotation will be different for
        each individual oscillator (so each molecule), each frame.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    Syst : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
        The specific oscillator for which the transformation is required.

    Returns
    -------
    rotation_matrix : `np.ndarray`
        A 3*3 matrix containing the rotation matrix. If a vector in
        global coordinates is multiplied with this matrix, the result
        should be that vector expressed in the coordinate system of this
        oscillator.
    """

    x_uvec = (osc.positions_box[1] - osc.positions_box[0]) @ Syst.boxvects
    x_uvec /= GM_MF.vec3_len(x_uvec)
    y_uvec = (osc.positions_box[3] - osc.positions_box[0]) @ Syst.boxvects
    y_uvec = GM_MF.project(x_uvec, y_uvec)
    y_uvec /= GM_MF.vec3_len(y_uvec)
    z_uvec = GM_MF.crossprod(x_uvec, y_uvec)
    z_uvec /= GM_MF.vec3_len(z_uvec)

    return np.array([x_uvec, y_uvec, z_uvec])


# returns the dipole position and vector for osc. To be used during a
# frame - must be fast.
# A map creator can write this function themselves, or let it be automatically
# generated by GEM during runtime

# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_dipole_dir` - see the manual for
# more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_get_dipole_dir(Printer, Map, Syst, osc):
    """Finds the dipole moment direction and its position of a given
    oscillator.

    Most spectroscopic techniques require to know the dipole moment of
    each oscillator. Usually, this dipole moment can be approximated
    easily without calculating it. When defining a dipole moment just
    in terms of atom positions (as facilitated in core.txt) does not
    suffice, this function can be used.

    .. note::
        This function is called by the program every time it needs to
        know the dipole moment
        of this group. This dipole will be different for
        each individual oscillator (so each molecule), each frame.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    Syst : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
        The specific oscillator for which the transformation is required.

    Returns
    -------
    r_vec : `np.ndarray`
        A length-3 vector containing the direction of the dipole moment.
        The vector must be normalized.
    r_pos : `np.ndarray`
        A length-3 vector containing the position of the dipole moment.
        The vector must lie within the simulation box.
    """

    r_vec = (osc.positions_box[1] - osc.positions_box[0]) @ Syst.boxvects
    r_pos = Syst.positions[osc.used_atoms[0]]
    return r_vec, r_pos


# the actual magnitude of the dipole moment

# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_dipole_mag` - see the manual for
# more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_get_dipole_mag(Printer, Map, Syst, osc):
    """Finds the magnitude for a given dipole moment.

    Most spectroscopic techniques require to know the dipole moment of
    each oscillator. Usually, this dipole moment can be approximated
    easily without calculating it. When defining a dipole moment magnitude
    using a base value and an optional standard-format VEG-dependence does not
    suffice, this function can be used.

    .. note::
        This function is called by the program every time it needs to
        know the magnitude of the dipole moment
        of this group. This magnitude could be different for
        each individual oscillator (so each molecule), each frame, so it
        will be called that often. But it doesn't always have to return
        something different.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    Syst : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
        The specific oscillator for which the transformation is required.

    Returns
    -------
    magnitude : `np.float32`
        The length that the dipole moment vector should have.
    """

    return np.float32(0.3)


# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_dipole` - see the manual for
# more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_calculate_dipole(Printer, Map, Syst, osc):
    """Finds a given dipole moment and its position.

    Most spectroscopic techniques require to know the dipole moment of
    each oscillator. Usually, this dipole moment can be approximated
    easily without calculating it. When a dipole has a more complex
    format than the program uses by default, this function can be used.

    .. note::
        This function is simply the call to GM_get_dipole_dir, and then
        multiplying the resulting r_vec with the result of
        GM_get_dipole_mag. If only one of those two needs to be changed,
        it is recommended to make the change there, instead of here.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    Syst : :class:`~GMAP.src.tools.SystemReader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
        The specific oscillator for which the transformation is required.

    Returns
    -------
    r_vec : `np.ndarray`
        A length-3 vector containing the direction of the dipole moment.
    r_pos : `np.ndarray`
        A length-3 vector containing the position of the dipole moment.
        The vector must lie within the simulation box.
    """

    r_vec, r_pos = Map.code.GM_get_dipole_dir(Printer, Map, Syst, osc)
    r_vec *= Map.code.GM_get_dipole_mag(Printer, Map, Syst, osc)
    return r_vec, r_pos


# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_VEG_ref` - see the manual for
# more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_get_VEG_ref_residues(Printer, Map, Syst, osc):
    atnums = []
    for atom in [0]:
        resnum = Syst.resnums[osc.used_atoms[atom]]
        atnums.extend([*range(
            Syst.residues.first_ix[resnum],
            Syst.residues.last_ix[resnum] + 1
        )])
    CoM = GM_PF.calc_CoM(Syst, atnums)
    return CoM


# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_VEG_ref` - see the manual for
# more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_get_VEG_ref_com(Printer, Map, Syst, osc):
    atnums = []
    for atom in [0, 1, 3, 4]:
        atnums.append(osc.used_atoms[atom])
    CoM = GM_PF.calc_CoM(Syst, atnums)
    return CoM


# A function to adjust the final python objects built out of the
# core.txt file. If more complex behaviour is desired than the file
# format currently supports, an alternative function can be created
# here.
# !!!!!!!!!!!!!!!!!!!!!
# is this actually needed? Or does this influence the customizable
# functions only, anyways?
def GM_adjust_map_core_results(Files, Printer, Map):
    """Makes the necessary changes to the results derived from core.txt

    Is expected to not return anything - return value is not caught.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass
