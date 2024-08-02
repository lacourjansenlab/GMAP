"""Main code file for AmideSC map.

Also is the template/explanation for all that a map can hand directly to
GMAP. Of course, more functions are allowed, and these files can import
other custom python files stored in the same directory (or a directory
therein) as this file.
"""

import numpy as np

import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.PhysicsFunctions as GM_PF


# A function to adjust the parameters of the map. For some kinds of
# parameter (especially if theres multiple that are linked), the way
# RunPar is built might not be correct. In this function, the user can
# fix that.
def GM_adjust_RunPars(Files, Map):
    """Makes the necessary changes to Map.RunPar.

    Is expected to not return anything - return value is not caught.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass


# A function to adjust the choices made in core.txt. Perhaps, based on
# a detected parameter, a different choice is preferred. This function
# allows to make a different choice, **in the same format as the file**.
# if more complex behaviour is desired, a separate function is needed.
def GM_adjust_map_core_raw(Files, Map):
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
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    choice = Map.RunPars.pos_choice
    match choice:
        case "C":  # the default
            Map.rawcore["position"] = ["0"]
        case "O":
            Map.rawcore["position"] = ["1"]
        case "N":
            Map.rawcore["position"] = ["3"]
        case "D":
            Map.rawcore["position"] = ["4"]


# A function to adjust the oscillators found for this map. Gets a list
# of oscillators, and is supposed to return a list of oscillators.
# For example, this function could remove some of the oscillators for
# some reason, and return the rest.
def GM_adjust_oscillators(Files, Map, Syst, oscillator_list):
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
def GM_post_init(Files, Map, Syst):
    pass


# A place to do things before the main loop starts (create datastructures
# to be filled in, for example). GEM itself builds the coupling table at
# this point in time. Any preparation stuff that only requires constant
# properties (masses, charges, bonds, for example) should be done here.
def GM_pre_run(Map, Syst):
    pass


# A place to do things before the properties for this frame are being
# calculated. Any preparation stuff that requires frame-dependent
# data should be done here. AIM calculated the CoMs here, GEM also
# builds hamiltonian (as its contents change per frame)
def GM_pre_frame(Map, Syst):
    pass


# A place to do things with the results from this frame. GEM itself
# writes information like the hamiltonian to files at this point in time.
def GM_post_frame(Map, Syst):
    pass


# A place to wrap up the entire calculation. GEM itself reports on
# calculation time and treated frames at this point in time.
def GM_post_run(Map, Syst):
    pass


# This is what GMAP assumes this function to contain if it is not specified.
# If oscillators belonging to this map should be reported any differently, that
# method should be specified here.
def placeholder_GM_str_osc(Syst, Map, osc):
    return f"living on residue number {Syst.resnums[osc.used_atoms[0]]}"


# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_rotation_matrix` - see the manual
# for more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_get_rotation_matrix(
    Map, Syst, osc
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
def placeholder_GM_get_dipole_dir(Map, Syst, osc):
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
def placeholder_GM_get_dipole_mag(Map, Syst, osc):
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
def placeholder_GM_calculate_dipole(Map, Syst, osc):
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
        Datatype of this array must be float32!
    r_pos : `np.ndarray`
        A length-3 vector containing the position of the dipole moment.
        The vector must lie within the simulation box.
        Datatype of this array must be float32!
    """

    r_vec, r_pos = Map.code.GM_get_dipole_dir(Map, Syst, osc)
    r_vec *= Map.code.GM_get_dipole_mag(Map, Syst, osc)
    return r_vec, r_pos


def placeholder_GM_calculate_frequency(Map, Syst, osc):
    return Map.Core.frequency_gas_phase + np.sum(np.multiply(
        osc.VEGout, Map.Core.frequency_data_array_linear))


def GM_calculate_raman(Map, Syst, osc):
    """Returns the raman tensor as a length-6 vector: (xx, xy, xz, yy, yz, zz)

    This method can easily be adapted by other maps for working with raman
    tensors. Make sure that rotation_matrix is an orthogonal 3*3 numpy array
    (so, the vectors making it up are orthonormal).
    Then, the raman_tensor_local can be freely chosen.

    As this is so easily adaptable, this could also be made a standard
    built-in function for GMAP. The only reason this is not the case
    currently, is because raman tensors from maps like this are not
    common yet, so a 'usual' way of determining them has not yet been
    created. Maybe, they won't stay of fixed magnitude in local coordinates
    forever, but depend on sth like VEG or atomic distances in the future.
    """

    # the rotation matrix is available as long as the map specifies
    # estatic_choice to be E or G (which is the case here). It is made
    # available immediately at the beginning of the frame.
    COvec = osc.roation_matrix[0, :]
    CNvec = osc.roation_matrixrot_mat[1, :]
    Zvec = osc.roation_matrixrot_mat[2, :]

    theta = 34*np.pi/180
    raman_tensor_local = np.diag([20, 4, 1])

    rotation_matrix = np.zeros((3, 3))
    rotation_matrix[0] = np.cos(theta) * COvec - np.sin(theta) * CNvec
    rotation_matrix[1] = np.sin(theta) * COvec + np.cos(theta) * CNvec
    rotation_matrix[2] = Zvec

    raman_tensor_system = (
        rotation_matrix.T @ raman_tensor_local @ rotation_matrix)

    # old (AIM) version:
    # def tp(vect1):  # tensor product
    #     tensor = np.zeros((6), dtype='float32')
    #     tensor[:3] = vect1[0]*vect1
    #     tensor[3:5] = vect1[1]*vect1[1:]
    #     tensor[5] = vect1[2]*vect1[2]
    #     return tensor
    # Rvec = tp(Rtens[0]) * 20 + tp(Rtens[1]) * 4  + tp(Rtens[2])
    # (here, Rtens is what the current version calls rotation_matrix)

    # now, to numpify this, first, redefine tp.
    # def tp(vect1):
    #     return (vect1[:, None] * vect1[None, :])[np.triu_indices(3)]

    # then, we can do the entire array at once:
    # consts = np.array([20, 4, 1])
    # Rvec = (
    #     Rtens[:, :, None] * Rtens[:, None, :] * consts[:, None, None]
    # ).sum(axis=0)[np.triu_indices(3)]

    # in summation notation (forgetting the triu-indices for flattening):
    # with A_ij == A[i, j]
    # Rvec[i, j] = sum{k=1 -> k=3}(Rtens[k, i] * Rtens[k, j] * consts[k])

    # now, is this equivalent to the new method? Lets derive the summation
    # notation for the new method! (R = rotation matrix, A = local raman tens)
    # Assuming A is diagonal (so only a[i, i] exist)
    # Rvec = R.T @ A @ R
    # Rvec[i, j] = sum{k=1 -> k=3}(R.T[i, k] * (A @ R)[k, j])
    #            = sum{k=1 -> k=3}(R[k, i] * A[k, k] * R[k, j])
    # this is the same as the summation for the AIM version!

    # footnote: what is (A @ R)[k, j]?
    # write it out: (A @ R)[i, j] = sum{k=1 -> k=3}(A[i, k] * R[k, j])
    # but, as only k==i exists for A (rest is 0), this becomes:
    # (A @ R)[i, j] = A[i, i] * R[i, j]

    return raman_tensor_system[np.triu_indices(3)]


# !!!! ATTENTION !!!! - THIS IS A PLACEHOLDER!
# GMAP will not actually 'see' this function and use it. If you want to
# have this function, just use `def GM_get_VEG_ref` - see the manual for
# more information. This placeholder is just here for illustration (but
# this map does not actually need this function).
def placeholder_GM_get_VEG_ref_residues(Map, Syst, osc):
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
def placeholder_GM_get_VEG_ref_com(Map, Syst, osc):
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
def GM_adjust_map_core_results(Files, Map):
    """Makes the necessary changes to the results derived from core.txt

    Is expected to not return anything - return value is not caught.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass
