.. _UserGuide_page_specifying_parameters:

################################
How to specify parameter choices
################################

Most runs by GMAP need some parameters to explain exactly what needs to be done. These need to be supplied to the program for it to function. This can be done three different ways - through the command line, using an input file, or in the default parameter file.

Here, the language used for specifying parameters is explained. If you want to see what parameters exist and see more information about them, :ref:`this page<UserGuide_page_parameter_overview>` is for you.


.. _UserGuide_page_specifying_parameters_commandline:

********************
In the commmand line
********************

When specifying parameters on the command line, whitespaces are used to separate both a parameter from its choices, the multiple different choices for a parameter, and between parameters. Therefore, the following rules are used to ensure proper identification:

A parameter name must be preceeded by two hyphens (--). So, if you want to specify the verbosity of the program, you use --verbose.
Some parameter names are long, and a shorthand is available as well. When using the shorthand, use only a single hyphen (-). 

| Boolean parameters (those accepting only True or False) can get the option ``True`` or ``False`` specified, but the choice can also be implicit. For example, both ``--prevent_overwrite True`` and ``--prevent_overwrite`` do the same. If you want to set one of these to False, this can again be done two ways - both ``--prevent_overwrite False`` and ``--noprevent_overwrite`` are treated the same. Just add ``no`` to the parameter name. This notation using ``no`` is referred to here as the nobool format.
| When using a shorthand, bp for example, ``-bp False`` and ``-nobp`` again do the same. In other words, the ``no`` prefix can be used with shorthands, too.

If a parameter belongs to a map, the name of the map must be prepended with a period (.) in between. For example, lets assume the map 'mymap' which has the parameter 'awesome_parameter', which has the shorthand 'ap' available. This parameter can be accessed through both ``--mymap.awesome_parameter`` and ``-mymap.ap``.
In the case this parameter is a boolean parameter, ``--mymap.awesome_parameter False``, ``--mymap.noawesome_parameter``, ``-mymap.ap False`` and ``-mymap.noap`` all do the same thing.

When a parameter is allowed to take more than one choice, the last choice must be appended with ``\;``. Even if there is only one choice actually given. Lets assume the parameter 'intpar', which is allowed to take multiple integer numbers. The choice for this parameter can be given as follows: ``--intpar 3 42 88\;``.


.. _UserGuide_page_specifying_parameters_file:

**************************
In an input parameter file
**************************

In the input parameter file, each parameter is specified on a separate line. First comes the entire name (no shorthands), then one or more whitespaces, and then the choices. If there are multiple choices, they are again separated by whitespaces.

Parameters belonging to maps must, just as in the command line, contain the map name too, denoted using a period (.) between the map name (comes first), and the parameter name.

When a hashtag (#) is found, it and everything ater it on that line will be ignored. This allows for making notes and comments in the file.

Please note that unlike the command line, parameter files don't allow the nobool format.


***************************
In a default parameter file
***************************

The parameters in the default parameter file are written in the same way as in the input parameter file. The only difference is that the default parameter file must have all parameters. Parameters of maps don't have to be in it, but if any parameter of any map is in there, all parameters of that specific map must be in there.
