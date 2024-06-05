r"""This module works independently from all other GMAP code.
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
import time
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

    return data


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
        This array represents the Hamiltonian. Initially, the
        frequencies of the chromophores are on the on-diagonal and the
        couplings between the chromophores are on the off-diagonal. This
        might change when ham is sliced.
    """

    ham = np.zeros((size, size))
    ham[np.triu_indices(size)] = data
    ham += np.triu(ham, 1).T
    return ham


def logify_ham(ham, size):
    """Rewrites the off-diagonal elements into log2.

    Parameters
    ----------
    ham : np.ndarray
        This array represents the Hamiltonian. Initially, the
        frequencies of the chromophores are on the on-diagonal and the
        couplings between the chromophores are on the off-diagonal. This
        might change when ham is sliced.
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


def ham_saver(ham, frame, outname, scale, cut):
    """Saves one matrix as (outname)_(idx).pdf.

    The matrix can represent the average of a selection of frames or a
    single frame. The matrix is stored in ham.

    Parameters
    ----------
    ham : np.ndarray
        This array represents the Hamiltonian. Initially, the
        frequencies of the chromophores are on the on-diagonal and the
        couplings between the chromophores are on the off-diagonal. This
        might change when ham is sliced.
    frame : int or list of int
        The index of the frame that is being plotted, or a list of
        frames for an average.
    outname : str
        A name used to name the file that is created.
    scale : str
        This string indicates if the couplings should be displayed
        logarithmically or linearly. If linear it also determines wether
        to lose data or range.
    cut : str
        This is formatted as either four integers seperated by commas or
        as 'False'. If it is 'False' the Hamiltonians in ham_list are
        not cut. Otherwise cut should be x1,x2,y1,y2. This slices the
        elements of ham_list as ham[x1:x2,y1:y2].
    """

    # Setting all diagonal terms to nan.
    off_diag = np.copy(ham)
    np.fill_diagonal(off_diag, np.nan)

    # Setting all off-diagonal terms to nan.
    on_diag_temp = np.diagonal(ham)
    on_diag = np.full_like(ham, np.nan)
    np.fill_diagonal(on_diag, on_diag_temp)

    print(cut)

    fig, ax = plt.subplots()

    plt.xlim(cut[0] - 0.5, cut[1] + 0.5)
    plt.ylim(cut[3] + 0.5, cut[2] - 0.5)

    match scale:
        case "lin_ld":
            # It is necessary that the most negative and positive numbers
            # extend equally far from 0 so that middle value corresponds to
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

        case "lin_lr":
            # This solution extends the positive and negative range out
            # to be equal to +-abs(x) where x is the value furthest from
            # 0 to ensure that 0 is white in the plot.

            end_of_range = max(np.nanmax(off_diag), abs(np.nanmin(off_diag)))
            neg_range = -1 * end_of_range
            pa = ax.imshow(
                on_diag, interpolation='nearest',
                cmap=plt.cm.get_cmap('coolwarm_r'))
            pb = ax.imshow(
                off_diag, interpolation='nearest', cmap=plt.cm.PRGn,
                vmax=end_of_range, vmin=neg_range)

        case "log2":
            # This solution extends the positive and negative range out
            # to be equal to +-abs(x) where x is the value furthest from
            # 0 to ensure that 0 is white in the plot.
            end_of_range = max(np.nanmax(off_diag), abs(np.nanmin(off_diag)))
            neg_range = -1 * end_of_range
            pa = ax.imshow(
                on_diag, interpolation='nearest',
                cmap=plt.cm.get_cmap('coolwarm_r'))
            pb = ax.imshow(
                off_diag, interpolation='nearest', cmap=plt.cm.PRGn,
                vmax=end_of_range, vmin=neg_range)

    cba = plt.colorbar(pa, shrink=0.4, cax=fig.add_axes([0.8, 0.5, 0.03, 0.3]))
    cbb = plt.colorbar(pb, shrink=0.4, cax=fig.add_axes([0.8, 0.1, 0.03, 0.3]))

    fig.subplots_adjust(right=0.75)

    cba.set_label('frequency', rotation=0, y=1.12, labelpad=-22)
    cbb.set_label('coupling', rotation=0, y=1.12, labelpad=-22)
    ax.set_title(outname)

    plt.savefig(f"{outname}_{frame}.pdf")


def verify_cut(cut, size):
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

    Returns
    -------
    cut : str
        This is formatted as either four integers seperated by commas or
        as 'False'. If it is 'False' the Hamiltonians in ham_list are
        not cut. Otherwise cut should be x1,x2,y1,y2. This slices the
        elements of ham_list as ham[x1:x2,y1:y2].
    """
    if cut != "False":
        cut = cut.split(",")
        cut = [int(cutidx) for cutidx in cut]
        if len(cut) != 4:
            raise HamVisException(
                "cut was incorrectly specified. It should either be 'False' "
                "or be 4 positive integers seperated only by commas. The cut "
                f"you provided was {cut} ."
            )
        if (cut[0] >= cut[1] or cut[2] >= cut[3]):
            raise HamVisException(
                "The start of the cut is larger than or equal to end of the "
                f"cut in the x or y direction. You specified: {cut}"
            )
        if (cut[1] > size or cut[3] > size):
            raise HamVisException(
                f"The indice you specified in cut : {cut} is larger than the "
                f"length of the Hamiltonian : {size}. Please select indices "
                "that don't exceed the size of the Hamiltonian."
            )
    else:
        cut = [0, size - 1, 0, size - 1]
    return cut


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

    # file_size is the size in bytes. Divide by 4 to get the size in
    # number of floats. Divide by 2 to be able to loop through it faster
    # if there is only 1 frame. Add 1 to ensure that we also check the
    # float after going over half of the items in the list in the case
    # that we have two frames.
    numbers = range(round(file_size / 4 / 2 + 1))

    # Check all numbers, starting from the second one, if they are integers.
    for number in numbers[1:]:
        candidate = np.fromfile(
            fname, count=1, dtype=np.float32, offset=number * 4
        )[0]

        # If an integer is found, take the indice. Every number that is
        # a whole number times that indice, must be an integer if that number
        # is indeed a frame number. We use whole numbers between 0 and one
        # below the expected number of lines. So in a file with 32 floats,
        # if we suspect that 8 is an integer, we verify that 0, 8, 16 and 24
        # are integers. If they are, the expected number of lines and length
        # of the line are correct.
        if candidate.is_integer():
            line_length = number
            line_amount = round(file_size / line_length)
            candidates = [
                np.fromfile(
                    fname, count=1, dtype=np.float32,
                    offset=line * line_length * 4
                )[0]
                for line in range(line_amount)
            ]
            if all(candidate_.is_integer() for candidate_ in candidates):
                return line_length, line_amount

    # If no line_length was discovered, it must be zero!
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
        This list contains all indices of the frames that the user wants
        plotted.
    """
    if frames == "all":
        frames = range(line_amount)
    else:
        frames_temp = frames.split(",")
        frames = []
        try:
            for idx, frame in enumerate(frames_temp):
                print(idx, frame)
                if frame == "...":
                    frames = [
                        *frames, *range(
                            int(int(frames_temp[idx-1])+1),
                            int(int(frames_temp[idx+1]))
                            )]
                else:
                    frames.append(int(frame))
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
        raise HamVisException(
            f"The frames present in {fname} are {all_frames}. The frames "
            f"specified to be graphed are {frames}. Frames that are not "
            "present in the data cannot be graphed. Please specify only frames"
            f"present in {fname}."
        )


def verify_input(input):
    """Verifies that the some user input is correct and unpacks it.

    Takes a list of str given by the user and unpacks it, as well as
    verify some parts of the input to check if it is correct.

    Parameters
    ----------
    input : list of str
        This contains all arguments passed by the user. Each element
        will be assigned its own variable.

    Returns
    -------
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
        logarithmically or linearly. If linear it also determines wether
        to lose data or range.
    file_type : str
        The filetype of fname. This should be either '.txt' or '.bin'.
    """

    if len(input) != 6:
        raise HamVisException(
            "You did not give the correct number of terms in your command. "
            "A correct command looks like:\n"
            "python HamVis.py fname frames average cut outname\n"
            "fname is the name of the file you want to turn into a figure.\n"
            "frames are the indices of the frames you want to investigate, "
            "seperated by ','. If '...' is given, the range between the "
            "preceeding and following index is filled. So 0,1,2,3 == 0,...,3\n"
            "average should be True or False depending on wether to average "
            "the frames.\n"
            "cut is the area you want to plot given as 'x0,x1,y0,y1', "
            "or 'False' if you dont want to exclude anything. x0 and y0 are "
            "inclusive and x1 and y1 are exclusive, so 0,1,0,1 will only give "
            "entry 0-0 of the Hamiltonian. \n"
            "outname is the name the output files should have.\n"
            "scale determines how the display of the couplings is scaled, this"
            "should either be 'lin_lr', 'lin_ld' or 'log2' to have the "
            "intensities of the couplings be displayed linearly with less "
            "range or data or be displayed with less range logarithmically in "
            "powers 2. \n"
            "Everything should be correctly capitalized. For examples please "
            "see the manual."
        )

    fname, frames, average, cut, outname, scale = input

    if average not in ["False", "True"]:
        raise HamVisException(
            f"The choice of average should be 'False' or 'True', not {average}"
        )
    if scale not in ["lin_lr", "lin_ld", "log2"]:
        raise HamVisException(
            "The supported scales are linear (lin_ld or lin_lr) or "
            f"logarithmic (log2). {scale} is neither of those."
        )

    file_path = Path(fname)
    if not file_path.is_file():
        raise HamVisException(
            f"{fname} does not exist or is not a file. Please specify an "
            "actual file."
        )
    file_type = fname[-4:]
    if file_type not in [".txt", ".bin"]:
        raise HamVisException(
            f"The file extension of {file_type} should be either .txt or .bin "
            "depending on the filetype."
        )

    return fname, frames, average, cut, outname, scale, file_type


def get_size(fname, file_type, line_length):
    match file_type:
        case ".txt":
            try:
                data = np.loadtxt(fname, max_rows=1)[1:]
            except Exception:
                raise HamVisException("There was an issue extracting data "
                                      f"{fname}. Please verify its integrity "
                                      "and that it is in the correct format.")
        case ".bin":
            try:
                data = np.fromfile(
                    fname, dtype=np.float32, count=line_length,
                    )[1:]
            except Exception:
                raise HamVisException("There was an issue extracting data "
                                      f"{fname}. Please verify its integrity "
                                      "and that it is in the correct format.")

    # len(data[0]) is a triangular number, size is the integer used
    # to construct that triangular number.
    size = round(np.sqrt(2 * len(data) + 0.25) - 0.5)

    return size


def HamVis(input):
    """Takes frames of Hamiltonians and saves them as a pdf image.

    It doesn't do much itself, it merely functions as a body to connect
    other functions in this module.

    Parameters
    ----------
    input : list of str
        This contains all arguments passed by the user. Each element
        will be assigned its own variable.
    """

    loadtime = 0
    convert_time = 0
    format_time = 0
    start_time = time.time()

    fname, frames, average, cut, outname, scale, file_type = verify_input(
        input
    )

    line_length, line_amount = find_lines(fname, file_type)
    frames = find_frames(frames, line_amount)
    verify_frames(fname, frames, line_amount)

    size = get_size(fname, file_type, line_length)
    cut = verify_cut(cut, size)
    verify_time = time.time() - start_time

    ham_average = None
    for frame in frames:

        start_loadtime = time.time()
        data = get_data(fname, file_type, frame, line_length)
        loadtime += time.time() - start_loadtime

        start_format_time = time.time()
        ham = format_ham(data, size)
        format_time += time.time() - start_format_time
        if scale == "log2":
            start_convert_time = time.time()
            ham = logify_ham(ham, size)
            convert_time += time.time() - start_convert_time
        if average == "False":
            ham_saver(ham, frame, outname, scale, cut)
        else:
            if ham_average is None:
                ham_average = ham
            else:
                ham_average += ham
    if average == "True":
        ham_average = np.divide(ham_average, len(frames))
        ham_saver(ham_average, frames, outname, scale, cut)

    totaltime = (time.time() - start_time)
    print(f"totaltime : {totaltime} \n convert_time : {convert_time} \n loadtime : {loadtime} \n verify_time : {verify_time} \n format_time : {format_time}")


if __name__ == "__main__":
    warnings.simplefilter("ignore")

    input = sys.argv[1:]
    HamVis(input)
