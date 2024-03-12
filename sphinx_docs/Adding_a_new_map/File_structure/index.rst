##############
File structure
##############

All maps are stored inside a map directory, that can be supplied to
the program using the `map_directory` keyword. The keyword can be given
multiple directories, in which case all given directories are searched for
maps.

Each map directory contains two directories: one named 'Singles', and one
named 'pairs'. Each of these directories then contains a separate directory
for each map added. The map-specific instructions that follow will refer to
this map-specific directory as the main directory.

The difference between 'Singles' and 'Pairs' is the type of maps they contain.
Maps stored in 'Singles' deal with a single active group. Such a map might
encode a way to calculate the frequency at which that specific group will
absorb light. Similarly, a method to find the dipole moment will be stored
here, among others, too. Maps stored in 'Pairs', on the other hand, deal
with pairs of groups. They will, for example, encode a way to calculate the
coupling between two groups (each of which is defined in 'Singles').

A map can take many different shapes. Both scientifically/physically speaking,
but also in regards to its digital structure in the program. Only one central
file is mandatory (the core file), a few other given files are optional, and from the optional .py file, a completely free collection of files can be accessed. Information
on each of the possible files can be found in the pages linked below.

.. toctree::

    core
    parameters
    main_py

