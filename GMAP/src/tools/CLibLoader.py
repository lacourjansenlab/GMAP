
# standard lib imports
import ctypes as ct


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

    def testadd(self, a, b):
        return self.clib.testadd(int(a), int(b))
