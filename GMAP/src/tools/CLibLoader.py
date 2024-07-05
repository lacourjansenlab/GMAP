
# standard lib imports
import ctypes as ct

# local imports
import GMAP.src.tools.CodingTools as GM_CT
from GMAP.src.tools.PrintTools import Printer


class VEG_CLib(metaclass=GM_CT.Singleton):
    """Stores and manages all c functions regarding electrostatics.

    Each (external) function in the library has it's own associated
    method on this class. The calls to C are ugly and convoluted due
    to c functions needing so many parameters (either single values
    or numpy arrays), so these methods make their calls more pythonic.
    They each require just the relevant classes, and unpack the required
    attributes themselves.

    Parameters
    ----------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
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

    def __init__(self, RunPars):
        try:
            self.clib = ct.CDLL(str(RunPars.VEG_clib_file))
        except Exception as ex:
            # OSError for invalid file (VEG.obj)
            # No others found yet.
            Printer().warning(
                f"\nThe file {RunPars.VEG_clib_file} was requested to be used "
                "as the VEG c-library. However, the file is invalid. ",
                "CL_VG_1", True, exception=ex
            )

        self.clib.calcVEG_perres_mm.argtypes = [
            ct.POINTER(ct.c_int),  # tocalc
            ct.c_int,  # n_osc_ats
            ct.POINTER(ct.c_float),  # spherepos
            ct.c_int,  # calc_choice
            ct.POINTER(ct.c_float),  # positioins
            ct.POINTER(ct.c_float),  # charges
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
        self.clib.calcVEG_perres_mm.restype = None

    def calcVEG_perres_mm(self, System, RunPars, oscillator):
        """Calculate the potential on each of the requested points.

        This is basically a wrapper for the c function of the same
        name. As c cannot return arrays, the output is instead written
        into the provided input array of the name ``VEGout_c`` (in
        python; in c it is called ``out``), which is an attribute of
        ``oscillator``. If you want to retrieve these values, read them
        from ``oscillator.VEGout``.

        Parameters
        ----------
        System : :class:`~GMAP.src.tools.SystemReader.System
            The object that stores everything the program currently knows
            about the system being treated (names, numbers, types, masses,
            charges of all atoms, for example)
        RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The 'main' RunPars instance containing all the basic
            run-defining parameters.
        oscillator : :class:`~GMAP.src.tools.SystemReader.Oscillator`
            The specific oscillator for which the potentials are required.
        """

        # each input has as a comment the name of that variable in c.
        self.clib.calcVEG_perres_mm(
            oscillator.electrostatic_atoms_c,  # tocalc
            oscillator.n_estatic_atoms,  # n_osc_ats
            oscillator.VEG_refpos_c,  # spherepos
            oscillator.Map.Core.electrostatic_choice_c,  # calc_choice
            System.positions_c,  # positions
            System.charges_c,  # charges
            System.residues.CoM_c,  # COMs
            System.residues.first_ix_c,  # res_first_ix
            System.residues.last_ix_c,  # res_last_ix
            System.nres,  # n_res
            oscillator.local_atoms_c,  # local_atoms
            oscillator.n_local_atoms,  # n_locals
            RunPars.estatic_range,  # r_sphere
            RunPars.estatic_smooth_range,  # r_smooth
            System.halfbox_c,  # halfbox
            System.boxdims_c,  # boxdims
            oscillator.VEGout_c  # out
        )
