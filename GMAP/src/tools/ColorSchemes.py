"""
Here, you can find my python adaptation of the color schemes found on
the following website: https://personal.sron.nl/~pault/

Currently, the following schemes are available:

Qualitative schemes and number of colors available:
bright(7),
high_contrast(5),
vibrant(7),
muted (10),
medium_contrast(8),
pale(6),
dark(6),
light(9)

Diverging schemes:
sunset, nightfall, BuRd, PRGn

Sequential schemes:
YlOrBr, iridescent, incandescent, smooth_rainbow

Bonus:
A sequential rainbow generator! Feed it the amount of colors you'd like,
and out comes a list of those colors nicely distributed along the rainbow.
"""

# 3rd party imports
import matplotlib.colors as mplC
from matplotlib import colormaps

# local imports
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.StringClasses as GM_SC


class PrinterColors(GM_CT.CustomClass):
    """Saves the provided color strings (ANSI sequences)"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coldict = kwargs
        self.coldict_r = {v: k for k, v in self.coldict.items()}


StandInColors = PrinterColors(**{
    col: GM_SC.ColStr(f"\033<{col}>") for col in (
        "clear", "pink_hc", "green_hc", "blue_hc", "red_hc", "red_todef",
        "green_lc")
})

DarkModeColors = PrinterColors(**{
    name: GM_SC.ColStr(code) for name, code in {
        "clear": "\033[0m",  # reset the colors

        # High contrast colors (bright on dark background)
        "pink_hc": "\033[38;2;240;96;112m",  # 4bit = bright red
        "green_hc": "\033[38;2;128;240;112m",  # 4bit = bright green
        "blue_hc": "\033[38;2;128;192;240m",  # light skyblue, 4bit=bright cyan
        "red_hc": "\033[38;2;255;0;0m",  # errors, 4bit = bright red
        "red_todef": "\033[38;2;255;160;176m",  # error text, 4bit = white

        # Low contrast colors (dark(er) on dark background)
        "green_lc": "\033[38;2;16;96;48m",  # 4bit = dark green
    }.items()
})


LightModeColors = PrinterColors(**{
    name: GM_SC.ColStr(code) for name, code in {
        "clear": "\033[0m",  # reset the color

        # High contrast colors (dark on light background)
        "pink_hc": "\033[38;2;188;64;64m",  # 4bit = dark red
        "green_hc": "\033[38;2;55;102;47m",  # 4bit = dark green
        "blue_hc": "\033[38;2;64;48;144m",  # night skyblue, 4bit = dark blue
        "red_hc": "\033[38;2;192;0;0m",  # errors, 4bit = dark red
        "red_todef": "\033[38;2;64;0;0m",  # error text, 4bit = black

        # Low contrast colors (light(er) on light background)
        "green_lc": "\033[38;2;48;208;64m",  # 4bit = bright green
    }.items()
})


class QualitativeColorScheme:
    def __init__(
        self, description, input_color_string, input_name_string,
        name="noname", last_is_bad_data=False
    ):
        self.description = description
        self.color_string = input_color_string
        self.name_string = input_name_string
        self.has_bad_data = last_is_bad_data

        colorlist = self.color_string.split()
        if self.has_bad_data:
            self.bad_data = colorlist[-1].strip("',")
            colorlist = colorlist[:-1]
        self.color_list = [item.strip("',") for item in colorlist]
        self.name_list = self.name_string.split()

        if len(self.color_list) != len(self.name_list):
            print(f"failed creating the {name} class, do not use it!")
            return

        self.color_dict = {
            label: col for label, col in zip(self.name_list, self.color_list)
        }

        if self.has_bad_data:
            self.color_dict["bad_data"] = self.bad_data

        self.name = name


class ContinuousColorScheme(mplC.ListedColormap):
    def __init__(
        self, description, input_color_string,
        name="noname", last_is_bad_data=False
    ):
        self.description = description
        self.color_string = input_color_string
        self.has_bad_data = last_is_bad_data

        colorlist = self.color_string.split()
        if self.has_bad_data:
            self.bad_data = colorlist[-1].strip("',")
            colorlist = colorlist[:-1]
        self.color_list = [item.strip("',") for item in colorlist]
        self.color_rgba_array = mplC.to_rgba_array(self.color_list)

        super().__init__(self.color_rgba_array)

        self.name = name


class DiscreteRainbowGenerator():
    colors_many = [
        "#777777",  # 'bad data'
        "#E8ECFB",  # _1
        "#D9CCE3",  # _2
        "#D1BBD7",  # _3
        "#CAACCB",  # _4
        "#BA8DB4",  # _5
        "#AE76A3",  # _6
        "#AA6F9E",  # _7
        "#994F88",  # _8
        "#882E72",  # _9
        "#1965B0",  # 10
        "#437DBF",  # 11
        "#5189C7",  # 12
        "#6195CF",  # 13
        "#7BAFDE",  # 14
        "#4EB265",  # 15
        "#90C987",  # 16
        "#CAE0AB",  # 17
        "#F7F056",  # 18
        "#F7CB45",  # 19
        "#F6C141",  # 20
        "#F4A736",  # 21
        "#F1932D",  # 22
        "#EE8026",  # 23
        "#E8601C",  # 24
        "#E65518",  # 25
        "#DC050C",  # 26
        "#A5170E",  # 27
        "#72190E",  # 28
        "#42150A",  # 29
    ]

    use_colors_many = {
        1: [10],
        2: [10, 26],
        3: [10, 18, 26],
        4: [10, 15, 18, 26],
        5: [10, 14, 15, 18, 26],
        6: [10, 14, 15, 17, 18, 26],
        7: [9, 10, 14, 15, 17, 18, 26],
        8: [9, 10, 14, 15, 17, 18, 23, 26],
        9: [9, 10, 14, 15, 17, 18, 23, 26, 28],
        10: [9, 10, 14, 15, 17, 18, 21, 24, 26, 28],
        11: [9, 10, 12, 14, 15, 17, 18, 21, 24, 26, 28],
        12: [3, 6, 9, 10, 12, 14, 15, 17, 18, 21, 24, 26],
        13: [3, 6, 9, 10, 12, 14, 15, 16, 17, 18, 21, 24, 26],
        14: [3, 6, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26],
        15: [3, 6, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28],
        16: [3, 5, 7, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28],
        17: [3, 5, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28],
        18: [
            3, 5, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 27, 28],
        19: [
            2, 4, 5, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 27,
            28],
        20: [
            2, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 20, 22, 24, 26,
            27, 28],
        21: [
            2, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 21, 23, 25,
            26, 27, 28],
        22: [
            2, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 21, 23, 25,
            26, 27, 28, 29],
        23: [
            2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 21, 23,
            25, 26, 27, 28, 29],
        24: [
            2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 21, 23,
            24, 25, 26, 27, 28, 29],
        25: [
            2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21,
            23, 24, 25, 26, 27, 28, 29],
        26: [
            2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 23, 24, 25, 26, 27, 28, 29],
        27: [
            2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 23, 24, 25, 26, 27, 28, 29],
        28: [
            2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29],
    }

    bad_data_hex = "#777777"
    bad_data_float32 = mplC.to_rgba_array(bad_data_hex)[:, :3]

    def __init__(self):
        pass

    def get_color_list_from_int(self, des_length, dtype="hex"):
        """
        Given an integer between 1 and 28 (inclusive), returns a list of
        colours of that length following the discrete rainbow scheme. If
        des_length does not meet these criteria, return an empty list.
        """

        color_id = self.use_colors_many.get(des_length, [])
        hexvals = [self.colors_many[id] for id in color_id]
        match dtype:
            case "hex":
                return hexvals
            case "rgbarrint8":
                return (
                    mplC.to_rgba_array(hexvals)[:, :3] * 128).astype("int8")
            case "rgbarrfloat32":
                return mplC.to_rgba_array(hexvals)[:, :3]
        return

    def get_color_list_from_iterable(self, datatoplot, dtype="hex"):
        """
        Given an iterable object of length between 1 and 28 (inclusive),
        returns a list of colours of the same length following the
        discrete rainbow scheme. If datatoplot does not meet these
        criteria, return an empty list.
        """
        num_colors_needed = len(datatoplot)
        return self.get_color_list_from_int(num_colors_needed, dtype)


def register_schemes(choice, prefix=""):
    """
    registers colormaps of choice in matplotlib.colormaps list of named
    colormaps. This allows the colormaps to be accessed by name in plotting
    functions.

    par choices:
    diverging, seqential, both

    par prefix:
    in case any of the names used in this script give clashes, a custom
    prefix can be given here - this is prepended to the standard names.
    """

    both = ("both", "b")
    diverging = ("diverging", "d", "div")
    sequential = ("sequential", "s", "seq")
    choice = choice.lower()

    base_maps = []

    if choice in both or choice in diverging:
        base_maps.extend(["sunset", "nightfall", "BuRd", "PRGn"])

    if choice in both or choice in sequential:
        base_maps.extend(
            ["YlOrBr", "iridescent", "incandescent", "smooth_rainbow"]
        )

    for map in base_maps:
        mapobj = globals()[map]
        setattr(mapobj, "name", prefix+map)
        colormaps.register(cmap=mapobj)
        globals()[prefix + map + "_r"] = mapobj.reversed()
        colormaps.register(globals()[prefix + map + "_r"])


bright = QualitativeColorScheme(
    "the main scheme for lines and their labels.",
    "'#4477AA', '#EE6677', '#228833', '#CCBB44', " +
    "'#66CCEE', '#AA3377', '#BBBBBB'",
    "blue cyan green yellow red purple grey",
    name="bright"
)


high_contrast = QualitativeColorScheme(
    "An alternative to the bright scheme, optimized for contrast. Also works" +
    " well for people with monochrome vision, or in monochrome printout.",
    "'#FFFFFF', '#004488', '#DDAA33', '#BB5566', '#000000'",
    "white yellow red blue black",
    name="high_contrast"
)


vibrant = QualitativeColorScheme(
    "An alternative to the bright scheme, based around TensorBoard.",
    "'#EE7733', '#0077BB', '#33BBEE', '#EE3377', " +
    "'#CC3311', '#009988', '#BBBBBB'",
    "blue cyan teal orange red magenta grey",
    name="vibrant"
)


muted = QualitativeColorScheme(
    "An alternative to the bright scheme, with more colors, lacking a clear " +
    "red or medium yellow.",
    "'#CC6677', '#332288', '#DDCC77', '#117733', '#88CCEE', '#882255', " +
    "'#44AA99', '#999933', '#AA4499', '#DDDDDD'",
    "indigo cyan teal green olive sand rose wine purple",
    name="muted",
    last_is_bad_data=True
)


medium_contrast = QualitativeColorScheme(
    "An alternative to the high_contrast scheme, with more colors. Still " +
    "suitable for monochrome, but differences are inevitably smaller. Meant " +
    "for situations needing color pairs.",
    "'#FFFFFF', '#6699CC', '#004488', '#EECC66', '#994455', '#997700', " +
    "'#EE99AA', '#000000'",
    "white light_yellow light_red light_blue dark_yellow dark_red " +
    "dark_blue black",
    name="medium_contrast"
)


pale = QualitativeColorScheme(
    "Use for the background of black text, for example to highlight cells " +
    "in a table.",
    "'#BBCCEE', '#CCEEFF', '#CCDDAA', '#EEEEBB', '#FFCCCC', '#DDDDDD'",
    "pale_blue pale_cyan pale_green pale_yellow pale_red pale_grey",
    name="pale"
)


dark = QualitativeColorScheme(
    "Use for text itelf on a white background, for example to mark a large " +
    "block of text. Use one for support, not all combined, and not for just " +
    "one word.",
    "'#222255', '#225555', '#225522', '#666633', '#663333', '#555555'",
    "dark_blue dark_cyan dark_green dark_yellow dark_red dark_grey",
    name="dark"
)


light = QualitativeColorScheme(
    "A hybrid of the bright and pale schemes, for when more colors than in " +
    "the pale scheme are needed and/or when the colored areas are small.",
    "'#77AADD', '#EE8866', '#EEDD88', '#FFAABB', '#99DDFF', '#44BB99', " +
    "'#BBCC33', '#AAAA00', '#DDDDDD'",
    "light_blue light_cyan mint pear olive light_yellow orange pink pale_grey",
    name="light"
)


sunset = ContinuousColorScheme(
    "Diverging colour scheme that works in colour-blind vision. " +
    "The colours can be used as given or linearly interpolated. The scheme " +
    "is related to the ColorBrewer RdYlBu scheme, but with darker central " +
    "colours and make more symmetric.",
    "'#364B9A', '#4A7BB7', '#6EA6CD', '#98CAE1', '#C2E4EF', '#EAECCC', "
    + "'#FEDA8B', '#FDB366', '#F67E4B', '#DD3D2D', '#A50026', '#FFFFFF",
    name="sunset",
    last_is_bad_data=True
)


nightfall = ContinuousColorScheme(
    "Diverging colour scheme that works in colour-blind vision. " +
    "The colours are linearly interpolated or every second colour is " +
    "skipped when used as given. The scheme is inspired by the ColorBrewer " +
    "PuBuGn and YlOrRd schemes",
    "'#125A56', '#00767B', '#238F9D', '#42A7C6', '#60BCE9', '#9DCCEF', " +
    "'#C6DBED', '#DEE6E7', '#ECEADA', '#F0E6B2', '#F9D576', '#FFB954', " +
    "'#FD9A44', '#F57634', '#E94C1F', '#D11807', '#A01813', '#FFFFFF'",
    name="nightfall",
    last_is_bad_data=True
)


BuRd = ContinuousColorScheme(
    "Diverging colour scheme that works in colour-blind vision. " +
    "The colors can be used as given, or linearly interpolated. This is the " +
    "reversed ColorBrewer RdBu scheme",
    "'#2166AC', '#4393C3', '#92C5DE', '#D1E5F0', '#F7F7F7', '#FDDBC7', " +
    "'#F4A582', '#D6604D', '#B2182B', '#FFEE99'",
    name="BuRd",
    last_is_bad_data=True
)


PRGn = ContinuousColorScheme(
    "Diverging colour scheme that works in colour-blind vision. " +
    "The colors can be used as given, or linearly interpolated. This is the " +
    "ColorBrewer PRGn scheme, with green A6DBA0 shifted to ACD39E to make " +
    "it print-friendly",
    "'#762A83', '#9970AB', '#C2A5CF', '#E7D4E8', '#F7F7F7', '#D9F0D3', " +
    "'#ACD39E', '#5AAE61', '#1B7837', '#FFEE99'",
    name="PRGn",
    last_is_bad_data=True
)


YlOrBr = ContinuousColorScheme(
    "Sequential colour scheme that works in colour-blind vision. " +
    "The colours can be used as given or linearly interpolated. This is the " +
    "ColorBrewer YlOrBr scheme, with orange FE9929 shifted to FB9A29 to " +
    "make it print-friendly. Pale yellow FFFFE5 can be set to completely " +
    "white FFFFFF, for example in density histograms",
    "'#FFFFE5', '#FFF7BC', '#FEE391', '#FEC44F', '#FB9A29', '#EC7014', " +
    "'#CC4C02', '#993404', '#662506', '#888888'",
    name="YlOrBr",
    last_is_bad_data=True
)


iridescent = ContinuousColorScheme(
    "Sequential colour scheme that works in colour-blind vision. " +
    "The colours should be linearly interpolated, optionally extended " +
    "towards white and black. The grey is meant for bad data",
    "'#FEFBE9', '#FCF7D5', '#F5F3C1', '#EAF0B5', '#DDECBF', '#D0E7CA', " +
    "'#C2E3D2', '#B5DDD8', '#A8D8DC', '#9BD2E1', '#8DCBE4', '#81C4E7', " +
    "'#7BBCE7', '#7EB2E4', '#88A5DD', '#9398D2', '#9B8AC4', '#9D7DB2', " +
    "'#9A709E', '#906388', '#805770', '#684957', '#46353A', '#999999'",
    name="iridescent",
    last_is_bad_data=True
)


incandescent = ContinuousColorScheme(
    "Sequential colour scheme that works in colour-blind vision, but is " +
    "not print-friendly. The colours should be linearly interpolated, " +
    "optionally extended towards white and black. Take into account that " +
    "pale cyan CEFFFF is almost white in red-blind vision.",
    "'#CEFFFF', '#C6F7D6', '#A2F49B', '#BBE453', '#D5CE04', '#E7B503', "
    + "'#F19903', '#F6790B', '#F94902', '#E40515', '#A80003', '#888888'",
    name="incandescent",
    last_is_bad_data=True
)


smooth_rainbow = ContinuousColorScheme(
    "The colours are ment to be linearly interpolated: for a discrete " +
    "rainbow scheme, use the DiscreteRainbowGenerator class. \nOften it " +
    "is better to use only a limited range of these colours. Starting " +
    "at purple, bad data can be shown white, whereas starting at off-white, " +
    "The most distinct grey is given as bad data. If the lowest data value " +
    "occurs often, start at off-white instead of purple. If the highest " +
    "data value occurs often, end at red instead of brown. For colour-blind " +
    "people, the light purples and light blues should not be mixed much.",
    "'#E8ECFB', '#DDD8EF', '#D1C1E1', '#C3A8D1', '#B58FC2', '#A778B4', " +
    "'#9B62A7', '#8C4E99', '#6F4C9B', '#6059A9', '#5568B8', '#4E79C5', " +
    "'#4D8AC6', '#4E96BC', '#549EB3', '#59A5A9', '#60AB9E', '#69B190', " +
    "'#77B77D', '#8CBC68', '#A6BE54', '#BEBC48', '#D1B541', '#DDAA3C', " +
    "'#E49C39', '#E78C35', '#E67932', '#E4632D', '#DF4828', '#DA2222', " +
    "'#B8221E', '#95211B', '#721E17', '#521A13', '#666666'",
    name="smooth_rainbow",
    last_is_bad_data=True
)
