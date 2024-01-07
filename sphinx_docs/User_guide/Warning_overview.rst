================
Warning overview
================

Here you can find more information about the different warnings that can pop up.

Codes starting with SU
======================

SU_FP
-----

SU_FP_1
^^^^^^^
The user attempted to supply their own reference parameter file. This behaviour is not yet supported. Instead, please use a default parameter file. Change the .ref extension to a .txt, and make sure the file structure matches the example in [ADD CROSSLINK!].

SU_FP_2
^^^^^^^
The file structure for reference parameter files is different than that of default parameter files. Make sure the file structure matches the example in [ADD CROSSLINK!].

SU_FP_3
^^^^^^^
The type of a parameter in the reference parameter file has been specified slightly wrong. The format is recognized, but the contents are probably misspelled. See the examples in [ADD CROSSLINK!].

SU_FP_4
^^^^^^^
An unexpected error was encountered while parsing the types of parameters in the reference parameter file. See if the examples in [ADD CROSSLINK!] help fixing it. It might be that there is a mistake in the (type or amount of) brackets used, whitespaces between the brackets, and many more.

SU_FP_5
^^^^^^^
While parsing the choice of a parameter in the reference parameter file, there was a wrong type. Either the parameter has an unexpected python type, or a bool was specified with an choice of the wrong type (it couldn't be converted to a True or False). [ADD CROSSLINK!]

SU_FP_6
^^^^^^^
While parsing the choice of a parameter in the reference parameter file, an unexpected amount of choices was encountered. If the type of the parameter does not contain 'list\_', only one choice can be given. [ADD CROSSLINK!]

SU_FP_7
^^^^^^^
While parsing the choice of a parameter in the reference parameter file, a different error occurred. See if the examples in [ADD CROSSLINK!] help fixing it.


SU_WP
-----

SU_WP_1
^^^^^^^
This error is raised when the parameter choices on the command line couldn't be understood. Make sure that each parameter name is preceeded by '-' or, where applicable, '--'. [ADD CROSSLINK!]

SU_WP_2
^^^^^^^
One of the parameters supplied on the command line contains a '.' indicating that this parameter is part of a map. The map name should be before the '.', while the parameter name should go directly after. The combination of map and parameter name was not recognized by the program. [ADD CROSSLINK!]

SU_WP_3
^^^^^^^
One of the parameters supplied on the command line was not recognized. [ADD CROSSLINK!]

SU_WP_4
^^^^^^^
The given parameter requires a choice to be provided, but this did not happen. [ADD CROSSLINK!]

SU_WP_5
^^^^^^^
When specifying a choice for a parameter that can accept multiple choices, the last choice must always be appended by '\\;', without spaces between the last choice and the '\\;'. [ADD CROSSLINK!]

SU_WP_6
^^^^^^^
One of the parameters supplied in a parameter file (either input or default, see error message) was not recognized. [ADD CROSSLINK!]

SU_WP_7
^^^^^^^
A default parameter file must contain a choice for every available parameter. [ADD CROSSLINK!]

SU_WP_8
^^^^^^^
One of the parameters supplied in a parameter file (either input or default, see error message) did not have a choice specified. Each parameter (except bool-type) must come with a choice, so one should be given. If you do not want to make a choice, you can remove the line (if the file is not a default parameter file) [ADD CROSSLINK!]

SU_WP_9
^^^^^^^
One of the parameters supplied in a parameter file (either input or default, see error message) had too many choices specified. Only one was expected. [ADD CROSSLINK!]

SU_WP_10
^^^^^^^^
One of the parameters supplied in a parameter file (either input or default, see error message) expects a bool for a choice (either True or False), but something else was given. It was unclear which was meant. [ADD CROSSLINK!]

SU_WP_11
^^^^^^^^
One of the parameters supplied in a parameter file (either input or default, see error message) has a choice, but it is not allowed. See [ADD CROSSLINK!] for what choices are allowed.

SU_WP_12
^^^^^^^^
One of the parameters supplied in a parameter file (either input or default, see error message) could not be converted to the correct type. Most likely, a number was expected, but there were letters in there, or an integer (whole number) was expected, and the choice contains a decimal point. [ADD CROSSLINK!]

SU_WP_13
^^^^^^^^
Default parameter files must contain all parameters, but there is an exception. There is a subclass of parameters that are not allowed in the default parameter file, because it would simply not make sense. This parameter is one of them, and should be removed from the default parameter file. [ADD CROSSLINK!]

SU_WP_14
^^^^^^^^
Default parameter files must contain all parameters, but this one is missing. Please add it. [ADD CROSSLINK!]

SU_WP_15
^^^^^^^^
One of the parameters supplied in a parameter file (either input or default, see error message) contained a '.' indicating that this parameter is part of a map. The map name should be before the '.', while the parameter name should go directly after. The combination of map and parameter name was not recognized by the program. [ADD CROSSLINK!]


SU_NP
-----

SU_NP_1
^^^^^^^
The program needs a choice for the parameter, but none was found. Most likely, this is a parameter that is not allowed to be specified in both the default and reference parameter files, and should therefore be specified in the input parameter file or on the command line. [ADD CROSSLINK!]

SU_NP_2
^^^^^^^
After interpreting the choices made on the command line, input-, default- and reference parameter files, the mentioned choice was decided on. However, the found filename does not exist. Either, there is a typo in the path specified, or a mistake has been made in where the path should be specified relative to. One option is to see if this error persists if you specify the absolute path. [ADD CROSSLINK!]

SU_NP_3
^^^^^^^
After interpreting the choices made on the command line, input-, default- and reference parameter files, the mentioned choice was decided on. However, the found directory name does not exist. Either, there is a typo in the path specified, or a mistake has been made in where the path should be specified relative to. One option is to see if this error persists if you specify the absolute path. [ADD CROSSLINK!]


SU_PP
-----

SU_PP_1
^^^^^^^
The specified choice of how the program should run was not recognized. Use the suggested line to see the options.

SU_PP_2
^^^^^^^
The chosen way of running this program needs an input file. See [ADD CROSSLINK!] on how to correctly specify one.

SU_PP_3
^^^^^^^
The chosen input parameter file on the command line was not found. Make sure you spelled it correctly. Also see [ADD CROSSLINK!]

SU_PP_4
^^^^^^^
The command line contains the same parameter name more than once. Make sure to only give it once. If you use the shorthand, the full name is not needed. If there is a parameter that takes multiple choices, see [ADD CROSSLINK!] on how to supply those.


SU_FH
-----

SU_FH_1
^^^^^^^
The chosen default parameter file could not be found. Either, there is a typo in the path specified, or a mistake has been made in where the path should be specified relative to. One option is to see if this error persists if you specify the absolute path. [ADD CROSSLINK!]

SU_FH_2
^^^^^^^
The program requires some reference as to what parameters are required. For some reason, this file went missing. See if this error persists with a fresh installation.

SU_FH_3
^^^^^^^
Probably, the wrong file was supplied for this parameter. The program expects a plain text file, as can be made/edited using notepad, nano, vi, less, etc. [ADD CROSSLINK!]


SU_MR
-----

SU_MR_1
^^^^^^^
When supplying a parameter name for a map, it may at most contain one '.'.


Other codes
===========

howtogethere
^^^^^^^^^^^^
As far as I know, there is no way to actually trigger this one. If you managed to do so, congratulations! Please let us know how you did so!



