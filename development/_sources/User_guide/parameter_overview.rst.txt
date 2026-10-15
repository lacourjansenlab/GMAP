.. _UserGuide_page_parameter_overview:

##################
parameter overview
##################


Here, an overview of the different available parameters is given. If you want to know how exactly to specify your choice, :ref:`this page <UserGuide_page_specifying_parameters>` is for you.

Parameters can be specified in multiple places (here referred to as the 'source') - the command line, the input parameter file, and the default parameter file. A handful of parameters is not allowed to be present in the default parameter file, wherever this is the case, this is mentioned.

When multiple sources are used, the choices in the command line take precedence above the choices in the input file, which take precedence over those in the default parameter file.

Please note that when paths are supplied, they should either be absolute, or specified relative to the source.

Some parameters store paths that can be relative to a directory stored in a different parameter. Where this is the case, this is denoted. Please note that when a file path and a directory path are given, the file path is assumed relative to the directory path. If only the file path is given, it is assumed relative to the source. If only the directory is given, file paths from lower-precedence sources are assumed relative to it.



****************************************
Frequently used parameters
****************************************

You are likely to be looking for these:

- :ref:`verbose <UserGuide_page_parameter_overview_verbose>` indicates how much information the program should give while running.
- :ref:`safe_mode <UserGuide_page_parameter_overview_safemode>` can be useful if your command line software cannot deal with some things printed.
- :ref:`topology_file <UserGuide_page_parameter_overview_topfile>` is used to indicate what file the topology should be read from.
- :ref:`trajectory_file <UserGuide_page_parameter_overview_trjfile>` is used to indicate what file the trajectory should be read from.
- :ref:`number_cores <UserGuide_page_parameter_overview_numcores>` is used to run GMAP parallel.
- :ref:`prevent_overwrite <UserGuide_page_parameter_overview_prevoverwr>` indicates what the program should do if the requested filename is already used.
- :ref:`output_format <UserGuide_page_parameter_overview_outform>` indicates whether you'd like a binary output, text output, or both.
- :ref:`maps_to_use <UserGuide_page_parameter_overview_usemaps>` indicates what kind of singles/oscillators/molecules GMAP should perfrom the calculation on.
- :ref:`couplings_to_use <UserGuide_page_parameter_overview_usecoup>` indicates whether and how couplings should be calculated.
- :ref:`estatics_method <UserGuide_page_parameter_overview_estatmeth>` indicates what method of calculating electrostatics should be used. This influences the results, and some maps might request a certain choice here.
- :ref:`estatic_range <UserGuide_page_parameter_overview_estatrange>` indicates how far away charges may be and still influence the computed electrostatics



****************************************
Example input file
****************************************

The input file supports python-style comments - anything after the '#' character is ignored by GMAP. 

This example is suitable for a first run when doing just a small number of frames. When doing long runs suitable for NISE spectra, mind the 'output_format' parameter - we only want binary output when considering more than a few frames!

.. code-block:: text

    # The directory containing this input file contains another directory
    # called 'MD_data', which contains the topology and trajectory files.
    topology_file                        MD_data/1AKI_topology.tpr
    trajectory_file                      MD_data/1AKI_trajectory.xtc

    maps_to_use                          AmideBB AmideSC
    couplings_to_use                     ProteinAmide :All

    # These are for the first test run on your system, they allow checking
    # whether everything goes as it should!
    output_format                        txt  # change to bin for longer runs
    number_frames                        2
    verbose_logfile                      4

    # Example using parameters from maps
    AmideSC.frequency_map_choice         Jansen
    AmideSC.dipole_map_choice            Jansen
    AmideBB.frequency_map_choice         Jansen
    AmideBB.dipole_map_choice            Jansen
    ProteinAmide.coupling_choice         TCC
    ProteinAmide.NN_coupling_choice      GLDP



**********************
Parameters for visuals
**********************

These change how GMAP looks in the command line.

.. _UserGuide_page_parameter_overview_verbose:

verbose
=======
| (no shorthand available)
| (options: 0, 1, 2, 3, 4)
| (used by: GEM, DEPICT)

How verbose the prints to the command line should be. When 0 is chosen, nothing but errors will be reported. Different from the parameter verbose_logfile

.. _UserGuide_page_parameter_overview_safemode:

safe_mode
=========
| (shorthand: -safe)
| (options: true, t, false, f)
| (used by: GEM, DEPICT)

Whether to run the program in safe mode. If weird errors occur, it might be wise to specify this **directly on the command line**. Currently only influences the color palette used.


dark_mode
=========
| (shorthand: -dm)
| (options: true, t, false, f)
| (used by: GEM, DEPICT)

Whether to run the program in dark mode. Dark mode means that the colors are chosen for good visibility on a dark background. When turned off, the colors are chosen for good visibility on a light background. Has no influence if the program is set to black-white only.


command_line_color
==================
| (no shorthand available)
| (options: white, 4bit, 24bit)
| (used by: GEM, DEPICT)

What color palette to use. White uses black or white letters (the opposite of the background of the command line). 4bit uses `the 4bit ANSI colors <https://en.wikipedia.org/wiki/ANSI_escape_code#Colors>`__, 24bit uses the full color spectrum.

These colors will not be used for writing the log file.

.. tip::
    Do you have some vision issues (like limited color vision)? Then, 4bit colors will probably work better for you than 24bit ones, as the 4bit color usage has been designed with color blindness in mind.

    We know vision issues are a spectrum, and many people experience them differently. We truly appreciate any feedback on the 4bit color usage! Please note that we cannot pick `the 16 colors used <https://en.wikipedia.org/wiki/ANSI_escape_code#Colors>`__, but we can choose which to use!

.. tip::
    You can still use colors while running an automated job on a high-performance cluster! Most likely, you will then not see the command line (for long jobs) directly, it will be written to an output file instead (like slurm.out). To open/view these files with colors active, use the following command::
        less -R [filename]  (unix)
        more -R [filename]  (windows)


command_line_length
===================
| (no whorthand available)
| (used by: GEM, DEPICT)

How long lines are allowed to be. If a line turns out longer, the program will automatically attempt to wrap it at a whitespace. If a single 'word' (like file locations) is too long, it will not be cut off.

Applies both to the command line output, as to the files written by the program.



*************************
parameters for file paths
*************************

.. _UserGuide_page_parameter_overview_sourcedir:

source_directory
================
| (shorthand: -sd)
| (used by: GEM, DEPICT)

The location of the sourcefiles directory. This directory stores all data required for the program to run. The parameter default_parameter_filename will be assumed relative to this directory when applicable.


.. _UserGuide_page_parameter_overview_defpar:

default_parameter_filename
==========================
| (shorthand: -dpf)
| (used by: GEM, DEPICT)

The filename of the default parameter file. This parameter is not allowed to be present in the default parameter file. This file must contain all possible parameters (except those it cannot). It does not need to contain any parameters from maps, but if it contains any from any map, it must contain all of that specific map. The path stored here will be assumed to be relative to the directory given in the parameter source_directory when applicable. 


.. _UserGuide_page_parameter_overview_VEGlib:

VEG_clib_file
=============
| (no shorthand available)
| (used by: GEM, DEPICT)

The filename of the (compiled!) VEG c-library. This will be either a '.dll' file (Windows), a '.so' file (Linux), or a '.dylib' file (MacOS). This file contains the code for calculating electrostatic properties of the system. The path stored in this parameter will be assumed to be relative to the directory given in the parameter source_directory when applicable.


.. _UserGuide_page_parameter_overview_logdir:

log_directory
=============
| (no shorthand available)
| (used by: GEM, DEPICT)

The location of the log directory. In this directory, all files relating to logging the program flow are located. The parameter log_filename will be assumed relative to this directory when applicable.


.. _UserGuide_page_parameter_overview_logfile:

log_filename
============
| (no shorthand available)
| (used by: GEM, DEPICT)

The filename of the log file. This file contains the same, or similar information as the prints to the command line, depending on the choice for the parameters verbose and verbose_logfile. The path stored here will be assumed to be relative to the directory given in the parameter log_directory when applicable.


.. _UserGuide_page_parameter_overview_proffile:

log_profiling_filename
======================
| (no shorthand available)
| (used by: GEM)

The file name of the output file for the profiling functionality. This file is not meant for human eyes - it should either be parsed interactively using a command line parser, or be turned into a graph. The path stored here will be assumed to be relative to the directory given in the parameter log_directory when applicable.

.. hint::
    This is a parameter that should only be needed by GMAP developers, and maybe a map developer here or there. The file is created using/by the cProfile module.


.. _UserGuide_page_parameter_overview_proftemp:

log_profiling_tempfile
======================
| (no shorthand available)
| (used by: GEM)

The file name of the temporary file for the profiling functionality. This file is not meant to be stored, but it has to exist at some point in time. This is a way to make sure that we're not accidentally overwriting an important file; just to delete it later. The path stored here will be assumed to be relative to the directory given in the parameter log_directory when applicable.

.. hint::
    The contents of this file aren't directly relevant. The file is written by the gprof2dot module, and will only be created by GMAP when running dot. After dot is done, the file is removed. The contents of this file are then found in the resulting png, in a much more human-readable format.


.. _UserGuide_page_parameter_overview_profgraphfile:

log_profiling_graph_filename
============================
| (no shorthand available)
| (used by: GEM)

The file name of output image for the profiling functionality. This image is the main purpose of the profiler, and can be easily understood. The path stored here will be assumed to be relative to the directory given in the parameter log_directory when applicable.

.. hint::
    This is a parameter that should only be needed by GMAP developers, and maybe a map developer here or there. The file is created using/by the dot command of the graphvis program that needs to be installed separately. This image is the main goal of profiling GMAP.


.. _UserGuide_page_parameter_overview_outdir:

output_directory
================
| (no shorthand available)
| (used by: GEM, DEPICT)

The location of the output directory. All output files generated by the program will be put here. The parameters output_hamiltonian_filename and output_dipole_filename will be assumed relative to this directory when applicable.


.. _UserGuide_page_parameter_overview_outparfile:

output_parameter_filename
=========================
| (no shorthand available)
| (used by: GEM)

The filename of the output parameter file, _with_ extension! The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.

The output parameter files contains all parameters set for the run, and can be used as an input (or default) parameter file in future runs to replicate the same settings as for the current run.


output_legend_filename
======================
| (no shorthand available)
| (used by: GEM)

The filename of the legend output file, _with_ extension! The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.

The legend file contains a short description of each oscillator respresented in the output files generated during the run, allowing to trace values back to atoms in the MD system.


output_couplingvis_filename
===========================
| (no shorthand available)
| (used by: GEM)
| (extensions possible: png, pdf, ps, eps and svg)

The filename of the couplingvis output file, _with_ extension! The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.

There are multiple choices of extension available - the exact set will differ per os. In most cases, the following types are supported: png, pdf, ps, eps and svg.

This file will only be created when 'ham' is among the choices for the parameter output_data.


output_estatics_filename
========================
| (used by: DEPICT)

The filename of the electrostatics output file, _with_ extension! This file contains electrostatic properties. The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.


.. _UserGuide_page_parameter_overview_outhamfile:

output_hamiltonian_filename
===========================
| (shorthand: -ohf)
| (used by: GEM)

The filename of the Hamiltonian output file, _without_ extension! Depending on the output format of choice, this file may either be in binary, or in txt format. The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.


output_energies_filename
===========================
| (shorthand: -oef)
| (used by: GEM)

The filename of the energies output file, _without_ extension! Depending on the output format of choice, this file may either be in binary, or in txt format. The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.

The energies file contains just the diagonal of the Hamiltonian.


.. _UserGuide_page_parameter_overview_outdipfile:

output_dipole_filename
======================
| (shorthand: -odf)
| (used by: GEM)

The filename of the dipole output file, _without_ extension! Depending on the output format of choice, this file may either be in binary, or in txt format. The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.


.. _UserGuide_page_parameter_overview_outramfile:

output_raman_filename
======================
| (shorthand: -orf)
| (used by: GEM)

The filename of the raman output file, _without_ extension! Depending on the output format of choice, this file may either be in binary, or in txt format. The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.


.. _UserGuide_page_parameter_overview_outposfile:

output_positions_filename
=========================
| (shorthand: -opf)
| (used by: GEM)

The filename of the positions output file, _without_ extension! Depending on the output format of choice, this file may either be in binary, or in txt format. The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.


output_doublepos_filename
=========================
| (shorthand: -opf)
| (used by: GEM)

The filename of the double positions output file, _without_ extension! Depending on the output format of choice, this file may either be in binary, or in txt format. The path stored here will be assumed to be relative to the directory given in the parameter output_directory when applicable.


.. _UserGuide_page_parameter_overview_mapdir:

map_directory
=============
| (shorthand: -md)
| (used by: GEM, DEPICT)

The location of the maps directory. Multiple directories are allowed to be given. Within a maps directory, the maps that can be used are stored. See :ref:`adding a new map <UserGuide_page_adding_map>` for more information on what maps are and how to make one.


.. _UserGuide_page_parameter_overview_topfile:

topology_file
=============
| (shorthand: -top)
| (used by: GEM, DEPICT)

The filename and location of the topology file to be used during the calculation. Allowed filetypes are the ones listed `here <https://userguide.mdanalysis.org/stable/formats/index.html>`__ that have a tick in the column labeled 'topology'.

A topology file contains all the information that stays the same during the calculation. What are all atoms named? Which atom lives in which residue? What are those residues named? What masses and charges do the atoms have? What element and type are they?

The following have been tested/confirmed usable with GMAP:

- GROMACS: .tpr (recommended)
- CHARMM/NAMD: .psf
- Amber: .top


The following have been tested/confirmed **not** usable with GMAP:

- GROMACS: .gro (lacks charge information)


.. _UserGuide_page_parameter_overview_trjfile:

trajectory_file
===============
| (shorthand: -trj)
| (used by: GEM, DEPICT)

The filename and location of the trajectory file to be used during the calculation. Allowed filetypes are the ones listed `here <https://userguide.mdanalysis.org/stable/formats/index.html>`__ that have a tick in the column labeled 'coordinates'.

A trajectory file contains all information that could change during the simulation - most notably the positions of atoms and the dimensions of the periodic bounding box.

The following have been tested/confirmed usable with GMAP:

- GROMACS: .xtc (recommended), .gro
- CHARMM/NAMD: .dcd
- Amber: .mdcrd*, .nc

\* Note that there appear to be different types of amber .mdcrd files. Some do contain information on the dimensions of the simulation box, others do not. GMAP needs one that does.


The following have been tested/confirmed **not** usable with GMAP:

- CHARMM/NAMD: .crd (lacks PBC box dimensions), .cor (MDAnalysis does not support this file type)


*********************************
parameters for how to write files
*********************************


.. _UserGuide_page_parameter_overview_verboselog:

verbose_logfile
===============
| (no shorthand available)
| (options: 0, 1, 2, 3, 4)
| (used by: GEM, DEPICT)

How verbose the prints to the log file should be. Different from the parameter verbose.


dont_report_error
=================
| (no shorthand available)
| (used by: GEM, DEPICT)

What errors shouldn't be printed. Error codes are of the format AA_BB_C. To silence a very specific error, give the entire code. To silence a specific group, leave the varying parts blank (but leave the underscores): AA_BB\_ will silence all errors starting with AA_BB\_, AA__C will silence all errors that start with AA and end with C (with variable middle part), etc. You can keep as many parts blank as you want.


.. _UserGuide_page_parameter_overview_prevoverwr:

prevent_overwrite
=================
| (no shorthand available)
| (options: true, t, false, f)
| (used by: GEM, DEPICT)

Whether the files created by the program should or shouldn't overwrite existing files. When set to True, the existing file will be renamed, and the requested name will be used for the new file. When set to False, the old file will be overwritten, and the data inside lost forever.


.. _UserGuide_page_parameter_overview_outform:

output_format
=============
| (no shorthand available)
| (options: bin, txt)
| (used by: GEM)

In what format the output files should be created. Bin for binary format, txt for text. Both are in a format that NISE can read them. In case multiple options are provided, a file will be created in each requested format.


.. _UserGuide_page_parameter_overview_output_data:

output_data
===========
| (no shorthand available)
| (options: ham, dip, ene, ram, pos, dbp)
| (used by: GEM)

What kind of data the program should generate. Multiple choices can be provided. 'ham' lets the program output a Hamiltonian for each frame, 'dip' makes it output dipoles. 'ene' is used to output the energies file (the diagonal of the hamiltonian). 'ram' outputs the raman tensor, 'pos' outputs the positions file (a single position per oscillator), 'dbp' outputs the doublepos file (two positions per oscillator).

hamiltonian_units
=================
| (no shorthand available)
| (options: cm-1, eV)
| (used by: GEM)

In what units the output hamiltonian should be written. Cannot be used together with hamiltonian_multiplier.

hamiltonian_multiplier
======================
| (no shorthand available)
| (used by: GEM)

The output hamiltonian (in cm-1) will be multiplied by this value before saving. Cannot be used together with hamiltonian_units.

energies_units
==============
| (no shorthand available)
| (options: cm-1, eV)
| (used by: GEM)

In what units the output energies file should be written. Cannot be used together with energies_multiplier.

energies_multiplier
===================
| (no shorthand available)
| (used by: GEM)

The output energies file (in cm-1) will be multiplied by this value before saving. Cannot be used together with energies_units.

dipoles_units
=============
| (no shorthand available)
| (options: Debye, eBohr)
| (used by: GEM)

In what units the output dipoles should be written. Cannot be used together with dipoles_multiplier.

dipoles_multiplier
==================
| (no shorthand available)
| (used by: GEM)

The output dipoles (in Debye) will be multiplied by this value before saving. Cannot be used together with dipoles_units.

raman_units
=============
| (no shorthand available)
| (options: Ang3, Bohr3)
| (used by: GEM)

In what units the output raman tensors should be written. Cannot be used together with raman_multiplier.

raman_multiplier
==================
| (no shorthand available)
| (used by: GEM)

The output dipoles (in Debye) will be multiplied by this value before saving. Cannot be used together with dipoles_units.

positions_units
===============
| (no shorthand available)
| (options: ang, bohr, nm)
| (used by: GEM)

In what units the output positions should be written. Cannot be used together with positions_multiplier.

positions_multiplier
====================
| (no shorthand available)
| (used by: GEM)

The output positions (in angstrom) will be multiplied by this value before saving. Cannot be used together with positions_units.

doublepos_units
===============
| (no shorthand available)
| (options: ang, bohr, nm)
| (used by: GEM)

In what units the output doublepos should be written. Cannot be used together with doublepos_multiplier.

doublepos_multiplier
====================
| (no shorthand available)
| (used by: GEM)

The output doublepos (in angstrom) will be multiplied by this value before saving. Cannot be used together with doublepos_units.


positions_center
================
| (no shorthand_available)
| (used by: GEM)

The positions and doublepos files generated by the program have all the positions placed in a certain interval. By default, all positions lie within 0 and 1 of the box axes (meaning for orthorhombic boxes, no negative values are saved), meaning they are centered around the midpoint of each of the axes. This default could be recreated by using ``positions_center 0.5 0.5 0.5`` (input file) or ``--positions_center 0.5 0.5 0.5\;`` (command line).
When set to ``0 0 0`` instead, all positions will be as close to the origin as possible. Any float value is allowed.


couplingvis_figsize
===================
| (no shorthand available)
| (used by: GEM)

The width of the couplingvis output image, in inches.


couplingvis_dpi
===============
| (no shorthand available)
| (used by: GEM)

The resolution of the couplingvis output image.



**********************************************
parameters for specifying calculation settings
**********************************************


.. _UserGuide_page_parameter_overview_usemaps:

maps_to_use
===========
| (shorthand: -um)
| (used by: GEM, DEPICT)

Which maps should be considered in the calculation. Or, in other words, which kinds of oscillators should be found, and calculated properties for. There are limited choices - namely, the names of the maps supplied through the parameter map_directory.


.. _UserGuide_page_parameter_overview_usecoup:

couplings_to_use
================
| (no shorthand available)
| (used by: GEM)

.. note::
    This parameter differs from the others in that it may be used multiple times within a single file.

.. important::
    This parameter pulls information from lower priority sources, even if specified in a higher priority one:

    If the default file says 'all couplings should be dipole-dipole', and you specify in the input file that the coupling between groups of type 'A' should be 'X', then couplings between groups of type 'B' will remain dipole-dipole, as you didn't specify anything else for them.

    In other words, for every type of coupling, the program separately walks through all parameter files.

    If a certain type of pair is covered by multiple lines in the same parameter file, the one lowest down will take precedence.

Which couplings should be used in the calculation, and for what purpose. A MD system contains a certain number of oscillators (selected by 'maps_to_use'), that have their oscillating frequencies coupled inside the hamiltonian.

By default, all oscillators are coupled using the dipole-dipole coupling method (denoted using ``couplings_to_use   DipDip :All``), but a different choice can be made. If you want to choose a different coupling method for a certain oscillator, you can!

The general format is as follows: ``couplings_to_use  [coupling map name] [group selection]``

The options available for the coupling map name depend on the maps you've loaded in - all options are the names of folders inside the 'Pairs' folder, which is inside the maps folder (the one(s) provided using 'map_directory'). One extra option is always available: 'None', for if you don't want the program to calculate any coupling. This will lead to a value of 0 for those couplings. You can only specify one coupling map per line!

Then, group selection is where you explain what type of oscillators are to be coupled using the specific map. There are a few options here. You can use multiple ones on a single line. They should be separated by (any amount of) whitespaces.
- ':All' indicates all possible pairs of oscillators
- ':same' indicates all couplings between two oscillators of the same type (for example, coupling two (protein backbone) amide groups, or two (bact-c) chlorophyll molecules)
- ':diff' indicates all couplings between two oscillators of a different type (for example, coupling an amide group with a chlorophyll molecule)
- 'X:Y' indicates couplings between one oscillator of type 'X', and one of type 'Y'. The available oscillator types are the same as the available choices for the parameter 'maps_to_use'. There should be no spaces between group names and the colon!
- 'X:' indicates any couplings involving an oscillator of type 'X' - the type of the other oscillator does not matter. The available oscillator types are the same as the available choices for the parameter 'maps_to_use'. There should be no spaces between group names and the colon!


.. _UserGuide_page_parameter_overview_scalecoup:

couplings_scale
===============
| (no shorthand available)
| (used by: GEM)

.. warning::
    This parameter is similar to the parameter 'dielectric_constant', and GMAP allows the two to be used together. Read very careful which of the two you need, and be **even more careful** if you decide to use both.

.. note::
    This parameter differs from the others in that it may be used multiple times within a single file.

.. important::
    This parameter pulls information from lower priority sources, even if specified in a higher priority one:

    If the default file says 'all couplings should be multiplied by 2.0', and you specify in the input file that the couplings of type 'A' should be multiplied by 3.5, then couplings of type 'B' will still be multiplied by 2.0, as you didn't specify anything else for them.

    In other words, for every type of coupling, the program separately walks through all parameter files.

    If a certain type of pair is covered by multiple lines in the same parameter file, the one lowest down will take precedence.

The value by which to multiply all couplings of the given type. This parameter expects two parts on each line. Just as with the parameter couplings_to_use, the first one is the name of the coupling map. This may be any map, including those only assigned through other coupling maps. The second part is the value by which the couplings should be multiplied.

If the requested coupling map shows up in the 'couplingvis' pdf, those values will be multiplied by the value provided on this line.

If this parameter is used together with the parameter 'dielectric_constant', both will be applied multiplicatively.


dielectric_constant
===================
| (no shorthand available)
| (used by: GEM)

.. warning::
    This parameter is similar to the parameter 'couplings_scale', and GMAP allows the two to be used together. Read very careful which of the two you need, and be **even more careful** if you decide to use both.

The value for the dielectric constant to assume. The constant is applied in two places:
- All electrostatic values (potential, electric field and gradient) are divided by the value chosen for the dielectric constant.
- All couplings are divided by the value chosen for the dielectric constant. Even those that also have a multplication for the parameter couplings_scale!

Note for map makers: Some mappings in literature use a specified scaling or dielectric constant. The GMAP mapping assumes you to apply such scalings either through the dielectric_constant or through the couplings_scale. It should not be a part of a mapping.


.. _UserGuide_page_parameter_overview_singWL:

singles_whitelist
=================
| (no shorthand available)
| (used by: GEM)

Unlike the influencers, both the whitelist and blacklist variants of this parameter are allowed in a single file. You may even have multiple occurences of each in a single file. First, all whitelists are read/interpreted in order of occurence in the file, then all blacklists.

This parameter gives you more control over what singles/oscillators should be treated. Ones that are chosen will have their properties (frequency/dipole moment/position) calculated and written to the output files. Those that are omitted will not be treated at all.

Anything whitelisted will be included, unless a more specific blacklist rule excludes it again.

This parameter takes a variable number of arguments. If a map doesn't make any changes, there's two or three: ``singles_whitelist [maps] [method] [choice]``
``maps`` indicates to which map(s) the choice should be applied. ``:All`` applies the filter to all maps used. ``AA`` applies the choice to only the map named 'AA' (use the same names as those used for the parameter maps_to_use), ``AA,BB`` applies it to both the map named 'AA' and the map named 'BB'. You can put any number of maps here, just make sure that there are no white spaces!

.. note::
    A map can change the function applying these black- and whitelists. That means maps can support more ways of filtering, or exclude existing ones. Check the documentation of your maps to see what options are available - if nothing is noted/specified, the map should just use the default implementation mentioned here.

``method`` explains how the rest of this line should be interpreted. How you want to select. The two most simple ones are ``:All`` (just whitelist all singles) and ``:None`` (whitelist none of the singles). The other two options are ``resnums`` and ``resnames``. Individual maps may add/remove choices here.

``choice`` gives more details. If you picked 'resnums' as the method, you can give the numbers of the residues that should be included. Any oscillator whose first atom is within a residue with its index / residue number in the provided list will be selected for. You can either provide a list of individual numbers (separated by whitespaces), or a range of numbers: ``1 3-5 7`` means the same as ``1 3 4 5 7``. If you picked 'resnames' as the method, the program instead looks at the name of the residue of the first atom of the oscillator. If you want to allow multiple options, you just add them, separated by a whitespace.

By default, this parameter has the following setting: ``singles_whitelist :All :All``


.. _UserGuide_page_parameter_overview_singBL:

singles_blacklist
=================
| (no shorthand available)
| (used by: GEM)

Unlike the influencers, both the whitelist and blacklist variants of this parameter are allowed in a single file. You may even have multiple occurences of each in a single file. First, all whitelists are read/interpreted in order of occurence in the file, then all blacklists.

This parameter gives you more control over what singles/oscillators should be treated. Ones that are chosen will have their properties (frequency/dipole moment/position) calculated and written to the output files. Those that are omitted will not be treated at all.

Anything blacklisted will be omitted. For more details on exact specifications, see the parameter 'singles_whitelist' above.

By default, this parameter has the following setting: ``singles_blacklist :All :None``


.. _UserGuide_page_parameter_overview_inflWL:

influencers_whitelist
=====================
| (no shorthand available)
| (used by: GEM, DEPICT)

.. important::
    only one of 'influencers_whitelist', 'influencers_blacklist', 'influencers_file' and 'influencers_select_atoms' may be present in a single parameter source. Between sources, multiple can occur: the command line can use 'influencers_blacklist', and the input parameter file can use 'influencers_file'. The selection of the most 'important' source will be used, the rest is ignored. This means that the commandline 'influencers_blacklist' cannot use definitions in the 'influencers_file' given in the input parameter file.

Atoms belonging to a residue of (one of) the given name(s) will be taken into account when calculating electrostatics for the oscillators. For more information on how to specify influencers, see :ref:`Specifying influencers <UserGuide_page_influencer_specification>`.


.. _UserGuide_page_parameter_overview_inflBL:

influencers_blacklist
=====================
| (no shorthand available)
| (used by: GEM, DEPICT)

.. important::
    only one of 'influencers_whitelist', 'influencers_blacklist', 'influencers_file' and 'influencers_select_atoms' may be present in a single parameter source. Between sources, multiple can occur: the command line can use 'influencers_blacklist', and the input parameter file can use 'influencers_file'. The selection of the most 'important' source will be used, the rest is ignored. This means that the commandline 'influencers_blacklist' cannot use definitions in the 'influencers_file' given in the input parameter file.

Atoms belonging to a residue of (one of) the given name(s) will **not** be taken into account when calculating electrostatics for the oscillators. For more information on how to specify influencers, see :ref:`Specifying influencers <UserGuide_page_influencer_specification>`.


.. _UserGuide_page_parameter_overview_inflfile:

influencers_file
================
| (no shorthand available)
| (used by: GEM, DEPICT)

.. important::
    only one of 'influencers_whitelist', 'influencers_blacklist', 'influencers_file' and 'influencers_select_atoms' may be present in a single parameter source. Between sources, multiple can occur: the command line can use 'influencers_blacklist', and the input parameter file can use 'influencers_file'. The selection of the most 'important' source will be used, the rest is ignored. This means that the commandline 'influencers_blacklist' cannot use definitions in the 'influencers_file' given in the input parameter file.

Atoms belonging to a residue of (one of) the given name(s) on the line starting with 'choice' in this file will be taken into account when calculating electrostatics for the oscillators. For more information on how to specify influencers, see :ref:`Specifying influencers <UserGuide_page_influencer_specification>`. This file should be given relative to the place where the parameter is specified.


.. _UserGuide_page_parameter_overview_inflSA:

influencers_select_atoms
========================
| (no shorthand available)
| (used by: GEM, DEPICT)

.. important::
    only one of 'influencers_whitelist', 'influencers_blacklist', 'influencers_file' and 'influencers_select_atoms' may be present in a single parameter source. Between sources, multiple can occur: the command line can use 'influencers_blacklist', and the input parameter file can use 'influencers_file'. The selection of the most 'important' source will be used, the rest is ignored. This means that the commandline 'influencers_blacklist' cannot use definitions in the 'influencers_file' given in the input parameter file.

In case the influencers should be defined differently from the 'default' method of giving residue names, this parameter allows to use the atom selection syntax from MDAnalysis. The given choice for this parameter will be fed as a string to MDAnalysis.select_atoms(). Instructions for how to build this string can be found on `MDAnalysis <https://docs.mdanalysis.org/stable/documentation_pages/selections.html>`__.

.. note::
    The used MDAnalysis functionality can make a noticable impact on calculation times, especially when using the program in parallel (multiple CPUs / cores / nodes). Most usecases should be fine, but if you notice a big difference for your calculations, please reach out to the developers of GMAP.


.. _UserGuide_page_parameter_overview_estatmeth:

estatics_method
===============
| (no shorthand available)
| (options: perres, perres_nocut)
| (used by: GEM)

How the electrostatics should be calculated. For perres_nocut, if the centre of mass of an influencing residue is within range of the oscillating residue, all its atoms can influence all oscillating atoms. This is the way AIM calculated the electrostatic properties. This method ignores any choices made for estatic_smooth_range. 
For perres, if an influencer is within range of the oscillating residues, its individual atoms are considered. Only the atoms that are within range of the oscillating residue will actually be considered, the others are ignored.


neutral_charge_threshold
========================
| (no shorthand available)
| (used by: GEM, DEPICT)

How close to zero the total charge needs to be to be considered neutral. Essentially, all values between 0 - neutral_charge_threshold and 0 + neutral_charge_threshold will be considered 0.


guess_bonds
===========
| (no shorthand available)
| (options: true, t, false, f)
| (used by: GEM, DEPICT)

Whether the program should guess bonds for the supplied universe. This should only be used if bond information if absolutely necessary, and there really is no topology file with bond information available. Bonds are guessed by `MDAnalysis <https://userguide.mdanalysis.org/stable/formats/guessing.html#types>`__.


treat_box
=========
| (no shorthand available)
| (options: auto, orthorhombic, triclinic)
| (used by: GEM, DEPICT)

As what kind of box the system should be treated. 'orthorhombic' is intended for any system where all box vectors are on 90 degree angles, 'triclinic' is intended for the others. When choosing either of these options, that mode is forced on your system, regardless of whether it's angles match. When set to 'auto', GMAP will look at your system, use 'orthorhombic' whenever possible (as it is much faster), and 'triclinic' for the other cases.

.. tip::
    How much faster is orthorhombic exactly? This will depend on multiple factors. But we've seen runs take 25% - 50% less time so far.


.. _UserGuide_page_parameter_overview_estatrange:

estatic_range
=============
| (no shorthand available)
| (used by: GEM, DEPICT)

To what distance charges should be considered when computing the electrostatic properties. If the parameter estatic_smooth_range is set to 0, any charges within estatic_range will be fully considered, any outside won't be at all. For details how the parameter estatic_smooth_range influences this, see that entry for more info.


estatic_smooth_range
====================
| (no shorthand available)
| (options: 0 for no smoothing, else any positive value)
| (used by: GEM, DEPICT)

Over what distance the weight of charges should decrease. This less abrupt edge to the sphere of charges makes for less chaotic results (less variation with slightly different choice of estatic_range).

Lets say estatic_range = R, estatic_smooth_range = S. Any charges within R - S/2 will be considered fully, while any outside R + S/2 will not be considered at all. Between those two distances, the charge will be considered partially, with the part decreasing linearly with distance.



.. _UserGuide_page_parameter_overview_startframe:

start_frame
===========
| (no shorthand available)
| (used by: GEM, DEPICT)

At what frame number the calculation must start. Counting starts at 0. May occur in a parameter file together with number_frames and/or stop_frame, but the combination of them must make sense.
With start_frame at 10, number_frames at 20, and stop_frame at 30, the first 10 frames (numbered 0 through 9) will be skipped, the following 20 frames (numbered 10 to 29) will be treated, and the remaining frames (30 and up) will be skipped.


.. _UserGuide_page_parameter_overview_numframe:

number_frames
=============
| (no shorthand available)
| (used by: GEM, DEPICT)

The amount of frames that the program should treat. Counting starts at 0. May occur in a parameter file together with start_frame and/or stop_frame, but the combination of them must make sense.
With start_frame at 10, number_frames at 20, and stop_frame at 30, the first 10 frames (numbered 0 through 9) will be skipped, the following 20 frames (numbered 10 to 29) will be treated, and the remaining frames (30 and up) will be skipped.

.. note::
    For DEPICT use, this parameter stores not the amount of MD frames to be treated (that is by definition only one), but instead the amount of different radii to
    use (the amount of different estatic_range). Each whole number starting from estatic_range will be used.


.. _UserGuide_page_parameter_overview_stopframe:

stop_frame
==========
| (no shorthand available)
| (used by: GEM)

At what frame number the calculation must stop (exclusive). Counting starts at 0. May occur in a parameter file together with start_frame and number_frames, but the combination of them must make sense.
With start_frame at 10, number_frames at 20, and stop_frame at 30, the first 10 frames (numbered 0 through 9) will be skipped, the following 20 frames (numbered 10 to 29) will be treated, and the remaining frames (30 and up) will be skipped.


.. _UserGuide_page_parameter_overview_prof:

profiler
========
| (no shorthand available)
| (options: true, t, false, f)
| (used by: GEM)

Whether the program should be profiled. This gives more detailed insight in calculation run times and why it wasn't faster. This parameter should reasonably only be relevant for GMAP developers, and maybe sometimes a map developer.


.. _UserGuide_page_parameter_overview_profgraph:

profiler_graph
==============
| (no shorthand available)
| (options: true, t, false, f)
| (used by: GEM)

Whether the program should make a pretty image with profiling information. This gives more detailed insight in calculation run times and why it wasn't faster. This parameter should reasonably only be relevant for GMAP developers, and maybe sometimes a map developer.

This parameter has no meaning/use when the ``profiler`` parameter is set to false.


.. _UserGuide_page_parameter_overview_timelimit:

time_limit
==========
| (no shorthand available)
| (used by: GEM)

How long the calculation is allowed to take (in minutes). Every 'batch_size' (see below) amount of frames, the program will consider how long it has ran, and how long the next batch of frames will take. If there is not enough time to finish two more batches, another will not be started, to make sure there is enough time to properly close the program.

.. tip::
    It is recommended to use this parameter when working on a cluster, and set it to the same amount of time as has been requested to use on the cluster.


batch_size
==========
| (no shorthand available)
| (used by: GEM)

Every how many frames the program should reconsider the time limit. Counting happens relative to the start frame, so if start_frame is set to 3, and batch_size to 10, the program will check if it can continue the calculation before starting frame 13, 23, 33, etc.

.. _UserGuide_page_parameter_overview_numcores:

number_cores
============
| (shorthand: -nc)
| (used by: GEM)

How many cores GMAP should use for the calculation. Note that not all calculations make use of additional cores!
When using this option, make sure you have enough memory available. Memory usage roughly scales linearly with amount of cores used.

Please note that the parallellization of GMAP utilizes calls to itself - so the initialization of the calculation and reading of the MD output files is done by each core. This means that the parallellization is not infinitely scaleable. Please perform a short test to confirm the requested cores function as expected on your system!

.. tip::
    The first time GMAP encounters your MD files, they will be indexed. This process takes a (relatively) long time. It is therefore recommended to first let GMAP get to know these files through a single-core run treating a single frame. After that run finishes, you can do the proper (full) calculation with multiple cores.

    If you later want to treat those same MD files with a different GMAP calculation, this 1-core, 1-frame step is not needed.

    **Bonus tip for computing cluster users:**
    The extra step is necessary for creating the "_offsets.npz" file that is stored along with your MD trajectory file. To get the full advantage of the parallellization, make sure that this file is available for your computation!

These GMAP features can currently support parallel computations:
- GMAP GEM run

