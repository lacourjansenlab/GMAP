"""Main code file for AmideSC map.

Also is the template/explanation for all that a map can hand directly to
GMAP. Of course, more functions are allowed, and these files can import
other custom python files stored in the same directory (or a directory
therein) as this file.

how about adding these?
 - post_init()
 - pre_run()  # just before per-frame loop
 - pre_frame()
 - post_frame()
 - post_run()

 - calculate_freq()
 - calculate_dipole()
"""


def GM_adjust_oscillators(Files, Printer, Map, Syst, oscillator_list):
    return [oscillator_list[2]]
