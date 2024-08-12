
# standard lib imports
from pathlib import Path

# 3rd party lib imports
import dataframe_image
import matplotlib.colors as mplC
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# local imports
import GMAP.src.tools.ColorSchemes as GM_CS
import GMAP.src.tools.constants as GM_con
import GMAP.src.tools.MathFunctions as GM_MF
# from GMAP.src.tools.PrintTools import devprint as dpr


# ========== Functions for users ==========

def plot_coupling_choices(RunPars, System):
    """Creates the plot showing what coupling method is picked for each entry.

    The plot has a maximum of 28 colors (different coupling methods) it
    can display at a time. Colors are picked automatically to have the
    largest possible separation.

    Parameters
    ----------
     RunPars : :class:`~GMAP.src.tools.ParameterParser.RunPars`
        The 'main' RunPars instance containing all the basic run-defining
        parameters.
    System : :class:`~GMAP.src.tools.SystemReader.System
        The object that stores everything the program currently knows
        about the system being treated (names, numbers, types, masses,
        charges of all atoms, for example)

    Returns
    -------
    fig : `matplotlib.figure.Figure`
        The figure in which the plot was made. Should not be caught in
        a normal run, this output is just for testing purposes.
    ax : `matplotlib.axes._axes.Axes`
        The axis on which the plot was made. Should not be caught in a
        normal run, this output is just for testing purposes.
    """

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


# ========== Functions for developers (go to manual) ==========

def val_to_color(val):
    hex = mplC.to_hex([int(num)/255 for num in val])
    return (
        f"background-color:{hex};"  # color the background according to value
        "color:#00000000;"  # 0 alpha -> letters won't display
        "font-size:2.5pt;"  # tiny so the cells have a usable width
        "font-family:Monospace"  # so all files have exactly the same size
    )


def plot_color_conv():
    step = 16
    data_points = [*range(0, 255, step)] + [255]

    # make the plot three different ways (slicing by red, green and blue)
    for seq in ("rgb", "gbr", "brg"):
        for pri in data_points:  # we make a table for each primary
            # build data for in the table
            table = []
            for sec in data_points:
                row = []
                for ter in data_points:
                    rgb = {letter: par for letter, par in zip(
                        seq, (pri, sec, ter))}
                    # first the full-color one
                    r, g, b = (rgb["r"], rgb["g"], rgb["b"])
                    row.append((f"{r:0>3}", f"{g:0>3}", f"{b:0>3}"))
                    # then the adjusted-color one
                    r, g, b = GM_con.printed_colors_r[GM_MF.convert_color_24_4(
                        rgb["r"], rgb["g"], rgb["b"]
                    )]
                    row.append((f"{r:0>3}", f"{g:0>3}", f"{b:0>3}"))
                table.append(row)

            # create pandas dataframe from the built data
            col = pd.MultiIndex.from_product([data_points, ["", " "]])
            df = pd.DataFrame(data=table, columns=col)
            labeldict = {"r": "Red", "g": "Green", "b": "Blue"}
            rowlabels = {ix: val for ix, val in enumerate(data_points)}

            # make it pretty!
            df = df.rename(index=rowlabels)
            df = df.rename_axis(labeldict[seq[1]])
            # because of the multiindex, the labels should be a list
            df = df.rename_axis([labeldict[seq[2]], None], axis='columns')
            dfs = df.style.set_table_styles([
                {"selector": "th", "props": [("text-align", "center")]},
                {
                    "selector": "caption",
                    "props": "font-size:200%; margin:10px"}])
            dfs = dfs.map(val_to_color)
            dfs = dfs.set_caption(f"{labeldict[seq[0]]}: {pri}")
            for column in data_points:
                dfs.set_table_styles({
                    (column, " "): [{
                        "selector": "",
                        "props": "border-right: 5px solid black"}],
                    (column, ""): [{
                        "selector": ".level0",
                        "props": "border-right: 5px solid black"}]
                }, axis=0, overwrite=False)
            dfs.hide(axis=1, level=1)
            dataframe_image.export(
                dfs, f"color_table_{seq}_temp{pri}.png", max_cols=-1)

        arrays = []
        for pri in data_points:
            arr = plt.imread(f"color_table_{seq}_temp{pri}.png")
            arrshape = arr.shape
            arrshape = (40,) + arrshape[1:]
            arrays.append(np.zeros_like(arr, shape=arrshape))
            arrays[-1] += 1
            arrays.append(arr)

        arr = np.concatenate(arrays)
        plt.imsave(f"color_table_{seq}.png", arr)

        for pri in data_points:
            file = Path(f"color_table_{seq}_temp{pri}.png")
            file.unlink()
