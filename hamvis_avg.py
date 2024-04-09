import numpy as np
from numpy.ma import masked_array
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import sys


def get_data(fname):
	with open(fname) as fhand:
		data = fhand.readlines()[:5]  #Hammy.txt is corrupted past line 28
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


def hammy_saver(hammy):
	off_diag = masked_array(hammy, hammy > 100)
	on_diag = masked_array(hammy, hammy <= 100)

	normalize = mc.Normalize(vmin=-11.5, vmax=11.5)

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
	ax.set_title("Hamiltonian using Skinner and TCC maps")
	plt.savefig("Hammy.png")


fname = "Hammy.txt"
data, size = get_data(fname)
hammy = format_hammy(data[0], size)
loggy = logify_hammy(hammy, size)
hammy_saver(loggy)
