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


***************
Basic structure
***************

There are a few objects that occur quite often as an argument for these functions. Here is a quick overview of them:

Map
=====
An instance of :class:`~GMAP.src.tools.MapReader.SingleMap`. Stores all information of this class. This is the most important object, as it stores everything related to this class. As functions of the map can change how the map is registered, this object will look different during the different functions. Here is an overview of all attributes the class can have, at each function it will be explained/highlighted what attributes are available at that point.

It is probable that the map wants to save information between functions, too, just like the main program. These data structures must be saved as an attribute to the instance of the class, as per good coding practices. This overview of attributes should help indicate what names are and aren't available.

- self.directory (type pathlib.Path) is the path to the directory the map is saved in on the current machine.
- self.corepath (type pathlib.Path) is the path to the core.txt file of the map.
- self.name (type str) is the name of the map - i.e. the name of the directory in which all map files live.
- self.type (type str) is the type of the map - either Singles or Pairs. Singles maps operate on a single oscillator (think of maps giving an oscillator frequency), Pairs maps operate on a pair of oscillators (think of maps giving a coupling value).
- self.success (type bool) denotes whether the map has (until this point) been read successfully. An unsuccessful map will not trigger the program to quit, as long as the user does not want to use this map.
- self.avail_files (type list of pathlib.Path) is a list of all files that are in the same map directory in this map (or in its parent directory). These are the files that can be used for appending using 'add_corefile' in the core file.
- self.RefPars (type :class:`~GMAP.src.tools.ParameterParser.RefPars`) contains all information from the map-specific reference parameters file.
- self.DefPars (type :class:`~GMAP.src.tools.ParameterParser.RawPars`) contains all choices for parameters for this map that were found in the default parameter file. Either all parameters are present, or none, depending on the default parameter file.
- self.InPars (type :class:`~GMAP.src.tools.ParameterParser.RawPars`) contains all choices for parameters for this map that were found in the input parameter file. May be empty.
- self.CmdPars (type :class:`~GMAP.src.tools.ParameterParser.RawPars`) contains all choices for parameters for this map that were found on the command line. May be empty.
- self.RunPars (type :class:`~GMAP.src.tools.ParameterParser.RunPars` or None) contains the combination of all parameter sources, where self.CmdPars \> self.InPars \> self.DefPars \> self.RefPars. If this behaviour is too naive, the contents can be changed with the function GM_adjust_RunPars listed below. This is where other functions should retrieve parameter choices from.

  .. tip:: self.RunPars also has a reference to the main-program RunPars - it is stored as self.RunPars.MainRunPars.
- self.code (type module) contains all functions defined in main.py. Any functions that the program needs, but are not specified in main.py are automatically filled in. Any object that the program does not require, but is still there, is also available.
- self.rawcore (type dict of str-list pairs) contains the information from core.txt, before parsing. The function GM_adjust_map_core_raw can change this simple structure before it is being parsed into more complex structures and functions later.
- self.Core (type :class:`~GMAP.src.tools.MapReader.SingleCore`) contains the information from core.txt, after parsing.


Files
======
An instance of :class:`~GMAP.src.tools.FileHandler.FileLocations`. Stores filepaths and such.


Syst
====
An instance of :class:`~GMAP.src.tools.SystemReader.System`. Stores all available information about the MD system used. Think atom-based information on it's name, element, type, the name and number of its residue, molecule, segment. Also charges, positions, masses and such are in here. 


.. important:: 
    When your functions should report/print anything, **do not** use the python build-in function print. Instead, import the GMAP PrintTools module (``from GMAP.src.tools import PrintTools as GM_PT``), from which you can call an instance of the Printer class. This instance is a singleton (so all print settings for that run are already set), so don't change it! But you can have it print (``GM_PT.Printer().print``), or even trigger an error (``GM_PT.Printer().warning``). See :class:`~GMAP.src.tools.PrintTools.Printer` for detailed information on using these functions.


*************************
Overview of all functions
*************************

The function are in the order at which they're called by the program. This means that if any functions create additional attributes for the class, any functions listed below those functions will have access to those attributes, any functions listed above them will not.



GM_adjust_RunPars(Files, Map)
======================================
Makes the necessary changes to Map.RunPar.

Is expected to not return anything - return value is not caught.


Example uses
------------

interlinked parameters
^^^^^^^^^^^^^^^^^^^^^^
Take the three parameters start_frame, end_frame and frames_tocalc. In the default file, these may be set to 0, 100 and 100 respectively. This makes sense, as if you start on frame 0 and end at frame 100 (exclusive), you will see 100 frames. But if in the input file the choice to start at frame 10 was given, the default RunPars creation will select the numbers 10, 100, 100, which doesn't make sense (there is not 100 frames to treat between frames 10 and 100). Custom code can change these to 10, 100, 90.

dependent parameters
^^^^^^^^^^^^^^^^^^^^
Some maps are designed with certain assumptions in mind. These assumptions don't always mix. Because of this, it can happen that when a choice for one parameter is made, not all choices should be available for another. Custom code can solve this kind of conflicts.

Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code

Parameters
----------
Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
    Contains all currently known paths and other file-related properties.
    Has to be updated after RunPars is finalized.
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.



GM_adjust_map_core_raw(Files, Map)
===========================================

Makes the necessary changes to the 'raw' input read from core.txt.

Is expected to not return anything - return value is not caught.

The core.txt file is stored in Map.rawcore. It has not yet been parsed, just loaded into a dictionary. In this dictionary, each keyword is its own dictionary key. Most keywords can only occur once in the file - those have a list of the 'words' on the line as their value. The parameters that are allowed to occur more than once have a list as value, in which other lists appear - one for each line.

The purpose of this function is to change this dictionary. Perhaps, a rule in core.txt is dependent on a parameter of the map. This function can make a decision based on those parameters (stored in Map.RunPars).


Example uses
------------

Dependency on map parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The core.txt file gives the option to link a file containing the map constants. There are cases (for example, the Amide-I stretch) for which multiple different sets of constants have been developed. In this case, it would be useful for this function to select a different file with map constants based on a map-specific parameter.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore


Parameters
----------
Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
    Contains all currently known paths and other file-related properties.
    Has to be updated after RunPars is finalized.
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.



GM_adjust_oscillators(Files, Map, Syst, oscillator_list)
=================================================================

Finalizes the list of oscillators.

Is expected to return a list of oscillators - by default, it returns oscillator_list.

The purpose of a map is to define how to calculate the properties for a certain kind of oscillator. The program will find instances of that oscillator in the MD system based on the choice for 'functional_group' in core.txt. After they've been found, they are passed to this function. The reason for this is twofold. Fistly, this allows the map to change this list if it were necessary (see example uses). Secondly, it allows the map to 'see' the oscillators for the first time, allowing it to identify the type of an oscillator, for example.


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


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
    Contains all currently known paths and other file-related properties.
    Has to be updated after RunPars is finalized.
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
oscillator_list : list of :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillators that were identified as a good match for this map.



GM_post_init(Files, Map, Syst)
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

One could either do the conversion first, and save the converted constants with the correct assumptions in the files supplied to GMAP, or let GMAP do this conversion. The latter might be preferred if one wants the files to match the original publication of the map. In that case, this function here is the best place for a map to do the conversion. To make the conversion easy, use the function Map.Core.change_map_units().


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Files : :class:`~GMAP.src.tools.FileHandler.FileLocations`
    Contains all currently known paths and other file-related properties.
    Has to be updated after RunPars is finalized.
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.



GM_pre_run(Map, Syst)
=======================================

Allows the user to prepare the structures needed for the run.

Is expected to not return anything.


Example uses
------------

New output type
^^^^^^^^^^^^^^^
If the map wants to compute a new property / output type, the data structure storing that property could be initialized here.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.



GM_pre_frame(Map, Syst)
=======================================

Allows the user to compute information that will change for each frame.

Is expected to not return anything.

If such a property is only needed once, it should be calculated at the time it is needed. But if multiple outputs (frequency and dipole, for example) or multiple oscillators need it, it should go here. If the property is not position/frame dependent, it should be computed in GM_pre_run.


Example uses
------------

To be added
^^^^^^^^^^^
To be explained.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.



GM_post_frame(Map, Syst)
=======================================

Allows the user to finalize the frame.

Is expected to not return anything.


Example uses
------------

New output type
^^^^^^^^^^^^^^^
If the map wants to compute a new property / output type, the computed data should be written to a file here.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.



GM_post_run(Map, Syst)
=======================================

Allows the user to do some final reports.

Is expected to not return anything.


Example uses
------------

Reporting on the calculation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the user should know anything about the computation that has been performed, they can be told by this function.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.



GM_str_osc(Map, Syst, osc)
==========================

Returns the (human-readable) string representation of an oscillator of this type.

This function is used whenever the program needs to report some information about an oscillator to the user. This could either be as part of an error warning, or as general reporting (legend of the output files, what each oscillator actually looks like).
By default (if this function is not present) this representation is the following: ``Oscillator of type [mapname] living on residue number [resnum]``. Here, ``[mapname]`` will be replaced by the program with the actual name of the map the oscillator belongs to, and ``[resnum]`` will be replaced with the residue number of the first atom (in ``used_atoms``) of the oscillator.


Example uses
------------

Clearly indicating an oscillator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The default is very generic, and should give some information to identify an oscillator. However, for some kinds of oscillator, this information might not be sufficient, or hard to interpret. For example, any protein-related maps will most likely want to print the residue name along with its number, as that is how literature usually refers to them. 
 

Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillator for which the rotation matrix should be determined.



GM_get_rotation_matrix(Map, Syst, osc)
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


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillator for which the rotation matrix should be determined.


Returns
-------
rotation_matrix : `np.ndarray`
    The matrix that should be used to convert the electrostatic properties. rotation_matrix[0] should return a vector of length 3 defining what the box-x vector should look like, in cartesian coordinates. Same for [1] giving the y, and [2] giving the z. The three vectors are orthonormal.



GM_get_dipole_dir(Map, Syst, osc)
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


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillator for which the dipole moment vectors should be determined.


Returns
-------
r_vec : `np.ndarray`
    The (length-3) vector that represents the direction of the dipole moment of this oscillator. It should have the dtype `float32`, and the vector must be normalized.
r_pos : `np.ndarray`
    The (length-3) position vector at which the dipole vector lies. The vector must lie within the simulation box.



GM_get_dipole_mag(Map, Syst, osc)
==========================================

Returns the magnitude of the dipole vector in Debye.

.. tip::
    The magnitude of the dipole vector should be in units of Debye, and will by default be applied to the direction found by GM_get_dipole_dir()


Example uses
------------

The default method of providing the dipole vector direction is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes, the magnitude has a more complex dependence than the one offered by default. In those cases, it might be more appropriate to write the code here.



Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillator for which the dipole moment magnitude should be determined.


Returns
-------
magnitude : `np.float32`
    The length that the dipole moment vector should have.



GM_calculate_dipole(Map, Syst, osc)
============================================

Returns the dipole vector and its position in cartesian coordinates.

.. tip::
    By default (for single-VEG dependence, or no VEG dependence), this function is the combination of GM_get_dipole_dir and GM_get_dipole_mag. If only the functionality of one of those needs to be changed, doing that instead of imposing different behaviour here is adviced.


Example uses
------------

The default method of providing the dipole vector is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes, the dipole moment is determined in a more complex method than supported by the program. In those cases, it might be more appropriate to write the code here.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillator for which the dipole moment magnitude should be determined.


Returns
-------
r_vec : `np.ndarray`
    The vector that represents the dipole moment of this oscillator. It should have the dtype `float32`, and the vector should be normalized.
r_pos : `np.ndarray`
    The position at which the dipole vector lies.



GM_calculate_frequency(Map, Syst, osc)
===============================================

Returns the frequency at which the oscillator is expected to give a signal (resonate), in units of cm-1.


Example uses
------------

The default method of providing the frequency is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes, the frequency is determined in a more complex method than supported by the program. In those cases, it might be more appropriate to write the code here.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillator for which the dipole moment magnitude should be determined.


Returns
-------
freq : float
    The frequency at which this oscillator is expected to absorb.



GM_get_VEG_ref(Map, Syst, osc)
=================================================================

Returns the centerpoint for the sphere of charges contributing to the calculated electrostatics.

.. tip::
    In order to arrive at the correct result, this function should take into account the PBC. More information on PBC can be found :ref:`in the theory section<Theory_page_PBC>`. To help, the oscillator object provided has the attribute osc.positions_box - this array contains the positions of all atoms in used_atoms, transposed to box coordinates. To convert the final answer back to cartesian coordinates, multiply it with System.boxvects.


Example uses
------------

The default method of providing the elecctrostatics sphere center is not sufficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some techniques cannot be used in exclusively box coordinates, and can therefore not be used through core.txt. In those cases, it might be more appropriate to write the code here.


Available attributes of Map
---------------------------

.. hlist::
    :columns: 4

    * self.directory
    * self.corepath
    * self.name
    * self.type
    * self.success
    * self.avail_files
    * self.RefPars
    * self.DefPars
    * self.InPars
    * self.CmdPars
    * self.RunPars
    * self.code
    * self.rawcore
    * self.Core


Parameters
----------
Map : :class:`~GMAP.src.tools.MapReader.Map`
    The object that stores everything the program currently knows
    about this map.
Syst : :class:`~GMAP.src.tools.SystemReader.System`
    The object that stores everyting the program currently knows about the MD system.
osc : :class:`~GMAP.src.tools.SystemReader.Oscillator`
    The oscillator for which the rotation matrix should be determined.


Returns
-------
VEG_ref : `np.ndarray`
    The position at which the sphere should be centered.


