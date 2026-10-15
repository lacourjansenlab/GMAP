.. _AddMap_FileStruct_PairMainPy:

#######
main.py
#######

(this applies to pairs maps. If you are looking for singles maps instead, go to :ref:`the singles version of this page.<AddMap_FileStruct_SingMainPy>`)

This file contains the code for the map. Pair maps do need to have some code - this is the distinguishing factor between them. Within this file, there are a few functions the program will look for. If they are missing, that is no issue, but their names should not be used for any other purpose.

The file can contain other functions (or even call functions from other files in the map directory), to allow for writing any kind of code yourself. However, creating your own new function (or class/variable/module) names has a danger - if the program assumes any of them to have a special meaning, the code may function differently than expected. In order to avoid any name clashes, you should avoid any of the following (categories of) names:

- Names starting with "GM\_" - These are reserved for functions expected by GMAP. Even if a name starting with GM\_ isn't used by the program yet, it might be in the future, so its best practice to just avoid them in general.
- Names starting with "CP\_" - These are reserved for other coupling maps requesting information.
- Any of the names that should be avoided courtesy of general coding good practices.



***************
Basic structure
***************

There are a few objects that occur quite often as an argument for these functions. Here is a quick overview of them:

map\_
=====
An instance of :class:`~GMAP.src.tools.map_reader.PairMap`. Stores all information of this class. This is the most important object, as it stores everything related to this class. As functions of the map can change how the map is registered, this object will look different during the different functions. Here is an overview of all attributes the class can have, at each function it will be explained/highlighted what attributes are available at that point.

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
- self.core (type :class:`~GMAP.src.tools.map_reader.PairCore`) contains the information from core.txt, after parsing.
- self.allpairs (type numpy array, dtype int32, shape (npairs, 2) ) contains all pairs that should be coupled using this pair map. This array has already taken into account any changes due to the function change_coup_type. Looping over a numpy array isn't fast, so map developers are encouraged to use these arrays wisely.


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
Makes the necessary changes to map\_.run\_pars.

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



.. #region GM_change_coup_type

GM_change_coup_type
==========================================================

Decides what coupling map should be used for a given pair of oscillators.

Is expected to return the name of the map that should be used for this oscillator pair.

The program should determine for any given pair of oscillators what map should be used to calculate the interaction between the two. This determination, however, is exactly as crude as the input parameter file implies: the program can base itself on only the name of the map associated with each oscillator. Using just the names of the maps for this could work in some cases, but maybe not in others. If a pair of oscillators (based on their map names) was assigned this map, this function is called. This function allows for further selection after that.


Example uses
------------

Amide groups in protein backbones
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Proteins consist of aminoacids. These are bonded together through amide bonds, the shortest path through these bonds is the backbone of the protein. If the user wants to use a certain map for amides, any pair of amides will be given to that map. This is actually an issue - two so-called neighbouring amide bonds are close enough that any through-space methods (like dipole-dipole coupling) are not accurate. However, the required properties for such coupling are not defined for non-neighbouring amides. So, we need a different map for neighbouring groups vs non-neighbouring. Through this function, this map can say 'hey, I'm designed for neighbouring groups only, you two are not neighbours, you should use that map over there instead'.


Water molecules with two internal vibrations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Water is a special little molecule. It turns out that a good way of simulating the water spectrum is to cut it up - have each molecule correspond to two oscillators (one for each OH bond). This means that there will be two types of couplings - between two oscillators in the same molecule (intramolecular), or between two oscillators in different molecules (intermolecular). Just as with the amides, it turns out that it is not physically accurate to use the same kind of map for both inter- and intramolecular couplings. This function allows the map to see which it is, and assign a certain coupling map to this exact pair based on that.


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
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
oscix1 : int
    The oscillator index of the first oscillator of this pair. This is its index in output structures, like the hamiltonian or dipoles file.
osc1 : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The first oscillator in this pair.
oscix2 : int
    The oscillator index of the second oscillator of this pair. This is its index in output structures, like the hamiltonian or dipoles file.
osc2 : :class:`~GMAP.src.tools.system_reader.Oscillator`
    The second oscillator in this pair.

Returns
-------
map_to_use : str
    The name of the map that should treat this coupling pair.

Default implementation
----------------------

.. code-block:: python

    def GM_change_coup_type(map_, system, oscix1, osc1, oscix2, osc2):
        return map_.name
.. #endregion



.. #region GM_prep_coupling

GM_prep_coupling
==========================================================

Any preparation that the map needs to do for calculating couplings is done here.

Is not expected to return anything - return value is not caught.

Most coupling methods take some property of each oscillator in the pair, and combine these to arrive at the coupling. These properties are not always readily available, but might need some calculations themselves. Due to efficiency considerations, anything that can be done per oscillator (as opposed to per pair) should be done that way. That's what this function is for.

Important to note is the fact that this function is called once per frame, per map. That means that the map itself must loop over all the oscillators if desired.


Example uses
------------

Dipole-dipole coupling
^^^^^^^^^^^^^^^^^^^^^^
When calculating the coupling between two dipoles, the dipole moment and position of each is required. Important to realize here, is the fact that this kind of coupling is incredibly common - it is very probable that hamiltonians with thousands or even millions of these kinds of couplings will be treated.

This means that efficiency is incredibly important. The kinds of optimizations considered for this map require that all those dipole moments and dipole positions are saved close to each other (data structure / harddisk wise). This function collects those properties and saves them in dedicated structures (numpy arrays). This allows an increase in speed of up to a factor 100.


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
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
oscixlist : list of int
    The oscillator indices of all oscillators that are treated by this map. Some might be only in a single pair, others in many.
osclist : list of :class:`~GMAP.src.tools.system_reader.Oscillator`
    All oscillators treated by this map.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_prep_coupling(map_, system, oscixlist, osclist)
        pass
.. #endregion



.. #region GM_calc_coupling

GM_calc_coupling
==========================================================

Calculates the coupling for each pair associated with this map, and saves the result in the hamiltonian.

Is not expected to return anything - return value is not caught.

Important to note is the fact that this function is called once per frame. That means that the map itself must make sure to treat all pairs, instead of one. A list (or any other structure chosen) of the pairs that should be treated is saved as the attribute map\_.allpairs.

.. important::
    Depending on how many oscillators are present in the MD system, this function could very well be the reason why the program runs slow. That means that this should most likely be the first target for any optimizations. Optimizations could be made using clever numpy use (doing all calculations vectorized), numba, or even writing your own c library. The function GM_prep_coupling() could aid further in this.

.. danger::
    This function is provided with the entire hamiltonian (which must happen to allow various speedup methods). This also means that it could change anything within there. Be very careful to only edit the values associated with the pairs this map is responsible for. This avoids all kinds of hard-to-find bugs.


Example uses
------------

Dipole-dipole coupling
^^^^^^^^^^^^^^^^^^^^^^
When calculating the coupling between two dipoles, the dipole moment and position of each is required. Important to realize here, is the fact that this kind of coupling is incredibly common - it is very probable that hamiltonians with thousands or even millions of these kinds of couplings will be treated.

This means that efficiency is incredibly important. The kinds of optimizations considered for this map require control over how we treat the pairs. Instead of looping (the python way) through all pairs, and calculating each (and saving it in the hamiltonian), it is much, much faster to do a vectorized numpy calculation, where all pairs go through the same steps simultaneously. Yet another option is to have this loop happen in c, either through numba or a separate c library. However, properly vectorized c code is preferred if possible.


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
system : :class:`~GMAP.src.tools.system_reader.System`
    The object that stores everyting the program currently knows about the MD system.
hamiltonian : `np.ndarray`
    The hamiltonian of the full system. Consists of float32, has a column and a row for each oscillator.

Returns
-------
(nothing)

Default implementation
----------------------

.. code-block:: python

    def GM_calc_coupling(map_, system, hamiltonian)
        pass
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


.. code-block:: python

    import GMAP.src.tools.physics_functions as GM_pf

    def GM_report_references(map_, system):
        return map_.references


.. #endregion
