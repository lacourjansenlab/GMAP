
# 3rd party lib imports
# import matplotlib.pyplot as plt
import numpy as np

# local imports
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.ColorSchemes as GM_CS
import GMAP.src.tools.Plotter as GM_Pl


def test_plot_coupling_choices(tmp_path):

    # build test data:
    osclist = ["a"] * 4 + ["b"] * 7 + ["c"] * 3 + ["d"] * 5
    coupmaps = [GM_CT.CustomClass(**{"allpairs": []}) for _ in range(5)]
    coupmapnames = [
        "bbNearNeigh",
        "cdCoupler",
        "diffmaps",
        "aaCoupler",
        "acCoupler"
    ]
    for ix1, map1 in enumerate(osclist):
        for ix2, map2 in enumerate(osclist):
            if ix2 <= ix1:
                continue
            pair = (ix1, ix2)
            if map1 == "b" and map2 == "b" and ix2 == ix1 + 1:
                coupmaps[0].allpairs.append(pair)
            elif map1 == "c" and map2 == "d":
                coupmaps[1].allpairs.append(pair)
            elif map1 == "a" and map2 == "c":
                coupmaps[4].allpairs.append(pair)
            elif map1 != map2:
                coupmaps[2].allpairs.append(pair)
            elif map1 == "a":
                coupmaps[3].allpairs.append(pair)

    runpars = GM_CT.CustomClass(**{
        "requested_pairmapdict": {
            name: map_ for name, map_ in zip(coupmapnames, coupmaps)},
        "couplingvis_figsize": 8,
        "couplingvis_dpi": 100,
        "output_couplingvis_filename": tmp_path / "couplingvis.pdf"
    })
    system = GM_CT.CustomClass(**{"nosc": len(osclist)})

    # run the code
    fig, ax = GM_Pl.plot_coupling_choices(runpars, system)

    # -----------------------------------------------------------------
    # evaluate:

    plot_array = ax.get_images()[0].get_array().astype("float32")
    assert np.all(plot_array == plot_array.transpose((1, 0, 2)))

    ncoupmaps = len(runpars.requested_pairmapdict)
    used_colors = list(
        GM_CS.DiscreteRainbowGenerator().get_color_list_from_int(
            ncoupmaps, "rgbarrfloat32").astype("float32"))
    used_colors.append(
        GM_CS.DiscreteRainbowGenerator.bad_data_float32.astype("float32"))
    plot_colors = list(np.unique(
        plot_array.reshape(-1, plot_array.shape[-1]), axis=0))
    for color in plot_colors:
        assert any(
            np.all(color.round(4) == usecol.round(4))
            for usecol in used_colors)
