import numpy as np
from numpy.ma import masked_array
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import sys


def get_data(fname):
	with open(fname) as fhand:
		data = fhand.readlines()[:20]  #Hammy.txt is corrupted past line 28
	data = [frame.split() for frame in data]
	data = [[float(number) for number in frame][1:] for frame in data]

	size = int(np.sqrt(2 * len(data[0]) + 0.25) + 0.5) - 1

	return data, size


def format_hammy(data, size):
	ham = np.zeros((size, size))
	ham[np.triu_indices(size)] = data
	ham = np.triu(ham) + np.tril(ham.T, -1)

	return ham


def logify_hammy(ham, size):
	minimum = 0.001
	ham[abs(ham) < minimum] = 0
	diag = np.diag(ham)
	logs = np.log2(np.abs(ham))
	logs -= np.log2(minimum)
	logs[ham < 0] *= -1

	logs[np.diag_indices(size)] = diag

	return logs


def hammy_saver(hammy, idx, outname):
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


def HamVis(fname, frames, average, cut, outname):
	ham_list = []
	data, size = get_data(fname)
	if frames == "all":
		frames = range(len(data))
	else:
		frames = list(frames.split(","))
		frames = [int(frame) for frame in frames]
	for frame in frames:
		ham = format_hammy(data[frame], size)
		ham = logify_hammy(ham, size)
		ham_list.append(ham)
	if average == "True":
		ham_list = [sum(ham_list) / len(ham_list)]
		frames = [frames]
	if cut is not False:
		cut = list(cut.split(","))
		cut = [int(cutidx) for cutidx in cut]
	ham_list = [ham[cut[0]:cut[1], cut[2]:cut[3]] for ham in ham_list]
	print(frames)
	print(len(ham_list))
	for idx, hammy in zip(frames, ham_list):
		hammy_saver(hammy, idx, outname)


if __name__ == "__main__":
	if len(sys.argv) != 6:
		print(
			"You did not give the correct number of terms in your command. "
			"A correct command looks like:\n"
			"python3 HamVis.py fname frames cut outname\n"
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

