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


# A function to adjust the parameters of the map. For some kinds of
# parameter (especially if theres multiple that are linked), the way
# RunPar is built might not be correct. In this function, the user can
# fix that.
def GM_adjust_RunPars(Files, Printer, Map):
    """Makes the necessary changes to Map.RunPar.

    Is expected to not return anything - return value is not caught.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass


# A function to adjust the choices made in core.txt. Perhaps, based on
# a detected parameter, a different choice is preferred. This function
# allows to make a different choice, **in the same format as the file**.
# if more complex behaviour is desired, a separate function is needed.
def GM_adjust_map_core_raw(Files, Printer, Map):
    """Makes the necessary changes to the 'raw' input read from core.txt.

    Is expected to not return anything - return value is not caught.

    The core.txt file is stored in Map.rawcore. It has not yet been
    parsed, just loaded into a dictionary. In this dictionary, each
    keyword is its own dictionary key. Most keywords can only occur once
    in the file - those have a list of the 'words' on the line as
    their value. The parameters that are allowed to occur more than once
    have a list as value, in which other lists appear - one for each
    line.

    The purpose of this function is to change this dictionary. Perhaps,
    a rule in core.txt is dependent on a parameter of the map. This
    function can make a decision based on those parameters (stored in
    Map.RunPars).

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass


# A function to adjust the final python objects built out of the
# core.txt file. If more complex behaviour is desired than the file
# format currently supports, an alternative function can be created
# here.
# !!!!!!!!!!!!!!!!!!!!!
# is this actually needed? Or does this influence the customizable
# functions only, anyways?
def GM_adjust_map_core_results(Files, Printer, Map):
    """Makes the necessary changes to the results derived from core.txt

    Is expected to not return anything - return value is not caught.

    Parameters
    ----------
    Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
        Contains all currently known paths and other file-related
        properties.
        Has to be updated after RunPars is finalized.
    Printer : :class:`~GMAP.src.tools.PrintTools.Printer`
        The object that allows to cleanly log and print during runtime,
        and handle errors.
    Map : :class:`~GMAP.src.tools.MapReader.Map`
        The object that stores everything the program currently knows
        about this map.
    """

    pass
