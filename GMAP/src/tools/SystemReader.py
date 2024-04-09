
# import sys

# 3rd party imports
import MDAnalysis as MDA
import numpy as np

# local imports
import GMAP.src.tools.ParameterParser as GM_PP
import GMAP.src.tools.PrintTools as GM_PT
from GMAP.src.tools.PrintTools import devprint as dpr
dpr("", end="")  # to disable error of dpr unused


class System:
    """Stores all information on the MD system and objects therein

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.

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
    residues : :class:`~GMAP.src.tools.SystemReader.Residues`
        This class contains information on a per-residue basis instead
        of a per-atom basis like this class does.
    molnums : `np.ndarray`
        A 1D array of length self.natoms storing the number of the
        molecule each atom belongs to. First molecule is numbered 0,
        each subsequent molecule gets an index 1 larger than the
        previous one. Counting never resets.
    rightangled : bool
        Whether self.angles only contains 90 degree angles.
    neutral : bool
        Whether the total charge of the MD system (the sum of
        self.charges) equals 0. The precision used can be changed using
        the parameter
        :ref:`neutral_charge_threshold<UserGuide_page_parameter_overview>`.
    oscillators : list of :class:`~GMAP.src.tools.SystemReader.Oscillator`
        All oscillators that were found in the MD system. These are the
        ones calculations will be performed on.
    influencers_atix : list of int
        The indices of all atoms that should be considered influencers.
    """

    def __init__(self, Files, Printer, RunPars):
        self.universe = gen_universe(Printer, RunPars)
        self.set_properties(Printer)
        self.basic_boxchecks(Printer, RunPars)

        self.find_influencers(Printer, RunPars)

        self.find_oscillators(Files, Printer, RunPars)

    def basic_boxchecks(self, Printer, RunPars):
        """Performs the first basic analyses on the provided universe.

        Doesn't return anything - if anything is amiss, it will just
        throw a fatal error.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        """

        self.rightangled = check_box_rightangled(self.universe)
        if not self.rightangled:
            Printer.warning(
                "\nSubmitted MD system is not of cubic, tetragonal or "
                "orthorhombic symmetry. In the current state, this program "
                "only supports right-angled systems.",
                "MD_SU_2", True
            )

        self.neutral = check_box_charge(Printer, RunPars, self.charges)

        try:
            self.universe.bonds
        except MDA.exceptions.NoDataError as ex:
            # there are no bonds, but we don't need them, either.
            if not RunPars.detected_requires_bonds:
                pass
            else:
                Printer.warning(
                    "\nSubmitted MD system does not contain any "
                    "information on "
                    "bonds, but the requested maps do require this. Either "
                    "choose a different map, or provide a different input.",
                    "MD_SU_5", True, exception=ex
                )

    # TO DO inside!
    def set_properties(self, Printer):
        """Sets the basic properties of the system.

        Extracts them from self.universe.atoms, and saves them in self.
        """
        self.atnums = self.universe.atoms.ix
        self.atnames = self.universe.atoms.names
        self.resnums = self.universe.atoms.resnums
        self.resnames = self.universe.atoms.resnames
        self.positions = self.universe.atoms.positions
        self.masses = self.universe.atoms.masses
        self.charges = self.universe.atoms.charges
        self.types = self.universe.atoms.types
        self.segids = self.universe.atoms.segids

        self.natoms = np.int32(self.resnums.shape[0])

        # dpr(set(self.masses))
        # for name, mass, type1, type2 in zip(
        #     self.atnames, self.masses, self.types,
        #     self.universe.atoms.elements
        # ):
        #     if int(mass) == 14:
        #         dpr(name, mass, type1, type2)

        # make sure resums always follow AIM-convention (regardless of MD input
        # used)
        self.abs_resnums(Printer)

        self.nres = np.int32(self.resnums[-1] + 1)

        self.boxdims = self.universe.dimensions[:3].astype('float32')
        self.halfbox = self.boxdims/2
        self.halfbox = self.halfbox.astype('float32')
        self.angles = self.universe.dimensions[3:].astype('float32')
        self.boxvects = MDA.lib.mdamath.triclinic_vectors(
            self.universe.dimensions
        )
        self.safesphere = 0.5 * self.boxvects.diagonal().min()
        self.boxvects_inv = np.linalg.inv(self.boxvects)

        # TO DO - analogue of AIMs ResidueFinder and IXFinder
        self.residues = Residues(self)

        # TO DO - way to find molnums for non-gromacs systems
        #         ?is this necessary? or can we make do without??

        self.molnums = self.universe.atoms.molnums

        # TO DO - analogue for AIM's residues.protein_init?
        #         or should this be part of the protein maps?

        # TO DO - analogue for AIM's RunPar.SetOPLS?
        #         or should this be part of maps that require to know
        #         whether OPLS is being used?

        # TO DO - C support?
        # if RunPar.use_c_lib:
        #     self.charges = self.charges.astype('float32')
        #     self.charges_c = np.ctypeslib.as_ctypes(self.charges)
        #     self.masses = self.masses.astype('float32')
        #     self.masses_c = np.ctypeslib.as_ctypes(self.masses)
        #     self.res_COM_c = np.ctypeslib.as_ctypes(
        #         np.zeros((self.nres * 3), dtype='float32'))

    def abs_resnums(self, Printer):
        """Renumbers residue numbers so they start at 0, and never reset

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        """

        prevresnum = -1
        writeresnum = -1
        for atomnum, ix in enumerate(self.atnums):
            if atomnum != ix:
                # yes, we could just force atomnum to match ix. But if this
                # MD software does this differently, it might very well do
                # other things differently as well, so please, check that!
                Printer.warning(
                    f"\nThe atom number of the atom at position {atomnum} "
                    "does "
                    "not match its position in the list.",
                    "MD_SU_4", True
                )
            resnum = self.resnums[atomnum]
            if resnum != prevresnum:
                writeresnum += 1
            self.resnums[atomnum] = writeresnum
            prevresnum = resnum

    def find_influencers(self, Printer, RunPars):
        """Find the indices of all atoms that are influencers

        Influencers are the atoms whose charge should be considered
        while calculating the VEG for a given point. This is a first
        guess, things like local-ix, spheresize and the like are not
        yet considered.

        Parameters
        ----------
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
        """

        groupdict = {}
        groupdict["All"] = set(self.residues.resnames)
        groupdict["None"] = set("")
        for map_ in RunPars.requested_mapdict.values():
            # Here, allow maps to add their own custom definitions!
            all_map_influencers = map_.rawcore.get("influencer_group", [])
            for map_inflgroup in all_map_influencers:
                name = map_inflgroup[0]
                group_def = " ".join(map_inflgroup[1:])
                groupdict[name] = GM_PP.parse_influencerfile_line(
                    Printer, group_def, groupdict, map_.corepath
                )

        for key, val in groupdict.items():
            dpr(key, val)

        Printer.print(1, f"\n{GM_PT.make_header('Influencers', '-')}\n\n")

        if isinstance(RunPars.influencers, list):
            choice = GM_PP.parse_influencer_par(" ".join(RunPars.influencers))
            choice = GM_PP.parse_influencerfile_line(
                Printer, choice, groupdict,
                "parameter file "
            )
            self.influencers_atix = self.residues.manage_influencers(choice)
            influencers_not_included = groupdict["All"] - choice
            Printer.print(
                1,
                "Residue names included in influencers:\n"
                + ", ".join(choice) +
                "\n\nResidue names NOT included in influencers:\n"
                + ", ".join(influencers_not_included)
            )
        elif isinstance(RunPars.influencers, str):
            try:
                atgroup = self.universe.select_atoms(RunPars.influencers)
            except Exception as ex:
                Printer.warning(
                    "Some problem occured while selecting atoms for the "
                    "influencers",
                    "SU_NP_6", True, exception=ex
                )
            self.influencers_atix = atgroup.atoms.ix.tolist()
        else:  # must be a separate file
            choice = GM_PP.parse_influencerfile(
                Printer, RunPars.influencers, groupdict)
            if "choice" in choice:
                choice = choice["choice"]
            else:
                Printer.warning(
                    "When using a file to specify influencers, the final "
                    "choice of influencers must be given using the group "
                    "'choice'.",
                    "SU_NP_5", True
                )
            self.influencers_atix = self.residues.manage_influencers(choice)
            influencers_not_included = groupdict["All"] - choice
            Printer.print(
                1,
                "Residue names included in influencers:\n"
                + ", ".join(choice) +
                "\n\nResidue names NOT included in influencers:\n"
                + ", ".join(influencers_not_included)
            )

        # all kinds of influencer parameters
        atixprint = GM_PT.intlist_to_rangelist(
            self.influencers_atix, self.natoms
        )
        Printer.print(
            3,
            "Atoms included in influencers:\n"
            + ", ".join(atixprint[0]) +
            "\n\nAtoms NOT included in influencers:\n"
            + ", ".join(atixprint[1])
        )
        self.influencers_atix = np.asarray(
            self.influencers_atix, dtype=np.int32
        )

    def find_oscillators(self, Files, Printer, RunPars):
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
        Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
            Contains all currently known paths and other file-related
            properties.
            Has to be updated after RunPars is finalized.
        Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
            The object that allows to cleanly log and print during runtime,
            and handle errors.
        RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic run-defining
            parameters.
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
        allgroups = [
            self.find_oscillators_perstruct(struct, map_)
            for map_ in RunPars.requested_mapdict.values()
            for struct in map_.Core.functional_group
        ]

        # feed the found oscillators to the maps, let them have a look
        # at them / edit.
        checked_oscillators = []
        for oscillators in allgroups:
            map_ = oscillators[0].Map
            checked = map_.code.GM_adjust_oscillators(
                Files, Printer, map_, self, oscillators
            )
            if checked:
                checked_oscillators.append(checked)

        # PRINTS!!!!

        # PRINT FOUND OSCILLATORS
        # for oscillators in checked_oscillators:
        #     if not oscillators:
        #         continue
        #     dpr(oscillators[0].Map.name, len(oscillators))
        #     for oscillator in oscillators:
        #         dpr(
        #             self.resnames[oscillator.used_atoms[0]],
        #             [(ix, self.atnames[ix]) for ix in oscillator.used_atoms]
        #         )

        # PRINT ATOMS OF CERTAIN GROUP FOR SCANNING PURPOSES
        # for ix, name in enumerate(self.residues.resnames):
        #     if name == "CYS":
        #         for atix in range(
        #             self.residues.first_ix[ix],
        #             self.residues.last_ix[ix] + 1
        #         ):
        #             dpr(atix, self.atnames[atix])
        #             if self.atnames[atix] == "SG":
        #                 dpr(self.universe.atoms[atix].bonded_atoms)

        self.oscillators = [
            oscillator for oscillators in checked_oscillators
            for oscillator in oscillators
        ]

    def find_oscillators_perstruct(self, struct, map_):
        """Finds all oscillators matching the given structure.

        Considers residue and atoms names, as well as bonds defined in
        the map.

        Parameters
        ----------
        struct : :class:`~GMAP.src.tools.MapReader.Structure`
            The structure template that will be matched.
        map_ : :class:`~GMAP.src.tools.MapReader.Map`
            The map instance the structure belongs to.

        Returns
        -------
        all_oscillators : list of \
            :class:`~GMAP.src.tools.SystemReader.Oscillator`
            All oscillators that were found matching the given structure.
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

        all_oscillators = [Oscillator(osc, map_) for osc in all_oscillators]
        return all_oscillators

    def find_oscillators_residue(self, residue):
        """Finds all oscillators matching the given residue template.

        Only considers residue and atoms names.

        Parameters
        ----------
        residue : :class:`~GMAP.src.tools.MapReader.Residue`
            The desired residue template for which the MD system will be
            searched.

        Returns:
        --------
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
        struct : :class:`~GMAP.src.tools.MapReader.Structure`
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
        struct : :class:`~GMAP.src.tools.MapReader.Structure`
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

        # convert struct-ix to residue-ix
        target_residue, target_local_ix = struct.indices[new_local_ix]

        # check all residues that could be added on
        for new_residue in all_oscillators[target_residue]:
            new_ix = new_residue[target_local_ix]  # get global index
            # if it is attached, add it
            if self.confirm_bond(found_ix, new_ix):
                new_osc = base_residue[:]

                # write the global indices of added piece to original
                # oscillator
                for index in struct.indices_per_residue[target_residue]:
                    new_osc[index] = new_residue[struct.indices[index][1]]
                outlist.append(new_osc)
        return outlist


class Residues:
    """Creates and stores information on the system on a per-residue basis

    The System class has a lot of information on a per-atom basis, this
    class has it on a per residue.

    Parameters
    ----------
    syst : :class:`~GMAP.src.tools.SystemReader.System`
        The class containing all the information on the system of the
        MD trajectory.

    Attributes
    ----------
    first_ix : list of int
        A list as long as there are residues in the MD system. For each
        residue, it stores the index of the first atom.
    last_ix : list of int
        A list as long as there are residues in the MD system. For each
        residue, it stores the index of the last atom.
    resnames : list of str
        A list as long as there are residues in the MD system. For each
        residue, it stores its residue name.
    influencer_names : set()
        All residue names that are considered influencers this run.
    influencer_ix : list of int
        The indices of all residues that are influencers.
    """

    def __init__(self, syst):
        self.find_markers(syst)

    def find_markers(self, syst):
        """Make lookup tables (len=nres) for basic residue-based properties.

        1D arrays are built with a length equal to the amount of
        residues in the system. For each residue, we save the index
        (atnum) of the first and last atom it consists of, as well as
        its name.
        Knowing where a residue starts/ends is very useful for further
        analysis of the MD system.

        Parameters
        ----------
        syst : :class:`System`
            This object stores all important information about the MD
            system that will be analyzed.
        """
        self.first_ix = []
        self.resnames = []
        self.last_ix = []

        last_resnum = -1
        current_resnum = -1

        for atnum, resnum in enumerate(syst.resnums):
            last_resnum = current_resnum
            current_resnum = resnum

            # We're only looking for when a new residue starts.
            if last_resnum == current_resnum:
                continue

            # now, we know we've just found a new residue
            if last_resnum != -1:
                self.last_ix.append(atnum - 1)
            self.resnames.append(syst.resnames[atnum])
            self.first_ix.append(atnum)
        else:
            self.last_ix.append(atnum)

        self.first_ix = np.array(self.first_ix)
        self.last_ix = np.array(self.last_ix)

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
    atoms : list of int
        The indices of the atoms that make up this oscillator. All atoms
        specified in functional_group are in here.
    map_ : :class:`~GMAP.src.tools.MapReader.Map`
        The map that this oscillator belongs to.

    Attributes
    ----------
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The map that this oscillator belongs to.
    used_atoms : list of int
        Using Map.used_atoms - contains the system indices of the atoms
        the map actually requires. Note that Map.used_atoms contains
        the local indices.
    electrostatic_atoms : list of int
        The system indices of all atoms that the map should calculate
        the electrostatic properties for.
    positions_box : `np.ndarray`
        The positions of all atoms given in used_atoms, in box
        coordinates.
    """

    def __init__(self, atoms, map_):
        self.Map = map_
        self.used_atoms = [atoms[index] for index in self.Map.Core.used_atoms]
        self.electrostatic_atoms = [
            self.used_atoms[index]
            for index in self.Map.Core.electrostatic_atoms
        ]

    def frame_update(self, Syst):
        """Update the frame-specific attributes of the instance.

        When a new frame starts, the system positions array is updated,
        so the information in this class that depends on that must be
        updated, too.

        Parameters
        ----------
        Syst : :class:`~GMAP.src.tools.SystemReader.System`
            The object that stores all information on the MD system
        """
        self.positions_box = (
            Syst.positions[self.used_atoms] @ Syst.boxvects_inv)


def gen_universe(Printer, RunPars):
    """Calls MDAanalysis.Universe on the supplied files and catches errors.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.

    Returns
    -------
    universe : `MDAnalysis.Universe`
        The universe that will be analyzed this run
    """

    try:
        universe = MDA.Universe(
            RunPars.topology_file, RunPars.trajectory_file,
            guess_bonds=RunPars.guess_bonds
        )
    except FileNotFoundError as ex:
        Printer.warning(
            "\nCould not find the topology or trajectory file. "
            "Please make sure "
            "the names are correct.",
            "MD_SU_1", True, exeption=ex
        )
    except ValueError as ex:
        Printer.warning(
            "\nThe given topology and/or trajectory files are of the "
            "wrong type."
            " Please remember that only certain file types and combinations "
            "thereof are currently supported by the program.",
            "MD_SU_1", True, exception=ex
        )
    except Exception as ex:
        Printer.warning(
            "\nThe given topology and/or trajectory files could not be "
            "interpreted.",
            "MD_SU_1", True, exception=ex
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


def check_box_charge(Printer, RunPars, charges):
    """Checks whether the supplied universe has neutral charge.

    If the box has a non-integer charge, the program throws an error
    and quits.

    Parameters
    ----------
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
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
    threshold = RunPars.neutral_charge_threshold

    # if charge is not basically 0:
    if abs(total_charge) > threshold:
        # if charge is not basically integer:
        if abs(round(total_charge) - total_charge) > threshold:
            Printer.warning(
                "\nThe total charge of the MD system deviates too far from an "
                "integer number. Check whether the files are correct, and "
                "whether the chosen threshold is relevant for this system.",
                "MD_SU_3", True
            )
        else:
            Printer.warning(
                "\nThe total charge of the MD system is of integer, but not "
                "neutral value. Check whether the files are correct - usually "
                "md systems have a neutral charge. The program will continue, "
                "but be aware that this might yield incorrect results!",
                "MD_SU_3"
            )
        return False
    return True
