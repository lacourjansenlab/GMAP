.. _UserGuide_page_parameter_overview:

##################
parameter overview
##################


Here, an overview of the different available parameters is given. If you want to know how exactly to specify your choice, :ref:`this page<UserGuide_page_specifying_parameters>` is for you.

Parameters can be specified in multiple places (here referred to as the 'source') - the command line, the input parameter file, and the default parameter file. A handful of parameters is not allowed to be present in the default parameter file, wherever this is the case, this is mentioned.

When multiple sources are used, the choices in the command line take precedence above the choices in the input file, which take precedence over those in the default parameter file.

Please note that when paths are supplied, they should either be absolute, or specified relative to the source.

Some parameters store paths that can be relative to a directory stored in a different parameter. Where this is the case, this is denoted. Please note that when a file path and a directory path are given, the file path is assumed relative to the directory path. If only the file path is given, it is assumed relative to the source. If only the directory is given, file paths from lower-precedence sources are assumed relative to it.


*************************
parameters for file paths
*************************

source_directory
================
(shorthand: -sd)

The location of the sourcefiles directory. This directory stores all data required for the program to run. The parameter default_parameter_filename will be assumed relative to this directory when applicable.


default_parameter_filename
==========================
(shorthand: -dpf)

The filename of the default parameter file. This parameter is not allowed to be present in the default parameter file. This file must contain all possible parameters (except those it cannot). It does not need to contain any parameters from maps, but if it contains any from any map, it must contain all of that specific map. The path stored here will be assumed to be relative to the directory given in the parameter source_directory when applicable. 


log_directory
=============
(no shorthand available)

The location of the log directory. In this directory, all files relating to logging the program flow are located. The parameter log_filename will be assumed relative to this directory when applicable.


log_filename
============
(no shorthand available)

The filename of the log file. This file contains the same, or similar information as the prints to the command line, depending on the choice for the parameters verbose and verbose_logfile. The path stored here will be assumed to be relative to the directory given in the parameter log_directory when applicable.


map_directory
=============
(shorthand: -md)

The location of the maps directory. Multiple directories are allowed to be given. Within a maps directory, the maps that can be used are stored. See :ref:`adding a new map<UserGuide_page_adding_map>` for more information on what maps are and how to make one.


topology_file
=============
(shorthand: -top)

The filename and location of the topology file to be used during the calculation. Allowed filetypes are the ones listed `here <https://userguide.mdanalysis.org/stable/formats/index.html>`__ that have a tick in the column labeled 'topology'.


trajectory_file
===============
(shorthand: -trj)

The filename and location of the trajectory file to be used during the calculation. Allowed filetypes are the ones listed `here <https://userguide.mdanalysis.org/stable/formats/index.html>`__ that have a tick in the column labeled 'coordinates'.


*********************************
parameters for how to write files
*********************************


verbose
=======
| (no shorthand available)
| (options: 0, 1, 2, 3, 4)

How verbose the prints to the command line should be. When 0 is chosen, nothing but errors will be reported.


verbose_logfile
===============
| (no shorthand available)
| (options: 0, 1, 2, 3, 4)

How verbose the prints to the log file should be.


prevent_overwrite
=================
| (no shorthand available)
| (options: true, t, false, f)

Whether the files created by the program should or shouldn't overwrite existing files. When set to True, the existing file will be renamed, and the requested name will be used for the new file. When set to False, the old file will be overwritten, and the data inside lost forever.


**********************************************
parameters for specifying calculation settings
**********************************************

maps_to_use
===========
(shorthand: -um)

Which maps should be considered in the calculation. Or, in other words, which kinds of oscillators should be found, and calculated properties for. There are limited choices - namely, the names of the maps supplied through the parameter map_directory.


neutral_charge_threshold
========================
(no shorthand available)

How close to zero the total charge needs to be to be considered neutral. Essentially, all values between 0 - neutral_charge_threshold and 0 + neutral_charge_threshold will be considered 0.

guess_bonds
===========
| (no shorthand available)
| (options: true, t, false, f)

Whether the program should guess bonds for the supplied universe. This should only be used if bond information if absolutely necessary, and there really is no topology file with bond information available. Bonds are guessed by `MDAnalysis<https://userguide.mdanalysis.org/stable/formats/guessing.html#types>`__.

