"""
Interface between C-level functions and python code.

Instead of having the python hooks in the C code directly (like numpy
for example), GMAP leaves the C library as standard c. The ctypes module
is used to access this c code, and numpy.ctypeslib.as_ctypes is used to
get data to/from it. 

Classes
-------
VEG_CLib
    Has a method for each function in the VEG C library. These serve
    akin to wrappers; they take complicated python objects, and extract
    from those the actually needed c-type objects.
"""


# standard lib imports
import ctypes as ct

# local imports
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.print_tools as GM_pt


class VEG_CLib(metaclass=GM_ct.Singleton):
    """Stores and manages all c functions regarding electrostatics.

    Each (external) function in the library has it's own associated
    method on this class. The calls to C are ugly and convoluted due
    to c functions needing so many parameters (either single values
    or numpy arrays), so these methods make their calls more pythonic.
    They each require just the relevant classes, and unpack the required
    attributes themselves.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.

    Notes
    -----
    C functions cannot return more than a single value. Therefore, most
    will write their output into an array provided as an input. This
    array must be of a c-friendly datatype, use
    ``np.ctypeslib.as_ctypes()``
    for creating these. This version must be saved along with the
    original, so, for example, you have both ``my_arr`` and
    ``my_arr_c``, where ``my_arr_c`` is defined as
    ``np.ctypeslib.as_ctypes(my_arr)``. This results in two views of the
    same array, meaning that any changes to any values made in
    ``my_arr`` will also apply to ``my_arr_c``, and vice versa.

    Attributes
    ----------
    clib : `ctypes.CDLL`
        The actual compiled c-code. Must be compiled to be a library,
        so a .dll (windows), .so (linux) or .dylib (macOS) file.
    """

    def __init__(self, run_pars):
        try:
            msg = (
                f"\nThe file {run_pars.VEG_clib_file} was requested to be used "
                "as the VEG c-library. However, the file is invalid. "
            )
            self.clib = ct.CDLL(str(run_pars.VEG_clib_file))
        except Exception as ex:
            GM_pt.Printer.warning(
                msg, "CL_VG_1", True, exception=ex,
                GMAPerrclass=GM_ex.GmapOSError
            )

        self.clib.transform_vectors.restype = None
        self.clib.transform_vectors.argtypes = [
            ct.POINTER(ct.c_float),  # vectors_in
            ct.c_int,  # n_vects
            ct.POINTER(ct.c_float),  # tr_matrix
            ct.POINTER(ct.c_float)  # vectors_out
        ]

        self.clib.calc_CoM_box.restype = None
        self.clib.calc_CoM_box.argtypes = [
            ct.POINTER(ct.c_float),  # positions_box
            ct.POINTER(ct.c_float),  # masses
            ct.POINTER(ct.c_int),  # res_first_ix
            ct.POINTER(ct.c_int),  # res_last_ix
            ct.c_int,  # nres
            ct.POINTER(ct.c_float),  # CoM_box
        ]

        self.clib.calcVEG_perres_mm_rhombic.restype = None
        self.clib.calcVEG_perres_mm_rhombic.argtypes = [
            ct.POINTER(ct.c_int),  # tocalc
            ct.c_int,  # n_osc_ats
            ct.POINTER(ct.c_float),  # spherepos
            ct.c_int,  # calc_choice
            ct.POINTER(ct.c_float),  # positions
            ct.POINTER(ct.c_float),  # charges
            ct.POINTER(ct.c_int),  # influencer_atoms
            ct.c_int,  # n_influencers
            ct.POINTER(ct.c_float),  # COMs
            ct.POINTER(ct.c_int),  # res_first_ix
            ct.POINTER(ct.c_int),  # res_last_ix
            ct.c_int,  # n_res
            ct.POINTER(ct.c_int),  # local_atoms
            ct.c_int,  # n_locals
            ct.c_float,  # r_sphere
            ct.c_float,  # r_smooth
            ct.POINTER(ct.c_float),  # halfbox
            ct.POINTER(ct.c_float),  # boxdims
            ct.POINTER(ct.c_float)  # out
        ]

        self.clib.calcVEG_perres_mm_rhombic_nocut.restype = None
        self.clib.calcVEG_perres_mm_rhombic_nocut.argtypes = [
            ct.POINTER(ct.c_int),  # tocalc
            ct.c_int,  # n_osc_ats
            ct.POINTER(ct.c_float),  # spherepos
            ct.c_int,  # calc_choice
            ct.POINTER(ct.c_float),  # positions
            ct.POINTER(ct.c_float),  # charges
            ct.POINTER(ct.c_int),  # influencer_atoms
            ct.c_int,  # n_influencers
            ct.POINTER(ct.c_float),  # COMs
            ct.POINTER(ct.c_int),  # res_first_ix
            ct.POINTER(ct.c_int),  # res_last_ix
            ct.c_int,  # n_res
            ct.POINTER(ct.c_int),  # local_atoms
            ct.c_int,  # n_locals
            ct.c_float,  # r_sphere
            ct.POINTER(ct.c_float),  # halfbox
            ct.POINTER(ct.c_float),  # boxdims
            ct.POINTER(ct.c_float)  # out
        ]

        self.clib.calcVEG_perres_mm_triclin.restype = None
        self.clib.calcVEG_perres_mm_triclin.argtypes = [
            ct.POINTER(ct.c_int),  # tocalc
            ct.c_int,  # n_osc_ats
            ct.POINTER(ct.c_float),  # spherepos
            ct.c_int,  # calc_choice
            ct.POINTER(ct.c_float),  # positions_box
            ct.POINTER(ct.c_float),  # charges
            ct.POINTER(ct.c_int),  # influencer_atoms
            ct.c_int,  # n_influencers
            ct.POINTER(ct.c_float),  # COMs_box
            ct.POINTER(ct.c_int),  # res_first_ix
            ct.POINTER(ct.c_int),  # res_last_ix
            ct.c_int,  # n_res
            ct.POINTER(ct.c_int),  # local_atoms
            ct.c_int,  # n_locals
            ct.c_float,  # r_sphere
            ct.c_float,  # r_smooth
            ct.POINTER(ct.c_float),  # boxvects
            ct.POINTER(ct.c_float),  # boxvects_inv
            ct.POINTER(ct.c_float)  # out
        ]

        self.clib.calcVEG_perres_mm_triclin_nocut.restype = None
        self.clib.calcVEG_perres_mm_triclin_nocut.argtypes = [
            ct.POINTER(ct.c_int),  # tocalc
            ct.c_int,  # n_osc_ats
            ct.POINTER(ct.c_float),  # spherepos
            ct.c_int,  # calc_choice
            ct.POINTER(ct.c_float),  # positions_box
            ct.POINTER(ct.c_float),  # charges
            ct.POINTER(ct.c_int),  # influencer_atoms
            ct.c_int,  # n_influencers
            ct.POINTER(ct.c_float),  # COMs_box
            ct.POINTER(ct.c_int),  # res_first_ix
            ct.POINTER(ct.c_int),  # res_last_ix
            ct.c_int,  # n_res
            ct.POINTER(ct.c_int),  # local_atoms
            ct.c_int,  # n_locals
            ct.c_float,  # r_sphere
            ct.POINTER(ct.c_float),  # boxvects
            ct.POINTER(ct.c_float),  # boxvects_inv
            ct.POINTER(ct.c_float)  # out
        ]

    def positions_to_box(self, system):
        self.clib.transform_vectors(
            system.positions_c,
            system.natoms,
            system.boxvects_inv_c,
            system.positions_box_c
        )

    def calc_CoM_box(self, system):
        self.clib.calc_CoM_box(
            system.positions_box_c,
            system.masses_c,
            system.residues.first_ix_c,
            system.residues.last_ix_c,
            system.nres,
            system.residues.CoM_box_c
        )

    def CoM_frombox(self, system):
        self.clib.transform_vectors(
            system.residues.CoM_box_c,
            system.nres,
            system.boxvects_c,
            system.residues.CoM_c
        )

    def calcVEG_perres_main(self, system, run_pars, oscillator):
        # First letter (n/c) is (No)Cut.
        # Second letter (r/t) is Rhombic/Triclinic
        allfuncs = {
            "rc": self.calcVEG_perres_mm_rhombic,
            "rn": self.calcVEG_perres_mm_rhombic_nocut,
            "tc": self.calcVEG_perres_mm_triclin,
            "tn": self.calcVEG_perres_mm_triclin_nocut
        }
        if run_pars.treat_box == "orthorhombic":
            key = "r"
        elif run_pars.treat_box == "triclinic":
            key = "t"
        else:
            key = "t"
        if run_pars.estatics_method == "perres":
            key += "c"
        elif run_pars.estatics_method == "perres_nocut":
            key += "n"

        allfuncs[key](system, run_pars, oscillator)

    def calcVEG_perres_mm_triclin(self, system, run_pars, oscillator):
        """Calculate the potential on each of the requested points.

        This is basically a wrapper for the c function of the same
        name. As c cannot return arrays, the output is instead written
        into the provided input array of the name ``VEGout_c`` (in
        python; in c it is called ``out``), which is an attribute of
        ``oscillator``. If you want to retrieve these values, read them
        from ``oscillator.VEGout``.

        In this function, an atom only counts towards the electrostatics
        if the centre of mass of its residue is in range, AND the atom
        itself is also in range.

        See Also
        --------
        calcVEG_perres_mm_nocut
            This function recreates the method of AIM: if a residue's
            centre of mass is in range, all atoms in that residue count
            towards the total electrostatics.

        Parameters
        ----------
        system : :class:`~GMAP.src.tools.system_reader.System`
            The object that stores everything the program currently knows
            about the system being treated (names, numbers, types, masses,
            charges of all atoms, for example)
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
            The specific oscillator for which the potentials are required.
        """

        # each input has as a comment the name of that variable in c.
        self.clib.calcVEG_perres_mm_triclin(
            oscillator.electrostatic_atoms_c,  # tocalc
            oscillator.n_estatic_atoms,  # n_osc_ats
            oscillator.VEG_refpos_c,  # spherepos
            oscillator.map.core.electrostatic_choice_c,  # calc_choice
            system.positions_box_c,  # positions_box
            system.charges_c,  # charges
            system.influencers_atix_c,  # influencer_atoms
            system.n_influencers,  # n_influencers
            system.residues.CoM_box_c,  # COMs_box
            system.residues.first_ix_c,  # res_first_ix
            system.residues.last_ix_c,  # res_last_ix
            system.nres,  # n_res
            oscillator.local_atoms_c,  # local_atoms
            oscillator.n_local_atoms,  # n_locals
            run_pars.estatic_range,  # r_sphere
            run_pars.estatic_smooth_range,  # r_smooth
            system.boxvects_c,  # boxvects
            system.boxvects_inv_c,  # boxvects_inv
            oscillator.VEGout_c  # out
        )

    def calcVEG_perres_mm_triclin_nocut(self, system, run_pars, oscillator):
        """Calculate the potential on each of the requested points.

        This is basically a wrapper for the c function of the same
        name. As c cannot return arrays, the output is instead written
        into the provided input array of the name ``VEGout_c`` (in
        python; in c it is called ``out``), which is an attribute of
        ``oscillator``. If you want to retrieve these values, read them
        from ``oscillator.VEGout``.

        In this function, an atom only counts towards the electrostatics
        if the centre of mass of its residue is in range.

        See Also
        --------
        calcVEG_perres_mm
            This function is the intended improved method by GEM:
            an atom only counts towards the electrostatics if the centre
            of mass of its residue is in range, AND the atom itself is
            also in range.

        Parameters
        ----------
        system : :class:`~GMAP.src.tools.system_reader.System`
            The object that stores everything the program currently knows
            about the system being treated (names, numbers, types, masses,
            charges of all atoms, for example)
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
            The specific oscillator for which the potentials are required.
        """

        # each input has as a comment the name of that variable in c.
        self.clib.calcVEG_perres_mm_triclin_nocut(
            oscillator.electrostatic_atoms_c,  # tocalc
            oscillator.n_estatic_atoms,  # n_osc_ats
            oscillator.VEG_refpos_c,  # spherepos
            oscillator.map.core.electrostatic_choice_c,  # calc_choice
            system.positions_box_c,  # positions_box
            system.charges_c,  # charges
            system.influencers_atix_c,  # influencer_atoms
            system.n_influencers,  # n_influencers
            system.residues.CoM_box_c,  # COMs_box
            system.residues.first_ix_c,  # res_first_ix
            system.residues.last_ix_c,  # res_last_ix
            system.nres,  # n_res
            oscillator.local_atoms_c,  # local_atoms
            oscillator.n_local_atoms,  # n_locals
            run_pars.estatic_range,  # r_sphere
            system.boxvects_c,  # boxvects
            system.boxvects_inv_c,  # boxvects_inv
            oscillator.VEGout_c  # out
        )

    def calcVEG_perres_mm_rhombic(self, system, run_pars, oscillator):
        """Calculate the potential on each of the requested points.

        This is basically a wrapper for the c function of the same
        name. As c cannot return arrays, the output is instead written
        into the provided input array of the name ``VEGout_c`` (in
        python; in c it is called ``out``), which is an attribute of
        ``oscillator``. If you want to retrieve these values, read them
        from ``oscillator.VEGout``.

        In this function, an atom only counts towards the electrostatics
        if the centre of mass of its residue is in range, AND the atom
        itself is also in range.

        See Also
        --------
        calcVEG_perres_mm_nocut
            This function recreates the method of AIM: if a residue's
            centre of mass is in range, all atoms in that residue count
            towards the total electrostatics.

        Parameters
        ----------
        system : :class:`~GMAP.src.tools.system_reader.System`
            The object that stores everything the program currently knows
            about the system being treated (names, numbers, types, masses,
            charges of all atoms, for example)
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
            The specific oscillator for which the potentials are required.
        """

        # each input has as a comment the name of that variable in c.
        self.clib.calcVEG_perres_mm_rhombic(
            oscillator.electrostatic_atoms_c,  # tocalc
            oscillator.n_estatic_atoms,  # n_osc_ats
            oscillator.VEG_refpos_c,  # spherepos
            oscillator.map.core.electrostatic_choice_c,  # calc_choice
            system.positions_c,  # positions
            system.charges_c,  # charges
            system.influencers_atix_c,  # influencer_atoms
            system.n_influencers,  # n_influencers
            system.residues.CoM_c,  # COMs
            system.residues.first_ix_c,  # res_first_ix
            system.residues.last_ix_c,  # res_last_ix
            system.nres,  # n_res
            oscillator.local_atoms_c,  # local_atoms
            oscillator.n_local_atoms,  # n_locals
            run_pars.estatic_range,  # r_sphere
            run_pars.estatic_smooth_range,  # r_smooth
            system.halfbox_c,  # halfbox
            system.boxdims_c,  # boxdims
            oscillator.VEGout_c  # out
        )

    def calcVEG_perres_mm_rhombic_nocut(self, system, run_pars, oscillator):
        """Calculate the potential on each of the requested points.

        This is basically a wrapper for the c function of the same
        name. As c cannot return arrays, the output is instead written
        into the provided input array of the name ``VEGout_c`` (in
        python; in c it is called ``out``), which is an attribute of
        ``oscillator``. If you want to retrieve these values, read them
        from ``oscillator.VEGout``.

        In this function, an atom only counts towards the electrostatics
        if the centre of mass of its residue is in range.

        See Also
        --------
        calcVEG_perres_mm
            This function is the intended improved method by GEM:
            an atom only counts towards the electrostatics if the centre
            of mass of its residue is in range, AND the atom itself is
            also in range.

        Parameters
        ----------
        system : :class:`~GMAP.src.tools.system_reader.System`
            The object that stores everything the program currently knows
            about the system being treated (names, numbers, types, masses,
            charges of all atoms, for example)
        run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        oscillator : :class:`~GMAP.src.tools.system_reader.Oscillator`
            The specific oscillator for which the potentials are required.
        """

        # each input has as a comment the name of that variable in c.
        self.clib.calcVEG_perres_mm_rhombic_nocut(
            oscillator.electrostatic_atoms_c,  # tocalc
            oscillator.n_estatic_atoms,  # n_osc_ats
            oscillator.VEG_refpos_c,  # spherepos
            oscillator.map.core.electrostatic_choice_c,  # calc_choice
            system.positions_c,  # positions
            system.charges_c,  # charges
            system.influencers_atix_c,  # influencer_atoms
            system.n_influencers,  # n_influencers
            system.residues.CoM_c,  # COMs
            system.residues.first_ix_c,  # res_first_ix
            system.residues.last_ix_c,  # res_last_ix
            system.nres,  # n_res
            oscillator.local_atoms_c,  # local_atoms
            oscillator.n_local_atoms,  # n_locals
            run_pars.estatic_range,  # r_sphere
            system.halfbox_c,  # halfbox
            system.boxdims_c,  # boxdims
            oscillator.VEGout_c  # out
        )
