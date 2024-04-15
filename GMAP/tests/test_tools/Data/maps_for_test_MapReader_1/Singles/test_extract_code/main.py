

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

    if Map.RunPars.overwrite_neutral_charge_threshold != 0:
        setattr(
            Map.RunPars.MainRunPars,
            "neutral_charge_threshold",
            Map.RunPars.overwrite_neutral_charge_threshold
        )


def for_testing(number):
    return 10 - number
