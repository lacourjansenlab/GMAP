"""
tests missing:

(@ September 17th '24):
 (0 missed statements)

- None!
"""

# 3rd party imports
import pytest

# local imports
import GMAP.src.tools.ColorSchemes as GM_CS
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.StringClasses as GM_SC


class TestErrCode:
    def test_equalities(self):
        assert GM_SC.ErrCode("AA_BB_33") == "AA_BB_33"
        assert GM_SC.ErrCode("AA_BB_") == "AA_BB_33"
        assert GM_SC.ErrCode("AA__33") == "AA_BB_33"
        assert GM_SC.ErrCode("BB__33") != "AA_BB_33"
        assert not GM_SC.ErrCode("BB__33") == "AA_BB_33"

    def test_CT_EC_1(self):
        init()
        with pytest.raises(GM_Ex.GmapTypeError, match="CT_EC_1$"):
            assert GM_SC.ErrCode("AA_BB_33") == 5

        with pytest.raises(GM_Ex.GmapTypeError, match="CT_EC_1$"):
            assert 5 == GM_SC.ErrCode("AA_BB_33")

    def test_CT_EC_2(self):
        init()
        with pytest.raises(GM_Ex.GmapValueError, match="CT_EC_2$"):
            assert GM_SC.ErrCode("AA_BB_33") == "5"
        with pytest.raises(GM_Ex.GmapValueError, match="CT_EC_2$"):
            assert GM_SC.ErrCode("5") == "AA_BB_33"


class TestColStr():
    def test_add(self):
        assert GM_SC.ColStr("A") + "B" == GM_SC.ColStr("AB")

    def test_radd(self):
        assert "A" + GM_SC.ColStr("B") == GM_SC.ColStr("AB")

    def test_getitem(self):
        init()
        colstr = self.get_rainbowstr()
        colors = GM_CS.DarkModeColors
        h = "H"
        assert colstr[2] == colors.blue_hc + h
        assert colstr[1::2] == colors.green_hc + h + colors.clear + h

        with pytest.raises(GM_Ex.GmapIndexError):
            _ = colstr[5]

        with pytest.raises(GM_Ex.GmapNotImplementedError):
            _ = colstr[::-1]

    def test_iter(self):
        colstr = self.get_rainbowstr()
        colors = GM_CS.DarkModeColors
        h = "H"
        assert list(colstr) == [
            colors.red_hc + h,
            colors.green_hc + h,
            colors.blue_hc + h,
            colors.clear + h
        ]

    def test_mul(self):
        assert GM_SC.ColStr("A") * 3 == GM_SC.ColStr("AAA")

    def test_rmul(self):
        assert 3 * GM_SC.ColStr("A") == GM_SC.ColStr("AAA")

    def test_change_color(self):
        colstr = GM_SC.ColStr("\033[38;2;255;255;0mHello\033[0m")
        assert colstr.change_color("4bit") == GM_SC.ColStr(
            "\033[33;1mHello\033[0m")
        colstr = GM_SC.ColStr("\033[48;2;255;255;0mHello\033[0m")
        assert colstr.change_color("4bit") == GM_SC.ColStr(
            "\033[43mHello\033[0m")

    def test_PT_CC_1(self):
        init()
        with pytest.raises(GM_Ex.GMAPexception, match="PT_CC_1$"):
            _ = GM_SC.ColStr("\033[38;2;0mHello\033[0m").change_color("4bit")

        with pytest.raises(GM_Ex.GMAPexception, match="PT_CC_1$"):
            _ = GM_SC.ColStr("\033[48;2;0mHello\033[0m").change_color("4bit")

        with pytest.raises(GM_Ex.GMAPexception, match="PT_CC_1$"):
            _ = GM_SC.ColStr("\033[39;2;0mHello\033[0m").change_color("4bit")

    def get_rainbowstr(self):
        # "clear", "pink_hc", "green_hc", "blue_hc", "red_hc", "red_todef",
        # "green_lc"
        colors = GM_CS.DarkModeColors
        h = "H"
        return (
            colors.red_hc + h
            + colors.green_hc + h
            + colors.blue_hc + h
            + colors.clear + h
        )


class TestHeader:
    def test_format_title(self):
        head = GM_SC.Header.__new__(GM_SC.Header)
        setattr(head, "title", GM_SC.ColStr("some test title"))
        head.format_title(79, 1)
        assert head.title == "some test title"
        assert head.title_lines == 1

        head.format_title(10, 1)
        assert head.title == "some\ntest\ntitle"
        assert head.title_lines == 3

    def test_align_title(self):
        head = GM_SC.Header.__new__(GM_SC.Header)
        setattr(head, "title", GM_SC.ColStr("some\nvery long title"))
        setattr(head, "title_lines", 2)
        head.align_title("centered", " ")
        assert head.title == [
            "     some      ",
            "very long title"
        ]

        setattr(head, "title", GM_SC.ColStr("some\nvery long title"))
        head.align_title("leftadj", " ")
        assert head.title == [
            "some           ",
            "very long title"
        ]

        setattr(head, "title", GM_SC.ColStr("some\nvery long title"))
        head.align_title("rightadj", " ")
        assert head.title == [
            "           some",
            "very long title"
        ]

    def test_make_lines(self):
        head = GM_SC.Header.__new__(GM_SC.Header)
        setattr(head, "longest_length", 5)
        setattr(head, "title_lines", 2)
        head.make_lines("ol", 1)
        assert head.over == " -------"
        assert head.under == ""
        assert head.left == ["|"] * 2
        assert head.right == [""] * 2

    def test_line_overunder(self):
        head = GM_SC.Header.__new__(GM_SC.Header)
        assert head.line_overunder("-", "++", "c", 5, "u") == "+     +"
        assert head.line_overunder("-", "++", "d", 5, "u") == ""
        assert head.line_overunder("-", "++", "ur", 5, "u") == "----- "

    def test_line_sides(self):
        head = GM_SC.Header.__new__(GM_SC.Header)
        assert head.line_sides("|", "ul", 2, "l") == ["|", "|"]
        assert head.line_sides("|", "uo", 2, "l") == ["", ""]
        assert head.line_sides("|", "c", 2, "l") == [" ", " "]

    def test_specials_replace(self):
        head = GM_SC.Header.__new__(GM_SC.Header)
        line = GM_SC.ColStr("-" * 10)
        assert head.specials_replace("u", {"V": [[2], [4], [6, 8]]}, line) == (
            "--V-V-VV--"
        )

        line = [GM_SC.ColStr("-")] * 10
        assert head.specials_replace("l", {"V": [[2], [4], [6, 8]]}, line) == (
            [GM_SC.ColStr(char) for char in "--V-V-VV--"]
        )


def init():
    _ = GM_FH.FileLocations()
