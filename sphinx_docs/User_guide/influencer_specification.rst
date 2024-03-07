.. _UserGuide_page_influencer_specification:

######################
Specifying influencers
######################

Influencers are the atoms that are allowed to contribute to the electrostatics calculated for an oscillator. If only the main molecule is taken as an influencer, the results will be as if that molecule is in a vacuum, completely ignoring its surroundings.

Influencers are (in most cases) specified to the program as groups of residue names. How to specify these groups will be explained on this page. whatever method was used, the program always reports the selected influencers, be sure to check this selection to confirm it matches your intentions!


*************
Set operators
*************

The groups of residue names are internally handled as sets. A logical consequence of this is to also use set operators when defining these groups. The following examples should explain how these work.

Imagine a system with residues that each have a unique name. There are 4 residues in total: A, B, C and D. We can define a group named x, consisting of residue names B and D, in the following way:

``x = B | D``

Similarly, the group named y consisting of C and D can be defined like this:

``y = C | D``

Groups of atoms (as opposed to residue names) can be selected using a colon:

``B | D = :x``

The union of groups combines all entries:

``B | C | D = :x | :y``

The intersection only contains the items that are present in both:

``D = :x & :y``

The difference contains all items of the first, that don't occur in the second:

``B = :x - :y``

``C = :y - :x``

The symmetric difference contains all items that are present in either one, but not both:

``B | C = :x ^ :y``

The program has two groups hardcoded - :All contains all residue names found in the MD simulation, :None contains nothing. This allows selecting 'unknown' groups:

``A = :All - (:x | :y)``


*********************************************
Specifying influencers using influencers_file
*********************************************

The influencers_file allows the user to define different groups. Consider the following example::

    Water             SOL | WAT
    K                 K | K+
    Na                NA | NA+ | Na+
    Cl                CL | CL- | CLA
    Ions              :K | :Na | :Cl
    Solvent           :Water | :Ions

Here, a variety of different groups has been defined in a concise, structured way. However, it is not yet clear to the program what influencers the user wants. It is assumed that the user wants to use the selection saved as the group 'choice'. A simple change to the above fixes this::

    Water             SOL | WAT
    K                 K | K+
    Na                NA | NA+ | Na+
    Cl                CL | CL- | CLA
    Ions              :K | :Na | :Cl
    Solvent           :Water | :Ions
    choice            :Solvent

Now, we've indicated that we only want to consider the influence of the solvent, and explained what the solvent actually is. If, however, we would like to blacklist the solvent, it would look like this::

    Water             SOL | WAT
    K                 K | K+
    Na                NA | NA+ | Na+
    Cl                CL | CL- | CLA
    Ions              :K | :Na | :Cl
    Solvent           :Water | :Ions
    choice            :All - :Solvent

The group ':All' does not have to be defined, as it is already defined within the program itself. Mappings also have the option to create groups to aid with selections in systems they were specifically designed for. For example, the Amide maps are meant for use with proteins, so they contain the definitions for protein groups.

.. danger::
    Nothing stops you from creating a new group called 'All'. This would overwrite the predetermined group. For this reason, the group names 'All' and 'None' must be avoided at all costs! Similarly, groups defined by mappings can be overwritten in the same way.


******************************************
Specifying influencers in a parameter file
******************************************

Instead of the influencers file, the choice of influencers can also be given in a parameter file, or on the command line. In those cases, no new groups can be created, but groups already defined (either by the program, or by mappings used) can be used.

There are two ways of defining influencers, either using whitelists, or blacklists. If, for example, you only want to consider the influence of the solvent (which consists of residues named 'SOL', 'CL' and 'NA') this can be specified as ``influencers_whitelist  SOL | CL | NA``, when in the input- or default parameter file. Other set operations (``-``, ``^``, ``&``) work, too, and parentheses can be used for setting the right order. Already defined groups can be used just as in influencer files, using a colon (``:``).

If such a line includes multiple residue names and/or groups, but not a single set operator, the program assumes the union was meant. In other words, ``influencers_whitelist SOL CL NA`` does the same as the version above.

If you want to exclude specific groups instead of include them, you can use the parameter ``influencers_blacklist``. You can only use one of the four influencer-related parameters at a time.


******************************************
Specifying influencers on the command line
******************************************

Just like any other parameter that can be used in the input parameter file, the parameters for influencers can also be used on the command line. Be sure to append the last bit with ``\;``.

Please do note, however, that characters like ``|`` or ``^`` (can) have a special meaning on the command line. If you only need the union (``|``), then you can just give a list of residue names (or groups) like explained for parameter files. If you need other characters, too, you can try using escape characters.


******************************************
More complex selections than residue names
******************************************

In some cases, it might not be enough to 'just' define which types of residues should(n't) be considered. You might want to exclude some water molecules, but not others. For these cases, you can use the parameter ``influencers_select_atoms``. This parameter takes the given command, and uses it for MDAnalysis' ``select_atoms()`` function. This function should allow to make literally any selection under the sun. The full documentation of this function can be found `on the MDAnalysis documentation pages <https://docs.mdanalysis.org/stable/documentation_pages/selections.html>`__, but here are a few more simple examples to help you get started.


Selecting specific residues
===========================

``influencers_select_atoms   resnum 4-6 or resnum 10``

In this example, atoms that belong to residues with the following numbers will be selected: 4, 5, 6, 10. Just as with atoms, these ranges are inclusive, and if you want to use multiple ranges, you have to use 'or resnum' in between.


Selecting specific atoms
========================

``influencers_select_atoms    index 0 or index 2-10``

In this example, the atoms with the following indices are selected: 0, 2, 3, 4, 5, 6, 7, 8, 9, 10. Two things to note here: firstly, when using a range, the endpoint of the range is inclusive - it will be selected. Secondly, you can select multiple ranges (or single numbers) by using 'or' (and repeating the 'index' keyword). This is because any atom you select must either have the index 0, **or** it must have an index between 2 and 10. If you were to use 'and' instead of 'or', you will only select atoms that have both an index of 0, **and** have an index between 2 and 10. However, this is not possible - any atom can only have a single index. Therefore, not a single atom will be found.


Special selections
==================

Using the above methods, you should be able to select any group of atoms already. However, it can sometimes be cumbersome to determine beforehand what indices you want to include. Below are some examples that are slightly more intricate. While these options may look interesting, please do note that some queries might take a while to compute. If the calculation time becomes much longer after making a change in this parameter, that might be why.

Please also note that things like atom names can very well differ between forcefields, or MD packages used. Make sure to confirm whether the reported selection is indeed the desired one.

Not all topology files save all kinds of information about atoms. If an error occurs while parsing the string, confirm whether your requested property is stored in your file in the `MDAnalysis format overview <https://userguide.mdanalysis.org/stable/formats/index.html#topology>`__.


``influencers_select_atoms    not resname SOL and element O``

The above selects all atoms that are oxygen, but not those that are part of any residue named 'SOL'. As 'SOL' is a common name to use for solvent water, this selects all the oxygen atoms except those that are part of the solvent.


``influencers_select_atoms    not (resname SOL and element O)``

Similar to the example above, but now we select all atoms, except those that are part of residues named 'SOL', while also being oxygen. In other words, we blacklist only the oxygen atoms of the solvent.


``influencers_select_atoms    protein and (name O or name C or name CA or name N or name H or name HA)``

This selects only the atoms that are part of the backbone of a protein (those are commonly named C, O, CA, HA, N and H). It doesn't select the terminal O and/or H atoms. For the full backbone, MDAnalysis has another special keyword - use 'backbone'. (MDAnalysis is designed with proteins in mind).


``influencers_select_atoms    (resname ASN or resname GLN) and not resnum 10``

This selects all atoms that belong to a residue of the name ASN or GLN, except those that also happen to have the residue number 10. This means the 10th residue in the MD system, not necessarily the 10th residue of the name ASN or GLN.

