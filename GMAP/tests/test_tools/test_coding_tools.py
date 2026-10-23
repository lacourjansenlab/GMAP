"""
Tests all the functions/classes/methods in the file:
src/tools/cmd_interface.py.

Missing tests:

(@ October 23rd '26):
  (0 missed statements)

- None!

"""

# 3rd party imports
import pytest

# Local imports
import GMAP.src.tools.coding_tools as GM_ct


class TestFrozenDict:
    def test_retrieve(self):
        mydict = {2: 3, 4: 5}
        frozendict = GM_ct.FrozenDict(mydict)
        assert mydict[2] == frozendict[2]

    def test_add(self):
        mydict = {2: 3, 4: 5}
        frozendict = GM_ct.FrozenDict(mydict)
        mydict = {1: 0, 0: 1}
        with pytest.raises(TypeError):
            _ = frozendict + mydict

    def test_radd(self):
        mydict = {2: 3, 4: 5}
        frozendict = GM_ct.FrozenDict(mydict)
        mydict = {1: 0, 0: 1}
        with pytest.raises(TypeError):
            _ = mydict + frozendict

    def test_setitem(self):
        mydict = {2: 3, 4: 5}
        frozendict = GM_ct.FrozenDict(mydict)
        with pytest.raises(TypeError):
            frozendict[1] = 1

    def test_update(self):
        mydict = {2: 3, 4: 5}
        frozendict = GM_ct.FrozenDict(mydict)
        mydict = {1: 0, 0: 1}
        with pytest.raises(TypeError):
            frozendict.update(mydict)
