"""
tests missing:

(@ July 22nd '24):
  (0 missed statements)

- Nothing is missing!
"""


# local imports
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT


# Leave this here (out of order!) so the line number doesn't have to be
# changed so often!
def test_devprint(capsys):
    GM_PT.devprint("this is a test")
    captured = capsys.readouterr()
    assert captured.out == (
        "(line   19) this is a test (from test_devprint in test_PrintTools.py)"
        "\n"
    )


class TestPrinter:
    def test_warning(self, capsys):
        _ = GM_FH.FileLocations()  # initializes printer also
        pr = GM_PT.Printer()
        pr.setenv(False, True)
        pr.set_state("running", 2, 3, "white", 79)
        pr.warning("this is a test", "AA_BB_33")
        captured = capsys.readouterr()
        assert captured.out.startswith("\nWARNING:\nthis is a test")


class TestTimer:
    def test_init(self):
        timer = GM_PT.Timer()
        assert isinstance(timer.zero, int)


def test_intlist_to_rangelist():
    intlist = [0, 1, 2, 6, 7, 10]
    maxint = 12

    rangelist, shadow = GM_PT.intlist_to_rangelist(intlist, maxint, False)
    assert rangelist == ["0-2", "6", "7", "10"]
    assert shadow is None

    rangelist, shadow = GM_PT.intlist_to_rangelist(intlist, maxint, True)
    assert rangelist == ["0-2", "6", "7", "10"]
    assert shadow == ["3-5", "8", "9", "11"]


def test_time_to_str():
    # ints are in units of ns:
    # 1 sec = 1,000 ms = 1,000,000 us = 1,000,000,000 ns
    # 1 ms = 1,000 us = 1,000,000 ns

    # 2 days, 3 hours, 4 minutes and 5 seconds =
    # ((2 * 24 + 3) * 60 + 4) * 60 + 5 seconds =
    # 183845 seconds.
    assert GM_PT.time_to_str(
        183845300200100, precision="ns") == "2-03:04:05.300200100"
    assert GM_PT.time_to_str(
        183845300200100, precision="us") == "2-03:04:05.300200"
    assert GM_PT.time_to_str(
        183845300200100, precision="ms") == "2-03:04:05.300"
    assert GM_PT.time_to_str(
        183845300200100) == "2-03:04:05"

    # 200 days, 20 hours, 15 minutes and 43 seconds =
    # ((200 * 24 + 20) * 60 + 15) * 60 + 43 =
    # 17352943 seconds.
    assert GM_PT.time_to_str(
        17352943030020010, precision="ns") == "200-20:15:43.030020010"
    assert GM_PT.time_to_str(
        17352943003002001, precision="ns") == "200-20:15:43.003002001"
