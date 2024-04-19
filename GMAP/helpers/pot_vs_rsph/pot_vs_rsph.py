import subprocess
import numpy as np
import matplotlib.pyplot as plt

# def make_inpfile(estatic_range):
#     with (
#         open("base_inpar.txt", "r") as basefile,
#         open("use_inpar.txt", "w") as usefile
#     ):
#         for line in basefile:
#             usefile.write(line)
#         usefile.write(f"estatic_range {estatic_range}\n")


# deprecated (DEPICT handles this)
def do_run(estatic_range):
    subprocess.run(
        f"GMAP GEM run base_inpar.txt --estatic_range {estatic_range} "
        f"-odf outdir/{pre}_r{estatic_range}{post[:-4]}"
    )


def gen_data():
    length = 1
    start = 10
    subprocess.run(
        f"GMAP DEPICT calculate base_inpar.txt --estatic_range {start} "
        f"--number_frames {length} -oef {pre}{post}"
    )

    # all_results = np.zeros((length, 4))
    # for estatic_range in range(start, start + length):
    #     do_run(estatic_range)
    #     all_results[estatic_range-start, 0] = estatic_range
    #     all_results[estatic_range-start, 1:] = np.genfromtxt(
    #         f"outdir/{pre}_r{estatic_range}{post}",
    #         usecols=(1, 2, 3))

    # with open(f"{pre}{post}", "w") as fhand:
    #     all_results = np.round(all_results, decimals=6)
    #     np.savetxt(fhand, all_results)


def plot_data():
    files = [
        "pots_perres_sr0L_neutral_",
        "pots_perres_sr2L_neutral_",
        "pots_perres_sr5L_neutral_",
        "pots_perres_sr0L_uncorrected_",
        "pots_perres_sr2L_uncorrected_",
        "pots_perres_sr5L_uncorrected_",
        "pots_perres_sa0L_neutral_",
        "pots_perres_sa2L_neutral_",
        "pots_perres_sa5L_neutral_",
        "pots_perres_sa0L_uncorrected_",
        "pots_perres_sa2L_uncorrected_",
        "pots_perres_sa5L_uncorrected_"
    ]
    files = [name + "Vtube_r1000.txt" for name in files]
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
        with open(f"sorted/Vtube/{file}", "r") as fhand:
            data = np.genfromtxt(fhand)

        plt.plot(data[:, 0], data[:, 2] - data[:, 1], label=label, color=color)

    plt.legend()
    plt.show()


# deprecated (DEPICT handles this)
def reshape_data():
    with open(f"outdir/{pre}_r10{post}", "r") as fhand:
        data = np.genfromtxt(fhand)
    data = data[1:]

    data = data.reshape((3, 200)).T

    with open(f"{pre}{post}", "w") as fhand:
        outarr = np.zeros((200, 4))
        outarr[:, 0] = np.arange(10, 210)
        outarr[:, 1:] = data
        all_results = np.round(outarr, decimals=6)
        np.savetxt(fhand, all_results)


pre = "pots_perres"
post = "_sr0L_uncorrected.txt"

gen_data()
# plot_data()
