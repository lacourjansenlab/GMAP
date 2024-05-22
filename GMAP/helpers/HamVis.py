r"""This module works independantly from all other GMAP code.
Invoking this module with the correct arguments will create images of
the Hamiltonians stored in the selected file.

The functions in this module are not tested with pytest because this
module is not supposed to interact with the rest of GMAP, nor be
modified. If this changes in the future this module should be subject to
testing.

This module can be called with:

python HamVis.py fname frames average cut outname
    fname is the name of the file you want to turn into a figure.
    frames are the frames you want to investigate, seperated by ','.
    average should be True or False depending on wether to average
    the frames.
    cut is the area you want to plot given as 'x0,x1,y0,y1',
    or 'False' if you dont want to exclude anything.'
    outname is the name the output files should have.
    For examples please see the manual.

"""

# standard libary imports
import sys
import warnings
from pathlib import Path

# 3rd party library imports
import matplotlib.pyplot as plt
import numpy as np


class HamVisException(Exception):
    __module__ = "builtins"

    def __init__(self, message):
        sys.tracebacklimit = 0


def get_data(fname, file_type, frame, line_length):
    r"""Gets the data from fname and returns it as a list of lists.

    The data from the file must be in a .txt format and formatted as
    specified in the documentation. .txt files containing Hamiltonians
    of frames created by GEM should work.

    Parameters
    ----------
    fname : str
        The name of the file from where data is extracted.
    file_type : str
       The filetype of fname. This should be either '.txt' or '.bin'.
    frame : int
        The index of the frame from which data is extracted,
    line_length : int or None
        This is the length of the Hamiltonians in fname. It is the
        number of bytes in case file_type is .bin. It is None if
        file_type is .txt.

    Returns
    -------
    data : list of list of float
        Each sublist represents a frame each float within each sublist
        represents either a frequency or a coupling, for a more detailed
        overview please read the manual.
    size : int
        The size that the Hamiltonian will have. As it is a size * size
        matrix.
    """

    # try:
    match file_type:
        case ".txt":
            try:
                data = np.loadtxt(fname, skiprows=frame, max_rows=1)[1:]
            except Exception:
                raise HamVisException("There was an issue extracting data "
                                      f"{fname}. Please verify its integrity "
                                      "and that it is in the correct format.")
        case ".bin":
            try:
                skipped_bytes = round((frame) * line_length * 4)
                data = np.fromfile(fname, dtype=np.float32, count=line_length,
                                   offset=skipped_bytes
                                   )[1:]
            except Exception:
                raise HamVisException("There was an issue extracting data "
                                      f"{fname}. Please verify its integrity "
                                      "and that it is in the correct format.")

    # len(data[0]) is a triangular number, size is the integer used
    # to construct that triangular number.
    size = round(np.sqrt(2 * len(data) + 0.25) - 0.5)

    return data, size


def format_ham(data, size):
    """Formats the data into the shape of the Hamiltonian.

    Parameters
    ----------
    data : list of list of float
        Each sublist represents a frame each float within each sublist
        represents either a frequency or a coupling, for a more detailed
        overview please read the manual.
    size : int
        The size that the Hamiltonian will have. As it is a size * size matrix.

    Returns
    -------
    ham : np.ndarray
        This array is the Hamiltonian, with frequencies on the diagonal
        and couplings on the off-diagonal.
    """

    try:
        ham = np.zeros((size, size))
        ham[np.triu_indices(size)] = data
        ham += np.triu(ham, 1).T
    except Exception:
        raise HamVisException(
            "There was an error formatting the data into a matrix."
        ) from None
    return ham


def logify_ham(ham, size):
    """Rewrites the off-diagonal elements into log2.

    Parameters
    ----------
    ham : np.ndarray
        This array is the Hamiltonian, with frequencies on the diagonal
        and couplings on the off-diagonal.
    size : int
        The size that the Hamiltonian will have. As it is a size * size
        matrix.

    Returns
    -------
    logs : np.ndarray
        This is the same as ham, but the off-diagonal components are
        written as log2.
    """

    # Sets all very small items, smaller than minimum, to minimum.
    minimum = 0.001
    ham[abs(ham) < minimum] = minimum

    # Save the diagonal elements of the Hamiltonian.
    diag = np.diag(ham)

    # Takes the absolute value of items in ham and turns them into
    # log2.
    logs = np.log2(np.abs(ham))

    # This subtracts the log of minimum from all items. Items that
    # were minimum or smaller are now thus zero.
    logs -= np.log2(minimum)

    # Makes items that were negative in ham negative again.
    logs[ham < 0] *= -1

    # Restores the diagonal items to not be in log2 again.
    logs[np.diag_indices(size)] = diag

    return logs


def ham_saver(ham, frame, outname, scale):
    """Saves one matrix as (outname)_(idx).pdf.

    The matrix can represent the average of a selection of frames or a
    single frame. The matrix is stored in ham.

    Parameters
    ----------
    ham : np.ndarray
        This array is the Hamiltonian, with frequencies on the diagonal
        and couplings on the off-diagonal.
    frame : int or list of int
        The index of the frame that is being plotted, or a list of
        frames for an average.
    outname : str
        A name used to name the file that is created.
    scale : str
        This string indicates if the couplings should be displayed
        logarithmically or linearly.
    """

    # Setting all diagonal terms to nan.
    off_diag = np.copy(ham)
    np.fill_diagonal(off_diag, np.nan)

    # Setting all off-diagonal terms to nan.
    on_diag_temp = np.diagonal(ham)
    on_diag = np.full_like(ham, np.nan)
    np.fill_diagonal(on_diag, on_diag_temp)

    # # Masking the nan values in the matrices.
    # on_diag = ma.masked_array(on_diag, np.isnan(on_diag))
    # off_diag = ma.masked_array(off_diag, np.isnan(off_diag))

    fig, ax = plt.subplots()

    match scale:
        case "lin":
            # It is necessary that the most negative and positive numbers
            # extend equally far from zero so that middle value corresponds to
            # white in the plot. This is technically not a completely physical
            # but there is no perfect solution.

            end_of_range = min(np.nanmax(off_diag), abs(np.nanmin(off_diag)))
            neg_range = -1 * end_of_range
            pa = ax.imshow(
                on_diag, interpolation='nearest',
                cmap=plt.cm.get_cmap('coolwarm_r'))
            pb = ax.imshow(
                off_diag, interpolation='nearest', cmap=plt.cm.PRGn,
                vmax=end_of_range, vmin=neg_range)

        case "log2":
            pa = ax.imshow(
                on_diag, interpolation='nearest',
                cmap=plt.cm.get_cmap('coolwarm_r'))
            pb = ax.imshow(
                off_diag, interpolation='nearest', cmap=plt.cm.PRGn
            )

    cba = plt.colorbar(pa, shrink=0.4, cax=fig.add_axes([0.8, 0.5, 0.03, 0.3]))
    cbb = plt.colorbar(pb, shrink=0.4, cax=fig.add_axes([0.8, 0.1, 0.03, 0.3]))

    fig.subplots_adjust(right=0.75)

    cba.set_label('frequency', rotation=0, y=1.12, labelpad=-22)
    cbb.set_label('coupling', rotation=0, y=1.12, labelpad=-22)
    ax.set_title(outname)

    plt.savefig(f"{outname}_{frame}.pdf")


# def format_frame_selection(frames, data):
#     """Turns 'frames' from a string into a list of integers.

#     If frames contains integers seperated by commas, the integers will
#     correspond to the frames of the data that will be processed. A list
#     of them is returned. If frames is "all", a list containing all
#     indices in frames is returned, starting at 1 for the first frame.

#     Parameters
#     ----------
#     frames : str
#         Contains integers split by commas or is the string "all". If if
#         is integers split by commas, the integers will correspond to the
#         one-based indices frames of the data that will be processed.
#         "all" will create a list containing all one-based indices of
#         all of the frames contained in data for the first
#         frame.
#     data : list of list of float
#         Each sublist represents a frame each float within each sublist
#         represents either a frequency or a coupling, for a more detailed
#         overview please read the manual.

#     Returns
#     -------
#     frames_int : list of int
#         Contains a list of integers that correspond to frames of the
#         data.
#     """

#     if frames == "all":
#         frames_int = range(1, len(data) + 1)
#     else:
#         frames = frames.split(",")
#         try:
#             frames_int = [int(frame) for frame in frames]
#         except ValueError:
#             raise HamVisException(
#                 "Frames can only be given as integers and seperated by "
#                 "nothing but a comma. To select all frames, specify 'all'."
#             ) from None
#         for frame in frames_int:
#             if frame > len(data):
#                 raise HamVisException(
#                     "A frame was selected for rendering that does not exist "
#                     "in the selected sourcefile."
#                 )
#     return frames_int


# def average_ham(average, ham, frames):
#     """Returns an updated ham_list and frames if average is 'True'.

#     The function changes frames and ham_list depending on wether on the
#     value of average. If True, frames will be a list that contains the
#     input list as its only entry and ham_list will only have one entry,
#     which will be the average of the input. ham_list and frames remain
#     the same if average is 'False'

#     Parameters
#     ----------
#     average : str
#         This should be 'False' or 'True'. If this is 'True' the function
#         average all entries in ham_list and puts frames into a sublist.
#     ham : np.ndarray
#         This array is the Hamiltonian, with frequencies on the diagonal
#         and couplings on the off-diagonal.
#     frames : str
#         Contains integers split by commas or is the string "all". If if
#         is integers split by commas, the integers will correspond to the
#         one-based indices frames of the data that will be processed.
#         "all" will create a list containing all one-based indices of
#         all of the frames contained in data for the first
#         frame.

#     Returns
#     -------
#     ham : np.ndarray
#         This array is the Hamiltonian, with frequencies on the diagonal
#         and couplings on the off-diagonal.
#     frames : str
#         Contains integers split by commas or is the string "all". If if
#         is integers split by commas, the integers will correspond to the
#         one-based indices frames of the data that will be processed.
#         "all" will create a list containing all one-based indices of
#         all of the frames contained in data for the first
#         frame.
#     """
#     if average == "True":
#         ham = [sum(ham) / len(ham)]
#         frames = [frames]
#     else:
#         if average != "False":
#             raise HamVisException(
#                 f"average should be True or False, not {average}."
#             )
#     return ham, frames


def cut_ham(cut, size, ham):
    """This function slices the Hamiltonian so only a part is shown.

    This is mostly intended to allow the user to zoom in on certain
    sections of a Hamiltonian. It slices all of the Hamiltonians of
    ham_list at the same time according to cut. If cut is 'False', the
    function returns simply the original ham_list.

    Parameters
    ----------
    cut : str
        This is formatted as either four integers seperated by commas or
        as 'False'. If it is 'False' the Hamiltonians in ham_list are
        not cut. Otherwise cut should be x1,x2,y1,y2. This slices the
        elements of ham_list as ham[x1:x2,y1:y2].
    size : int
        The size that the Hamiltonian will have. As it is a size * size
        matrix.
    ham_list : np.ndarray of float
        The numpy array contains a matrix that represents one Hamiltonian.

    Returns
    -------
    ham : np.ndarray
        This array is the Hamiltonian, with frequencies on the diagonal
        and couplings on the off-diagonal.
    """
    if cut != "False":
        cut_list = cut.split(",")
        cut_list = [int(cutidx) for cutidx in cut_list]
        if (cut_list[0] >= cut_list[1] or cut_list[2] >= cut_list[3]):
            raise HamVisException("The start of the cut is larger than or "
                                  "equal to end of the cut in the x or y "
                                  f"direction. You specified: {cut}")
        if (cut_list[1] > size or cut_list[3] > size):
            raise HamVisException(f"The indice you specified in cut : {cut} "
                                  "is larger than the length of the "
                                  f"Hamiltonian : {size}. Please select "
                                  "indices that don't exceed the size of the "
                                  "Hamiltonian.")
        if len(cut_list) != 4:
            raise HamVisException(
                "cut was incorrectly specified. It should either be 'False' "
                "or be 4 positive integers seperated only by commas. The cut "
                f"you provided was {cut} ."
            )
        ham = ham[cut_list[2]:cut_list[3], cut_list[0]:cut_list[1]]
    return ham


def find_lines_bin(fname, file_size):
    """A subroutine for find_lines specifically for binary files.

    Parameters
    ----------
    fname : str
        The name of the file from where data is extracted.
    file_size :int
        This is the number of bytes that make up fname.

    Returns
    -------
    line_length : int or None
        This is the length of the Hamiltonians in fname. It is the
        number of bytes in case file_type is .bin. It is None if
        file_type is .txt.
    line_amount : int
        This is the number of lines in fname with content in a .txt
        file. It is always the number of Hamiltonians contained in
        fname.
    """

    numbers = range(round(file_size / 4 / 2 + 1))
    for number in numbers[1:]:
        candidate = np.fromfile(fname, count=1, dtype=np.float32,
                                offset=number * 4)[0]
        if candidate.is_integer():
            line_length = number
            line_amount = round(file_size / line_length)
            candidates = [np.fromfile(fname, count=1, dtype=np.float32,
                                      offset=line * line_length * 4)[0] for
                          line in range(line_amount)]
            if all(candidate_.is_integer() for candidate_ in candidates):
                return line_length, line_amount

    line_length = round(file_size / 4)
    line_amount = 1
    return line_length, line_amount


def find_lines(fname, file_type):
    """Discovers the length and amount of lines in fname

    Parameters
    ----------
    fname : str
        The name of the file from where data is extracted.
    file_type : str
        The filetype of fname. This should be either '.txt' or '.bin'.

    Returns
    -------
    line_length : int or None
        This is the length of the Hamiltonians in fname. It is the
        number of bytes in case file_type is .bin. It is None if
        file_type is .txt.
    file_type : str
        The filetype of fname. This should be either '.txt' or '.bin'.
    """
    match file_type:
        case ".bin":
            file_path = Path(fname)
            # number of floats in file
            file_size = round(file_path.stat().st_size / 4)
            line_length, line_amount = find_lines_bin(fname, file_size)
        case ".txt":
            with open(fname) as fhand:
                line_length = None
                line_amount = 0
                for _ in fhand:
                    line_amount += 1
    return line_length, line_amount


def find_frames(frames, line_amount):
    """This finds all frames that the user wants to be processed

    Parameters
    ----------
    frames : str
        Contains integers split by commas or is the string "all". If if
        is integers split by commas, the integers will correspond to the
        one-based indices frames of the data that will be processed.
        "all" will create a list containing all one-based indices of
        all of the frames contained in data for the first
        frame.
    line_amount : int
        This is the number of lines in fname with content in a .txt
        file. It is always the number of Hamiltonians contained in
        fname.

    Returns
    -------
    frames : list of int
        This list contains all indices of the 
    """
    if frames == "all":
        frames = range(line_amount)
    else:
        frames = frames.split(",")
        try:
            frames = [int(frame) for frame in frames]
        except ValueError:
            raise HamVisException(
                "Frames can only be given as integers and seperated by "
                "nothing but a comma. To select all frames, specify 'all'."
            ) from None
    return frames


def verify_frames(fname, frames, line_amount):
    """This verifies that the given frames do exist in the given file.

    Parameters
    ----------
    fname : str
        The name of the file from where data is extracted.
    frames : str
        Contains integers split by commas or is the string "all". If if
        is integers split by commas, the integers will correspond to the
        one-based indices frames of the data that will be processed.
        "all" will create a list containing all one-based indices of
        all of the frames contained in data for the first
        frame.
    line_amount : int
        This is the number of lines in fname with content in a .txt
        file. It is always the number of Hamiltonians contained in
        fname.
    """
    all_frames = range(line_amount)

    if not set(frames).issubset(set(all_frames)):
        raise HamVisException(f"The frames present in {fname} are "
                              f"{all_frames}. The frames specified to be "
                              f"graphed are {frames}. Frames that are not "
                              "present in the data cannot be graphed. "
                              "Please specify only frames present in "
                              f"{fname}.")


def verify_file_is_correct(fname):
    """Verifies that the filename exists and is .bin or .txt.

    The filetype is discovered based on the extension. The filetype that
    is found is also returned.

    Parameters
    ----------
    fname : str
        The name of the file from where data is extracted.

    Returns
    -------
    file_type : str
        The filetype of fname. This should be either '.txt' or '.bin'.
    """

    file_path = Path(fname)
    if not file_path.is_file():
        raise HamVisException(f"{fname} does not exist or is not a file."
                              "Please specify an actual file.")
    file_type = fname[-4:]
    if file_type not in [".txt", ".bin"]:
        raise HamVisException(f"The file extension of {file_type} should be "
                              "either .txt or .bin depending on the "
                              "filetype.")

    return file_type


def verify_scale(scale):
    """Verifies that the scale given by the user is supported.

    Parameters
    ----------
    scale : str
        This string indicates if the couplings should be displayed
        logarithmically or linearly.
    """
    if scale not in ["lin", "log2"]:
        raise HamVisException("The supported scales are linear (lin) and "
                              f"logarithmic (log2). {scale} is neither of "
                              "those.")


def HamVis(fname, frames, average, cut, outname, scale):
    """Saves frames of Hamiltonians and saves them as a pdf image.

    It doesn't do much itself, it merely functions as a body to connect
    other functions in this module.

    Parameters
    ----------
    fname : str
        The name of the file from where data is extracted.
    frames : str
        Contains integers split by commas or is the string "all". If if
        is integers split by commas, the integers will correspond to the
        one-based indices frames of the data that will be processed.
        "all" will create a list containing all one-based indices of
        all of the frames contained in data for the first
        frame.
    average : str
        This should be 'False' or 'True'. If this is 'True' the function
        average all frames in fname that are listed in the frames
        variable.
    cut : str
        This is formatted as either four integers seperated by commas or
        as 'False'. If it is 'False' the Hamiltonians in ham_list are
        not cut. Otherwise cut should be x1,x2,y1,y2. This slices the
        elements of ham_list as ham[x1:x2,y1:y2].
    outname : str
        A name used to name the file that is created.
    scale : str
        This string indicates if the couplings should be displayed
        logarithmically or linearly.
    """

    file_type = verify_file_is_correct(fname)
    verify_scale(scale)

    line_length, line_amount = find_lines(fname, file_type)
    frames = find_frames(frames, line_amount)

    verify_frames(fname, frames, line_amount)

    ham_average = None
    for frame in frames:
        data, size = get_data(fname, file_type, frame, line_length)
        ham = format_ham(data, size)
        if scale == "log2":
            ham = logify_ham(ham, size)
        ham = cut_ham(cut, size, ham)
        if average == "False":
            ham_saver(ham, frame, outname, scale)
        else:
            if ham_average is None:
                ham_average = ham
            else:
                ham_average += ham
    if average == "True":
        ham_average = np.divide(ham_average, len(frames))
        ham_saver(ham_average, frames, outname, scale)


if __name__ == "__main__":
    warnings.simplefilter("ignore")

    if len(sys.argv) != 7:
        print(
            "You did not give the correct number of terms in your command. "
            "A correct command looks like:\n"
            "python HamVis.py fname frames average cut outname\n"
            "fname is the name of the file you want to turn into a figure.\n"
            "frames are the frames you want to investigate, seperated by ,.\n"
            "average should be True or False depending on wether to average "
            "the frames.\n"
            "cut is the area you want to plot given as 'x0,x1,y0,y1', "
            "or 'False' if you dont want to exclude anything.'\n"
            "outname is the name the output files should have.\n"
            "scale determines how the display of the couplings is scaled, this"
            "should either be 'lin' or log2 to have the intensities of the "
            "couplings be displayed linearly or as logarithmically in powers "
            "2.\n"
            "For examples please see the manual."
        )
    else:
        fname, frames, average, cut, outname, scale = sys.argv[1:]
        HamVis(fname, frames, average, cut, outname, scale)
