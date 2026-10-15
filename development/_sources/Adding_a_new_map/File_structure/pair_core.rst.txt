.. _AddMap_FileStruct_PairCore:

#############
core.txt file
#############

(this applies to pairs maps. If you are looking for singles maps instead, go to :ref:`the singles version of this page.<AddMap_FileStruct_SingCore>`)

This file forms the basis for any map. For pair maps, it is not required, but optional. It explains the context of the map - what other things should be available to the program, what kind of groups this map is allowed to treat. It works somewhat similar to how one creates input parameter files. All available keywords will be listed here, with an explanation.


**************
requre_singles
**************

*optional parameter*

Multiple choices can be provided, separated by whitespaces.

Any singles maps specified here must be present. They do not have to be chosen by the user, none of their oscillators have to be present, the only requirement is that the files of the map itself must be present, as this map needs them.


**************
requrire_pairs
**************

*optional parameter*

Multiple choices can be provided, separated by whitespaces.

Any pairs maps specified here must be present. They do not have to be chosen by the user (nor by other maps), the only requirement is that the files of the map itself must be present, as this map needs them.

The most common reason for a pair map to require other pair maps is because it wants to assign certain pairs to it. It knows that it'll receive invalid pairs that should be treated by that one instead. This can, of course, only happen if that map choice is available during the calculation.


****************
require_keywords
****************

*optional parameter*

Multiple choices can be provided, separated by whitespaces. If the coupling map is named 'A', and the choice here is 'kw', the program will look in the core.txt files of singles map for the keyword 'A.kw'.

Any oscillator coupled by this map must belong to a map which has this keyword present in its core.txt file. The most likely reason for this is because this coupling map requires some property that GMAP itself doesn't need. This keyword can either contain all information on that property, or a filepath to a file with more information.


****************
require_mapfuncs
****************

*optional parameter*

Multiple choices can be provided, separated by whitespaces. If the coupling map is named 'A', and the choice here is 'mf', the map is expected to contain the function 'CP_A_mf'. Any functions in this maps 'main.py' should call this function themselves, but this convention (the 'CP_[mapname]' prefix) should be conserved to protect namespaces. Also, the automated check from GMAP to see if a map has this function looks for that name.

Any oscillator coupled by this map must belong to a map which has this function present in its main.py file. The most likely reason for this is because this coupling map requires some property that GMAP itself doesn't need. The property cannot easily be generalized, so cannot be treated through a keyword. Instead, that map must do some work for this one to function.


*****************
singles_whitelist
*****************

*optional parameter*

Multiple choices can be provided, separated by whitespaces.

Any oscillator coupled by this map must belong to one of the singles maps listed here. If the user requests anything else, the program will quit.


*****************
singles_blacklist
*****************

*optional parameter*

Multiple choices can be provided, separated by whitespaces.

Any oscillator coupled by this map cannot belong to one of the singles maps listed here. If the user requests anything else, the program will quit.


******************
valid_combinations
******************

*optional parameter*

Multiple choices can be provided, separated by whitespaces.

Only the specific pairs listed here are allowed to be coupled by this map. If the user requests anything else, the program will quit.

The syntax for defining these combinations is the same as the one used in the parameter file for choosing coupling maps. Here are a few examples, along with what they mean. (any '#' is followed by a remark; these exact explanations are not needed in the core.txt file)::

    valid_combinations    :all    # this map can couple any combination
    valid_combinations    :same   # both members of the pair must belong to the same map.
    valid combinations    :diff   # both members of the pair must belong to different maps.
    valid_combinations    ABC:   # any pair containing at least one ABC oscillator
    valid_combinations    A: B: C: # any pair containg at least one oscillator of either map A, B or C 
    valid_combinations    A:B    # one oscillator of map A, and one of map B.
    # The above doesn't treat a pair of two A's, or two B's.

    # These two lines (read on):
    valid_combinations    A:B
    valid_combinations    B:C

    # Mean the same as this single one:
    valid_combinations   A:B  B:C


    # Each of the following lines means the same:
    valid_combinations  A:B  B:B
    valid_combinations   A,B:B
    valid_combinations   B,A:B

    # Each of these following lines means the same
    valid_combinations  A,B:B,C  A,C:D
    valid_combinations   A:B  A:C  B:B  B:C   A:D  C:D




