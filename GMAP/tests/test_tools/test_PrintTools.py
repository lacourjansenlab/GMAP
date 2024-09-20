"""
tests missing:

(@ Sept 17th '24):
  623-642 (15 missed statements)

- Ever changing prints from color_test. Honestly too lazy to write out
  the test - luckily its a programmer helper function. (623-642)
"""

# standard library imports
import time

# local imports
import GMAP.src.tools.ColorSchemes as GM_CS
import GMAP.src.tools.FileHandler as GM_FH
import GMAP.src.tools.PrintTools as GM_PT


# Leave this here (out of order!) so the line number doesn't have to be
# changed so often!
def test_devprint(capsys):
    GM_PT.devprint("this is a test")
    captured = capsys.readouterr()
    assert captured.out == (
        "(line   23) this is a test (from test_devprint in test_PrintTools.py)"
        "\n"
    )


class TestPrinter:
    def test_warning(self, capsys):
        pr = prep_printer()
        pr.warning("this is a test", "AA_BB_33")
        captured = capsys.readouterr()
        assert captured.out.startswith("\nWARNING:\nthis is a test")

    def test_setenv(self):
        _ = GM_FH.FileLocations()  # initializes printer also
        pr = GM_PT.Printer()
        pr.setenv(True, False)
        assert pr.color_mode == "white"  # safe mode toggles white
        assert pr._colors == GM_CS.LightModeColors


class TestTimer:
    def test_init(self):
        timer = GM_PT.Timer()
        assert isinstance(timer.zero, int)

    def test_init_2(self):
        now = time.perf_counter_ns()
        timer = GM_PT.Timer(now)
        assert timer.zero == now
        assert timer.previous == ["start", now]

    def test_add_time(self):
        start = time.perf_counter_ns()
        timer = GM_PT.Timer(start)
        times = []
        for msg in ["A", "B", "A", "B", "C"]:
            timer.add_time(msg)
            times.append(timer.times[msg])
            assert timer.previous == [msg, times[-1]]
        assert timer.totals == {
            "start": times[0] - start,
            "A": times[1] - times[0] + times[3] - times[2],
            "B": times[2] - times[1] + times[4] - times[3]
        }

    def test_get_totals(self):
        start = time.perf_counter_ns()
        timer = GM_PT.Timer(start)
        times = []
        for msg in ["A", "B", "A", "B", "C"]:
            timer.add_time(msg)
            times.append(timer.times[msg])
        totals = {
            "start": times[0] - start,
            "A": times[1] - times[0] + times[3] - times[2],
            "B": times[2] - times[1] + times[4] - times[3]
        }

        ABtot = totals["A"] + totals["B"]
        assert timer.get_total_ns("A", "B") == ABtot

        s = ABtot // 1000000000  # extract seconds
        # we assume the test will take fewer than 10 seconds.
        assert timer.get_total_format("A", "B") == f"0-00:00:0{s}"


def test_header_custom(capsys):
    # only to see if things are passed correctly. Full functionality should
    # be tested by test_StringClasses::testHeader

    prep_printer()
    GM_PT.header(1, "test header", "custom")
    captured = capsys.readouterr()
    assert captured.out == (
        "-----------\n"
        "test header\n"
        "-----------\n"  # this last newline from python print(end='\n')
    )


def test_headerfooter_doublebox(capsys):
    pr = prep_printer()
    GM_PT.header(1, "test header", "doublebox")
    pr.print(1, "another test")
    GM_PT.footer(1, "test header", "doublebox")
    captured = capsys.readouterr()
    assert captured.out == (
        "\n\n"
        "╔═════════════╗\n"
        "║ test header ║\n"
        "╚╦════════════╝\n"
        " ║ \n"
        " ║ another test\n"
        " ║ \n"
        " ╚═══ End of test header ═════\n\n"
    )


def test_headerfooter_doublebox_bare(capsys):
    pr = prep_printer()
    GM_PT.header(1, "test header", "doublebox_bare")
    pr.print(1, "another test")
    GM_PT.footer(1, "test header", "doublebox_bare")
    captured = capsys.readouterr()
    assert captured.out == (
        "\n\n"
        "╔═════════════╗\n"
        "║ test header ║\n"
        "╚═════════════╝\n"
        "\n"
        "another test\n"
    )


def test_headerfooter_preline(capsys):
    pr = prep_printer()
    GM_PT.header(1, "test header", "nohead", preline="- ")
    pr.print(1, "a test\nand another\nand yet another")
    GM_PT.footer(1, "test header", "nohead", preline="- ")
    captured = capsys.readouterr()
    assert captured.out == (
        "test header\n"
        "- a test\n"
        "- and another\n"
        "- and yet another\n"
    )


def test_footer_custom(capsys):
    prep_printer()
    GM_PT.footer(1, "test header", "custom")
    captured = capsys.readouterr()
    assert captured.out == (
        "-----------\n"
        "test header\n"
        "-----------\n"  # this last newline from python print(end='\n')
    )


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


def prep_printer():
    _ = GM_FH.FileLocations()  # initializes printer also
    pr = GM_PT.Printer()
    pr.setenv(False, True)
    pr.set_state("running", 2, 3, "white", 79)
    return pr
