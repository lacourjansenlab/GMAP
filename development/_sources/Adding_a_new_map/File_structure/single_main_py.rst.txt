.. _AddMap_FileStruct_SingMainPy:

#######
main.py
#######

(this applies to singles maps. If you are looking for pairs maps instead, go to :ref:`the pairs version of this page.<AddMap_FileStruct_PairMainPy>`)

This file contains the code for the map. A map does not need to have any code - this file does not have to exist. If it does, there are a few functions the program will look for. If they are missing, that is no issue, but their names should not be used for any other purpose.

The file can contain other functions (or even call functions from other files in the map directory), to allow for writing any kind of code yourself. However, creating your own new function (or class/variable/module) names has a danger - if the program assumes any of them to have a special meaning, the code may function differently than expected. In order to avoid any name clashes, you should avoid any of the following (categories of) names:

- Names starting with "GM\_" - These are reserved for functions expected by GMAP. Even if a name starting with GM\_ isn't used by the program yet, it might be in the future, so its best practice to just avoid them in general.
- Names starting with "CP\_" - These are reserved for coupling maps. A coupling map might need more information from a single oscillator, which can be retrieved by using these kinds of functions.
- Any of the names that should be avoided courtesy of general coding good practices.

.. note::
    If the map ever needs to raise a warning, the error code should be of the following format: ``map_mapname_identifier``. Replace mapname with the name of your map, and identifier with the identifier for this specific warning. If you add warnings, make sure to also provide explanation on these warnings to users!


***************
Basic structure
***************

There are a few objects that occur quite often as an argument for these functions. Here is a quick overview of them:

map\_
=====
An instance of :class:`~GMAP.src.tools.map_reader.SingleMap`. Stores all information of this class. This is the most important object, as it stores everything related to this class. As functions of the map can change how the map is registered, this object will look different during the different functions. Here is an overview of all attributes the class can have, at each function it will be explained/highlighted what attributes are available at that point.

It is probable that the map wants to save information between functions, too, just like the main program. These data structures must be saved as an attribute to the instance of the class, as per good coding practices. This overview of attributes should help indicate what names are and aren't available.

- self.directory (type pathlib.Path) is the path to the directory the map is saved in on the current machine.
- self.corepath (type pathlib.Path) is the path to the core.txt file of the map.
- self.name (type str) is the name of the map - i.e. the name of the directory in which all map files live.
- self.type (type str) is the type of the map - either Singles or Pairs. Singles maps operate on a single oscillator (think of maps giving an oscillator frequency), Pairs maps operate on a pair of oscillators (think of maps giving a coupling value).
- self.success (type bool) denotes whether the map has (until this point) been read successfully. An unsuccessful map will not trigger the program to quit, as long as the user does not want to use this map.
- self.avail_files (type list of pathlib.Path) is a list of all files that are in the same map directory in this map (or in its parent directory). These are the files that can be used for appending using 'add_corefile' in the core file.
- self.ref_pars (type :class:`~GMAP.src.tools.parameter_parser.RefPars`) contains all information from the map-specific reference parameters file.
- self.def_pars (type :class:`~GMAP.src.tools.parameter_parser.RawPars`) contains all choices for parameters for this map that were found in the default parameter file. Either all parameters are present, or none, depending on the default parameter file.
- self.in_pars (type :class:`~GMAP.src.tools.parameter_parser.RawPars`) contains all choices for parameters for this map that were found in the input parameter file. May be empty.
- self.cmd_pars (type :class:`~GMAP.src.tools.parameter_parser.RawPars`) contains all choices for parameters for this map that were found on the command line. May be empty.
- self.run_pars (type :class:`~GMAP.src.tools.parameter_parser.RunPars` or None) contains the combination of all parameter sources, where self.cmd_pars \> self.in_pars \> self.def_pars \> self.ref_pars. If this behaviour is too naive, the contents can be changed with the function GM_adjust_run_pars listed below. This is where other functions should retrieve parameter choices from.

  .. tip:: self.run_pars also has a reference to the main-program RunPars - it is stored as self.run_pars.main_run_pars.
- self.code (type module) contains all functions defined in main.py. Any functions that the program needs, but are not specified in main.py are automatically filled in. Any object that the program does not require, but is still there, is also available.
- self.rawcore (type dict of str-list pairs) contains the information from core.txt, before parsing. The function GM_adjust_map_core_raw can change this simple structure before it is being parsed into more complex structures and functions later.
- self.core (type :class:`~GMAP.src.tools.map_reader.SingleCore`) contains the information from core.txt, after parsing.

system
======
An instance of :class:`~GMAP.src.tools.system_reader.System`. Stores all available information about the MD system used. Think atom-based information on it's name, element, type, the name and number of its residue, molecule, segment. Also charges, positions, masses and such are in here. 


.. important:: 
    When your functions should report/print anything, **do not** use the python build-in function print. Instead, import the GMAP print_tools module (``from GMAP.src.tools import print_tools as GM_pt``), from which you can call an instance of the Printer class. This instance is a singleton (so all print settings for that run are already set), so don't change it! But you can have it print (``GM_pt.Printer.print``), or even trigger an error (``GM_pt.Printer.warning``). See :class:`~GMAP.src.tools.print_tools.Printer` for detailed information on using these functions.


*************************
Overview of all functions
*************************

The function are in the order at which they're called by the program. This means that if any functions create additional attributes for the class, any functions listed below those functions will have access to those attributes, any functions listed above them will not.



.. #region GM_adjust_run_pars

GM_adjust_run_pars
======================================
Makes the necessary changes to map\_.run_pars.

Is expected to not return anything - return value is not caught.


Example uses
------------


interlinked parameters
^^^^^^^^^^^^^^^^^^^^^^
Take the three parameters start_frame, end_frame and frames_tocalc. In the default file, these may be set to 0, 100 and 100 respectively. This makes sense, as if you start on frame 0 and end at frame 100 (exclusive), you will see 100 frames. But if in the input file the choice to start at frame 10 was given, the default run_pars creation will select the numbers 10, 100, 100, which doesn't make sense (there is not 100 frames to treat between frames 10 and 100). Custom code can change these to 10, 100, 90.


dependent parameters
^^^^^^^^^^^^^^^^^^^^
Some maps are designed with certain assumptions in mind. These assumptions don't always mix. Because of this, it can happen that when a choice for one parameter is made, not all choices should be available for another. Custom code can solve this kind of conflicts.

Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code

Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_adjust_run_pars(map_):
        pass
.. #endregion



.. #region GM_adjust_map_core_raw

GM_adjust_map_core_raw
===========================================

Makes the necessary changes to the 'raw' input read from core.txt.

Is expected to not return anything - return value is not caught.

The core.txt file is stored in map\_.rawcore. It has not yet been parsed, just loaded into a dictionary. In this dictionary, each keyword is its own dictionary key. Most keywords can only occur once in the file - those have a list of the 'words' on the line as their value. The parameters that are allowed to occur more than once have a list as value, in which other lists appear - one for each line.

The purpose of this function is to change this dictionary. Perhaps, a rule in core.txt is dependent on a parameter of the map. This function can make a decision based on those parameters (stored in map\_.run_pars).


Example uses
------------

Dependency on map parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The core.txt file gives the option to link a file containing the map constants. There are cases (for example, the Amide-I stretch) for which multiple different sets of constants have been developed. In this case, it would be useful for this function to select a different file with map constants based on a map-specific parameter.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_adjust_map_core_raw(map_):
        pass
.. #endregion



.. #region GM_adjust_oscillators

GM_adjust_oscillators
=================================================================

Finalizes the list of oscillators.

Is expected to return a list of oscillators - by default, it returns oscillator_list.

The purpose of a map is to define how to calculate the properties for a certain kind of oscillator. The program will find instances of that oscillator in the MD system based on the choice for 'functional_group' in core.txt. After they've been found, they are passed to this function. The reason for this is twofold. Fistly, this allows the map to change this list if it were necessary (see example uses). Secondly, it allows the map to 'see' the oscillators for the first time, allowing it to identify the type of an oscillator, for example. When all oscillators are passed through this function, the (global) atom number of the first atom of this group (for example) can be linked to a specific property the group might need to know. This might be useful if a map needs to cover two very similar oscillators.

.. note::
    This function is called once for each map. This single call will contain all oscillators, sorted by struct (in the same struct order as in which the structs are defined). So take into account that the function could be provided with multiple different structs at a time


Example uses
------------

A map needs to deal with two kinds of oscillator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The AmideBB map is an example of this. When the second residue participating in the oscillator is the amino acid proline, some things need to be done differently. For example, the map parameters are different. In this function, the map can identify whether the presented oscillators are of the 'regular' type, or the 'pre-proline' type, and store this information accordingly.

Please do note that when using different 'kinds' of oscillator, this method is not always the desired solution. In some cases, it might be better to split the functionalities into two separate maps (like has been done with AmideSC and AmideBB).

A functional group is fully symmetrical
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The CystBridge map is an example of this. It is a map spanning two residues, but the two residues are functionally identical - the selection language does not allow to distinguish them. This means that every oscillator is found twice - once listing first A, then B, and once listing first B, then A. Here, A denotes the residue with the smallest atomic indices, B the one with the largest. This function can, in that case, be used to remove the BA instances, and only keep the AB ones.

A single functional group actually contains two oscillators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The water map is a good example of this. The map is designed such that two oscillators should be put in the hamiltonian for each water molecule. This function allows the map to return both, back to back.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
oscillator_list : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillators that were identified as a good match for this map.

Returns
-------
oscillator_list : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillators that were identified as a good match for this map.

Default implementation
----------------------

.. code-block:: python

    def GM_adjust_oscillators(map_, system, oscillator_list):
        return oscillator_list
.. #endregion



.. #region GM_filter_oscillators

GM_filter_oscillators
===========================

This is where a map is supposed to process the user choice for the parameters singles_whitelist and singles_blacklist. The choice for this parameter is saved (parsed) in the run_pars object. run_pars.singles_whitelist_dict for the whitelist choice, and run_pars.singles_blacklist_dict for the blacklist choice. Both contain a dictionary - if you enter the name of your map as a key into this dictionary, out pops a list. Each item in this list corresponds to a single line in the parameter file, and is itself a list of 'words' (result of line.split()). The parameter name and map name have already been stripped from the list, so the first item of the list is the ``method`` field as described on the  :ref:`input parameters page <UserGuide_page_parameter_overview>`.

This function is expected to return a list of oscillators, preferably in the same order as the oscillator_list that entered the function, but only containing those selected by the user.

.. tip::
    At first, this function might feel very similar to GM_adjust_oscillators. They are even called back-to-back by the program, with the output of GM_adjust_oscillators being the input for this one.

    It therefore, in theory, is possible to have one of these two do the work of both, but this is adviced against. While GM_adjust_oscillators is meant to find all oscillators present in the system exactly once, GM_filter_oscillators is meant to take a subset of all available onces based on user choice.


Example uses
------------

A map needs to know what groups were chosen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The (early) AmideBB map is an example of this. To calculate a certain correction to the frequency, it wants to know the positions of the neighbouring groups. However, it is possible that a group itself was selected for by a user, but (one of) its neighbours was not. This is an issue as GMAP does not automatically update/generate the positions of an oscillator that hasn't been chosen. Therefore, it wants to know which neighbours have not been chosen, so it can update them itself.

A different method of black-/whitelisting oscillators is desired
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The (future) AmideBB could be an example of this. GMAP only allows for looking for the residue number/name of the residue of the first atom. However, a user might want to sort by the residue name of the second half of the oscillator instead.

It is suggested that custom implementations still use the 'filter_single_line' function, as this allows to easily implement default behaviour. Then, if that function returns 'False' as success, it didn't recognize the method, indicating for the maps custom implementation that that line requires further processing.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
oscillator_list : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillators that were identified as a good match for this map.

Returns
-------
oscillator_list : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillators that were identified as selected by the user.

Default implementation
----------------------

This is an approximate implementation omitting some checks/safety/details, intended to get the idea across. If you need to see the full implementation, look at the function ``get_filter_oscillators`` from default_map_functions.py.

.. code-block:: python

    def GM_filter_oscillators(map_, system, oscillator_list):
        runpars = map_.run_pars.main_run_pars
        wl_rules = runpars.singles_whitelist_dict.get(map_.name, [[":All"]])
        bl_rules = runpars.singles_blacklist_dict.get(map_.name, [[":None"]])

        filtered = set()
        oscset = set(oscilator_list)
        for rule in wl_rules:
            filtered = filter_single_line(
                rule, "white", filtered, oscset, map_, system)
        
        for rule in bl_rules:
            filtered = filter_single_line(
                rule, "black", filtered, oscset, map_, system)
        
        filtered_list = [osc for osc in oscillator_list if osc in filtered]
        return filtered_list
    

    def filter_single_line(line, BW, found, avail, map_, system):
        match line[0].lower():
            case ":all":
                if BW == "white":
                    return True, avail.copy()
                else:
                    return True, set()
            case ":none":
                if BW == "white":
                    return True, set()
                else:
                    return True, found.copy()
            case "resnums":
                numbers = set(map_.core.allow_ranges(line[1:], system.nres))
                filtered = {
                    osc for osc in avail
                    if system.resnums[osc.used_atoms[0]] in resnums
                }
                if BW == "white":
                    found |= filtered
                else:
                    found -= filtered
                return True, found
            case "resnames":
                resnames = set(line[1:])
                filtered = {
                    osc for osc in avail
                    if system.resnames[osc.used_atoms[0]] in resnames
                }
                if BW == "white":
                    found |= filtered
                else:
                    found -= filtered
                return True, found
            case _:
                return False, found

.. #endregion



.. #region GM_post_init

GM_post_init
=======================================

Allows the user to do some final initialization steps. These can include building lookup-tables, or computing some basic properties for later use. This function is called when all initialization is done (maps, MD system, etc).

Is expected to not return anything.

If the property is position/frame dependent, it should instead be computed in GM_pre_frame. 


Example uses
------------

The map requires further information on the system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some mappings require further information. One example are the backbone amides - these live in a covalently bound chain, which makes it important to know which other oscillators are (closely) bound. It is easiest (and fastest) if this information is readily available during the calculation. Furthermore, this property will not change during the calculation / between frames.

This kind of information should be collected as part of the initialization. This function should be used to look this information up, and store it as an attribute of the Map object that is passed to this function.


Setting different values for certain parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some parameters are only set simply. Like local_ix. If a more complex selection of local_ix is desired, it can be enforced here.

Changing units
^^^^^^^^^^^^^^
The main purpose of a map is to provide constants to calculate spectroscopic properties. These constants assume that the properties they are combined with are provided in certain units (see the :ref:`units page<AddMap_units>` for more information). However, these assumptions might not always match this program. 

One could either do the conversion first, and save the converted constants with the correct assumptions in the files supplied to GMAP, or let GMAP do this conversion. The latter might be preferred if one wants the files to match the original publication of the map. In that case, this function here is the best place for a map to do the conversion. To make the conversion easy, use the function map\_.core.change_map_units().


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_post_init(map_, system)
        pass
.. #endregion



.. #region GM_pre_run

GM_pre_run
=======================================

Allows the user to prepare the structures needed for the run.

Is expected to not return anything.


Example uses
------------

New output type
^^^^^^^^^^^^^^^
If the map wants to compute a new property / output type, the data structure storing that property could be initialized here.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_pre_run(map_, system)
        pass
.. #endregion



.. #region GM_pre_frame

GM_pre_frame
=======================================

Allows the user to compute information that will change for each frame.

Is expected to not return anything.

If such a property is only needed once, it should be calculated at the time it is needed. But if multiple outputs (frequency and dipole, for example) or multiple oscillators need it, it should go here. If the property is not position/frame dependent, it should be computed in GM_pre_run.


Example uses
------------

To be added
^^^^^^^^^^^
To be explained.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_pre_frame(map_, system)
        pass
.. #endregion



.. #region GM_post_frame

GM_post_frame
=======================================

Allows the user to finalize the frame.

Is expected to not return anything.


Example uses
------------

New output type
^^^^^^^^^^^^^^^
If the map wants to compute a new property / output type, the computed data should be written to a file here.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_post_frame(map_, system)
        pass
.. #endregion



.. #region GM_post_run

GM_post_run
=======================================

Allows the user to do some final reports.

Is expected to not return anything.


Example uses
------------

Reporting on the calculation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the user should know anything about the computation that has been performed, they can be told by this function.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_post_run(map_, system)
        pass
.. #endregion



.. #region GM_str_osc

GM_str_osc
==============================

Returns the (human-readable) string representation of an oscillator of this type.

This function is used whenever the program needs to report some information about an oscillator to the user. This could either be as part of an error warning, or as general reporting (legend of the output files, what each oscillator actually looks like).
By default (if this function is not present) this representation is the following: ``Oscillator of type [mapname] living on residue number [resnum]``. Here, ``[mapname]`` will be replaced by the program with the actual name of the map the oscillator belongs to, and ``[resnum]`` will be replaced with the residue number of the first atom (in ``used_atoms``) of the oscillator.


Example uses
------------

Clearly indicating an oscillator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The default is very generic, and should give some information to identify an oscillator. However, for some kinds of oscillator, this information might not be sufficient, or hard to interpret. For example, any protein-related maps will most likely want to print the residue name along with its number, as that is how literature usually refers to them. 
 

Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the rotation matrix should be determined.

Returns
-------
print_string : str
    The string that should be printed to the legend file to explain what the oscillator looks like / which it is

Default implementation
----------------------

.. code-block:: python

    def GM_str_osc(map_, system, osc):
        return f"living on residue number {system.resnums[osc.used_atoms[0]]}"
.. #endregion



.. #region GM_report_system

GM_report_system
=================================

Reports what this part of the system looks like.

This function is used whenever the program needs to report some information about all oscillators of this type to the user, as part of a full system summary.

By default (if this function is not present) this representation is the following: ``[mapname]:      [amount]``. Here, ``[mapname]`` will be replaced by the program with the actual name of the map being reported on, and ``[amount]`` will be replaced with the amount of oscillators of this type.


Example uses
------------

Providing the total amount of oscillators is insufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The default is very generic, and only gives some information on how much of a certain (requested!) type of oscillator is present. This might, however, not be enough for all types of oscilators.

As an example, take the amide groups in protein backbones. It would be very useful to report these per protein chain instead: so, to first report the amount of chains, and then the amount of groups contained within each chain.
 

Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.

Returns
-------
print_string : str
    The string that should be printed to report on this part of the system.

Default implementation
----------------------

.. code-block:: python

    def GM_report_system(map_, system):
        name = map_.name + ":"
        amount = len(system.oscillators_ordered[map_.name])
        return f"{name: <21} {amount: >4}"
.. #endregion



.. #region GM_get_rotation_matrix

GM_get_rotation_matrix
===============================================

Returns the rotation matrix for the provided oscillator osc.

A map usually requires the electrostatic properties to be given in a certain coordinate basis. Usually, this is not the global cartesian coordinates, but rather those rotated in a certain way. The rotation matrix defines the desired basis in global cartesian coordinates.

.. important::
    The electrostatic field/gradient should only be rotated, not sheared or scaled. Therefore, the provided rotation matrix should consist of three orthonormal vectors.

If this function is not provided in the main.py file, the information stored in the parameters xyz_uvec in the core.txt file will be used instead to build a function with.

.. tip::
    In order to arrive at the correct result, this function should take into account the PBC. More information on PBC can be found :ref:`in the theory section<Theory_page_PBC>`. To help, the oscillator object provided has the attribute osc.positions_box - this array contains the positions of all atoms in used_atoms, transposed to box coordinates. To convert the final answer back to cartesian coordinates, multiply it with System.boxvects.


Example uses
------------

The default method of providing the rotation matrix is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some techniques cannot be used in box coordinates, and can therefore not be used through core.txt. In those cases, it might be more appropriate to write the code here.


Available attributes of map\_
------------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the rotation matrix should be determined.


Returns
-------
rotation_matrix : `np.ndarray`
    The matrix that should be used to convert the electrostatic properties. rotation_matrix[0] should return a vector of length 3 defining what the box-x vector should look like, in cartesian coordinates. Same for [1] giving the y, and [2] giving the z. The three vectors are orthonormal.

Default implementation
----------------------

The default implementation depends on the contents of the core.txt file. Here are a few examples of what the corefile could look like, and what the corresponding default function looks like:

A 'standard'-type molecule, with x as primary axis, y as secondary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

core.txt file::

    x_uvec  3 - 2
    y_uvec  1 - 2
    type standard

default code:

.. code-block:: python

    import numpy as np
    import GMAP.src.tools.math_functions as GM_mf

    def GM_get_rotation_matrix(map_, system, osc):
        x_uvec = (osc.positions_box[3] - osc.positions_box[2]) @ system.boxvects
        x_uvec /= GM_mf.vec3_len(x_uvec)

        y_uvec = GM_mf.project(x_uvec,
            (osc.positions_box[1] - osc.positions_box[2]) @ system.boxvects)
        y_uvec /= GM_mf.vec3_len(y_uvec)

        z_uvec = GM_mf.crossprod(x_uvec, y_uvec)
        z_uvec /== GM_mf.vec3_len(z_uvec)

        return np.array([x_uvec, y_uvec, z_uvec])


A 'standard'-type molecule, with y as primary axis, z as secondary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

core.txt file::

    y_uvec  3 - 2
    z_uvec  1 - 2
    type standard

default code:

.. code-block:: python

    import numpy as np
    import GMAP.src.tools.math_functions as GM_mf

    def GM_get_rotation_matrix(map_, system, osc):
        y_uvec = (osc.positions_box[3] - osc.positions_box[2]) @ system.boxvects
        y_uvec /= GM_mf.vec3_len(y_uvec)

        z_uvec = GM_mf.project(
            y_uvec,
            (osc.positions_box[1] - osc.positions_box[2]) @ system.boxvects)
        z_uvec /= GM_mf.vec3_len(z_uvec)

        x_uvec = GM_mf.crossprod(y_uvec, z_uvec)
        x_uvec /== GM_mf.vec3_len(x_uvec)

        return np.array([x_uvec, y_uvec, z_uvec])


A 'linear'-type molecule, with z as primary axis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

core.txt file::

    z_uvec  1 - 0
    type linear

default code:

.. code-block:: python

    import numpy as np
    import GMAP.src.tools.math_functions as GM_mf

    def GM_get_rotation_matrix(map_, system, osc):
        z_uvec = (osc.positions_box[1] - osc.positions_box[0]) @ system.boxvects
        z_uvec /= GM_mf.vec3_len(z_uvec)

        smalldir = np.argmin(np.abs(z_uvec))
        x_uvec = np.zeros((3))
        x_uvec[smalldir] = 1
        x_uvec = GM_mf.project(z_uvec, x_uvec)
        x_uvec /= GM_mf.vec3_len(x_uvec)

        y_uvec = GM_mf.crossprod(z_uvec, x_uvec)
        y_uvec /== GM_mf.vec3_len(y_uvec)

        return np.array([x_uvec, y_uvec, z_uvec])
.. #endregion



.. #region GM_get_dipole_dir

GM_get_dipole_dir
==========================================

Returns the direction of the dipole vector and its position in cartesian coordinates.

.. caution::
    This function is expected to return a normalized vector for the dipole moment - it's length should be 1!

.. tip::
    In order to arrive at the correct result, this function should take into account the PBC. More information on PBC can be found :ref:`in the theory section<Theory_page_PBC>`. To help, the oscillator object provided has the attribute osc.positions_box - this array contains the positions of all atoms in used_atoms, transposed to box coordinates. To convert the final answer back to cartesian coordinates, multiply it with System.boxvects.


Example uses
------------

The default method of providing the dipole vector direction is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some techniques cannot be used in box coordinates, and can therefore not be used through core.txt. In those cases, it might be more appropriate to write the code here.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the dipole moment vectors should be determined.


Returns
-------
r_vec : `np.ndarray`
    The (length-3) vector that represents the direction of the dipole moment of this oscillator. It should have the dtype `float32`, and the vector must be normalized.
r_pos : `np.ndarray`
    The (length-3) position vector at which the dipole vector lies. The vector must lie within the simulation box.


Default implementation
----------------------

The default implementation is dependent on the corefile. The marked lines in the code example are generated flexibly by the program upon reading the core.txt file, to match the user request. This method only allows for a simple direction definition, not the more complex one where each of the (local) x-, y- and z coordinates has its own dependence on the electrostatics from the environment. For that complex case, GM_calculate_dipole has a different implementation that does not depend on GM_get_dipole_dir.

core.txt file::

    r_vec  1 - 0  # dipole vector points in the direction from atom 0 to atom 1
    r_pos  (0 + 1) / 2.0  # dipole vector originates from halfway between atom 0 and 1

.. code-block:: python

    import numpy as np
    import GMAP.src.tools.math_functions as GM_mf

    def GM_get_dipole_dir(map_, system, osc):

        # First, main dipole vector:

        # main vector direction (in box coordinates)
        # This line is the code representation from the contents of the file.
        # All following lines for r_vec are independent of core.txt contents.
        r_vec = (osc.positions_box[1] - osc.positions_box[0]) @ system.boxvects
        
        # adjusting vector for PBC
        r_vec = (r_vec - np.floor(r_vec + 0.5))  # normalize box coordinates
        r_vec = r_vec @ system.boxvects  # back to cartesian coordinates

        # normalizing and correct type.
        r_vec /= GM_mf.vec3_len(r_vec)  # only a direction -> normalize!!
        r_vec = r_vec.astype('float32')  # correct numpy dtype

        # Then, position of dipole vector:
        # This line is the code representation from the contents of the file.
        # All following lines for r_pos are independent of core.txt contents.
        r_pos = (osc_positions_box[0] + osc_positions_box[1]) / 2.0

        # adjusting vector for PBC
        r_pos = (r_pos - np.floor(r_pos + 0.5))  # normalize box coordinates
        r_pos = r_pos @ system.boxvects  # back to cartesian coordinates

        # switching to correct type.
        r_pos = r_pos.astype('float32')  # correct numpy dtype

        return r_vec, r_pos
.. #endregion



.. #region GM_get_dipole_mag

GM_get_dipole_mag
==========================================

Returns the magnitude of the dipole vector in Debye.

.. tip::
    The magnitude of the dipole vector should be in units of Debye, and will by default be applied to the direction found by GM_get_dipole_dir()


Example uses
------------

The default method of providing the dipole vector direction is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes, the magnitude has a more complex dependence than the one offered by default. In those cases, it might be more appropriate to write the code here.



Available attributes of map\_
------------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the dipole moment magnitude should be determined.


Returns
-------
magnitude : `np.float32`
    The length that the dipole moment vector should have.


Default implementation
----------------------

The default implementation only works with a set magnitude, or a magnitude map. It does not allow for the xyz-dependent maps. When those kinds of maps are found, the implementation for GM_get_dipole changes such that it no longer uses this function.


.. code-block:: python

    import GMAP.src.tools.default_map_functions as GM_dmf

    def GM_get_dipole_mag(map_, system, osc):
        if map_.core.dipole_data_array is not None:
            return GM_dmf.uses_maps(
                map_.core.dipole_gas_phase,
                [osc.VEGout],
                [map_.core.dipole_data_array]
            )
        else:
            return map_.core.dipole_gas_phase
.. #endregion



.. #region GM_calculate_dipole

GM_calculate_dipole
============================================

Returns the dipole vector and its position in cartesian coordinates.

.. tip::
    By default (for single-VEG dependence, or no VEG dependence), this function is the combination of GM_get_dipole_dir and GM_get_dipole_mag. If only the functionality of one of those needs to be changed, doing that instead of imposing different behaviour here is adviced.


Example uses
------------

The default method of providing the dipole vector is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes, the dipole moment is determined in a more complex method than supported by the program. In those cases, it might be more appropriate to write the code here.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the dipole moment magnitude should be determined.


Returns
-------
r_vec : `np.ndarray`
    The vector that represents the dipole moment of this oscillator. It should have the dtype `float32`, and the vector should be normalized.
r_pos : `np.ndarray`
    The position at which the dipole vector lies.


Default implementation
----------------------

There are two main different ways of calculating the dipole moment. The first is by determining the dipole direction and magnitude following the GM_get_dipole_dir and GM_get_dipole_mag methods, and multiplying the two. However, as those methods also mention, that only works for some types of dipole specifications. When the dipole has each of its x-, y- and z-components depend on the electrostatics in a different way, a different method is needed. The actual implementation defines two possible ways of calculating the dipole moment, and then looks at the supplied map to see which is applicable, and return the correct method. That method selection should not be done within this function, but, eg. in the post_init function. It works as follows:

.. code-block:: python

    def function_determiner(map_):

        # if there is no array, just a set magnitude provided in the corefile:
        if map_.core.dipole_data_array is None:
            return dir_mag_method
        
        # there is a special array, it is 2D, so only 1 dependence:
        if len(map_.core.dipole_data_array.shape) == 2:
            return dir_mag_method
        
        # Otherwise, the array is 3-dimensional, so there are separate x, y
        # and z dependencies:
        return xyz_method

Again, these methods above are what this function contains, something like the above example is only for steps before the calculation (like post_init).

The contents of this function (GM_calculate_dipole) have two (the above-mentioned) possible defaults. The first is for 'simpler' dipoles with a provided direction and position (in the above code called dir_mag_method):

.. code-block:: python

    def GM_calculate_dipole(map_, system, osc):
        r_vec, r_pos = map_.code.GM_get_dipole_dir(map_, system, osc)
        r_vec *= map_.code.GM_get_dipole_mag(map_, system, osc)
        r_vec = r_vec.astype("float32")
        return r_vec, r_pos

In case of the separate x-, y- and z dependencies (in the above method selector referred to as xyz_method), the default implementation is as follows:

.. code-block:: python

    def GM_calculate_dipole(map_, system, osc):
        _, r_pos = map_.code.GM_get_dipole_dir(map_, system, osc)
        xyz = [
            uses_maps(omega, [osc.VEGout], [arr]) for omega, arr in zip(
                map_.core.dipole_gas_phase, map_.core.dipole_data_array)
        ]
        xyz_local = np.array(xyz, dtype="float32")
        xyz_cartesian = np.dot(xyz_local, osc.rotation_matrix)
        return xyz_cartesian, r_pos
.. #endregion



.. #region GM_calculate_frequency

GM_calculate_frequency
===============================================

Returns the frequency at which the oscillator is expected to give a signal (resonate), in units of cm-1.


Example uses
------------

The default method of providing the frequency is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes, the frequency is determined in a more complex method than supported by the program. In those cases, it might be more appropriate to write the code here.


Available attributes of map\_
-----------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the dipole moment magnitude should be determined.


Returns
-------
freq : float
    The frequency at which this oscillator is expected to absorb.


Default implementation
----------------------

There are multiple different ways of calculating the frequency. While all methods take the gas phase frequency as a base, the linear and quadratic dependencies are optional. That results in 4 total possible options.

Gas phase only
^^^^^^^^^^^^^^
.. code-block:: python

    def GM_calculate_frequency(map_, system, osc):
        return map_.core.frequency_gas_phase

Gas phase and linear dependence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    def GM_calculate_frequency(map_, system, osc):
        freq = uses_maps(
            map_.core.frequency_gas_phase, [osc.VEGout],
            [map_.core.frequency_data_array_linear]
        )
        return freq

Gas phase and quadratic dependence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    def GM_calculate_frequency(map_, system, osc):
        freq = uses_maps(
            map_.core.frequency_gas_phase, [osc.VEGout**2],
            [map_.core.frequency_data_array_quadratic]
        )
        return freq

Gas phase and both linear and quadratic dependence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    def GM_calculate_frequency(map_, system, osc):
        freq = uses_maps(
            map_.core.frequency_gas_phase,
            [osc.VEGout, osc.VEGout**2],
            [
                map_.core.frequency_data_array_linear,
                map_.core.frequency_data_array_quadratic]
        )
        return freq
.. #endregion



.. #region GM_calculate_raman

GM_calculate_raman
=========================================

Returns the expected raman tensor for the given oscillator. The raman tensor is (along with dipoles and frequencies) required for programs to calculate different kinds of spectra: raman spectrum, SFG spectrum, 2D-Raman spectrum, 2D-IR-Raman spectrum. 


Example uses
------------

A raman output is desired
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Calculating raman spectra is still relatively new, so a default method for doing so has not yet been developed. Therefore, if a raman output is desired, the map-maker must define their own method.


Available attributes of map\_
------------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the dipole moment magnitude should be determined.


Returns
-------
freq : float
    The frequency at which this oscillator is expected to absorb.


Default implementation
----------------------

Due to the highly specific nature of this functionality, no default method has been implemented (yet). If Raman calculations become more common (mroe than the current 1 or 2 available maps), a default method can be established.
.. #endregion



.. #region GM_get_VEG_ref

GM_get_VEG_ref
=================================================================

Returns the centerpoint for the sphere of charges contributing to the calculated electrostatics.

.. tip::
    In order to arrive at the correct result, this function should take into account the PBC. More information on PBC can be found :ref:`in the theory section<Theory_page_PBC>`. To help, the oscillator object provided has the attribute osc.positions_box - this array contains the positions of all atoms in used_atoms, transposed to box coordinates. To convert the final answer back to cartesian coordinates, multiply it with System.boxvects.


Example uses
------------

The default method of providing the elecctrostatics sphere center is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some techniques cannot be used in exclusively box coordinates, and can therefore not be used through core.txt. In those cases, it might be more appropriate to write the code here.


Available attributes of map\_
-------------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The oscillator for which the rotation matrix should be determined.


Returns
-------
VEG_ref : `np.ndarray`
    The position at which the sphere should be centered.


Default implementation
----------------------

There are multiple different ways of calculating the VEG reference position, depending on the method requested by the user in the core.txt file. 

residues method
^^^^^^^^^^^^^^^^

Takes the centre of mass of all atoms of the mentioned residues. If two mentioned atoms belong to the same residue, all atoms in that residue will be counted twice!

core.txt file::

    VEG_reference residues 0 6

default code:

.. code-block:: python

    import GMAP.src.tools.physics_functions as GM_pf

    def GM_get_VEG_ref(map_, system, osc):
        local_atoms = [int(num) for num in map_.local_atoms]

        atnums = []
        for atom in local_atoms:
            resnum = system.resnums[osc.used_atoms[atom]]
            atnums.extend([*range(
                system.residues.first_ix[resnum],
                system.residues.last_ix[resnum] + 1
            )])
        CoM = GM_pf.calc_CoM(system, atnums)
        return CoM


CoM method
^^^^^^^^^^^^^^^^

Takes the centre of mass of all provided atoms.

core.txt file::

    VEG_reference CoM 0 6

default code:

.. code-block:: python

    import GMAP.src.tools.physics_functions as GM_pf

    def GM_get_VEG_ref(map_, system, osc):
        local_atoms = [int(num) for num in map_.local_atoms]

        atnums = [osc.used_atoms[ix] for ix in local_atoms]
        CoM = GM_pf.calc_CoM(system, atnums)
        return CoM


Position method
^^^^^^^^^^^^^^^^

Allows the user to directly specify an exact position.

core.txt file::

    VEG_reference position 0.625 * 1 + 0.375 * 3

default code:

.. code-block:: python

    import GMAP.src.tools.physics_functions as GM_pf

    def GM_get_VEG_ref(map_, system, osc):
        # This line is the code representation from the contents of the file.
        # All following lines for refpos are independent of core.txt contents.
        refpos = (0.625 * osc_positions_box[0] + 0.375 * osc_positions_box[1])

        # adjusting vector for PBC
        refpos = (refpos - np.floor(refpos + 0.5))  # normalize box coordinates
        refpos = refpos @ system.boxvects  # back to cartesian coordinates

        return refpos

.. #endregion



.. #region GM_report_references

GM_report_references
=================================================================

Returns the references that should be reported for this map.

.. tip::
    This function becomes much easier to write when the references have well-chosen mapkeys. See the documentation on the reference file for more explanation on this field.

All references present in the references file are saved as ``map_.references``, this function is intended to only return a subset of that dictionary. The structure of the dictionary is as follows:

The keys in this dictionary are the separate keys listed in the reference.bib file's 'mapkey' field. If the reference has multiple keys in that field, it will occur multiple times in the dictionary, once for each key.

Associated with each key is a list of :class:`~GMAP.src.tools.reference_handler.Reference` objects, each of which corresponds to a single entry in the .bib file.


Example uses
------------

The map allows the application of multiple models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some functional groups have been mapped by multiple different research groups. Especially when they do have a similar structure, it makes sense to group all these different scientific maps (called 'models' from now to avoid confusion) within a single GMAP map. However, it happens that two different models don't come from a single paper. In these cases, the default would be that the papers of all models are referenced in the map references file, and GMAP reports them all. This is undesired, the correct behaviour would be to only report the paper of the model actually used. This function allows selecting the papers of a single model, instead of all of them. 


Available attributes of map\_
-------------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.ref_pars
    * self.def_pars
    * self.in_pars
    * self.cmd_pars
    * self.run_pars
    * self.code
    * self.rawcore
    * self.core
    * self.references


Parameters
----------
map\_ : :class:`~GMAP.src.tools.map_reader.Map`
    The object that stores everything the program currently knows
    about this map.
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.


Returns
-------
references_dict : dict
    A dictionary with all references to be cited, grouped by key. The structure of this dict should be the same as that of ``map_.references``, making slicing from the latter easier.


Default implementation
----------------------

The default is to just return the entire ``map_.references`` dictionary, without omitting anything.


default code:

.. code-block:: python

    import GMAP.src.tools.physics_functions as GM_pf

    def GM_report_references(map_, system):
        return map_.references


.. #endregion
