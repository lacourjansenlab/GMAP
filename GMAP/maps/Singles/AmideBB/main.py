
# 3rd party imports
import numpy as np

# GMAP imports
import GMAP.src.tools.constants as GM_con
import GMAP.src.tools.default_map_functions as GM_dmf
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.print_tools as GM_pt
from GMAP.src.tools.print_tools import devprint as dpr

# own module imports
import AmideBB_code.calculation_methods as MC_cm
import AmideBB_code.local_atoms_finder as MC_laf
import AmideBB_code.neighbor_manager as MC_nm
import AmideBB_code.parameter_changer as MC_pc


def GM_adjust_map_core_raw(map_):
    """Makes the necessary changes to the 'raw' input read from core.txt.

    Is expected to not return anything - return value is not caught.

    The core.txt file is stored in map_.rawcore. It has not yet been
    parsed, just loaded into a dictionary. In this dictionary, each
    keyword is its own dictionary key. Most keywords can only occur once
    in the file - those have a list of the 'words' on the line as
    their value. The parameters that are allowed to occur more than once
    have a list as value, in which other lists appear - one for each
    line.

    The core.txt file has to be changed because the parameters of this
    map allow to change between models, each of which has their own
    files.

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    # adjusting the names of functional_group
    all_amino_acid_codes = [
        "ARG", "HIS", "LYS", "ASP", "GLU", "SER", "THR", "ASN", "GLN",
        "CYS", "GLY", "PRO", "ALA", "VAL", "ILE", "LEU", "MET", "PHE",
        "TYR", "TRP"
    ]

    extended = set(map_.run_pars.include_protein_residues)
    extended.discard("None")
    if len(extended) > 0:
        extended = list(extended)
        all_amino_acid_codes += extended
    map_.amino_acid_codes = set(all_amino_acid_codes)

    amino_acids_joined = ",".join(all_amino_acid_codes)

    oldentry = map_.rawcore["functional_group"]

    map_.rawcore["functional_group"] = [
        [
            word.replace("anyprot", amino_acids_joined)
            for word in struct
        ] for struct in oldentry
    ]

    MC_pc.adjust_map_core_raw(map_)


def GM_adjust_oscillators(map_, system, oscillator_list):
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
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator_list : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
        All oscillators belonging to a single struct of this map.

    Returns
    -------
    oscillator_list : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
        All oscillators belonging to a single struct of this map.
    """

    # Sort oscillators into the correct order
    oscillator_list = MC_pc.oscillator_sorter(map_, system, oscillator_list)

    # tell each oscillator what/who it's neighbors are.
    # N term is first, C term is last
    for oscillator in oscillator_list:
        oscillator.NtermNB = None
        oscillator.CtermNB = None
    # used ats order:    res0{C O CA} res1{N H CA} ({N CD CA} for prepro)
    for Nosc in oscillator_list:
        for Cosc in oscillator_list:
            if Nosc.used_atoms[5] == Cosc.used_atoms[2]:
                Nosc.CtermNB = Cosc
                Cosc.NtermNB = Nosc
                break  # Nosc can at most have a single Cterm neighbour

    return oscillator_list


def GM_filter_oscillators(map_, system, oscillator_list):
    """Filter through the found oscillators based on the black- and
    whitelist settings.

    For this map specific, we just use the code provided by GM_dmf, but
    we use this custom function to intercept the results from the
    default version - we need to see whether the selected oscillators
    have any neighbours that are not in the selection.

    Reason for this is the nearest-neighbour correction to the
    frequency. This correction needs to know the positions of the atoms
    of the neighbouring oscillator, which are not updated/generated
    for oscillators that are not within system.oscillators.

    We notice those oscillators, so we can update them manually each
    frame, so the positions are available, up-to-date, and thus correct.

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator_list : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
        All oscillators belonging to this map.

    Returns
    -------
    filtered_oscs : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
        All oscillators belonging to a single struct of this map.
    """

    filterfunc = GM_dmf.get_filter_oscillators()
    filtered_oscs = filterfunc(map_, system, oscillator_list)

    CtermNBs = {osc.CtermNB for osc in filtered_oscs}
    NtermNBs = {osc.NtermNB for osc in filtered_oscs}

    filtered = set(filtered_oscs)
    # a group on a chain end has no NB (hence 'none') so we need to remove
    # that one too
    map_.non_filtered_oscs = (CtermNBs | NtermNBs) - filtered - {None}

    return filtered_oscs


# A place to do further initialization if a map requires it. Think of
# things like building further lookup tables, for instance.
# (for AmideBB - find neighbours!)
def GM_post_init(map_, system):
    """Do some final initializations that need to happen before the
    calculation starts.

    Checks include:
    - comparing run_pars of this map to that of AmideSC, if the latter is
      present and active
    - initializing the prepro properties/files
    - Assigning the correct functions based on the parameter choices
    - Finding and assigning the neighbours of each group
    - Identifying all atoms local to each oscillator.

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    """

    # verify that both dipole maps (if applicable) have the same map choices
    rps = map_.run_pars
    main_runpars = map_.run_pars.main_run_pars
    # is other map present?
    if "AmideSC" in main_runpars.requested_mapdict.keys():
        amSC_rps = main_runpars.requested_mapdict["AmideSC"].run_pars
        if (  # the maps do not match, and they're not allowed to mismatch.
            amSC_rps.frequency_map_choice != rps.frequency_map_choice
            and not rps.allow_map_mismatch
        ):
            GM_pt.Printer.warning(
                "Warning! The current calculation makes use of both the "
                "AmideBB and AmideSC maps, but they make use of different "
                "frequency maps. For most physical applications, this does "
                "not make sense. If you are absolutely sure that you want "
                "the two maps to have different methods, make sure to set "
                "AmideBB.allow_map_mismatch to true. When in doubt, "
                "consult the README.",
                "map_AmideBB_2", True
            )
        if (  # the maps do not match, and they're not allowed to mismatch.
            amSC_rps.dipole_map_choice != rps.dipole_map_choice
            and not rps.allow_map_mismatch
        ):
            GM_pt.Printer.warning(
                "Warning! The current calculation makes use of both the "
                "AmideBB and AmideSC maps, but they make use of different "
                "dipole maps. For most physical applications, this does "
                "not make sense. If you are absolutely sure that you want "
                "the two maps to have different methods, make sure to set "
                "AmideBB.allow_map_mismatch to true. When in doubt, "
                "consult the README.",
                "map_AmideBB_2", True
            )
        if (  # the maps do not match, and they're not allowed to mismatch.
            amSC_rps.legacy_mode != rps.legacy_mode
            and not rps.allow_map_mismatch
        ):
            GM_pt.Printer.warning(
                "Warning! The current calculation makes use of both the "
                "AmideBB and AmideSC maps, but they try to emulate different "
                "versions. For most physical applications, this does "
                "not make sense. If you are absolutely sure that you want "
                "the two maps to follow different methods, make sure to set "
                "AmideBB.allow_map_mismatch to true. When in doubt, "
                "consult the README.",
                "map_AmideBB_2", True
            )

    # Initialize the prepro data structures (those that GMAP did for
    # non-prepro groups)
    MC_pc.initialize_prepro_properties(map_)

    # assign correct dipole function
    if map_.run_pars.dipole_map_choice == "Torii":
        map_.code.GM_calculate_dipole = MC_cm.calc_dipole_Torii
        map_.core.dipole_gas_phase = np.float32(map_.core.dipole_gas_phase)
        map_.core.dipole_Torii_angle = np.float32(
            1 / np.tan(GM_con.deg2rad * map_.run_pars.Torii_dipole_angle))
    else:
        map_.code.GM_calculate_dipole = MC_cm.calc_dipole_Jansen

    if map_.run_pars.legacy_mode == "AIM":
        map_.code.GM_get_position_DMF = map_.code.GM_get_position
        map_.code.GM_get_position = MC_cm.get_position

    # now, knowing neighbors, we can determine the local atoms.
    oscillator_list = system.oscillators_ordered["AmideBB"]
    MC_laf.find_local_atoms(map_, system, oscillator_list)

    MC_nm.read_maps(map_)
    MC_cm.determine_maps(oscillator_list, map_, system)

    if "TrEsp" in main_runpars.requested_pairmapdict.keys():
        trespmap = main_runpars.requested_pairmapdict["TrEsp"]
        map_.rawcore["TrEsp.charges_filename"] = ["TrEsp_gen.txt"]
        map_.core.TrEsp_gen_charges = trespmap.code.get_charges(trespmap, map_)
        map_.rawcore["TrEsp.charges_filename"] = ["TrEsp_pro.txt"]
        map_.core.TrEsp_pro_charges = trespmap.code.get_charges(trespmap, map_)

    if not map_.success:
        GM_pt.Printer.warning(
            "An issue occurred while initializing the AmideBB map stored at "
            f"{map_.directory}. Please first try restarting, then "
            "reinstalling, then contacting the map developer, as this map "
            "cannot be used like this. See the error above for more "
            "information. Quitting!",
            "map_AmideBB_0", True
        )

    # Interpret user choice for shift_base and shift_label
    map_.citerefs_mapkey = set()
    for parname in ("base", "label"):
        choice = getattr(map_.run_pars, "shift_" + parname)
        if choice in ("C12", "C12_O16", "natural"):
            setattr(map_.run_pars, "shift_" + parname, 0.0)
        elif choice in ("C13", "C13_O16"):
            setattr(map_.run_pars, "shift_" + parname, -45.0)
            map_.citerefs_mapkey.add("C13labelshift")
        elif choice in ("C13_O18"):
            setattr(map_.run_pars, "shift_" + parname, -59.6)
            map_.citerefs_mapkey.add("C13O18labelshift")
        else:
            try:
                setattr(map_.run_pars, "shift_" + parname, float(choice))
            except Exception as ex:
                GM_pt.Printer.warning(
                    "\nDid not recognise choice for the parameter "
                    f"AmideBB.shift_{parname}. Please make sure you either "
                    "chose a valid name, or you gave a valid decimal number.",
                    "map_AmideBB_5",
                    True, ex, GM_ex.GmapValueError
                )
    map_.citerefs_mapkey = list(map_.citerefs_mapkey)

    # Interpret user choice for labels
    choice = map_.run_pars.labels
    if choice[0] == "None":
        map_.labels = set()
    elif len(choice) < 2:
        GM_pt.Printer.warning(
            "\nInvalid number of arguments provided for the parameter "
            "AmideBB.labels. Please make sure you both provide a mode of "
            "selecting, and a choice for that mode.",
            "map_AmideBB_6", True
        )
    elif choice[0] == "resnums":
        amideoscs = [
            osc.resnums[0] for osc in system.oscillators_ordered[map_.name]]
        map_.labels = set(map_.Core.allow_ranges(
            choice[1:], max(amideoscs)))
        if len(map_.labels - set(amideoscs)) > 0:
            GM_pt.Printer.warning(
                "\nInvalid residues chosen using the parameter "
                "AmideBB.labels. Please make sure all residue numbers provided"
                " are in fact backbone amide groups.",
                "map_AmideBB_6", True
            )
    elif choice[0] == "resnames":
        choiceset = set(choice[1:])
        if len(choiceset - map_.amino_acid_codes) > 0:
            GM_pt.Printer.warning(
                "\nInvalid residues chosen using the parameter "
                "AmideBB.labels. Please make sure all residue names provided "
                "are valid 3-letter amino acid codes.",
                "map_AmideBB_6", True
            )
        map_.labels = set([
            osc.resnums[0]
            for osc in system.oscillators_ordered[map_.name]
            if osc.resnames[0] in choiceset
        ])
    else:
        GM_pt.Printer.warning(
            "\nInvalid choice of mode made for the parameter AmideBB.labels. "
            "The choice can either be 'None', or a mode listed in the README "
            "along with a specific choice for that mode.",
            "map_AmideBB_6", True
        )


def GM_pre_frame(map_, system):
    """Do the things that need to happen in preparation for the next
    frame.

    We just need to update the oscillators that are not requested for
    calculations themselves, but next to oscillators that are. See
    the docstring of GM_filter_oscillators for more info.

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    """

    for oscillator in map_.non_filtered_oscs:
        oscillator.frame_update(system)


def GM_str_osc(map_, system, oscillator):
    """Explains how an oscillator should be printed.

    Example print: 'binding the residues GLY36 and LYS37'

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the string is required.

    Returns
    -------
    string : str
        The string that should be printed.
    """

    at0 = oscillator.used_atoms[0]
    at3 = oscillator.used_atoms[3]
    return (
        # example: binding the residues GLY36 and LYS37
        f"binding the residues {system.resnames[at0]}{system.resnums[at0]}"
        f" and {system.resnames[at3]}{system.resnums[at3]}"
    )


def CP_TrEsp_get_charges(map_, system, osc):
    if osc.resnames[1] == "PRO":
        return map_.core.TrEsp_pro_charges
    else:
        return map_.core.TrEsp_gen_charges


def GM_calculate_frequency(map_, system, osc):
    """Calculates the oscillating frequency for a given oscillator

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the frequency is required.

    Returns
    -------
    freq : float
        The frequency calculated for this oscillator this frame.
    """

    if osc.resnames[1] == "PRO":
        gasfreq = map_.core.frequency_gas_phase_prepro
        freqarr = map_.core.frequency_data_array_linear_prepro
    else:
        gasfreq = map_.core.frequency_gas_phase
        freqarr = map_.core.frequency_data_array_linear

    freq = gasfreq + np.sum(np.multiply(osc.VEGout, freqarr))

    if (
        map_.run_pars.frequency_map_choice != "Tokmakoff"
        and map_.run_pars.consider_nearest_neighbours
    ):
        freq += MC_cm.neighbor_influence(map_, system, osc)

    # paper says D2O = 0.791 * H2O + 340 -> inverting this gives the below.
    if map_.run_pars.solvent == "H2O":
        freq = (freq - 340) / 0.791

    if osc.resnums[0] in map_.labels:
        freq += map_.run_pars.shift_label
    else:
        freq += map_.run_pars.shift_base

    return freq


def GM_calculate_raman(map_, system, osc):
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

    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)
    osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
        The specific oscillator for which the transformation is required.

    Returns
    -------
    raman_tensor : `np.ndarray`
        The raman tensor calculated for this oscillator this frame.
    """

    # the rotation matrix is available as long as the map specifies
    # estatic_choice to be E or G (which is the case here). It is made
    # available immediately at the beginning of the frame.
    COvec = osc.rotation_matrix[0, :]
    CNvec = osc.rotation_matrix[1, :]
    Zvec = osc.rotation_matrix[2, :]

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


def GM_report_references(map_, system):
    """Returns all references that should be reported for this map.

    This function does not have to account for which outputs are
    actually requested from the program - the text in the reporttext
    field in the references.bib file already does that. It indicates
    for which methods it should be reported, and with which text.

    If this function is absent from a main.py, map_.references will be
    returned in it's entirety. The purpose of this function is to
    return a selection/subset of that dictionary, instead.

    In the case of this mapping, there are different methods for
    computing the different properties of the system, so we only want
    to send those of the selected mapping through, and leave the rest.

    Parameters
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.Map`
        The object that stores everything the program currently knows
        about this map.
    system : :class:`~GMAP.src.tools.system_reader.System`
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)

    Returns
    -------
    references_dict : dict
        This dict should be a slice/part of the full map_.references
        dict. Therefore, an explanation of the map_.references dict:

        The keys in this dictionary are the separate keys listed in the
        reference.bib file's 'mapkey' field. If the reference has
        multiple keys in that field, it will occur multiple times in the
        dictionary, once for each key.

        Associated with each key is a list of
        :class:`~GMAP.src.tools.reference_handler.Reference` objects,
        each of which corresponds to a single entry in the .bib file.
    """

    report_these = []

    # This map has a whole bunch of references stored, but not (nearly) all
    # are actually used in a single calculation... Find those that are.
    report_these.append("RamanAmide")
    report_these.extend(map_.citerefs_mapkey)

    # Report the paper used for converting from D2O to H2O
    if map_.run_pars.solvent == "H2O":
        report_these.append("H20conv")

    # Report the paper used for converting from D2O to H2O
    if map_.run_pars.solvent == "H2O":
        report_these.append("H20conv")

    # do we have any pros?
    pro_present = any(
        osc.resnames[1] == "PRO"
        for osc in system.oscillators_ordered["AmideBB"]
    )
    gen_present = not all(
        osc.resnames[1] == "PRO"
        for osc in system.oscillators_ordered["AmideBB"]
    )

    # freq map used:
    if gen_present:
        report_these.append(f"Emap{map_.run_pars.frequency_map_choice}Gen")
    if pro_present:
        report_these.append(f"Emap{map_.run_pars.frequency_map_choice}Pro")

    report_dict = {key: map_.references[key] for key in report_these}

    # dip map used:
    # in order to have the DipDip coupling map correctly understand which
    # references should be cited, we add them to the correct mapkey entry
    # in the dict.
    report_dict["CP_DipDip"] = []
    if map_.run_pars.dipole_map_choice == "Torii":
        report_dict["CP_DipDip"].extend(map_.references["DmapTorii"])
    else:
        if gen_present:
            report_dict["CP_DipDip"].extend(map_.references["DmapJansenGen"])
        if pro_present:
            report_dict["CP_DipDip"].extend(map_.references["DmapJansenPro"])

    # select the actual references for the chosen keys
    return report_dict
