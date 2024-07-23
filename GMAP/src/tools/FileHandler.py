
# standard library imports
import ctypes as ct
import datetime
from pathlib import Path
import sys
import time

# 3rd party lib imports
import numpy as np

# local imports
import GMAP
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.PrintTools as GM_PT


class FileLocations:
    """Deals with paths

    Stores all paths used by the program.

    .. seealso::
        :class:`~GMAP.src.tools.PrintTools.Printer`
            The class involved in printing (copies the print-related paths
            from here).
        :class:`~GMAP.src.tools.ParameterParser.RunPars`
            The class involved in storing other run-based information than
            paths.

    Attributes
    ----------
    script_dir : `pathlib.Path`
        The location where GMAP is installed. (The parent of GMAP.__file__).
    cwd : `pathlib.Path`
        The location from where the program was invoked (the current working
        directory of the terminal/command prompt at submitting command).
    now : datetime.datetime
        The moment at which the program was invoked, in original datetime
        format.
    now_str : str
        The moment at which the program was invoked, as a formatted string of
        the form year-month-day_hour-minute-second.
    sourcedir_hc : `pathlib.Path`
        The hardcoded sourcefiles directory. While the aim of the program is
        to have as few hardcoded things as possible, we need a standard place
        to look for the reference parameter file, where we can store the rest
        of the information
    mapdir_hc : `pathlib.Path`
        Same as with `sourcedir_hc` - some defaults are still hard coded.
    refparfilename_hc : str
        The name of the hardcoded reference parameter file.
    exec_os : str
        The platform on which the program runs. Might be 32- or 64 bit Windows,
        Linux, or MacOS.
    """

    def __init__(self) -> None:
        self.start = time.perf_counter_ns()
        self.script_dir = Path(GMAP.__file__).parent.resolve()
        self.cwd = Path(".").resolve()
        self.now = datetime.datetime.now()
        self.now_str = self.now.strftime("%Y-%m-%d_%H-%M-%S")

        self.sourcedir_hc = self.script_dir / "sourcefiles"
        self.mapdir_hc = self.script_dir / "maps"
        self.refparfilename_hc = "reference_parameters.ref"

        GM_PT.Printer(self)  # initialize the printer!

    def set_exec_os(self):
        """Find and set the exec_os attribute.

        .. seealso::
            find_exec_os
                The function actually identifying the executing os.
        """

        self.exec_os = find_exec_os()


def find_exec_os():
    """Determines which os the system is running on.

    Returns
    -------
    exec_os : str
        The platform on which the program runs. Might be 32- or 64 bit Windows,
        Linux, or MacOS.
    """

    exec_os = None

    if sys.platform == "win32":
        bits = ct.sizeof(ct.c_void_p)*8
        if bits == 32:
            exec_os = "Win32bit"
        elif bits == 64:
            exec_os = "Win64bit"
        else:
            GM_PT.Printer().warning(
                "\nEnvironment was determined to be windows, but it is "
                "neither a"
                f" 32, nor 64 bit version. It appears to be {bits} bit. Please"
                " contact the developers to solve this.",
                "howtogethere", True, GMAPerrclass=GM_Ex.GmapOSError
            )
    elif sys.platform == "darwin":
        exec_os = "MacOS"
    elif sys.platform == "linux":
        exec_os = "Linux"
    else:
        GM_PT.Printer().warning(
            f"\nexecuting OS not recognised... sys.platform = {sys.platform}. "
            "Please contact the developers to solve this. ",
            "howtogethere", True, GMAPerrclass=GM_Ex.GmapOSError
        )

    return exec_os


def get_file(
    Files, dir_parname, file_parname, dir_hc, files_hc,
    cmd_pardict, pardicts=[], parfilelocs=[]
):
    """Determine the path to a file given all input sources

    As there are 4 places that might store information regarding the file's
    path, each of which can contain 2 bits of information, which don't both
    have to be there, the dicision tree is somewhat complex, see the
    devnotes file for a table on what parameters are used in which case.

    The naively found path is returned, but not checked for existence or
    validity. That is a separate step the caller should invoke.

    .. seealso::
        :func:`get_bare_file`
            Does the same, but for files which are not assumed relative to
            a path stored in another parameter.
        :func:`try_file`
            Checks the existence and file-ness of a given path.
        :func:`check_file_readability`
            Checks whether the given file can actually be read.

    Parameters
    ----------
    Files : :class:`FileLocations`
        Contains all currently known paths and other file-related properties.
    dir_parname : str
        The name of the parameter storing the directory path to which the
        desired parameter path is assumed relative to.
    file_parname : str
        The name of the parameter storing the path of the desired file.
    dir_hc : `pathlib.Path`
        In case the parameter in `dir_parname` does not exist in any of the
        given inputs, use this one.
    files_hc : list of `pathlib.Path`
        In case the parameter in `file_parname` does not exist in any of the
        given inputs, use this one.
    cmd_pardict : dict
        The dict storing all parameter choices from the command line.
    pardicts : list of dicts, default=[]
        All dicts storing parameter choices, ordered by importance - if a
        parameter is found in a dict earlier in the list, don't use any
        occurences later in the list.
    parfilelocs : list of `pathlib.Path`, default=[]
        The paths to the files whose contents are in the pardicts list, in the
        same order.

    Returns
    -------
    names : list of `pathlib.Path`
        The path to the desired file.
    file_is_hc : bool
        Whether the dir_hc/file_hc fallback had to be used.
    """

    file_is_hc = False
    dicts = [cmd_pardict]
    flocs = [Files.cwd]

    for dict_, floc in zip(pardicts, parfilelocs):
        if dict_:
            dicts.append(dict_)
            flocs.append(floc.parent)

    for ix, (dict_, floc) in enumerate(zip(dicts, flocs)):
        if dir_parname in dict_:
            dirname = floc / dict_[dir_parname][0]
            for dict_ in dicts[ix:]:
                if file_parname in dict_:
                    filenames = dict_[file_parname]
                    break
            else:
                filenames = files_hc
            break
        elif file_parname in dict_:
            dirname = floc
            filenames = dict_[file_parname]
            break
    else:
        dirname = dir_hc
        filenames = files_hc
        file_is_hc = True

    names = [dirname / name for name in filenames]

    return names, file_is_hc


def get_bare_file(
    Files, file_parname, files_hc, floc_hc, cmd_pardict, pardicts=None,
    parfilelocs=None
):
    """Determine the path to a file given all input sources

    There are 4 places that might store information regarding the file's path,
    which should be considered in a set order.

    The naively found path is returned, but not checked for existence or
    validity. That is a separate step the caller should invoke.

    .. seealso::
        :func:`get_file`
            Does the same, but for files which are assumed relative to a path
            stored in another parameter.
        :func:`try_file`
            Checks the existence and file-ness of a given path.
        :func:`check_file_readability`
            Checks whether the given file can actually be read.

    Parameters
    ----------
    Files : :class:`FileLocations`
        Contains all currently known paths and other file-related properties.
    file_parname : str
        The name of the parameter storing the path of the desired file.
    file_hc : list of `pathlib.Path`
        In case the parameter in `file_parname` does not exist in any of the
        given inputs, use this one.
    floc_hc : `pathlib.Path`
        The base location from where the paths should be taken.
    cmd_pardict : dict
        The dict storing all parameter choices from the command line.
    pardicts : list of dicts, default=[]
        All dicts storing parameter choices, ordered by importance - if a
        parameter is found in a dict earlier in the list, don't use any
        occurences later in the list.
    parfilelocs : list of `pathlib.Path`, default=[]
        The paths to the files whose contents are in the pardicts list, in the
        same order.

    Returns
    -------
    names : list of `pathlib.Path`
        The path to the desired file
    """

    if pardicts is None:
        pardicts = []
    if parfilelocs is None:
        parfilelocs = []

    dicts = [cmd_pardict]
    flocs = [Files.cwd]

    for dict_, floc in zip(pardicts, parfilelocs):
        if dict_:
            dicts.append(dict_)
            flocs.append(floc.parent)

    for dict_, floc in zip(dicts, flocs):
        if file_parname in dict_:
            names = [floc / name for name in dict_[file_parname]]
            break
    else:
        names = [floc_hc / name for name in files_hc]

    return names


def get_def_parfile(
    Files, cmd_pardict, in_parfile=None, in_pardict=None
):
    """
    Given the parameter information on the command line, a new Files instance,
    and, optionally, an input parameters file and its contents, finds out
    the location of the default parameters file.

    If the user specified anything (either the sourcedir or the name of the
    default parameter file), the program checks that. If nothing is present
    there or if it isn't a file, an error is raised, and the program quits.

    Parameters
    ----------
    Files : :class:`FileLocations`
        Contains all currently known paths and other file-related properties.
    cmd_pardict : dict
        The dict storing the parameter choices from the command line.
    in_parfile : `pathlib.Path` or NoneType, default=None
        The filename of the input parameter file.
    in_pardict : dict, default={}
        The parameters supplied in the input parameter file.
    """

    if in_pardict is None:
        in_pardict = {}

    name, file_is_hc = get_file(
        Files, "source_directory", "default_parameter_filename",
        Files.sourcedir_hc, [Files.refparfilename_hc],
        cmd_pardict, [in_pardict], [in_parfile]
    )

    file_found = try_file(name[0])

    if not file_found:
        GM_PT.Printer().warning(
            f"\nThe requested default parameter file {name} could not be "
            "found, or is not a file. "
            "Please make sure you specified it correctly.\n",
            "SU_FH_1", True, GMAPerrclass=GM_Ex.GmapFileNotFoundError
        )

    # We need a file to check if the default file is complete (AIM did this
    # using hard-coded parameters)
    if file_is_hc:
        check_file_found = file_found
    else:
        name = Files.sourcedir_hc / Files.refparfilename_hc
        check_file_found = try_file(name)
        if not check_file_found:
            GM_PT.Printer().warning(
                "\nThe requested default parameter file requires the presence "
                f"of the file {name}, but this file could not be found. "
                "Please make sure you specified it correctly.\n",
                "SU_FH_2", True, GMAPerrclass=GM_Ex.GmapFileNotFoundError
            )

    return file_found


def try_file(fname):
    """Checks if the given location exists, and is a file.

    If so, returns pathlib.Path.resolve(location), otherwise, returns None.
    Does not check whether the file is of a readable format.

    .. seealso::
        :func:`check_file_readability`
            Checks whether the given file can actually be read.

    Parameters
    ----------
    fname : `pathlib.Path`
        The path to check

    Returns
    -------
    fname : `pathlib.Path` or None
        The resolved path, or, if the input doesn't exist, None.
    """

    if fname.is_file():
        return fname.resolve()
    else:
        return None


def check_file_readability(fname, doprint=True, doquit=True):
    """Checks if a given file can be read.

    If not, lets GM_PT.Printer raise the appropriate error.

    .. seealso::
        :func:`try_file`
            Checks the existence and file-ness of a given path.

    Parameters
    ----------
    fname : `pathlib.Path`
        The path to the file to check.
    doprint : bool, default=True
        Whether failure of this test should be reported to the user.
    doquit : bool, default=True
        Whether the program should raise an error if the file fname is
        not readable to the program.

    Returns
    -------
    is_readable : bool
        Whether the file is readable.
    """

    try:
        with open(fname, 'r', encoding='utf-8') as file:
            for _ in file:
                pass
    except UnicodeDecodeError:
        if doprint:
            GM_PT.Printer().warning(
                f"\n The file {fname} is of the wrong type, please make sure "
                "it is a plain text file. ",
                "SU_FH_3", doquit, GMAPerrclass=GM_Ex.GmapUnicodeDecodeError
            )
        return False
    return True


def write_output(RunPars, framenum, outputs):
    """Write the output for a single frame to files.

    Writes all outputs - all (requested) datastructures in all
    (requested) formats.

    Parameters
    ----------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    framenum : int
        The number of the frame currently being written
    outputs : dict of str: `np.ndarray` pairs
        The outputs the program is requested to generate. Currently
        contains hamiltonian and dipole arrays.
    """

    framenum_arr = np.array([framenum], dtype='float32')

    if "ham" in RunPars.output_data:
        hamiltonian = outputs["hamiltonian"]
        hamiltonian *= RunPars.hamiltonian_multiplier
        reshaped = hamiltonian[np.triu_indices_from(hamiltonian)]
        write_single(
            RunPars, framenum, framenum_arr,
            RunPars.output_hamiltonian_filename, reshaped
        )

    if "ene" in RunPars.output_data:
        energies = outputs["energies"]
        energies *= RunPars.energies_multiplier
        write_single(
            RunPars, framenum, framenum_arr, RunPars.output_energies_filename,
            energies
        )

    if "dip" in RunPars.output_data:
        dipoles = outputs["dipoles"]
        dipoles *= RunPars.dipoles_multiplier
        reshaped = dipoles.T.flatten()
        write_single(
            RunPars, framenum, framenum_arr,
            RunPars.output_dipole_filename, reshaped
        )


def write_single(RunPars, framenum, framenum_arr, fname, data):
    """Write a single datastructure to files of given name.

    Writes to all different requested formats at once.

    Parameters
    ----------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    framenum : int
        The number of the frame currently being written
    framenum_arr : `np.ndarray`
        The framenumber as float32 array, ready for binary writing
    fname : `pathlib.Path`
        The name + location of the file to which to write. This filename
        should not include the extension!
    data : `np.ndarray`
        The data that should be written to the file.
    """

    if "bin" in RunPars.output_format:
        with open(fname.parent / f"{fname.name}.bin", "ab") as fhand:
            framenum_arr.tofile(fhand)  # write frame number
            data.tofile(fhand)  # write data itself (Ham or Dip or ...)

    if "txt" in RunPars.output_format:
        with open(
            fname.parent / f"{fname.name}.txt", "a", encoding='utf-8'
        ) as fhand:
            fhand.write(f"{framenum} ")  # write frame number
            # data = np.round(data, decimals=6)
            decs = 6
            data = np.rint(data*10**decs)/(10**decs)
            # write data itself (Ham or Dip or ...)
            # data.tofile(fhand, sep=" ", format="%#.6g")
            data.tofile(fhand, sep=" ")
            fhand.write("\n")


def clear_output(RunPars):
    """Prepare an empty file for each output

    If files already exist, clears them. If not, creates them.

    Parameters
    ----------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    """

    if "ham" in RunPars.output_data:
        clear_single(RunPars, RunPars.output_hamiltonian_filename)
    if "dip" in RunPars.output_data:
        clear_single(RunPars, RunPars.output_dipole_filename)
    if "ene" in RunPars.output_data:
        clear_single(RunPars, RunPars.output_energies_filename)


def clear_single(RunPars, fname):
    """Clears any file if it exists prior to writing

    A file shouldn't contain anything when first appended to.

    Parameters
    ----------
    RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    fname : `pathlib.Path`
        The name + location of the file to which to write. This filename
        should not include the extension!
    """

    if "bin" in RunPars.output_format:
        with open(fname.parent / f"{fname.name}.bin", "wb") as _:
            pass
    if "txt" in RunPars.output_format:
        with open(fname.parent / f"{fname.name}.txt", "w") as _:
            pass
