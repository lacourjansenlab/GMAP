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

# 3rd party library imports
import matplotlib.pyplot as plt
import numpy as np
from numpy.ma import masked_array


class HamVisException(Exception):
	__module__ = "builtins"

	def __init__(self, message):
		sys.tracebacklimit = 0


def get_data(fname):
	r"""Gets the data from fname and returns it as a list of lists.

	The data from the file must be in a .txt format and formatted as
	specified in the documentation. .txt files containing Hamiltonians
	of frames created by GEM should work.

	Parameters
	----------
	fname : str
		The name of the file from where data is extracted.

	Returns
	-------
	data : list of list of float
		Each sublist represents a frame each float within each sublist
		represents either a frequency or a coupling, for a more detailed
		overview please read the manual.
	size : int
		The size that the hamiltonian will have. As it is a size * size
		matrix.
	"""
	try:
		with open(fname) as fhand:
			data = [frame.split() for frame in fhand.readlines()]
		data = [[float(number) for number in frame][1:] for frame in data]
		# len(data[0]) is a triangular number, size is the integer used
		# to construct that triangular number.
		size = round(np.sqrt(2 * len(data[0]) + 0.25) - 0.5)
	except Exception:
		raise HamVisException(
			f"There was an error extracting data from {fname}, please verify "
			"that it is a Hamiltonian in .txt format as described in the "
			"manual."
		) from None

	return data, size


def format_ham(data, size):
	"""Formats the data into the shape of the hamiltonian.

	Parameters
	----------
	data : list of list of float
		Each sublist represents a frame each float within each sublist
		represents either a frequency or a coupling, for a more detailed
		overview please read the manual.
	size : int
		The size that the hamiltonian will have. As it is a size * size matrix.

	Returns
	-------
	ham : np.ndarray
		This array is the hamiltonian, with frequencies on the diagonal
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
		This array is the hamiltonian, with frequencies on the diagonal
		and couplings on the off-diagonal.
	size : int
		The size that the hamiltonian will have. As it is a size * size
		matrix.

	Returns
	-------
	logs : np.ndarray
		This is the same as ham, but the off-diagonal components are
		written as log2.
	"""
	try:
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

	except Exception:
		raise HamVisException(
			"There was an issue rewriting the elements of the Hamiltonian "
			"into exponentials."
		) from None
	return logs


def ham_saver(ham, idx, outname):
	"""Saves one matrix as (outname)_(idx).pdf.

	The matrix can represent the average of a selection of frames or a
	single frame. The matrix is stored in ham.

	Parameters
	----------
	ham : np.ndarray
		This array is the hamiltonian, with frequencies on the diagonal
		and couplings on the off-diagonal.
	idx : int
		The index of the frame that is being plotted, or a list of
		frames for an average.
	outname : str
		A name used to name the file that is created.
	"""

	try:
		off_diag = masked_array(ham, ham > 100)
		on_diag = masked_array(ham, ham <= 100)

		fig, ax = plt.subplots()
		pa = ax.imshow(
			on_diag, interpolation='nearest', cmap=plt.cm.get_cmap('coolwarm_r'))
		cba = plt.colorbar(pa, shrink=0.4, cax=fig.add_axes([0.8, 0.5, 0.03, 0.3]))

		pb = ax.imshow(
			off_diag, interpolation='nearest', cmap=plt.cm.PRGn
		)
		cbb = plt.colorbar(pb, shrink=0.4, cax=fig.add_axes([0.8, 0.1, 0.03, 0.3]))
		fig.subplots_adjust(right=0.75)

		cba.set_label('frequency', rotation=0, y=1.12, labelpad=-22)
		cbb.set_label('coupling', rotation=0, y=1.12, labelpad=-22)
		ax.set_title(outname)

		plt.savefig(f"{outname}_{idx}.pdf")
	except Exception:
		raise HamVisException(
			f"There was an issue saving the Hamiltonian of frame {idx} as an "
			"image."
		) from None


def format_frame_selection(frames, data):
	"""Turns the frames from a string into a list of integers.

	If frames contains integers seperated by commas, the integers will
	correspond to the frames of the data that will be processed. A list
	of them is returned. If frames is "all", a list containing all
	indices in frames is returned, starting at 1 for the first frame.

	Parameters
	----------
	frames : str
		Contains integers split by commas or is the string "all". If if
		is integers split by commas, the integers will correspond to the
		one-based indices frames of the data that will be processed.
		"all" will create a list containing all one-based indices of
		all of the frames contained in data for the first
		frame.
	data : list of list of float
		Each sublist represents a frame each float within each sublist
		represents either a frequency or a coupling, for a more detailed
		overview please read the manual.

	Returns
	-------
	frames_int : list of int
		Contains a list of integers that correspond to a one-based index
		frames of the data.
	"""

	if frames == "all":
		frames_int = range(1, len(data) + 1)
	else:
		frames = list(frames.split(","))
		try:
			frames_int = [int(frame) for frame in frames]
		except ValueError:
			raise HamVisException(
				"Frames can only be given as integers and seperated by "
				"nothing but a comma. To select all frames, specify 'all'."
			) from None
		for frame in frames_int:
			if frame > len(data):
				raise HamVisException(
					"A frame was selected for rendering that does not exist "
					"in the selected sourcefile."
				)
	return frames_int


def average_ham(average, ham_list, frames):
	"""Returns an updated ham_list and frames if average is 'True'.

	The function changes frames and ham_list depending on wether on the
	value of average. If True, frames will be a list that contains the
	input list as its only entry and ham_list will only have one entry,
	which will be the average of the input. ham_list and frames remain
	the same if average is 'False'

	Parameters
	----------
	average : str
		This should be 'False' or 'True'. If this is 'True' the function
		average all entries in ham_list and puts frames into a sublist.
	ham_list : list of np.ndarray of float
		This is a list of numpy arrays. The numpy arrays each contain a
		matrix that represents one Hamiltonian.
	frames : str
		Contains integers split by commas or is the string "all". If if
		is integers split by commas, the integers will correspond to the
		one-based indices frames of the data that will be processed.
		"all" will create a list containing all one-based indices of
		all of the frames contained in data for the first
		frame.

	Returns
	-------
	ham_list : list of np.ndarray of float
		This is a list of numpy arrays. The numpy arrays each contain a
		matrix that represents one Hamiltonian.
	frames : str
		Contains integers split by commas or is the string "all". If if
		is integers split by commas, the integers will correspond to the
		one-based indices frames of the data that will be processed.
		"all" will create a list containing all one-based indices of
		all of the frames contained in data for the first
		frame.
	"""
	if average == "True":
		ham_list = [sum(ham_list) / len(ham_list)]
		frames = [frames]
	else:
		if average != "False":
			raise HamVisException(
				f"average should be True or False, not {average}."
			)
	return ham_list, frames


def cut_ham(cut, ham_list):
	"""This function slices the hamiltonian so only a part is shown.

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
	ham_list : list of np.ndarray of float
		This is a list of numpy arrays. The numpy arrays each contain a
		matrix that represents one Hamiltonian.

	Returns
	-------
	ham_list : list of np.ndarray of float
		This is a list of numpy arrays. The numpy arrays each contain a
		matrix that represents one Hamiltonian.
	"""
	try:
		if cut != "False":
			cut = list(cut.split(","))
			cut = [int(cutidx) for cutidx in cut]
			if len(cut) != 4:
				raise Exception
			ham_list = [ham[cut[2]:cut[3], cut[0]:cut[1]] for ham in ham_list]
	except Exception:
		raise HamVisException(
			"cut was incorrectly specified, please see the manual for more "
			"details."
		) from None
	return ham_list


def HamVis(fname, frames, average, cut, outname):
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
		average all entries in ham_list and puts frames into a sublist.
	cut : str
		This is formatted as either four integers seperated by commas or
		as 'False'. If it is 'False' the Hamiltonians in ham_list are
		not cut. Otherwise cut should be x1,x2,y1,y2. This slices the
		elements of ham_list as ham[x1:x2,y1:y2].
	outname : str
		A name used to name the file that is created.
	"""
	ham_list = []
	data, size = get_data(fname)
	frames = format_frame_selection(frames, data)

	for frame in frames:
		ham = format_ham(data[frame - 1], size)
		ham = logify_ham(ham, size)
		ham_list.append(ham)

	ham_list = cut_ham(cut, ham_list)
	ham_list, frames = average_ham(average, ham_list, frames)

	for idx, ham in zip(frames, ham_list):
		ham_saver(ham, idx, outname)


if __name__ == "__main__":
	warnings.simplefilter("ignore")

	if len(sys.argv) != 6:
		print(
			"You did not give the correct number of terms in your command. "
			"A correct command looks like:\n"
			"python HamVis.py fname frames average cut outname\n"
			"fname is the name of the file you want to turn into a figure.\n"
			"frames are the frames you want to investigate, seperated by ','.\n"
			"average should be True or False depending on wether to average "
			"the frames.\n"
			"cut is the area you want to plot given as 'x0,x1,y0,y1', "
			"or 'False' if you dont want to exclude anything.'\n"
			"outname is the name the output files should have.\n\n"
			"For examples please see the manual."
		)
	else:
		fname, frames, average, cut, outname = sys.argv[1:]
		HamVis(fname, frames, average, cut, outname)
