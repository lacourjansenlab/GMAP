
###############################################################################
Using default map functions
###############################################################################

Here, we will look at the water map. The water map wants to make use of some of the default functions in GMAP, but add a step of its own. Here, we will see how to call/invoke those default functions.

Default functions are those used when your map does not specify a function itself. They are constructed by GMAP considering the core.txt contents of your map. While for some maps different functions are needed, the default does suffice for the water map. It just wants to save the result elsewhere!

If you want, you can view the entire map in the maps directory. Do note, however, that this map had to do multiple things in order to run, so not all code in the map main.py will be discussed here.



****************************************
The problem
****************************************

The water map is designed in a very weird manner: the equation for its dipole moment depends on the frequency it is excited at. To have access to this frequency value in the dipole function, it must be saved during the frequency calculation. Of course, we also have to make sure that the frequency is calculated first, but this is true by default (adding the line ``ham_first False`` in the core.txt makes the dipole come first).



****************************************
The solution
****************************************

The solution for this map is to define a new function that is basically a wrapper of the default one - calling it, saving the output, and returning that output. In order to have generate and have access to that default one, we do this before the actual calculation:

.. code-block:: python

    import GMAP.src.tools.default_map_functions as GM_dmf

    def GM_post_init(map_, system):
        def calculate_frequency(map_, system, osc):
            freq = calc_frequency(map_, system, osc)
            osc.freq = freq
            return freq

        calc_frequency = GM_dmf.get_calculate_frequency(map_)
        map_.code.GM_calculate_frequency = calculate_frequency
        return

The new function ``calculate_frequency`` defined here should be pretty clear. The two interesting things to explain here are the two lines outside it. Pay attention to not confuse the ``calc_frequency`` and ``calculate_frequency`` objects here, they are (and need to be) different!

Firstly, the module GM_dmf contains all the logic for generating all functions a map needs. Any function GMAP will attempt to call from a map (see :ref:`the singles main.py <AddMap_FileStruct_SingMainPy>` or :ref:`the pairs main.py <AddMap_FileStruct_PairMainPy>` for a complete overview) actually needs to be present for GMAP to function. So, when first interpreting a map, GMAP will check if all are present, and if some are missing, build default versions  of them based on the map's core.txt file.

This map uses that same logic - it calls the generator of the function ``GM_calculate_frequency``, the generator is named ``get_calculate frequency``. The generator uses the ``Map`` object to base a frequency function on, and returns the result, which is saved here as ``calc_frequency`` so the newly defined function ``calculate_frequency`` can use it.

Now, we need to access the place where GMAP stores all functions it finds in the main.py file: that is under ``Map.code``. We are creating the function ``GM_calculate_frequency``, so need to save our new function there.
