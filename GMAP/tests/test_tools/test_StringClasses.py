
# 3rd party imports
import pytest

# local imports
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


# def test_header_specials():
#     lines = {
#         "over": "+------+",
#         "under": "+------+",
#         "left": ["|"] * 6,
#         "right": ["|"] * 6
#     }

#     expected = {k: v for k, v in lines.items()}
#     expected = "+-V--V-+"
#     assert GM_PT._header_specials(
#         {"u": {"replace": {"V": [[2], [-3]]}}}, lines) == expected
#     expected["over"] = "+-FG-FG+"
#     assert GM_PT._header_specials(
#         {"o": {"replace": {"FG": [[2], [-3]]}}}, lines) == expected
#     expected["left"] = ["|", "V", "|", "|", "|", "V"]
#     assert GM_PT._header_specials(
#         {"l": {"replace": {"V": [[1], [-1]]}}}, lines) == expected


# def test_header_textwrap():
#     txt = "123\n123456\n12"
#     header = GM_SC.Header(txt, alignment="leftadj")
#     assert header.title == ([
#         "123   ",
#         "123456",
#         "12    "
#     ], 6)

#     assert GM_PT._header_textwrap(txt, "rightadj", "-") == ([
#         "---123",
#         "123456",
#         "----12"
#     ], 6)

#     assert GM_PT._header_textwrap(txt, "centered", " ") == ([
#         " 123  ",
#         "123456",
#         "  12  "
#     ], 6)


def init():
    _ = GM_FH.FileLocations()
