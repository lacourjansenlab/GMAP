
import numpy as np
import matplotlib.pyplot as plt


def plot_data():
    files = [
        "pots_perres_sr0L_neutral_Vtube_r1000.txt",
        "pots_perres_sr2L_neutral_Vtube_r1000.txt",
        "pots_perres_sr5L_neutral_Vtube_r1000.txt",
        "pots_perres_sr0L_uncorrected_Vtube_r1000.txt",
        "pots_perres_sr2L_uncorrected_Vtube_r1000.txt",
        "pots_perres_sr5L_uncorrected_Vtube_r1000.txt",
        "pots_perres_sa0L_neutral_Vtube_r1000.txt",
        "pots_perres_sa2L_neutral_Vtube_r1000.txt",
        "pots_perres_sa5L_neutral_Vtube_r1000.txt",
        "pots_perres_sa0L_uncorrected_Vtube_r1000.txt",
        "pots_perres_sa2L_uncorrected_Vtube_r1000.txt",
        "pots_perres_sa5L_uncorrected_Vtube_r1000.txt"
    ]
    labels = [
        "perres sr0L neutral",
        "perres sr2L neutral",
        "perres sr5L neutral",
        "perres sr0L uncorrected",
        "perres sr2L uncorrected",
        "perres sr5L uncorrected",
        "perres sa0L neutral",
        "perres sa2L neutral",
        "perres sa5L neutral",
        "perres sa0L uncorrected",
        "perres sa2L uncorrected",
        "perres sa5L uncorrected"
    ]

    colors = [
        "lightcoral",
        "firebrick",
        "darkred",
        "gold",
        "goldenrod",
        "darkgoldenrod",
        "springgreen",
        "mediumseagreen",
        "seagreen",
        "lightsteelblue",
        "cornflowerblue",
        "royalblue"
    ]

    for file, label, color in zip(files, labels, colors):
        with open(file, "r") as fhand:
            data = np.genfromtxt(fhand)

        plt.plot(data[:, 0], data[:, 2] - data[:, 1], label=label, color=color)

    plt.legend()
    plt.show()


plot_data()
