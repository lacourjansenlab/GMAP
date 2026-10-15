##############
File structure
##############

All maps are stored inside a map directory, that can be supplied to
the program using the ``map_directory`` keyword. The keyword can be given
multiple directories, in which case all given directories are searched for
maps.

Each map directory contains two directories: one named 'Singles', and one
named 'Pairs'. Each of these directories then contains a separate directory
for each map added. The map-specific instructions that follow will refer to
this map-specific directory as the main directory.

The difference between 'Singles' and 'Pairs' is the type of maps they contain.
Maps stored in 'Singles' deal with a single active group. Such a map might
encode a way to calculate the frequency at which that specific group will
absorb light. Similarly, a method to find the dipole moment will be stored
here, among others, too. Maps stored in 'Pairs', on the other hand, deal
with pairs of groups. They will, for example, encode a way to calculate the
coupling between two groups (each of which is defined in 'Singles').

Because of this nature, it is possible that pair maps require some extra information on the singles they couple. That means that its possible that if you want a pair map to treat a specific single, that single map must have additional keywords present in the core.txt file, or specific functions in its main.py file. If a pair map requires this, it must clearly indicate so.

A map can take many different shapes. Both scientifically/physically speaking,
but also in regards to its digital structure in the program. For singles maps one central file is mandatory (the core file), a few other given files are optional, and from the optional .py file, a completely free collection of files can be accessed. 

For pairs maps, the core file is optional, while the main.py file is mandatory. Pairs can also make use of a parameter file, just like singles, and any other required files can be accessed by the map itself through the code file. Information on each of the possible files can be found in the pages linked below.


***************************************
pages for singles maps
***************************************

.. grid:: 1 2 2 3

    .. grid-item-card::
        :margin: 0 3 0 0
        :link: single_core
        :link-type: doc

        **core.txt (singles)**
        ^^^^^^^^^^^^^^^^
        How to make a core.txt file for singles maps.

    .. grid-item-card::
        :margin: 0 3 0 0
        :link: parameters
        :link-type: doc

        **Parameters**
        ^^^^^^^^^^^^^^
        How to add map-specific parameters to your map.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: single_main_py
        :link-type: doc

        **main.py (singles)**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        How to make a core.txt file for singles maps.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: references_bib
        :link-type: doc

        **references**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        How to make a references file for your map.
    
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: GMAPconstants
        :link-type: doc

        **GMAP constants file**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        All the constants available for use while creating your map.



***************************************
pages for pairs maps
***************************************

.. grid:: 1 2 2 3

    .. grid-item-card::
        :margin: 0 3 0 0
        :link: pair_core
        :link-type: doc

        **core.txt (pairs)**
        ^^^^^^^^^^^^^^^^
        How to make a core.txt file for pairs maps.

    .. grid-item-card::
        :margin: 0 3 0 0
        :link: parameters
        :link-type: doc

        **Parameters**
        ^^^^^^^^^^^^^^
        How to add map-specific parameters to your map.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: pair_main_py
        :link-type: doc

        **main.py (pairs)**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        How to make a core.txt file for pairs maps.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: references_bib
        :link-type: doc

        **references**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        How to make a references file for your map.

    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: GMAPconstants
        :link-type: doc

        **GMAP constants file**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        All the constants available for use while creating your map.




.. toctree::
    :hidden:

    single_core
    parameters
    single_main_py
    references_bib
    GMAPconstants

.. toctree::
    :hidden:

    pair_core
    parameters
    pair_main_py
    references_bib
    GMAPconstants

