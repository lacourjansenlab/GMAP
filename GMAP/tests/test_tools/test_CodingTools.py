"""
Tests all the functions/classes/methods in the file:
src/tools/CodingTools.py.

Missing tests:

(@ August 6th '24):
  none  (0 missed statements)

"""

# 3rd party imports
import pytest

# local imports
import GMAP.src.tools.CodingTools as GM_CT
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.FileHandler as GM_FH


class TestErrCode:
    def test_equalities(self):
        assert GM_CT.ErrCode("AA_BB_33") == "AA_BB_33"
        assert GM_CT.ErrCode("AA_BB_") == "AA_BB_33"
        assert GM_CT.ErrCode("AA__33") == "AA_BB_33"
        assert GM_CT.ErrCode("BB__33") != "AA_BB_33"
        assert not GM_CT.ErrCode("BB__33") == "AA_BB_33"

    def test_CT_EC_1(self):
        init()
        with pytest.raises(GM_Ex.GmapTypeError, match="CT_EC_1$"):
            assert GM_CT.ErrCode("AA_BB_33") == 5

        with pytest.raises(GM_Ex.GmapTypeError, match="CT_EC_1$"):
            assert 5 == GM_CT.ErrCode("AA_BB_33")

    def test_CT_EC_2(self):
        init()
        with pytest.raises(GM_Ex.GmapValueError, match="CT_EC_2$"):
            assert GM_CT.ErrCode("AA_BB_33") == "5"
        with pytest.raises(GM_Ex.GmapValueError, match="CT_EC_2$"):
            assert GM_CT.ErrCode("5") == "AA_BB_33"


def init():
    _ = GM_FH.FileLocations()
