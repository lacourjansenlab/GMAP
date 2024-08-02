
# 3rd party lib imports
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np

# local imports
import GMAP.src.tools.ColorSchemes as GM_CS
# from GMAP.src.tools.PrintTools import devprint as dpr


def plot_coupling_choices(RunPars, System):
    nosc = System.nosc  # amount of oscillators

    # Obtain colors for plotting
    ncoupmaps = len(RunPars.requested_pairmapdict)
    if ncoupmaps > 28:  # the discrete rainbow can support 28 colors max.
        colors = GM_CS.DiscreteRainbowGenerator().get_color_list_from_int(
            28, "rgbarrfloat32")
    else:
        colors = GM_CS.DiscreteRainbowGenerator().get_color_list_from_int(
            ncoupmaps, "rgbarrfloat32")
    no_data = GM_CS.DiscreteRainbowGenerator.bad_data_float32

    # Build the image
    coupmap_image = np.zeros((nosc, nosc, 3), dtype="float32")
    coupmap_image[:, :] = no_data
    for ix, coupmap in enumerate(RunPars.requested_pairmapdict.values()):
        rows, cols = np.array(coupmap.allpairs).T
        coupmap_image[rows, cols, :] = colors[ix % 28]
        coupmap_image[cols, rows, :] = colors[ix % 28]

    # Plot the image
    fig, axs = plt.subplots(
        figsize=(4, 3), layout='constrained', squeeze=False)
    ax = axs.flat[0]
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.imshow(coupmap_image)

    # Add the legend
    colors = np.concatenate((no_data, colors))
    handles = [Rectangle((0, 0), 1, 1, color=col) for col in colors]
    labels = ["no coupling"] + list(RunPars.requested_pairmapdict.keys())
    ax.legend(handles, labels)

    # Save the figure
    fig.set_size_inches(
        RunPars.couplingvis_figsize, RunPars.couplingvis_figsize * 0.75)
    fig.savefig(
        RunPars.output_couplingvis_filename, bbox_inches='tight',
        dpi=RunPars.couplingvis_dpi)
    return fig, ax  # Should not be caught in program, just for testing.
