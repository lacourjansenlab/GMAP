
###############################################################################
Reading other map's information (and raising errors)
###############################################################################

Here, we will look at the AmideBB map. The AmideBB map wants to know what settings the AmideSC map uses, to make sure the two maps make sense together.

.. warning::
    The tools here are very powerful, but every power comes with danger. Use the tools responsibly, and **never ever** make changes to other maps, or GMAP itself.

If you want, you can view the entire map in the maps directory. Do note, however, that this map had to do multiple things in order to run, so not all code in the map main.py will be discussed here.



****************************************
The problem
****************************************

The AmideBB and AmideSC maps have been developed together. Both apply on amide groups in proteins, both model the Amide-I vibration. The only difference is that the AmideBB map models the groups in the protein backbone, while the SC map models those in the sidechains. As experimentally both are usually measured together, both are usually also computed together, and the results only make physical sense if both maps are run with the same model and other parameters.

Therefore, it is important that one map (the AmideBB map was chosen as the 'more important' map here) tests this equality, and raises an error if there are issues.



****************************************
The solution
****************************************

The main challenge here lies in finding other maps' data. The map objects are stored within the main GMAP RunPars object, which silently can be accessed through every map's own RunPars object.

So, what's the RunPars object? The main GMAP one is the best example. When a user of the program gives GMAP instructions on how to perform a run (what files to use for input/output, what settings to use, etc), they do so through the parameter files, or on the command line. The final choices for these parameters (after combining all sources) are stored in the RunPars object. It knows what calculation to perform.

The RunPars objects of maps are the same - if a map has a parameter file to make extra parameters available to the user, these are stored in the map specific RunPars object.

Lets look at the following example, where the two maps both have parameters of the same name, and we want to see if both have the same choice:

.. code-block:: python

    def GM_post_init(map_, system):
        # verify that both dipole maps (if applicable) have the same map choices
        rps = map_.run_pars  # RunPars object of this map
        main_runpars = map_.run_pars.main_run_pars  # main GMAP RunPars object
        # is other map present?
        if "AmideSC" in main_runpars.requested_mapdict.keys():
            amSC_rps = main_runpars.requested_mapdict["AmideSC"].run_pars
            if amSC_rps.frequency_map_choice != rps.frequency_map_choice:
                doError()

Please note that the code above is a shorter version of the code actually in the map, illustrating the key points.

You can see in the code above that we first find the RunPars object of the current (AmideBB) map, and the main one of GMAP itself. Then, we check in the main one whether the AmideSC map is present - it could be that the user only wanted to apply one of the maps! But, if it *is* present, we find its RunPars object.

The two RunPars now in hand, we can easily compare them. In the example, we only compare their choices for the parameter 'frequency_map_choice'. Please note that this parameter only has the same name for both maps as they were developed by the same author, who chose to use the same parameter name for both! 



*******************************************************************************
Bonus: raising your own errors
*******************************************************************************

After we found a possible mismatch between the two maps, we should do something with it. There is a few options:

We could print some text, telling the user there is an issue. The user sees the message that the two maps don't match, but the program continues. The disadvantage of this option is that the user could simply miss out on a message, but the advantage is that if the user is okay with (or even intending for) that difference, the program can still continue. If you want to do it that way, the GMAP.src.tools.print_tools module contains the :class:`~GMAP.src.tools.print_tools.Printer` class. It has a method that allows for more detailed printing, and should *always* be used instead of the main python print method:


.. code-block:: python

    import GMAP.src.tools.print_tools as GM_pt

    GM_pt.Printer.print(2, "This message is moderately important")

In the main GMAP code, you'll see that if a lot needs to be printed, the Printer object is stored in a variable to make calling slightly easier/faster. The first argument (integer) is the verbose level at or above which this message should be printed. Be very conservative here! 0 (the lowest) is only used by GMAP for reporting errors that terminate the program, not even the logo is shown. If nothing bad happens, the program is completely silent.

The other option for dealing with our error is to raise a 'proper' error. If this is a non-fatal one, users might miss it as easily as a text message, but if it *is* a fatal one, this would prevent users from doing it on purpose. The AmideBB map went with this approach, raising a fatal error, but only if the flag saying the maps must match is set to True (which it is by default). So, lets look at how to do this by looking at the literal implementation of the first example:

.. code-block:: python

    import GMAP.src.tools.print_tools as GM_pt

    def GM_post_init(map_, system):
        # verify that both dipole maps (if applicable) have the same map choices
        rps = map_.run_pars  # run_pars object of this map
        main_runpars = map_.run_pars.main_run_pars  # main GMAP RunPars object
        # is other map present?
        if "AmideSC" in main_runpars.requested_mapdict.keys():
            amSC_rps = main_runpars.requested_mapdict["AmideSC"].run_pars
            if (  # the maps do not match, and they're not allowed to mismatch.
                amSC_rps.frequency_map_choice != rps.frequency_map_choice
                and not rps.allow_map_mismatch
            ):
                GM_pt.Printer.warning(
                    "Text of the warning",
                    "map_AmideBB_2", True
                )

You can see we have now implemented the 'allow_map_mismatch' parameter, which indicates whether the two maps should indeed match. If the two should match, but they don't, we raise an error using the Printer object (same as before). The call to the warning() function has three arguments used here (but there are more, check the documentation!): The first is the text the user should be shown when this error is triggered. The text should be as brief as possible, as well as containing enough information for the user to know how to solve the issue. The third argument is whether the error is fatal. 'True' tells GMAP to stop if this error is encountered, 'False' lets the program continue.

The second parameter is the error code of this problem. This error code serves multiple purposes: it allows the user to look up the code in documentation (so make sure to document all errors used by your map well in the README), but it also allows the user to silence the error. To serve both these purposes well, you must pick a good code. This is done as follows:

Every error code consists of 3 parts, separated by single underscores (_). In case of any map, the first part should be the text 'map', the second should be the name of the map, and the last a unique identifier. All errors in GMAP itself and maps have currently got a number there (starting at 1 and just counting up every time a new code is needed), so doing that would make it consistent. The program wouldn't break with letters in there, however (but no special characters should be used).

There are two more arguments you could pass on - these can be very useful, especially if other scripts are used together with GMAP. They're not essential, however.





