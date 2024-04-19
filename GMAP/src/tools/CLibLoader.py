
# standard lib imports
import ctypes as ct

# local imports
from GMAP.src.tools.PrintTools import devprint as dpr


class Singleton(type):
    """Metaclassing this class makes any class a singleton."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class VEG_CLib(metaclass=Singleton):
    def __init__(self, Printer, RunPars):
        try:
            self.clib = ct.CDLL(str(RunPars.VEG_clib_file))
        except Exception as ex:
            Printer.warning(
                f"\nThe file {RunPars.VEG_clib_file} was requested to be used "
                "as the VEG c-library. However, the file is invalid. "
                "CL_VG_1", True, exception=ex
            )

        self.clib.testadd.argtypes = [
            ct.c_int, ct.c_int
        ]
        self.clib.testadd.restype = ct.c_int

        self.clib.calcPot_perres_mm.argtypes = [
            ct.POINTER(ct.c_int),  # tocalc
            ct.c_int,  # n_osc_ats
            ct.POINTER(ct.c_float),  # spherepos
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
        self.clib.calcPot_perres_mm.restype = None

    def testadd(self, a, b):
        return self.clib.testadd(int(a), int(b))

    def calcPot_perres_mm(self, System, RunPars, oscillator):
        # This function does not return anything directly. Instead,
        # output is saved in the input parameter out.
        # dpr("1")
        # dpr("tocalc", oscillator.electrostatic_atoms)
        # dpr("nosc", oscillator.n_estatic_atoms)
        # dpr("spherepos", oscillator.VEG_refpos)
        # dpr("locals", oscillator.local_atoms)
        # dpr("n_locals", oscillator.n_local_atoms)
        # dpr("r_sphere", RunPars.estatic_range)
        # dpr("r_smooth", RunPars.estatic_smooth_range)
        # dpr("out", oscillator.VEGout)
        self.clib.calcPot_perres_mm(
            oscillator.electrostatic_atoms_c,  # tocalc
            oscillator.n_estatic_atoms,  # n_osc_ats
            oscillator.VEG_refpos_c,  # spherepos
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
        # dpr("2")
