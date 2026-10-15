.. _UserGuide_page_warning_overview:

################
Warning overview
################

Here you can find more information about the different warnings that can pop up.

**********************
Codes starting with SU
**********************

SU_FP
=====

SU_FP_1
-------
The user attempted to supply their own reference parameter file. This behaviour is not yet supported. Instead, please use a default parameter file. Change the .ref extension to a .txt, and make sure the file structure matches the example in [ADD CROSSLINK!].

SU_FP_2
-------
The file structure for reference parameter files is different than that of default parameter files. Make sure the file structure matches the example in [ADD CROSSLINK!].

SU_FP_3
-------
The type of a parameter in the reference parameter file has been specified slightly wrong. The format is recognized, but the contents are probably misspelled. 
If you are developing the file that triggered the error, :ref:`here <AddMap_page_map_parameters_types>` you can find more info on the different types, or look at the file 'reference_parameters.ref' that lives in the sourcefiles directory for examples.
If you have not touched the file that created this error, please get in touch with the person that created the file.

SU_FP_4
-------
An unexpected error was encountered while parsing the types of parameters in the reference parameter file. It might be that there is a mistake in the (type or amount of) brackets used, whitespaces between the brackets, and many more.
If you are developing the file that triggered the error, :ref:`here <AddMap_page_map_parameters_types>` you can find more info on the different types, or look at the file 'reference_parameters.ref' that lives in the sourcefiles directory for examples.
If you have not touched the file that created this error, please get in touch with the person that created the file.

SU_FP_5
-------
While parsing the choice of a parameter in the reference parameter file, there was a wrong type. Either the parameter has an unexpected python type, or a bool was specified with an choice of the wrong type (it couldn't be converted to a True or False). 
If you are developing the file that triggered the error, :ref:`here <AddMap_page_map_parameters_types>` you can find more info on the different types, or look at the file 'reference_parameters.ref' that lives in the sourcefiles directory for examples.
If you have not touched the file that created this error, please get in touch with the person that created the file.

SU_FP_6
-------
While parsing the choice of a parameter in the reference parameter file, an unexpected amount of choices was encountered. If the type of the parameter does not contain 'list\_', only one choice can be given.
If you are developing the file that triggered the error, :ref:`here <AddMap_page_map_parameters_types>` you can find more info on the different types, or look at the file 'reference_parameters.ref' that lives in the sourcefiles directory for examples.
If you have not touched the file that created this error, please get in touch with the person that created the file.

SU_FP_7
-------
While parsing the choice of a parameter in the reference parameter file, a different error occurred.
If you are developing the file that triggered the error, :ref:`here <AddMap_page_map_parameters_types>` you can find more info on the different types, or look at the file 'reference_parameters.ref' that lives in the sourcefiles directory for examples.
If you have not touched the file that created this error, please get in touch with the person that created the file.

SU_FP_8
-------
The reference parameter file was missing the parameters 'influencers_whitelist' and 'influencers_blacklist'. Make sure both are present.

SU_FP_9
-------
Due to definition conflicts, path-type parameters cannot take options in the reference file. If you want a user to pick between a number of files, give them names and use a string type parameter instead.


SU_WP
=====

SU_WP_1
-------
This error is raised when the parameter choices on the command line couldn't be understood. Make sure that each parameter name is preceeded by '-' or, where applicable, '--'. See :ref:`this page <UserGuide_page_specifying_parameters_commandline>` for more information on how to specify a parameter on the command line.

SU_WP_2
-------
One of the parameters supplied on the command line contains a '.' indicating that this parameter is part of a map. The map name should be before the '.', while the parameter name should go directly after. The combination of map and parameter name was not recognized by the program. See :ref:`this page <UserGuide_page_specifying_parameters_commandline>` for more information on how to specify a parameter on the command line, or consult the documentation of the map to see what parameters are allowed.

SU_WP_3
-------
One of the parameters supplied on the command line was not recognized. See :ref:`this page <UserGuide_page_specifying_parameters_commandline>` for more information on how to specify a parameter on the command line, and see :ref:`this page <UserGuide_page_parameter_overview>` for what parameters are available.

SU_WP_4
-------
The given parameter requires a choice to be provided, but this did not happen. See :ref:`this page <UserGuide_page_parameter_overview>` for more information about this parameter, and :ref:`this page <UserGuide_page_specifying_parameters_commandline>` for more information on how to specify a parameter on the command line.

SU_WP_5
-------
When specifying a choice (on the command line) for a parameter that can accept multiple choices, the last choice must always be appended by '\\;', without spaces between the last choice and the '\\;'. See :ref:`this page <UserGuide_page_specifying_parameters_commandline>` for more information on how to specify a parameter on the command line.

SU_WP_6
-------
One of the parameters supplied in a parameter file (either input or default, see error message) was not recognized. See :ref:`this page <UserGuide_page_parameter_overview>` for a list of all available parameters, and :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how to specify a parameter in a parameter file.

SU_WP_7
-------
A default parameter file must contain a choice for every available parameter. See :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how parameter files work.

SU_WP_8
-------
One of the parameters supplied in a parameter file (either input or default, see error message) did not have a choice specified. Each parameter must come with a choice, so one should be given. If you do not want to make a choice, you can remove the line (if the file is not a default parameter file). See :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how to specify a parameter in a parameter file.

SU_WP_9
-------
One of the parameters supplied in a parameter file (either input or default, see error message) had too many choices specified. Only one was expected. See :ref:`this page <UserGuide_page_parameter_overview>` for more information about this parameter, and :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how to specify a parameter in a parameter file.

SU_WP_10
--------
One of the parameters supplied in a parameter file (either input or default, see error message) expects a bool for a choice (either True or False), but something else was given. It was unclear which was meant. See :ref:`this page <UserGuide_page_parameter_overview>` for more information about this parameter, and :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how to specify a parameter in a parameter file.

SU_WP_11
--------
One of the parameters supplied in a parameter file (either input or default, see error message) has a choice, but it is not allowed. See :ref:`this page <UserGuide_page_parameter_overview>` for more information about this parameter including allowed choices, and :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how to specify a parameter in a parameter file.

SU_WP_12
--------
One of the parameters supplied in a parameter file (either input or default, see error message) could not be converted to the correct type. Most likely, a number was expected, but there were letters in there, or an integer (whole number) was expected, and the choice contains a decimal point. See :ref:`this page <UserGuide_page_parameter_overview>` for more information about this parameter, and :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how to specify a parameter in a parameter file.

SU_WP_13
--------
Default parameter files must contain all parameters, but there is an exception. There is a group of parameters that are not allowed in the default parameter file, because it would simply not make sense. This parameter is one of them, and should be removed from the default parameter file. See :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how parameter files work.

SU_WP_14
--------
Default parameter files must contain all parameters, but this one is missing. Please add it. See :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how parameter files work.

SU_WP_15
--------
One of the parameters supplied in a parameter file (either input or default, see error message) contained a '.' indicating that this parameter is part of a map. The map name should be before the '.', while the parameter name should go directly after. The combination of map and parameter name was not recognized by the program. See :ref:`this page <UserGuide_page_specifying_parameters_file>` for more information on how to specify a parameter on the command line, or consult the documentation of the map to see what parameters are allowed.

SU_WP_16
--------
For some groups of parameters, only one of the parameters can be used. Multiple parameters from such a group were used, make sure to only use one of those mentioned in the error message.

SU_WP_17
--------
Some groups of parameters are linked, meaning that the available choices for one parameter might depend on the choice(s) provided for (an)other(s). The mentioned parameters are linked, but their choices don't match.


SU_NP
=====

SU_NP_1
-------
The program needs a choice for the parameter, but none was found. Most likely, this is a parameter that is not allowed to be specified in both the default and reference parameter files, and should therefore be specified in the input parameter file or on the command line. [ADD CROSSLINK!]

SU_NP_2
-------
After interpreting the choices made on the command line, input-, default- and reference parameter files, the mentioned choice was decided on. However, the found filename does not exist. Either, there is a typo in the path specified, or a mistake has been made in where the path should be specified relative to. One option is to see if this error persists if you specify the absolute path. :ref:`This page <UserGuide_page_parameter_overview>` has more information on how file locations should be given.

SU_NP_3
-------
After interpreting the choices made on the command line, input-, default- and reference parameter files, the mentioned choice was decided on. However, the found directory name does not exist. Either, there is a typo in the path specified, or a mistake has been made in where the path should be specified relative to. One option is to see if this error persists if you specify the absolute path. :ref:`This page <UserGuide_page_parameter_overview>` has more information on how file locations should be given.

SU_NP_4
-------
Considering all parameter sources, it was found that the influencers should be defined by the given file. This file, however, contains (an) invalid character(s).

SU_NP_5
-------
The given parameter file contains a mistake in how things are specified. See the returned python error for more information. To see the error, set either the parameter 'verbose', or the parameter 'verbose_logfile' to 4.

SU_NP_6
-------
The given command for select_atoms triggered some error. See the returned python error for more information. To see the error, set either the parameter 'verbose', or the parameter 'verbose_logfile' to 4.

SU_NP_7
-------
The mentioned parameters have choices that are valid on their own, but their combination is not. Please make sure that these conflicts are resolved!

SU_NP_8
-------
The given parameter was provided with an invalid choice. The error gives more information on what parameter, and whats wrong.


SU_PP
=====

SU_PP_1
-------
The specified choice of how the program should run was not recognized. Use the suggested line to see the options.

SU_PP_2
-------
The chosen way of running this program needs an input file. See [ADD CROSSLINK!] on how to correctly specify one.

SU_PP_3
-------
The chosen input parameter file on the command line was not found. Make sure you spelled it correctly. Also see [ADD CROSSLINK!]

SU_PP_4
-------
The command line contains the same parameter name more than once. Make sure to only give it once. If you use the shorthand, the full name is not needed. If there is a parameter that takes multiple choices, see [ADD CROSSLINK!] on how to supply those.


SU_FH
=====

SU_FH_1
-------
The chosen default parameter file could not be found. Either, there is a typo in the path specified, or a mistake has been made in where the path should be specified relative to. One option is to see if this error persists if you specify the absolute path. [ADD CROSSLINK!]

SU_FH_2
-------
The program requires some reference as to what parameters are required. For some reason, this file went missing. See if this error persists with a fresh installation.

SU_FH_3
-------
Probably, the wrong file was supplied for this parameter. The program expects a plain text file, as can be made/edited using notepad, nano, vi, less, etc. [ADD CROSSLINK!]


SU_MR
=====

SU_MR_1
-------
When supplying a parameter name for a map, it may at most contain one '.'.


SU_GEM
======

SU_GEM_1
--------
The default parameter file supplied to gem is expected to be a .txt file. This error was triggered because the file has a different extension. .ref files are planned to be supported in the future (See SU_FP_1) [ADD CROSSLINK!]


SU_GM
=====

SU_GM_1
-------
When calling the program, 'GMAP' is followed by the program you'd like to use. Currently, GEM, Setup and DEPICT are available. The program couldn't recognize 'GEM', 'Setup' or 'DEPICT' from your command.


**********************
Codes starting with MI
**********************


MI_MR
=====

MI_MR_1
-------
For some reason, the main python file of the map could not be opened. This is an issue that most likely needs to be fixed by the developer of this file. If you set the verbose (or verbose logfile) level to 4, you can see the python traceback for more information.

MI_MR_2
-------
Could not find the core.txt file for the given map. A map is defined by its core, and cannot live without. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MR_3
-------
The given parameter had no choice defined. Each parameter needs a choice for a map to make sense. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MR_4
-------
The given parameter occurs on more than a single line in the file. However, it may only occur once. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MR_5
-------
An extra core file was requested to be appended to the given core file. However, some error occurred while trying to do this. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MR_6
-------
An extra core file was requested to be appended to the given core file. However, no file of the requested name could be found. If the developer did not provide additional instructions on extra files to add, this is an issue that most likely needs to be fixed by the developer of this map.

MI_MR_7
-------
A prerequisite part of the map was missing. This is an issue that most likely needs to be fixed by the developer of this map.


MI_MC
=====

MI_MC_1
-------
There are two ways of defining what the molecule a map operates on looks like. Either you specify each possible version of the molecule on a new line of core.txt using the parameter 'functional group', or, you choose to not define these in the core.txt file, but instead in a separate file (this might be preferred for maps operating on (very) large molecules). This file can be 'linked' by specifying its name using the parameter 'functional_group_file'.

The two methods are exclusive - all molecules must be in that single file, or all must be in the core.txt file. This warning was triggered because both systems were used simultaneously.

This is an issue that most likely needs to be fixed by the developer of this map.

MI_MC_2
-------
There are two ways of defining what the molecule a map operates on looks like (see error SU_MC_1). This definition is essential: without, the map cannot function. Neither of the two methods was used/recognized in the file, resulting in a non-functional map. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MC_3
-------
The map requires the given file to exist in order to recognize the molecule in the MD system. However, the file could not be found. Please make sure you copied the entire map-specific directory in your maps directory. If you did so, this is an issue that most likely needs to be fixed by the developer of this map.

MI_MC_4
-------
The map contains a definition of functional_group that couldn't be interpreted. This could either be in the mentioned file itself, or the file linked in that file under the parameter functional_group_file. This is an issue that most likely needs to be fixed by the developer of this map.

The error code given consists of three parts, separated by two dashes. The first part is the thing that went wrong (see overview below), the second and third indicate where this went wrong. The second number indicates which line (in the case of core.txt), or which newstruct (in the case of a provided file) triggered the error - 0 indicates the first, 1 indicates the second, etc. The 3rd number indicates the index of the atom that was last parsed successfully before the error triggered.

1
    The marker for the next residue (square brackets) was found, but the last residue was not yet complete: either the name wasn't registered, or there were no atoms associated with it.

2
    The encountered term had either a '[', or a ']', but not both. Make sure that the residue name definition does not contain any spaces between these two brackets!

3
    An atom was found to have a bond-marker (both '(' and ')' ). Within these parentheses, only integers (separated by a comma) are expected, but whatever was found inside could not be converted to an integer.

4
    An atom was found to only have '(' or ')', but not both. Make sure that the atom + bond definition does not contain any spaces!

5
    The end of the definition of this functional_group was found, but the last residue was not yet complete: either the name wasn't registered, or there were no atoms associated with it.

6
    | !!! careful! For this error, the 3rd number does not indicate the index of the last successful atom, but instead, the 'label' of the bond triggering the error !!!
    | When parsing the bonds defined within this structure (using parentheses), a certain bond identifier was found too often, or not often enough. Each identifier should occur exactly twice, a single atom may have multiple bond identifiers.

MI_MC_5
-------
The map contains a definition of 'functional_group_bonds' that cannot be interpreted. Make sure it contains exactly two indices (each consisting of numbers only), separated by only a hyphen. Spaces should only be used to separate bonds from each other. The indices should count along the atoms defined in 'functional_group', starting from 0. Residue names do not count in this counting method.

This is an issue that most likely needs to be fixed by the developer of this map.

MI_MC_6
-------
The core.txt of every map can contain a variety of parameters, some of which are optional. Others are mandatory. The listed parameter is mandatory, but was missing. It must be added before the map can function. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MC_7
-------
This parameter must be specified using only numbers and spaces, but something else was used. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MC_8
-------
The size of the integers for this parameter cannot exceed the amount of atoms given for the other mentioned parameter. Please note that counting starts at 0. This is an issue that most likely needs to be fixed by the developer of this map.

MI_MC_9
-------
The given parameter encodes a (position) vector, but its definition couldn't be interpreted. [Cite relevant manual page!!!]

MI_MC_10
--------
If type is set to be 'linear', only one axis needs to be defined. Any of x, y and z can be used, depending on the map constants used. The other two will be taken perpendicular to eachother, and the one defined.
If type is set to be 'standard', two of the three axes need to be defined. The first (any of x, y, and z) will take the direction as is, the second (any of the remainder of x, y and z) will have the component along the first removed. This means that for the second, only the perpendicular component will be used for the direction of the vector. The third is assumed by the program to be the cross product of the first vector with the second (first x second).

MI_MC_11
--------
There was an issue with the specification for the keyword 'valid_combinations' for one of the maps. [Cite relevant manual page!!]

MI_MC_12
--------
The mentioned parameter can only take a limited amount of options, and one of those used is not one of them. [Cite relevant manual page!!]

MI_MC_13
--------
The mentioned parameter can take either the form of a decimal number, or of something python can interpret. Any constants in the numpy library (e.g. np.pi) are available, as well as all constants in the GMAP constants module.  [Cite relevant manual page!!]


MI_MM
======

MI_MM_1
--------
The user requested the use of a certain map, but the program cannot use/find it. Make sure there is a directory of the requested name in the directory named 'singles' inside your maps directory. If there is, check the earlier errors - there might have been issues loading it in.

.. note::
    If there are indeed map-related warnings prior to this one, see if they pertain to the specific map(s) you want to use. If so, solve those errors first.

MI_MM_2
-------
Certain coupling maps require some additional information from oscillators which cannot be provided/determined by GMAP, or the coupling map itself. Therefore, the map for an oscillator must give it specifically for this coupling map (which is completely optional for a map to do). This error was triggered because the mentioned combination of maps is not supported.

MI_MM_3
-------
Certain couplings maps might indicate they cannot be used for certain types of oscillators. Make sure you only use a map for its intended purpose!

MI_MM_4
-------
Certain couplings maps might indicate they cannot be used for certain types of couplings. Make sure you only use a map for its intended purpose!

MI_MM_5
-------
Certain singles maps might indicate they cannot be used for certain types of outputs. Make sure you only use a map for its intended purpose!


**********************
Codes starting with MD
**********************


MD_SU
=====

MD_SU_1
-------
There was an issue with creating the universe from the supplied MD files (parameters 'topology_file' and 'trajectory_file').

MD_SU_2
-------
The supplied MD files contain a universe that has a bounding box with non-90-degree angles. The current version does not support this.

MD_SU_3
-------
The supplied MD files have a non-zero charge. The amount the charge is allowed to deviate is defined using the parameter neutral_charge_threshold. If the system has non-integer charge, the program will quit, if the charge is non-neutral, the program will throw a warning, but continue.

MD_SU_4
-------
The atoms in the supplied MD system have an unexpected convention - their numbering didn't start at 0 and/or resets counting. Please get in touch with the developers of GMAP!

MD_SU_5
-------
There is no bond information in the supplied MD system, but this information is required for the calculation to run. For the program to run, you should either use a different map, or provide a system with bond information. This can be done in two different ways:

- Use :ref:`the parameter guess_bonds<UserGuide_page_parameter_overview>` in the input file or command line to have the program guess bonds in the MD system (no guarantee this accurately detects the bonds in your system).

- Use a different format of topology file. `This website <https://userguide.mdanalysis.org/stable/formats/index.html>`__ has an extensive table of available formats for different MD software. Make sure you pick a format which lists 'bonds' in the column 'Attributes read'. Here an overview of options for a few common MD packages:

  - Gromacs: .tpr
  - Amber: .top, .prmtop or .parm7
  - Charmm: .psf
  - NAMD: .psf

MD_SU_6
-------
Some circular reference was found when determining what coupling map should be used to couple a certain pair of oscillators. The first one in the list is the one directly requested by the user, and that map determined that the second map in the list would be a better fit. Each map points to the next in the list, until one is encountered that has been requested before, starting this circular nature. This means the program will never find a suitable map, and thus quits.
The issue could lie with the initial (or any other) map not being a good fit, and therefore sorting out the pair wrongly. Alternatively, there's a mistake in the map's code directing it to a different map. 

MD_SU_7
-------
The supplied MD trajectory did not contain any of the requested oscillators.

*************************
Codes starting with Setup
*************************


Setup
=====

Setup_1
-------
The directory to which the sourcefiles and the maps are attempted to be copied, do not exist.

Setup_2
-------
A file named sourcefiles_copy already exists in the directory that is being copied to.

Setup_3
-------
A file named maps_copy already exists in the directory that is being copied to.



*************************
Codes starting with map
*************************

These codes are generated by installed maps. The second part of the error code is the name of the map that raised the error (if the map maker followed this requested convention), see the documentation of that map for more information about the warning.


***********
Other codes
***********

PF_MD_1
=======
During finalizing a parallel computation, GMAP tries to remove any temporary files/folders created during the run. If you encountered this error, the program couldn't delete such a temporary directory, as it contains files the program didn't expect. Please have a look at the directory yourself to see if files can be removed, and please let us know how you triggered this error, so we can bugfix!


CT_EC_1
=======
Something was compared to an error code, but wasn't one itself. If the error persists without using any custom maps, please contact the GMAP developers. If not, please contact the respective map authors.

CT_EC_2
=======
Something was compared to an error code, but had the wrong format. If the error persists without using any custom maps, please contact the GMAP developers. If not, please contact the respective map authors.

howtogethere
============
As far as I know, there is no way to actually trigger this one. If you managed to do so, congratulations! Please let us know how you did so!



