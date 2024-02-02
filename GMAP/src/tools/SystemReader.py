
import MDAnalysis as MDA
import numpy as np


class System:
    def __init__(self, Printer, RunPars):
        self.universe = gen_universe(Printer, RunPars)
        self.set_properties()
        self.basic_boxchecks(Printer, RunPars)

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
                "Submitted MD system is not of cubic, tetragonal or "
                "orthorhombic symmetry. In the current state, this program "
                "only supports right-angled systems.",
                "MD_SU_2", True
            )

        self.neutral = check_box_charge(Printer, self.charges, RunPars)

        try:
            self.universe.bonds
        except MDA.exceptions.NoDataError as ex:
            # there are no bonds, but we don't need them, either.
            if not RunPars.detected_requires_bonds:
                pass
            else:
                Printer.warning(
                    "Submitted MD system does not contain any information on "
                    "bonds, but the requested maps do require this. Either "
                    "choose a different map, or provide a different input.",
                    "MD_SU_5", True, exception=ex
                )

    # TO DO inside!
    def set_properties(self):
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

        # make sure resums always follow AIM-convention (regardless of MD input
        # used)
        self.abs_resnums()

        self.nres = np.int32(self.resnums[-1] + 1)

        self.boxdims = self.universe.dimensions[:3].astype('float32')
        self.halfbox = self.boxdims/2
        self.halfbox = self.halfbox.astype('float32')
        self.angles = self.universe.dimensions[3:].astype('float32')

        # TO DO - analogue of AIMs ResidueFinder and IXFinder

        # TO DO - way to find molnums for non-gromacs systems
        #         ?is this necessary? or can we make due without??

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
                    f"The atom number of the atom at position {atomnum} does "
                    "not match its position in the list.",
                    "MD_SU_4", True
                )
            resnum = self.resnums[atomnum]
            if resnum != prevresnum:
                writeresnum += 1
            self.resnums[atomnum] = writeresnum
            prevresnum = resnum


class Residues:
    def __init__(self, syst):
        pass


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
    universe : MDAnalysis.Universe
        The universe that will be analyzed this run
    """

    try:
        universe = MDA.Universe(
            RunPars.topology_file, RunPars.trajectory_file,
            guess_bonds=RunPars.guess_bonds
        )
    except FileNotFoundError as ex:
        Printer.warning(
            "Could not find the topology or trajectory file. Please make sure "
            "the names are correct.",
            "MD_SU_1", True, exeption=ex
        )
    except TypeError as ex:
        Printer.warning(
            "The given topology and/or trajectory files are of the wrong type."
            " Please remember that only certain file types and combinations "
            "thereof are currently supported by the program.",
            "MD_SU_1", True, exception=ex
        )
    except Exception as ex:
        Printer.warning(
            "The given topology and/or trajectory files could not be "
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
                "The total charge of the MD system deviates too far from an "
                "integer number. Check whether the files are correct, and "
                "whether the chosen threshold is relevant for this system.",
                "MD_SU_3", True
            )
        else:
            Printer.warning(
                "The total charge of the MD system is of integer, but not "
                "neutral value. Check whether the files are correct - usually "
                "md systems have a neutral charge. The program will continue, "
                "but be aware that this might yield incorrect results!",
                "MD_SU_3"
            )
        return False
    return True
