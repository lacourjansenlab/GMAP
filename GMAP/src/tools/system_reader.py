"""
Deals with the MD system.

Contains tools for storing and navigating all the MD files data.

Classes
-------
System
    Stores all information on the MD system and objects therein. Knows
    almost everything (partially through complex attributes).
Residues
    Stores some residue-level information from the MD system.
Oscillator
    Stores all information on a single oscillator.

Functions
---------
gen_universe
    Calls MDAanalysis.Universe on the supplied files and catches errors.
check_box_rightangled
    Checks whether the supplied universe has only right angles.
check_box_charge
    Checks whether the supplied universe has neutral charge.
"""


# import sys

# 3rd party imports
import MDAnalysis as MDA
import numpy as np

# local imports
import GMAP.src.tools.clib_loader as GM_cl
import GMAP.src.tools.default_map_functions as GM_dmf
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.parameter_parser as GM_pp
import GMAP.src.tools.print_tools as GM_pt


class System:
    """Stores all information on the MD system and objects therein

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.

    Attributes
    ----------
    universe : `MDAnalysis.Universe`
        The universe that is analyzed this run.
    atnums : `np.ndarray`
        A 1D array of length self.natoms storing the atom indices.
        First atom is numbered 0, every next index is 1 larger than the
        previous one. Counting never resets.
    atnames : `np.ndarray`
        A 1D array of length self.natoms storing the name of each atom.
    resnums : `np.ndarray`
        A 1D array of length self.natoms storing the number of the
        residue each atom belongs to. First residue is numbered 0, each
        subsequent residue gets an index 1 larger than the previous one.
        Counting never resets.
    resnames : `np.ndarray`
        A 1D array of length self.natoms storing the name of the residue
        each atom belongs to.
    positions : `np.ndarray`
        A 2D array of shape [self.natoms, 3] storing the position of
        each atom in the MD system.
    masses : `np.ndarray`
        A 1D array of length self.natoms storing the mass of each atom.
    charges : `np.ndarray`
        A 1D array of length self.natoms storing the charge of each
        atom. This is the charge as used by the MD system, not as a
        certain map might need it.
    types : `np.ndarray`
        A 1D array of length self.natoms storing the type of each atom.
        A type is often dependent on the forcefield used - each element
        can have multiple types associated with it. In the MD
        calculation, each type has certain force field parameters
        associated with it.
    segids : `np.ndarray`
        A 1D array of length self.natoms storing the name of the segment
        each atom belongs to.
    natoms : `np.int32`
        The amount of atoms found in the MD trajectory.
    nres : `np.int32`
        The amount of residues found in the MD trajectory.
    boxdims : `np.ndarray`
        The length of the 3 vectors defining the MD simulation box
        (its PBC). These are the first 3 entries returned by
        MDA.Universe.dimensions.
    halfbox : `np.ndarray`
        Same as boxdims, but each value is divided by 2.
    angles : `np.ndarray`
        The angles between the three vectors defining the MD simulation
        box (its PBC). These are the last 3 entries returned by
        MDA.Universe.dimensions.
    boxvects : `np.ndarray`
        The vectors defining the MD box. boxvects.shape == (3, 3).
        boxvects[i] returns one of the three vectors.
        The result of MDA.lib.mdamath.triclinic_vectors(
        self.universe.dimensions)
    boxvects_inv : `np.ndarray`
        The inverse of the rotation matrix self.boxvects.
    safesphere : float
        The radius of the sphere in which distances can be calculated
        accurately. If the length of any vector exceeds this size, there
        is a chance that vector is not actually the shortest available.
    residues : :class:`~GMAP.src.tools.system_reader.Residues`
        This class contains information on a per-residue basis instead
        of a per-atom basis like this class does.
    rightangled : bool
        Whether self.angles only contains 90 degree angles.
    neutral : bool
        Whether the total charge of the MD system (the sum of
        self.charges) equals 0. The precision used can be changed using
        the parameter
        :ref:`neutral_charge_threshold<UserGuide_page_parameter_overview>`.
    oscillators : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
        All oscillators that were found in the MD system. These are the
        ones calculations will be performed on.
    influencers_atix : list of int
        The indices of all atoms that should be considered influencers.
    nosc : int
        The amount of oscillators present in the system.
    oscillators_ordered : dict of str: list of \
        :class:`~GMAP.src.tools.system_reader.Oscillator` pairs
        All oscillators, but grouped by the map they belong to.
    oscillators_ordered_ix : dict of str: list of int pairs
        Same as oscillators_ordered, but only listing oscillator indices
        instead of oscillator objects.
    oscillators_ordered_coup : dict of str: list of \
        :class:`~GMAP.src.tools.system_reader.Oscillator` pairs
        All oscillators, but grouped by the coupling map they belong to.
        This structure is intended for use by prep-methods of coupling
        maps, as it is a simple overview of all oscillators that the
        coupling map will treat
    oscillators_ordered_coup_ix : dict of str: list of int pairs
        Same as oscillators_ordered_coup, but only listing oscillator indices
        instead of oscillator objects.
    """

    def __init__(self, run_pars, read_only=False):
        self.universe = gen_universe(run_pars)  # MDA universe creation
        # Extract numpy arrays from MDA universe
        self.set_properties(read_only=read_only)
        # see if box has correct size and charge
        self.basic_boxchecks(run_pars)

        # we only want to know basic parameters of the MD system, and don't
        # want to spend time/effort/resources looking for oscillators.
        if read_only:
            return

        self.find_influencers(run_pars)  # Find all influencing atoms

        # detect all valid oscillators and introduce them to the maps
        self.find_oscillators(run_pars)

        # sort all oscillators, make usable lookup-tables. Also, determine
        # correct coupling map for each oscillator pair (and build tables
        # for the pairs, too)
        self.order_oscillators_singles(run_pars)

        for oscillator in self.oscillators:
            oscillator.frame_update(self)

        # It would make sense to, just as with influencers, also report all
        # findings to the user (through printing to command line and log file).
        # However, we're not going to do that, as maps might need to do
        # more investigating on their oscillators to know what they are. So,
        # we want to give maps the time to do that, and only report on the
        # system once they're done! This means reporting happens after the
        # post-init call to each map!

    def basic_boxchecks(self, run_pars):
        """Performs the first basic analyses on the provided universe.

        Doesn't return anything - if anything is amiss, it will just
        throw a fatal error.

        Parameters
        ----------
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        """

        self.rightangled = check_box_rightangled(self.universe)
        if self.rightangled:
            if run_pars.treat_box == "auto":
                run_pars.treat_box = "orthorhombic"
        else:
            if run_pars.treat_box == "auto":
                run_pars.treat_box = "triclinic"

        self.neutral = check_box_charge(run_pars, self.charges)

        try:
            self.universe.bonds
        except MDA.exceptions.NoDataError as ex:
            # there are no bonds, but we don't need them, either.
            if not run_pars.detected_requires_bonds:
                pass
            else:
                GM_pt.Printer.warning(
                    "\nSubmitted MD system does not contain any "
                    "information on "
                    "bonds, but the requested maps do require this. Either "
                    "choose a different map, or provide a different input.",
                    "MD_SU_5", True, exception=ex,
                    GMAPerrclass=GM_ex.GmapParameterError
                )

    # TO DO inside!
    def set_properties(self, read_only=False):
        """Sets the basic properties of the system.

        Extracts them from self.universe.atoms, and saves them in self.
        """

        self.atnums = self.universe.atoms.ix
        self.atnames = self.universe.atoms.names
        self.resnums = self.universe.atoms.resnums
        self.resnames = self.universe.atoms.resnames
        self.positions = self.universe.atoms.positions.astype('float32')
        self.masses = self.universe.atoms.masses.astype('float32')
        self.charges = self.universe.atoms.charges.astype('float32')
        self.types = self.universe.atoms.types
        self.segids = self.universe.atoms.segids

        self.natoms = np.int32(self.resnums.shape[0])
        self.dt = self.universe.trajectory.dt

        # make sure resums always follow AIM-convention (regardless of MD input
        # used)
        self.abs_resnums()

        self.nres = np.int32(self.resnums[-1] + 1)

        self.determine_box()

        # analogue of AIMs ResidueFinder and IXFinder
        self.residues = Residues(self)

        # Next is for c calc, which we won't run this round.
        if read_only:
            return

        # C array preparation
        self.positions_c = np.ctypeslib.as_ctypes(np.ravel(self.positions))
        self.masses_c = np.ctypeslib.as_ctypes(self.masses)
        self.charges_c = np.ctypeslib.as_ctypes(self.charges)
        self.positions_box = np.zeros_like(self.positions)
        self.positions_box_c = np.ctypeslib.as_ctypes(np.ravel(
            self.positions_box))
        # calculate the box position of each atom
        clib = GM_cl.VEG_CLib()
        clib.positions_to_box(self)

    def abs_resnums(self):
        """Renumbers residue numbers so they start at 0, and never reset
        """

        prevresnum = -1
        writeresnum = -1
        prevsegid = -1  # definitely different from the segid strings
        # MDA format overview states 'segids' is always available
        segids = self.universe.atoms.segids
        for ix, atomnum in enumerate(self.atnums):
            if atomnum != ix:
                # yes, we could just force atomnum to match ix. But if this
                # MD software does this differently, it might very well do
                # other things differently as well, so please, check that!
                GM_pt.Printer.warning(
                    f"\nThe atom number of the atom at position {ix} "
                    "does "
                    "not match its position in the list.",
                    "MD_SU_4", True, GMAPerrclass=GM_ex.GmapMDFileError
                )
            resnum = self.resnums[atomnum]
            segid = segids[atomnum]
            if resnum != prevresnum or segid != prevsegid:
                writeresnum += 1
            self.resnums[atomnum] = writeresnum
            prevresnum = resnum
            prevsegid = segid

    def determine_box(self):
        """Find out what the simulation box looks like."""
        self.boxdims = self.universe.dimensions[:3].astype('float32')
        self.halfbox = self.boxdims/2
        self.halfbox = self.halfbox.astype('float32')
        self.angles = self.universe.dimensions[3:].astype('float32')
        self.boxvects = MDA.lib.mdamath.triclinic_vectors(
            self.universe.dimensions
        ).astype('float32')
        self.safesphere = 0.5 * self.boxvects.diagonal().min()
        self.boxvects_inv = np.linalg.inv(self.boxvects).astype('float32')

        self.boxvects_c = np.ctypeslib.as_ctypes(np.ravel(self.boxvects))
        self.boxvects_inv_c = np.ctypeslib.as_ctypes(np.ravel(
            self.boxvects_inv))

        self.boxdims_c = np.ctypeslib.as_ctypes(self.boxdims)
        self.halfbox_c = np.ctypeslib.as_ctypes(self.halfbox)

    def find_influencers(self, run_pars):
        """Find the indices of all atoms that are influencers

        Influencers are the atoms whose charge should be considered
        while calculating the VEG for a given point. This is a first
        guess, things like local-ix, spheresize and the like are not
        yet considered.

        Parameters
        ----------
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        """

        groupdict = {}
        groupdict["All"] = set(self.residues.resnames)
        groupdict["None"] = set("")
        for map_ in run_pars.requested_mapdict.values():
            # Here, allow maps to add their own custom definitions!
            all_map_influencers = map_.rawcore.get("influencer_group", [])
            for map_inflgroup in all_map_influencers:
                name = map_inflgroup[0]
                group_def = " ".join(map_inflgroup[1:])
                groupdict[name] = GM_pp.parse_influencerfile_line(
                    group_def, groupdict, map_.corepath
                )

        cb = GM_pt.Printer.colors.green_lc
        ct = GM_pt.Printer.colors.clear
        line = f"{cb}════{ct}"
        GM_pt.Printer.print(
            1, f"\n{line} Influencers {line}", detailed_instructions=[1])
        GM_pt.header(2, "Influencers", "doublebox")

        # names of residues or residue groups are given to specify infl.
        if isinstance(run_pars.influencers, list):
            choice = GM_pp.parse_influencer_par(" ".join(run_pars.influencers))
            choice = GM_pp.parse_influencerfile_line(
                choice, groupdict,
                "parameter file "
            )
            self.influencers_atix = self.residues.manage_influencers(choice)
            influencers_not_included = groupdict["All"] - choice
            if len(influencers_not_included) == 0:
                influencers_not_included.add("None")
            GM_pt.Printer.print(
                1,
                "Residue names included in influencers:\n  "
                + ", ".join(choice) +
                "\n\nResidue names NOT included in influencers:\n  "
                + ", ".join(influencers_not_included),
                wrap_preline="  "
            )

        # The MDA select_atoms functionality is used to define influencers.
        elif isinstance(run_pars.influencers, str):
            try:
                atgroup = self.universe.select_atoms(run_pars.influencers)
            except Exception as ex:
                GM_pt.Printer.warning(
                    "\nSome problem occured while selecting atoms for the "
                    "influencers",
                    "SU_NP_6", True, exception=ex
                )
            self.influencers_atix = atgroup.atoms.ix.tolist()

        # similar to the first, names of residues or residue groups are given.
        # however, this time, a separate file is used.
        else:  # must be a separate file
            choice = GM_pp.parse_influencerfile(
                run_pars.influencers, groupdict)
            if "choice" in choice:
                choice = choice["choice"]
            else:
                GM_pt.Printer.warning(
                    "\nWhen using a file to specify influencers, the final "
                    "choice of influencers must be given using the group "
                    "'choice'.",
                    "SU_NP_5", True, GMAPerrclass=GM_ex.GmapFileSyntaxError
                )
            self.influencers_atix = self.residues.manage_influencers(choice)
            influencers_not_included = groupdict["All"] - choice
            if len(influencers_not_included) == 0:
                influencers_not_included.add("None")
            GM_pt.Printer.print(
                1,
                "Residue names included in influencers:\n  "
                + ", ".join(choice) +
                "\n\nResidue names NOT included in influencers:\n  "
                + ", ".join(influencers_not_included),
                wrap_preline="  "
            )

        # influencers list must be sorted
        self.influencers_atix.sort()

        # all kinds of influencer parameters
        atixprint = GM_pt.intlist_to_rangelist(
            self.influencers_atix, self.natoms
        )
        if len(atixprint[1]) == 0:
            atixprint[1].append("None")
        GM_pt.Printer.print(
            3,
            "\nAtoms included in influencers:\n  "
            + ", ".join(atixprint[0]) +
            "\n\nAtoms NOT included in influencers:\n  "
            + ", ".join(atixprint[1]),
            wrap_preline="  "
        )
        GM_pt.footer(2, "influencers", "doublebox")
        self.influencers_atix = np.asarray(
            self.influencers_atix, dtype=np.int32
        )
        self.n_influencers = np.shape(self.influencers_atix)[0]
        self.influencers_atix_c = np.ctypeslib.as_ctypes(self.influencers_atix)

    def find_oscillators(self, run_pars):
        """Finds all the oscillators in the MD system

        Before an oscillator is considered 'found', it has to match the
        following criteria:

        Firstly, an oscillator must have matching residue and atom names
        with the definition in the map.

        Secondly, an oscillator must have all the bonds specified by the
        map.

        Lastly, an oscillator must pass the final check by the map
        itself.

        Parameters
        ----------
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        """

        # If only single-residue oscillators:
        # - Double for-loop! For each residue in system, for each map
        #   (or each struct?)
        # - If the residue and map residue match, see if atnames match
        # - (If applicable) see if bonds match

        # However, if oscillator lies on multiple residues, the above does
        # not work. Instead:
        # - Triple for loop! For each residue in system, for each residue of
        #   each struct
        # - If the residue and map residue match, see if the atnames match
        # - For the bonds, see which residues they actually connect.

        # Find the oscillators as defined in the maps
        allgroups = []
        for map_ in run_pars.requested_mapdict.values():
            mapgroups = []
            for struct in map_.core.functional_group:
                mapgroups.extend(self.find_oscillators_perstruct(struct, map_))
            allgroups.append(mapgroups)

        # If none are found, report an error. GMAP cannot run if there are
        # no oscillators present.
        nosc = sum([len(oscillators) for oscillators in allgroups])
        if nosc == 0:
            GM_pt.Printer.warning(
                "\nNone of the requested oscillators could be found in the "
                "supplied MD system. Either change the choice for the "
                "parameter maps_to_use, or for the parameters topology_file "
                "and/or trajectory_file. Quitting!",
                "MD_SU_7", True,
                GMAPerrclass=GM_ex.GmapValueError
            )

        # feed the found oscillators to the maps, let them have a look
        # at them / edit. General, run-independent edits only.
        checked_oscillators = []
        # allgroups contains one item per Singles map. That item is a list
        # of oscillator objects.
        for oscillators in allgroups:
            if len(oscillators) == 0:
                continue
            map_ = oscillators[0].map  # determine to what map these belong
            # Provide oscillators of this map only to the map. Allow it to make
            # any changes it likes (remove/add duplicates, for example).
            # Important is that what happens here, should *always* happen.
            checked = map_.code.GM_adjust_oscillators(
                map_, self, oscillators
            )
            if checked:
                checked_oscillators.append(checked)

        nosc = sum([len(oscillators) for oscillators in checked_oscillators])
        if nosc == 0:
            GM_pt.Printer.warning(
                "\nNone of the requested oscillators could be found in the "
                "supplied MD system. Either change the choice for the "
                "parameter maps_to_use, or for the parameters topology_file "
                "and/or trajectory_file. Quitting!",
                "MD_SU_7", True,
                GMAPerrclass=GM_ex.GmapValueError
            )

        # Same as before, feed the oscillators belonging to a specific map to
        # that map. Here, run-dependent edits can be made. More specifically,
        # this is where a map applies the black-/whitelist choices from the
        # run input file.
        filtered_oscillators = []
        for oscillators in checked_oscillators:
            if len(oscillators) == 0:
                continue
            map_ = oscillators[0].map
            filtered = map_.code.GM_filter_oscillators(
                map_, self, oscillators
            )
            if filtered:
                filtered_oscillators.append(filtered)

        self.oscillators = [
            oscillator for oscillators in filtered_oscillators
            for oscillator in oscillators
        ]
        for oscix, oscillator in enumerate(self.oscillators):
            oscillator.oscix = oscix

        self.nosc = len(self.oscillators)
        if self.nosc == 0:
            GM_pt.Printer.warning(
                "\nNone of the requested oscillators could be found in the "
                "supplied MD system. Most likely, one of the criteria defined "
                "using either 'singles_whitelist' or 'singles_blacklist' is "
                "too strict. Please make sure the chosen criteria match the "
                "chosen MD files. Quitting!",
                "MD_SU_7", True,
                GMAPerrclass=GM_ex.GmapValueError
            )

    def find_oscillators_perstruct(self, struct, map_):
        """Finds all oscillators matching the given structure.

        Considers residue and atoms names, as well as bonds defined in
        the map.

        Parameters
        ----------
        struct : :class:`~GMAP.src.tools.map_reader.Structure`
            The structure template that will be matched.
        map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
            The map instance the structure belongs to.

        Returns
        -------
        all_oscillators : list of \
            :class:`~GMAP.src.tools.system_reader.Oscillator`
            All oscillators that were found matching the given
            structure.
        """

        if len(struct.residues) == 1:
            # find all oscillators that conform to the atom/residue names
            all_oscillators = self.find_oscillators_residue(struct.residues[0])

            # only keep the oscillators which confirm to bond rules
            all_oscillators = [
                osc for osc in all_oscillators if all(
                    self.confirm_internal_bond(osc, bond)
                    for bond in struct.bonds
                )
            ]
        else:
            # find all groups of atoms that conform to the per-residue
            # atom/residue names
            all_oscillators = [
                self.find_oscillators_residue(residue)
                for residue in struct.residues
            ]
            # stick the different residues together, using the bonds.
            all_oscillators = self.match_residues(all_oscillators, struct)

        all_oscillators = [
            Oscillator(self, osc, map_) for osc in all_oscillators]
        return all_oscillators

    def find_oscillators_residue(self, residue):
        """Finds all oscillators matching the given residue template.

        Only considers residue and atoms names.

        Parameters
        ----------
        residue : :class:`~GMAP.src.tools.map_reader.Residue`
            The desired residue template for which the MD system will be
            searched.

        Returns
        -------
        oscillators : list of list of int
            The list of all oscillators found, matching the template.
            Each oscillator is a list of atnums of the atoms it consists
            of.
        """
        oscillators = []

        # loop over all residues in MD system
        for resnum, resname in enumerate(self.residues.resnames):
            # if resname of this MD residue matches that what we're looking for
            if resname in residue.resnames:
                oscillator = self.find_oscillators_atoms(resnum, residue.atoms)
                if oscillator:
                    oscillators.append(oscillator)

        return oscillators

    def find_oscillators_atoms(self, resnum, residue_atoms):
        """See if the found residue indeed matches the desired template

        Parameters
        ----------
        resnum : int
            The number of the MD residue to compare to the template
        residue_atoms: list of list of str
            The template for the residue - for each relevant position,
            a list of allowed atom names.

        Returns
        -------
        atoms_ix : None or list of int
            The MD atom indices (atnums) of the residue that match the
            template. If this residue is not a match, None is returned
            instead.
        """

        atoms_per_oscillator = len(residue_atoms)
        atoms_ix = [0] * atoms_per_oscillator
        atoms_found = [False] * atoms_per_oscillator

        # See if this residue also contains all atoms we're looking for

        # loop over all atoms in candidate MD residue
        for atom_ix in range(
            self.residues.first_ix[resnum],
            self.residues.last_ix[resnum] + 1
        ):
            atname = self.atnames[atom_ix]
            # loop over all atoms we're looking for
            for local_ix, atom_names in enumerate(residue_atoms):
                if atname in atom_names:
                    # if an atom of this name has already been found, see if
                    # more than one is needed.
                    if atoms_found[local_ix]:
                        continue
                    atoms_ix[local_ix] = atom_ix
                    atoms_found[local_ix] = True
                    break

        if all(atoms_found):
            return atoms_ix
        else:
            return None

    def confirm_internal_bond(self, oscillator, bond):
        """Check whether the given bond exists in the given oscillator

        Parameters
        ----------
        oscillator : list of int
            The system-indices of the atoms that make up the oscillator.
        bond : tup of int
            The oscillator-indices of the two atoms that should make up
            the bond.

        Returns
        -------
        is_bond : bool
            Whether the requested bond exists in the given group
        """

        ix1 = oscillator[bond[0]]
        ix2 = oscillator[bond[1]]
        return self.confirm_bond(ix1, ix2)

    def confirm_bond(self, ix1, ix2):
        """Check whether the given atoms are bonded

        Parameters
        ----------
        ix1, ix2 : int
            The system-indices of the two atoms to check

        Returns
        -------
        is_bond : bool
            Whether the two atoms are bonded
        """

        return (
            self.universe.atoms[ix1] in
            self.universe.atoms[ix2].bonded_atoms
        )

    def match_residues(self, all_oscillators, struct):
        """Finds the full oscillator from component residues

        Some oscillators live fully inside a single residue, but others
        don't. If they dont, the atoms of multiple residues have to
        match, and those residues must be correctly bonded. This method
        enforces that second part. It receives all groups of atoms that
        conform to the per-residue selection (exactly like
        single-residue oscillators), and sees which are bonded
        correctly.

        As an example, imagine an oscillator spanning 3 residues, that
        occurs 10 times in the system. Most likely, there will be 10
        candidates that look like the first residue of the oscillator,
        10 that look like the second, and 10 that look like the third.
        This function then checks which of the matches for the first
        residue is bonded to which of the matches for the second, and to
        those of the third.

        Parameters
        ----------
        all_oscillators : list of list of list of int
            Contains all groups of atoms that are a match for each of
            the residues in the oscillator.
            A list(1) with an item for each of the residues. Each of
            those items is a list(2), containing all groups that are a
            candidate for this residue. Each group in list(2) is itself
            a list of the (system-) indices of the atoms that make up
            the group.
        struct : :class:`~GMAP.src.tools.map_reader.Structure`
            What the oscillator we're looking for looks like.

        Returns
        -------
        oscillators_to_do : list of list of int
            All groups of atoms that match the template structure. Each
            group of atoms is a list of system-indices of the atoms it
            contains.
        """

        nats_res0 = len(struct.indices_per_residue[0])
        nats_all = len(struct.indices)

        oscillators_passed = []
        oscillators_to_do = [
            osc + [0]*(nats_all - nats_res0) for osc in all_oscillators[0]
        ]
        atoms_found = [True] * nats_res0 + [False] * (nats_all - nats_res0)

        bonds_do_later = []
        bonds_to_do = struct.bonds

        # Loop through all the bonds
        while len(bonds_to_do) > 0:
            for bond in bonds_to_do:
                # If none of the atoms in the bond are in the established bit,
                # skip this bond for later.
                if not any(atoms_found[ix] for ix in bond):
                    bonds_do_later.append(bond)
                    continue

                # If all of the atoms in the bond are in the established bit,
                # confirm whether this residue still qualifies
                elif all(atoms_found[ix] for ix in bond):
                    for base_residue in oscillators_to_do:
                        if self.confirm_internal_bond(base_residue, bond):
                            oscillators_passed.append(base_residue[:])

                # If only one of the atoms in the bond are in the established
                # bit, see what residues should be attached.
                else:
                    # determine which of the atoms in the bond is the known one
                    if atoms_found[bond[0]]:
                        found_local_ix, new_local_ix = bond
                    else:
                        new_local_ix, found_local_ix = bond

                    for base_residue in oscillators_to_do:
                        oscillators_passed.extend(self.extend_oscillator(
                            found_local_ix, new_local_ix, base_residue, struct,
                            all_oscillators
                        ))
                    if oscillators_passed:
                        target_res = struct.indices[new_local_ix][0]
                        for index in struct.indices_per_residue[target_res]:
                            atoms_found[index] = True

                oscillators_to_do = oscillators_passed
                oscillators_passed = []

            bonds_to_do = bonds_do_later
            bonds_do_later = []

        return oscillators_to_do

    def extend_oscillator(
        self, found_local_ix, new_local_ix, base_residue, struct,
        all_oscillators
    ):
        """Add all residues that are correctly bonded.

        Parameters
        ----------
        found_local_ix : int
            The local index of the atom in the bond that we already
            have.
        new_local_ix : int
            The local index of the atom in the bond that we are still
            missing.
        base_residue : list of int
            The system indices of the group we're trying to extend
        struct : :class:`~GMAP.src.tools.map_reader.Structure`
            What the oscillator we're looking for looks like.
        all_oscillators : list of list of list of int
            Contains all groups of atoms that are a match for each of
            the residues in the oscillator.
            A list(1) with an item for each of the residues. Each of
            those items is a list(2), containing all groups that are a
            candidate for this residue. Each group in list(2) is itself
            a list of the (system-) indices of the atoms that make up
            the group.

        Returns
        -------
        outlist : list of list of int
            All new groups that follow out of base_residue.
            Each list of int is a group that matches the current bond.
            It is made of the base_residue, with a new residue's worth
            of atoms added on.
        """

        outlist = []

        found_ix = base_residue[found_local_ix]  # get global index
        found_bounds = self.universe.atoms[found_ix].bonded_atoms
        found_bounds = set([atom.ix for atom in found_bounds])

        # convert struct-ix to residue-ix
        target_residue, target_local_ix = struct.indices[new_local_ix]

        # check all residues that could be added on
        for new_residue in all_oscillators[target_residue]:
            new_ix = new_residue[target_local_ix]  # get global index
            # if it is attached, add it
            if new_ix in found_bounds:
                new_osc = base_residue[:]

                # write the global indices of added piece to original
                # oscillator
                for index in struct.indices_per_residue[target_residue]:
                    new_osc[index] = new_residue[struct.indices[index][1]]
                outlist.append(new_osc)
        return outlist

    def order_oscillators_singles(self, run_pars):
        """Sort all present oscillators by their map.

        Parameters
        ----------
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        """

        # for each singles map, determine which oscillators are treated
        # by that map (no treated oscillators - not in the dict)
        self.oscillators_ordered = {}
        self.oscillators_ordered_ix = {}
        for oscix, oscillator in enumerate(self.oscillators):
            setattr(oscillator, "oscix", oscix)
            mapname = oscillator.map.name
            if mapname not in self.oscillators_ordered:
                self.oscillators_ordered[mapname] = [oscillator]
                self.oscillators_ordered_ix[mapname] = [oscix]
            else:
                self.oscillators_ordered[mapname].append(oscillator)
                self.oscillators_ordered_ix[mapname].append(oscix)

    def order_oscillators_pairs(self, run_pars):
        """Sort all present oscillators by their map.

        Parameters
        ----------
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        """

        # for each oscillator pair, determine which coupling map should
        # treat it. That coupling map has the chance to change it.
        coup_v_allpair = {}
        for oscix1, osc1 in enumerate(self.oscillators):
            for oscix2 in range(oscix1 + 1, self.nosc):
                osc2 = self.oscillators[oscix2]
                base_coupmap = None
                req_coupmap = run_pars.pair_v_coupling_dict[
                    (osc1.map.name, osc2.map.name)]
                all_req_maps = [req_coupmap]
                while base_coupmap != req_coupmap and req_coupmap is not None:
                    base_coupmap = req_coupmap
                    # ask the current map which map should actually be used
                    coupmap = run_pars.requested_pairmapdict[base_coupmap]
                    req_coupmap = coupmap.code.GM_change_coup_type(
                        coupmap, self, oscix1, osc1, oscix2, osc2)
                    if (
                        req_coupmap in all_req_maps
                        and req_coupmap != all_req_maps[-1]
                    ):
                        all_req_maps.append(req_coupmap)
                        mapseq = ", ".join(all_req_maps)
                        GM_pt.Printer.warning(
                            "\nAn issue occurred when determining which "
                            "coupling method should be used to couple the "
                            "following two oscillators:\n"
                            f"{osc1}\n{osc2}\nThe user requested to use "
                            f"{all_req_maps[0]}, which started the following "
                            f"circular chain: {mapseq}.\nThis might mean the "
                            "choice of coupling was unsuitable, or there is "
                            "a misstake in one of these maps.",
                            "MD_SU_6", True,
                            GMAPerrclass=GM_ex.GmapParameterError
                        )
                    else:
                        all_req_maps.append(req_coupmap)
                if req_coupmap in coup_v_allpair:
                    coup_v_allpair[req_coupmap].append((oscix1, oscix2))
                else:
                    coup_v_allpair[req_coupmap] = [(oscix1, oscix2)]

        # if any pairs shouln't be coupled, remove the 'none' choice from the
        # dict.
        try:
            del coup_v_allpair[None]
        except Exception:
            pass

        # save each list of pairs to the map that should be coupling it.
        for coupmapname, pairlist in coup_v_allpair.items():
            coupmap = run_pars.requested_pairmapdict[coupmapname]
            coupmap.allpairs = np.array(pairlist, dtype="int32")

        # for each coupling map, determine which oscillators are coupled
        # by that map (no coupled oscillators - not in the dict)
        self.oscillators_ordered_coup = {}
        self.oscillators_ordered_coup_ix = {}
        for oscix, oscillator in enumerate(self.oscillators):
            for coupmap, pairs in coup_v_allpair.items():
                for pair in pairs:
                    if oscix in pair:
                        if coupmap not in self.oscillators_ordered_coup:
                            self.oscillators_ordered_coup[coupmap] = [
                                oscillator]
                            self.oscillators_ordered_coup_ix[coupmap] = [oscix]
                        else:
                            self.oscillators_ordered_coup[coupmap].append(
                                oscillator)
                            self.oscillators_ordered_coup_ix[coupmap].append(
                                oscix)
                        # if this oscillator is part of this map, no need to
                        # check the other pairs!
                        break
        for coupmapname, oscillators in self.oscillators_ordered_coup.items():
            coupmap = run_pars.requested_pairmapdict[coupmapname]
            coupmap.check_singles_2(run_pars, oscillators)

    def update_properties(self, run_pars):
        """Reloads the frame-dependent properties of the system.

        This function is supposed to be called at the beginning of every
        frame to ensure that the properties stored inside are up to
        date.
        """

        printer = GM_pt.Printer

        printer.add_time(4, "positions and box:", "PosBox", "ms")
        self.positions = self.universe.atoms.positions.astype('float32')
        self.positions_c = np.ctypeslib.as_ctypes(np.ravel(self.positions))
        self.determine_box()
        printer.add_time(4, "Center of Mass:", "COM", "ms")

        # calculate the box position of each atom
        clib = GM_cl.VEG_CLib()
        clib.positions_to_box(self)

        self.residues.CoM_box = np.zeros((self.nres, 3), dtype="float32")
        self.residues.CoM_box_c = np.ctypeslib.as_ctypes(
            np.ravel(self.residues.CoM_box))
        clib.calc_CoM_box(self)  # fill CoM_c. Results are calculated in box c.

        if run_pars.treat_box == "orthorhombic":
            self.residues.CoM = np.zeros((self.nres, 3), dtype="float32")
            self.residues.CoM_c = np.ctypeslib.as_ctypes(
                np.ravel(self.residues.CoM))
            clib.CoM_frombox(self)

    def print_system(self, run_pars):
        """Reports what the MD system looks like - what oscillators were
        found

        Parameters
        ----------
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        """

        cb = GM_pt.Printer.colors.green_lc
        ct = GM_pt.Printer.colors.clear
        line = f"{cb}════{ct}"
        GM_pt.Printer.print(
            1, f"\n{line} MD system analysis {line}",
            detailed_instructions=[1])
        GM_pt.header(2, "MD system analysis", "doublebox")

        # reporting the amount of oscillators per oscillator type
        report_osctype = GM_dmf.get_report_system()  # generate function
        toprint = [
            report_osctype(map_, self)
            for map_ in run_pars.requested_mapdict.values()]

        # This should be printed if and only if verbose is set to 1.
        GM_pt.Printer.print(1, "\n".join(toprint), detailed_instructions=[1])

        # let each map decide how to report their oscillators.
        for mapname in self.oscillators_ordered.keys():
            map_ = run_pars.requested_mapdict[mapname]
            toprint = map_.code.GM_report_system(map_, self)
            GM_pt.Printer.print(2, toprint)

        GM_pt.footer(2, "MD system analysis", "doublebox")


class Residues:
    """Creates and stores information on the system on a per-residue
    basis

    The System class has a lot of information on a per-atom basis, this
    class has it on a per residue.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The class containing all the information on the system of the
        MD trajectory.

    Attributes
    ----------
    first_ix : np.ndarray
        An array as long as there are residues in the MD system, with
        dtype np.int32. For each residue, it stores the index of the
        first atom.
    last_ix : np.ndarray
        An array as long as there are residues in the MD system, with
        dtype np.int32. For each residue, it stores the index of the
        last atom.
    resnames : list of str
        A list as long as there are residues in the MD system. For each
        residue, it stores its residue name.
    influencer_names : set()
        All residue names that are considered influencers this run.
    influencer_ix : list of int
        The indices of all residues that are influencers.
    CoM : np.ndarray
        An array as long as there are residues in the MD system. For
        each residue, it stores its center of mass.
    """

    def __init__(self, system):
        self.find_markers(system)

    def find_markers(self, system):
        """Make lookup tables (len=nres) for basic residue-based
        properties.

        1D arrays are built with a length equal to the amount of
        residues in the system. For each residue, we save the index
        (atnum) of the first and last atom it consists of, as well as
        its name.
        Knowing where a residue starts/ends is very useful for further
        analysis of the MD system.

        Parameters
        ----------
        system : :class:`System`
            This object stores all important information about the MD
            system that will be analyzed.
        """

        self.first_ix = []
        self.resnames = []
        self.last_ix = []

        last_resnum = -1
        current_resnum = -1

        for atnum, resnum in enumerate(system.resnums):
            last_resnum = current_resnum
            current_resnum = resnum

            # We're only looking for when a new residue starts.
            if last_resnum == current_resnum:
                continue

            # now, we know we've just found a new residue
            if last_resnum != -1:
                self.last_ix.append(atnum - 1)
            self.resnames.append(system.resnames[atnum])
            self.first_ix.append(atnum)
        else:
            self.last_ix.append(atnum)

        self.first_ix = np.array(self.first_ix, dtype="int32")
        self.last_ix = np.array(self.last_ix, dtype="int32")
        self.first_ix_c = np.ctypeslib.as_ctypes(self.first_ix)
        self.last_ix_c = np.ctypeslib.as_ctypes(self.last_ix)

    def manage_influencers(self, influencerset):
        """Return all atom indices with one of the given residue names

        Parameters
        ----------
        influencerset : set
            All residue names that should be considered.
        """
        self.influencer_names = influencerset

        # resix
        self.influencer_ix = [
            resix for resix, resname in enumerate(self.resnames)
            if resname in influencerset
        ]

        influencer_atix = []
        for resix in self.influencer_ix:
            influencer_atix.extend([*range(
                self.first_ix[resix], self.last_ix[resix] + 1  # inclusive!
            )])
        return influencer_atix


class Oscillator:
    """Stores all information on a single oscillator.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The class containing all the information on the system of the
        MD trajectory.
    atoms : list of int
        The indices of the atoms that make up this oscillator. All atoms
        specified in functional_group are in here.
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map that this oscillator belongs to.

    Attributes
    ----------
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map that this oscillator belongs to.
    used_atoms : list of int
        Using map_.used_atoms - contains the system indices of the atoms
        the map actually requires. Note that map_.used_atoms contains
        the local indices.
    electrostatic_atoms : list of int
        The system indices of all atoms that the map should calculate
        the electrostatic properties for.
    local_atoms : list of int
        The system indices of all atoms that the map should calculate
        the electrostatic properties for.
    electrostatic_atoms_c : `ctypes.Array`
        The c-friendly variant of self.electrostatic_atoms
    local_atoms_c : `ctypes.Array`
        The c-friendly variant of self.local_atoms
    n_estatic_atoms : `np.int32`
        The c-friendly form for the length of self.electrostatic_atoms
    n_local_atoms : `np.int32`
        The c-friendly form for the length of self.local_atoms
    VEGout : `np.ndarray`
        The array to which the output of the VEG calculations will be
        written. Is of shape (n_estatic_atoms, 10).
    VEGout_c : `ctypes.Array`
        The c-friendly variant of self.VEGout
    positions_box : `np.ndarray`
        The positions of all atoms given in used_atoms, in box
        coordinates.
    VEG_refpos : `np.ndarray`
        The position on which the sphere defining the electrostatics
        should be centered.
    VEG_refpos_c : `ctypes.Array`
        The c-friendly variant of self.VEG_refpos_c.
    rotation_matrix : `np.ndarray`
        The definition of the local vectors. This 3*3 numpy array can be
        considered 3 vectors, the x, y, and z unit vector in
        MD-coordinates.
    oscix : int
        The index of this oscillator in the current MD system.
    dipole_vec : `np.ndarray`
        (Only used if dipoles are calculated this run!)
        The dipole moment calculated for this oscillator.
    dipole_pos : `np.ndarray`
        (Only used if dipoles are calculated this run!)
        The position at which the dipole moment lies.
    """

    def __init__(self, system, atoms, map_):
        self.system = system
        self.map = map_
        self.used_atoms = [atoms[index] for index in self.map.core.used_atoms]
        self.electrostatic_atoms = [
            self.used_atoms[index]
            for index in self.map.core.electrostatic_atoms
        ]
        self.process_atschoice("electrostatic_atoms")
        self.local_atoms = [
            self.used_atoms[index] for index in self.map.core.local_atoms
        ]
        self.process_atschoice("local_atoms")
        self.local_atoms.sort()

        self.VEGout = np.zeros((self.n_estatic_atoms, 10), dtype="float32")
        self.VEGout_c = np.ctypeslib.as_ctypes(np.ravel(self.VEGout))

        # So we have some default RM to avoid stupid bugs and checks later
        self.rotation_matrix = np.array(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype="float32")

    def __str__(self):
        return (
            f"{self.__class__.__name__} of type {self.map.name} "
            f"{self.map.code.GM_str_osc(self.map, self.system, self)}"
        )

    def process_atschoice(self, attname):
        """Converts the provided attribute into c-friendly objects.

        This has been turned into a separate function, so if maps want
        to change anything about the structures programmatically (as
        adjusting rawpars didn't offer the needed tools), they can call
        this as a finalizer.

        Parameters
        ----------
        attname : str
            The name of the attribute which should be converted.
            self.attname should be of type list of int.
        """

        if attname == "local_atoms":
            atoms = set(getattr(self, attname))
            setattr(self, attname, sorted(atoms))

        setattr(self, attname + "_c", np.ctypeslib.as_ctypes(np.array(
            getattr(self, attname), dtype="int32")))

        if attname == "electrostatic_atoms":
            setattr(self, "n_estatic_atoms", np.int32(
                len(getattr(self, attname))))
        else:
            setattr(self, "n_" + attname, np.int32(
                len(getattr(self, attname))))

    def rotate_VEG(self):
        """Rotate the stored VEG from cartesian to local basis.

        The local basis is defined in self.rotation_matrix. The
        potential is not rotated, only the field and gradient are.
        """

        # G as a matrix should look like this:
        # row \\ column   0   1   2
        #   0           (Gxx Gxy Gxz)
        #   1           (Gyx Gyy Gyz)
        #   2           (Gzx Gzy Gzz)

        # Here, VEGout has the following structure:

        # index   0  1   2   3   4   5   6   7   8   9
        #       ( V  Ex  Ey  Ez Gxx Gyy Gzz Gxy Gxz Gyz )

        # So, to build the square matrix, we need the following indices:
        # (4 7 8)
        # (7 5 9)
        # (8 9 6)

        # and to go back:  (coords in row, col)
        # VEGout[4:] = ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))

        # --------------------------------------------------------------
        # rotate E
        self.VEGout[:, 1:4] = self.VEGout[:, 1:4] @ self.rotation_matrix.T

        # --------------------------------------------------------------
        # rotate G

        # build square representation
        Gsq = self.VEGout[:, [4, 7, 8, 7, 5, 9, 8, 9, 6]].reshape((-1, 3, 3))

        # Do the rotation
        temp = self.rotation_matrix @ Gsq @ self.rotation_matrix.T

        # and back to other representation
        self.VEGout[:, 4:] = temp[:, [0, 1, 2, 0, 0, 1], [0, 1, 2, 1, 2, 2]]

    def apply_dielectric_constant(self, constant):
        """Divide the VEG array by the dielectric constant.

        Parameters
        ----------
        constant : float
            The dielectric constant to apply. The VEG array will be
            divided by it.
        """

        self.VEGout /= constant

    def frame_update(self, system):
        """Update the frame-specific attributes of the instance.

        When a new frame starts, the system positions array is updated,
        so the information in this class that depends on that must be
        updated, too.

        Parameters
        ----------
        system : :class:`~GMAP.src.tools.system_reader.System`
            The object that stores all information on the MD system
        """

        self.positions = system.positions[self.used_atoms]

        # to get usable box positions, not only convert to box, but also make
        # sure they are 'centered' around one of the atoms of the molecule.
        # the assumption here is that all atoms of the molecule are reasonably
        # close together (at least much closer than a box length)
        self.positions_box = system.positions_box[self.used_atoms]
        shift = self.positions_box[0].copy()
        self.positions_box -= shift
        self.positions_box -= np.floor(self.positions_box + 0.5) - shift

        self.VEG_refpos = self.get_VEG_ref(system)
        self.VEG_refpos_c = np.ctypeslib.as_ctypes(self.VEG_refpos)
        if self.map.core.electrostatic_choice in ("E", "G"):
            self.rotation_matrix = self.get_rotation_matrix(system)

    def get_VEG_ref(self, system):
        """Obtain the VEG point for the current system. Must be repeated
        every frame.

        Parameters
        ----------
        system : :class:`~GMAP.src.tools.system_reader.System`
            The class containing all the information on the system of the
            MD trajectory.

        Returns
        -------
        VEG_ref : `np.ndarray`
            A 1D array of length 3 and type float32. This point is the
            center of a sphere with radius spheresize. All charges
            located within that sphere will (if allowed by locals and
            influencers) make up the final potential, field and gradient
            calculated for this oscillator.
        """

        return self.map.code.GM_get_VEG_ref(
            self.map, system, self
        )

    def get_rotation_matrix(self, system):
        """Obtain the rotation matrix for the current system. Must be
        repeated every frame.

        Parameters
        ----------
        system : :class:`~GMAP.src.tools.system_reader.System`
            The class containing all the information on the system of
            the MD trajectory.

        Returns
        -------
        rotation_matrix : `np.ndarray`
            A 2D array of shape (3, 3) and type float32. The first row
            is the x-direction unit vector of the oscillator, defined
            in global (/system/MD) coordinates. The second row is the
            y-direction, the third the z. These three vectors must
            always be orthonormal (and real). It is used for example to
            rotate the computed field and gradient into the local
            coordinates (through multiplying with the transpose of the
            matrix provided here.
        """

        return self.map.code.GM_get_rotation_matrix(
            self.map, system, self)


def gen_universe(run_pars):
    """Calls MDAanalysis.Universe on the supplied files and catches
    errors.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.

    Returns
    -------
    universe : `MDAnalysis.Universe`
        The universe that will be analyzed this run
    """

    try:
        universe = MDA.Universe(
            run_pars.topology_file.resolve(),
            run_pars.trajectory_file.resolve(),
            guess_bonds=run_pars.guess_bonds
            # run_pars.topology_file, run_pars.trajectory_file,
            # guess_bonds=run_pars.guess_bonds
        )
    except FileNotFoundError as ex:
        GM_pt.Printer.warning(
            "\nCould not find the topology or trajectory file. "
            "Please make sure "
            "the names are correct.",
            "MD_SU_1", True, exeption=ex,
            GMAPerrclass=GM_ex.GmapFileNotFoundError
        )
    except ValueError as ex:
        GM_pt.Printer.warning(
            "\nThe given topology and/or trajectory files are of the "
            "wrong type."
            " Please remember that only certain file types and combinations "
            "thereof are currently supported by the program.",
            "MD_SU_1", True, exception=ex, GMAPerrclass=GM_ex.GmapValueError
        )
    except Exception as ex:
        GM_pt.Printer.warning(
            "\nThe given topology and/or trajectory files could not be "
            "interpreted.",
            "MD_SU_1", True, exception=ex, GMAPerrclass=GM_ex.GmapMDFileError
        )

    return universe


def check_box_rightangled(universe):
    """Checks whether the supplied universe has only right angles.

    Parameters
    ----------
    universe : MDAnalysis.Universe
        The universe that will be analyzed this run

    Returns
    -------
    rightangled : bool
        Whether this universe has right angles only.
    """

    angles = universe.dimensions[3:]

    if all(angle == 90 for angle in angles):
        return True
    else:
        return False


def check_box_charge(run_pars, charges):
    """Checks whether the supplied universe has neutral charge.

    If the box has a non-integer charge, the program throws an error
    and quits.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    charges : np.ndarray
        The charges of all atoms in the system. Array is 1-dimensional,
        with a length equal to the amount of atoms in the MD simulation.

    Returns
    -------
    is_neutral : bool
        True if the box charge is (within threshold) neutral
        False if the box charge is (within threshold) integer, but not
        neutral.
    """

    total_charge = charges.sum()
    threshold = run_pars.neutral_charge_threshold

    # if charge is not basically 0:
    if abs(total_charge) > threshold:
        # if charge is not basically integer:
        if abs(round(total_charge) - total_charge) > threshold:
            GM_pt.Printer.warning(
                "\nThe total charge of the MD system deviates too far from an "
                "integer number. Check whether the files are correct, and "
                "whether the chosen threshold is relevant for this system.",
                "MD_SU_3", True, GMAPerrclass=GM_ex.GmapParameterError
            )
        else:
            GM_pt.Printer.warning(
                "\nThe total charge of the MD system is of integer, but not "
                "neutral value. Check whether the files are correct - usually "
                "md systems have a neutral charge. The program will continue, "
                "but be aware that this might yield incorrect results!",
                "MD_SU_3"
            )
        return False
    return True
