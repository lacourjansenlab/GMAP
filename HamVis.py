r"""Usage description goes here
"""

# standard libary imports
import numpy as np
from numpy.ma import masked_array
import matplotlib.pyplot as plt
import sys
import warnings


class HamVisException(Exception):
	__module__ = "builtins"

	def __init__(self, message):
		sys.tracebacklimit = 0


def get_data(fname):
	r"""Gets the data from fname and returns it as a list of lists.

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
		The size that the hamiltonian will have. As it is a size * size matrix.
	"""
	try:
		with open(fname) as fhand:
			data = fhand.readlines()   # Hammy.txt is corrupted past line 28
		data = [frame.split() for frame in data]
		data = [[float(number) for number in frame][1:] for frame in data]

		size = int(np.sqrt(2 * len(data[0]) + 0.25) + 0.5) - 1  # triangle sum
	except Exception:
		raise HamVisException(
			f"There was an error extracting data from {fname}, please verify "
			"that it is a Hamiltonian in .txt format as described in the "
			"manual."
		) from None

	return data, size


def format_hammy(data, size):
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
	ham : 'ndarray'
		This array is the hamiltonian, with frequencies on the diagonal
		and couplings on the offdiagonal.
	"""
	try:
		ham = np.zeros((size, size))
		ham[np.triu_indices(size)] = data
		ham = np.triu(ham) + np.tril(ham.T, -1)
	except Exception:
		raise HamVisException(
			"There was an error formatting the data into a matrix."
		) from None
	return ham


def logify_hammy(ham, size):
	"""Rewrites the off-diagonal elements into powers of 2.

	Parameters
	----------
	ham : 'ndarray'
		This array is the hamiltonian, with frequencies on the diagonal
		and couplings on the off-diagonal.
	size : int
		The size that the hamiltonian will have. As it is a size * size
		matrix.

	Returns
	-------
	logs : 'ndarray'
		This is the same as ham, but the off-diagonal components are
		written as powers of 2.
	"""
	try:
		minimum = 0.001
		ham[abs(ham) < minimum] = 0
		diag = np.diag(ham)
		logs = np.log2(np.abs(ham))
		logs -= np.log2(minimum)
		logs[ham < 0] *= -1

		logs[np.diag_indices(size)] = diag
	except Exception:
		raise HamVisException(
			"There was an issue rewriting the elements of the Hamiltonian "
			"into exponentials."
		) from None
	return logs


def hammy_saver(hammy, idx, outname):
	"""Saves one matrix as (outname)_(idx).pdf.

	The matrix can represent the average of a selection of frames or a
	single frame.

	Parameters
	----------
	ham : 'ndarray'
		This array is the hamiltonian, with frequencies on the diagonal
		and couplings on the off-diagonal.
	idx : int
		The index of the frame that is being plotted, or a list of
		frames for an average.
	outname : str
		A name used to name the file that is created.
	"""

	try:
		off_diag = masked_array(hammy, hammy > 100)
		on_diag = masked_array(hammy, hammy <= 100)

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
	indexes in frames is returned, starting at 1 for the first frame.

	Parameters
	----------
	frames : str
		Contains integers split by commas or is the string "all". If if
		is integers split by commas, the integers will correspond to the
		one-based indexes frames of the data that will be processed.
		"all" will create a list containing all one-based indexes of
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
		for frame in frames:
			if frame > len(data):
				raise HamVisException(
					"A frame was selected for rendering that does not exist "
					"in the selected sourcefile."
				)
	return frames_int


def average_ham(average, ham_list, frames):
	"""Returns an updated ham_list and frames if average is True.
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
	try:
		if cut != "False":
			cut = list(cut.split(","))
			cut = [int(cutidx) for cutidx in cut]
			if len(cut) != 4:
				raise Exception
			ham_list = [ham[cut[0]:cut[1], cut[2]:cut[3]] for ham in ham_list]
	except Exception:
		raise HamVisException(
			"cut was incorrectly specified, please see the manual for more "
			"details."
		) from None
	return ham_list


def HamVis(fname, frames, average, cut, outname):
	ham_list = []
	data, size = get_data(fname)
	frames = format_frame_selection(frames, data)

	for frame in frames:
		ham = format_hammy(data[frame - 1], size)
		ham = logify_hammy(ham, size)
		ham_list.append(ham)

	ham_list = cut_ham(cut, ham_list)
	ham_list, frames = average_ham(average, ham_list, frames)

	for idx, hammy in zip(frames, ham_list):
		hammy_saver(hammy, idx, outname)


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
			"cut is the area you want to plot given as 'x0,x1,y0,y1',"
			"or 'False if you dont want to exclude anything.'\n"
			"outname is the name the output files should have.\n\n"
			"For examples please see the manual."
		)
	else:
		fname, frames, average, cut, outname = sys.argv[1:]
		HamVis(fname, frames, average, cut, outname)
