"""
Tests all the functions/classes/methods in the file:
src/tools/ColorSchemes.py.

Missing tests:

(@ Sept 20th '24):
  (0 missed statements)

- None

To hide this file from the overview, incomplete tests were added for the
following:
- None
"""

# 3rd party imports
import matplotlib.pyplot as plt
import numpy as np

# local imports
import GMAP.src.tools.ColorSchemes as GM_CS


class TestQualitativeColorScheme:
    def test_fails(self):
        mycolorscheme = GM_CS.QualitativeColorScheme(
            "A temporary colorscheme for testing",
            "'#3355DD', '#882277'",
            "Blue Purple Green"
        )
        assert not mycolorscheme.success


class TestDiscreteRainbowGenerator:
    def test_hexvals(self):
        rainbowgen = GM_CS.DiscreteRainbowGenerator()
        assert rainbowgen.get_color_list_from_int(2, dtype="hex") == [
            "#1965B0", "#DC050C"]

    def test_uint8(self):
        rainbowgen = GM_CS.DiscreteRainbowGenerator()
        assert np.all(
            rainbowgen.get_color_list_from_int(2, dtype="rgbarruint8") == (
                np.array([[25, 101, 176], [220, 5, 12]]).astype("uint8")
            ))

    def test_color_from_iter(self):
        rainbowgen = GM_CS.DiscreteRainbowGenerator()
        ite = ["first item in the list", "and a second"]
        assert rainbowgen.get_color_list_from_iterable(ite, dtype="hex") == [
            "#1965B0", "#DC050C"]


def test_register_schemes():
    GM_CS.register_schemes("both", "testimport_")
    avail_schemes = set(plt.colormaps())
    schemes_imported = ["sunset", "nightfall", "BuRd", "PRGn"]
    schemes_imported += [
        "YlOrBr", "iridescent", "incandescent", "smooth_rainbow"]
    schemes_imported = ["testimport_" + name for name in schemes_imported]
    schemes_r = [name + "_r" for name in schemes_imported]
    desired_schemes = set(schemes_imported + schemes_r)
    assert desired_schemes.issubset(avail_schemes)
