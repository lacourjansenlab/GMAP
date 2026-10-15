.. _AddMap_FileStruct_SingCore:

#############
Core.txt file
#############

(this applies to singles maps. If you are looking for pairs maps instead, go to :ref:`the pairs version of this page.<AddMap_FileStruct_PairCore>`)

This file forms the basis for any map. It must be present in all cases. It explains what the oscillator looks like, and what parts to treat, and the corresponding map coefficients. It works somewhat similar to how one creates input parameter files. All available keywords will be listed here, with an explanation.

Any keyword not given here can still be used, but all information given for that keyword is not being used by the program. It is, however, still saved, and can be accessed by the map's code in main.py.

.. hint::
    This page is written to be read as a tutorial. The explanation for parameters lower down will rely on knowledge on parameters further up - so make sure you are at least somewhat familiar with them. The ideal scenario is that you can create your own map while reading this document!

.. note::
    The variety of map structures in the spectroscopic community is too large to catch all of it in a single format like core.txt. That is what the main.py file is for: you can create additional behaviour. Maybe you want the choice for a parameter in core.txt to depend on a parameter in the parameters.ref file, or maybe you need other more complicated behaviour. In those cases, it might feel pointless to give a definition here for mandatory parameters. However, it can be invaluable to pick illustrative examples in this file, even if they're overwritten later by main.py. 

.. note::
    Because of this variety, it is possible that a pair map needs to know additional things about an oscillator (encoded by a single map). If they request so, this file might need one or more additional keywords to function appropriately.



**********
can_output
**********

*Mandatory parameter*

This parameter explains what kind of outputs this map can be used for. Among others, the program can use a map to calculate a molecules frequency or dipole. A map doesn't need to specify keywords mandatory to output types not mentioned here. Similarly, when a user requests use of a map for an output it doesn't mention, the program will automatically stop and request a change from the user. 
The available options here are the same as the available options for :ref:`the input parameter 'output_data'<UserGuide_page_parameter_overview_output_data>`.


****************
functional_group
****************

*Half-mandatory parameter*

Either this parameter, or functional_group_file must be present.

This parameter explains what a functional group looks like. A functional group is defined as one (or more) residue(s) of a certain name, containing atoms of certain names. The full syntax will be explained using a series of examples, that will, one by one, introduce more elements.


Step 1 - An oscillator on a single residue
==========================================

A good example is the definition for amide groups in the sidechains of proteins. An amide group consists of a C=O pair (carbon bonded to oxygen with a double bond) and a N-H pair (nitrogen bonded to hydrogen with a single bond), with the carbon and nitrogen being bonded together.

In proteins, there are only two types of residue that can contain an amide group in the sidechain. These are named GLN and ASN in most MD simulations. As some methods on amides require to know also the carbon that the previously mentioned carbon atom is bonded to, and both hydrogens on a nitrogen, we can say that an amide group in the sidechain consists of a carbon, a C=O pair, and a NH2 group.

Most MD packages attempt to give each atom a unique name. This then means that in an ASN residue, the atoms mentioned now have the following names: CG and OD1 for the C=O pair, CB is the carbon bonded to CG, and ND2, HD21, HD22 for the NH2 group. If you find all 6 of these atom names in a residue named ASN, you can be certain that you found a ASN-type sidechain amide group. We can explain this geometry to the program as follows::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22

Here, we say that the group consists of a single residue, named ASN. It consists of 6 atoms with the names CG, OD1, CB, ND2, HD21 and HD22. Similarly, the GLN amide will look like this::

    functional_group        [GLN]    CD  OE1  CG  NE2  HE21  HE22


Step 2 - An oscillator on multiple residues
===========================================

One of the tests for the oscillator selection was the cysteine bridge. Normally, a protein chain is a single, unbranched string of aminoacids. These aminoacids are chemically (covalently) bonded. A protein can consist of multiple chains, but they are generally held together through non-covalent bonds and/or interactions (vanderwaals forces, hydrogen bonds, dipole-dipole interactions, pi-pi stacking). One big exception to all this, is the cysteine bridge. It forms between two cysteine residues that happen to be close in space due to a bend in the chain. This means that a cysteine residue is the only one that is covalently bonded to three other aminoacids - two just like normal, and a third bond 'at the top', bonded to another cysteine.

The two atoms that share the bond are both called 'SG', each belonging to a different residue (both of which are named CYS in the MD simulation). Lets say that, to identify one of these cysteine residues, we need to also need to find the CB atom a SG is bonded to, as well as the C, CA and N that form the backbone. In that case, the definition would become::

    functional_group   [CYS]   C CA N CB SG

While we can find a single cysteine residue like this, it doesn't guarantee that this specific residue is indeed bonded to another one. To identify the bridge, therefore, we need to have two of these present. We add a second residue like this::

    functional_group   [CYS] C CA N CB SG  [CYS] C CA N CB SG

Now, there are two residues. All atoms that belong to the 'first' residue must be mentioned after the first residue-itentifying square brackets. Then, we start the second one, with all required atoms with it. Done, right?

Wrong. There is no indication of the actual bond yet. We only indicated that the group consists of two residues, but in this format, they can be meters apart. Whenever a group consists of more than one residue, we have to indicate how the given residues should be bonded. All residues should be bonded together, but there are no rules as to what residues should be bonded to which others, and in which order they should be given.

In this case, we only need a single bond - we need to indicate that the two sulfur atoms are bonded. Lets call our bond '1' (any index will do). We have to label the atoms that are bonded by bond 1 with a 1::

    functional_group   [CYS] C CA N CB SG(1)  [CYS] C CA N CB SG(1)

While a group of n residues (including a single residue) must contain at least n-1 bonds, it may always contain more. If you want, you can indicate each and every bond present - bonds don't have to be between different residues.

However, checking for more and more bonds takes time, and thus results in a slower execution of the program. We therefore advise to only specify the bonds that make this molecule different from another one, as well as the bonds that bind the residues together.

An atom may take part in multiple bonds, but a single bond identifier can only ever be used for 2 atoms. See this example of cyclopropane, where we don't specify the hydrogens::

    functional_group   [CPR] C1(1,2) C2(1,3) C3(2,3)

If an atom takes part in multiple bonds, all bonds are listed within the parentheses, separated by only commas. Don't use any whitespace within these parentheses!


Step 3 - multiple choices of names
==================================

Depending on the naming scheme used by the MD package and/or forcefield used to generate the input for GMAP, it can happen that one specific atom kind can have multiple names. Similarly, a given group of atom names can occur in multiple different residues. Take the amide backbone map, for example. The amide itself is the same as that in the sidechain (see step 1), but now it is part of the backbone itself - if two aminoacids bond together, the resulting bond between them is an amide. A common naming scheme for the atoms taking part in this bond are C, O, N and H. The C and N are bonded to a carbon, after which the following amide starts. This 'in-between' carbon is often called c-alpha (CA), and the sidechain is bonded to it. This means the amide is spread over multiple residues::

    functional_group   [prot] C O  [prot] N H

Here 'prot' is used to refer to any protein aminoacid. However, not a single residue will actually be called 'prot' - we need to list the options. Imagining a world where only 3 aminoacids exist (ASN, GLN, CYS), this definition would become::

    functional_group   [ASN,GLN,CYS] C(1) O CA  [ASN,GLN,CYS] N(1) H CA

Now, for the first residue, we are looking for a residue that has one of the three listed names, and all the atoms present. It must be bonded through an amide bond to another residue which must have one of the listed names. Any combination is allowed. Note how there are no spaces within the bracket!

Finally, for atom names, they can be varied in the same way as residue names. Consider this imaginary oscillator::

    functional_group   [x,y] A,B E(1)  [y,z] F(1) G,H

All of the following (linear) molecules are allowed: (residue names of each atom are given in parentheses, bonds using hyphens)

| A(x)-E(x)-F(z)-H(z)
| B(x)-E(x)-F(y)-H(y)
| B(y)-E(y)-F(y)-G(y)

In fact, as there are 4 parameters with 2 options, there are 2^4 = 16 total possible combinations. Each of the combinations found will be recognized as an oscillator, even if it shares some atoms with another oscillator found using the same map!

If you don't want all possible combinations, you will have to specify multiple lines. If, for example, the residue names are coupled (i.e. residue x may only bind to one named y, not z, and the one named y may only bind to one named z), it'd look like this::

    functional_group   [x] A,B E(1)  [y] F(1) G,H
    functional_group   [y] A,B E(1)  [z] F(1) G,H


Step 4 - multiple atoms with the same name
==========================================

While within the protein community it is standard to make sure that every atom within a residue has a unique name, this is not necessarily the case for all systems. Especially if a single residue gets large, it might be impractical to have unique atom names only. So, how do we specify which atom to select when there are multiple of the same name?

As a rule of thumb - within a residue, the first atom with the given name is chosen. If the same name occurs again, the next atom with the given name is picked. Lets illustrate using bonds, and ethene:

.. code-block:: text

    H11        H21
      \       /
       C1 = C2
      /       \
    H12        H22

This molecule is saved in a topology file like this:

.. code-block:: text

    ix   name  resname
    0    C     ETE     # This is C1
    1    H     ETE     # This is H11
    2    H     ETE     # This is H12
    3    C     ETE     # This is C2
    4    H     ETE     # This is H21
    5    H     ETE     # This is H22

Then, the following choice for functional_group would work::

    functional_group   [ETE]  C(1,2,3) H(2) H(3) C(1,4,5) H(4) H(5)

But this query would not find a match::

    functional_group   [ETE]  C(1,2,3) H(4) H(5) C(1,4,5) H(2) H(3)

The first would work, but not the second, as the first atom, C would be the first atom of name C found in the residue named ETE. This would be the one labelled C1 in the drawing. It is bound to H11 and H12 in the drawing - these will become the first and second occurence of 'H' in functional_group, respectively. Therefore, When saying the first occurrence of C should be bound to the third and fourth occurrence of H (as in the second example), no matches will be found.


Bonus - counting atoms
======================

Some other parameters link back to the definition given for this parameter. They often use the indices here, to denote certain atoms. When counting, the residue names are ignored, only atoms are counted. As an example, lets count for some of the examples above::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
                                     0   1    2   3    4     5

Thus, to select the oxygen atom, you would use 1. For selecting the nitrogen, 3.

Some more examples::

    functional_group   [CYS] C CA N CB SG(1)  [CYS] C CA N CB SG(1)
                             0 1  2 3  4            5 6  7 8  9

::

    functional_group   [x] A,B E(1)  [y] F(1) G,H
                           0   1         2    3

    functional_group   [y] A,B E(1)  [z] F(1) G,H
                           0   1         2    3

This means that every definition of a functional_group starts counting at 0. The program assumes different definitions to refer to the same structure, but slightly different names. A good example for this is the amide sidechain - both cases have the same elements with the same bonds, but slightly different names.


*********************
functional_group_file
*********************

*Half-mandatory parameter*

This parameter can be used instead of the parameter functional_group.

If an oscillator becomes really big, it might not make sense to define it on a single line as with the parameter functional_group. For those systems, it is an option to instead use a separate file. This file can be linked using the parameter functional_group_file::

    functional_group_file    funcgroup.txt

.. code-block:: text
    :caption: Contents of funcgroup.txt

    newstruct     # flag to indicate a new structure
                  # blank lines are fully optional
    [ASN]         # name of the residue. If multiple options, separate by a comma

    CG            # name of atom that will get index 0 in the array. If multiple, separate by comma
    OD1           # name of atom that will get index 1 in the array
    CB            # index 2
    ND2           # index 3
    HD21
    HD22


    newstruct

    [GLN]

    CD
    OE1
    CG
    NE2
    HE21
    HE22

In this file, the hashtag serves as a marker that anything after it (on that line) should be ignored. Empty lines are ignored, too, but might aid readability.

Basically, the language in this file is the same as that for functional_group, with the following changes:
- Where functional_group uses a new line for each allowed structure, the separate file uses the marker 'newstruct'. It must be on a separate line, indicating that the lines after will contain the next definition.
- Where functional_group separates the different names using whitespace, this file puts each on a new line. If there's multiple names for a single atom (or residue), they remain comma-separated on a single line.


**********************
functional_group_bonds
**********************

*Optional parameter*

This parameter allows to specify a bond without having to add it with parentheses in the notation for functional_group. If there are multiple definitions for functional_group, the bonds specified here will be applied to all of them. They can also apply to all definitions within the file defined using functional_group_file.

Bonds can be specified by giving the indices of the two atoms that should be bound, following the count of the parameter functional_group. For example, the following two definitions are identical (the '#' is an escape character - the program doesn't look at any information after it on that same line):

.. code-block:: text
    :caption: From the map AmideBB (with simplified residue names).

    # does not cover prepros
    functional_group [anyprot] N CA C(1) O [anyprot] N(1) H CA C

    # pre-prolines!
    functional_group [anyprot] N CA C(1) O [PRO] N(1) CD CA C


.. code-block:: text
    :caption: Alternative version, gives the same result as the block above.

    # does not cover prepros
    functional_group [anyprot] N CA C O [anyprot] N H CA C

    # pre-prolines!
    functional_group [anyprot] N CA C O [PRO] N CD CA C

    functional_group_bonds  2-4

Multiple bonds are separated using whitespace, again, two identical examples:

.. code-block:: text
    
    functional_group   [CPR] C1(1,2) C2(1,3) C3(2,3)


.. code-block:: text
    
    functional_group   [CPR] C1 C2 C3
    functional_group_bonds  1-2 2-3 1-3


**********
used_atoms
**********

*Mandatory parameter*

.. attention::
    This parameter uses indices. It filters through the 'functional_group' information, so the zeroeth atom of that line is selected here by index 0. All other indexing parameters take from the information presented here.

The purpose of any map is to define how to calculate certain properties for certain oscillators. For this, it is important that it is very clear what the oscillator is (or looks like), as defined by functional_group. However, not all atoms required for uniquely identifying an oscillator are actually needed for calculating its properties. This parameter defines what atoms are actually needed for the further calculations. For every oscillator, the atoms listed here are saved, so they can be used/accessed later for calculations. That means that if you need any property of any atom at any point, that atom should be part of this list.

Common reasons for adding an atom here might include:
- Wanting to calculate electrostatic properties for this oscillator, like the potential.
- Needing its position for, for example, defining the position, direction or magnitude of the dipole
- Needing to know its index to, for example, figure out if multiple oscillators of the same type are bonded (like figuring out which AmideBB oscillators are next to eachother in a single chain)

In short, any definition for any property (whether given in the core.txt file, or in main.py) can find any atom through this list. Mostly, a specific atom will be found by taking the nth atom in this list.

So, how do we define it? You give a list of the indices in functional_group of the atoms that you'd like to add. For example::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21

Or, if you want a completely different order of atoms::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              4 0 3 1   # HD21, CG, ND2, OD1

In this case, the zeroth atom in used atom will have the same name as the zeroeth atom in functional_group, its name will be CG. Similarly, the twoeth atom in used_atoms is defined to be the threeeth atom in functional_group, so its name will be ND2.

.. hint::
    Most programming languages count starting from 0. Therefore, referring to an item as the 'first' can get confusing - we associate first with 1, while it will actually be called 0. This is why a different set of names is often used for counting. You can say that the first letter of the alphabet is a, but you could also say that the zeroeth letter is a. alphabet[1] is b, so the oneth letter of the alphabet is b.

While the order of atoms in the definition of functional_group has to follow some rules (all atoms pertaining to a single residue must be grouped, multiple atoms of the same name will follow the same order as found in the topology file), the definition here does not. Here, you should pick an order that makes the most sense to you - the order here is what is used everywhere else in the map!

Additionally, some functional groups may be quite lengthy, and writing down each individual integer for each individual atom may be cumbersome. For such cases, it is useful if the user can select some range to be included rather than writing out all of the integers manually. This can be done easily by inserting a hyphen '-' between the two integers for which the range is to be defined. For example::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0-3 5   # CG  OD1  CB  ND2  HD22

This specific case does not include a long list of atoms in the functional group, but the ranges can still be useful here. In this case the used_atoms list will result to be 0 1 2 3 5.

In case that you would like to include the whole functional group, you may also simply write down "All"::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              All   # CG  OD1  CB  ND2  HD21  HD22

********************
electrostatic_choice
********************

*Mandatory parameter*

While some maps only need to know the electrostatic potential at certain points, others need to know the field or gradient. As it is significantly more expensive to compute the electric gradient than it is to compute the electric field, which in turn is significantly more expensive than the potential alone, it is valuable to specify which of these are actually needed. There are four options::

    electrostatic_choice    V   # only calculate the potential

::

    electrostatic_choice    E   # calculate the potential and the electric field

::

    electrostatic_choice    G   # calculate the potential, the electric field, and the gradient

::

    electrostatic_choice    None  # No elecctrostatic properties should be computed.

*******************
electrostatic_atoms
*******************

*Half-mandatory parameter*

.. attention::
    This parameter uses indices. It filters through the 'used_atoms' information, so the zeroeth atom of that line is selected here by index 0.

This parameter is not needed if electrostatic_choice is set to None.

Many maps need to know what the electrostatic potential, electric field, and/or electric gradient values are at the position of certain atoms. For example, based on the potential felt by different atoms in an oscillator, you can deduce at what frequency it absorbs light. This parameter defines at which atom's positions the electrostatic properties should be calculated. **The atoms are selected from used_atoms.** Lets look at the amide sidechain example::
    
    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N

Here, we say we want to know the electrostatic properties on the zeroeth and twoeth atoms in used_atoms, which in turn are the zeroeth and threeeth atoms in functional_group - C and N.

.. hint::
    Using ranges or "All" is also allowed when defining this property, but beware that the selection is defined with respect to the used_atoms list, rather than the functional_group list.

While it is very common for a map to need these properties, it is not universal. If these properties are not needed, instead, you say this::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     None


***********
local_atoms
***********

*Half-mandatory parameter*

.. attention::
    This parameter uses indices. It filters through the 'used_atoms' information, so the zeroeth atom of that line is selected here by index 0.

This parameter is not needed if electrostatic_choice is set to None.

Calculating the electrostatics for an oscillator is involved. Not all atoms will contribute to the electrostatic environment of the oscillator - most notably, the atoms of the oscillator itself.

The program is naive in calculating elecctrostatics - every atom within range can and will contribute to the elecctrostatics, unless it is specifically excluded. This parameter allows for excluding - any atoms mentioned here will be assumed part of the oscillator, and not contribute to the elecctrostatics. The atoms are selected from used_atoms. Lets look at the amide sidechain example::
    
    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4 5   # CG OD1 ND2 HD21 HD22
    local_atoms             0 1 2 3 4

Here, we say we dont want to include the atoms in used atoms, through giving the index of all five separately.

.. hint::
    Using ranges or "All" is also allowed when defining this property, but beware that the selection is defined with respect to the used_atoms list, rather than the functional_group list.

It might happen that a map is more complex. If a mapping would like to exclude more atoms, the recommended method is to add these to used_atoms. If the exclusion is variable (might be different for different oscillators), the local_ix of the separate oscillators must be changed manually. This can be done in main.py, the recommended place is within GM_post_init(). 


*****************
type and xyz_uvec
*****************

*Mandatory if electrostatic_choice is set to E or G*

.. attention::
    These parameters use indices. They filter through the 'used_atoms' information, so the zeroeth atom of that line is selected here by index 0.

When applying maps, symmetry must be taken into consideration - If we rotate all atoms in the simulation such that (in cartesian coordinates) x becomes y, y becomes z, and z becomes x, the frequency of any oscillator shouldn't change. If the oscillator is flat and lies in the xy plane, mirroring through this plane (z becomes -z) shouldn't change anything either.

To enforce this symmetry, most maps work in local coordinates instead of cartesian. These local coordinates are just a rotation of cartesian. Usually, certain bonds are selected to define the direction of the axes. This means that after the electrostatic properties are calculated, they must be rotated to lie along the correct axes. The parameters type and xyz_uvec are used to define what kind of rotation is needed.

type
======

There are two options here::

    type   linear  # for linear oscillators like CO2 or azide

::

    type   standard  # for all others


.. _map_defining_xyz_uvec:

xyz_uvec
========

These are actually 3 parameters: x_uvec, y_uvec and z_uvec. If ``type`` is set to ``linear`` only one of the three must be provided, otherwise, two. 

As an explanation, lets again use the amide as an example. It is conventional for amide mappings to have their x axis be defined pointing from C to its double-bonded O, whereas the y axis is defined by the C-N bond. In other words, the x vector is found by subtracting the position of the C atom from that of the O atom. This will make our map look like this::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C

We're basically just telling GMAP to subtract the position of the zeroeth atom in used_atoms from that of the oneth atom in used_atoms. The program knows to normalize.

.. note::
    Those familiar with MD simulations will notice an issue here: the atoms live in a pacman universe. This means that if an atom moves (for example) too much into the x direction, it'll be moved all the way to the other side. How much is too much, is defined by the periodic boundary conditions (PBC). Therefore, it might happen that although the atoms are still close together, the edge of the box passes in between them, so their saved coordinates are quite far apart. GMAP takes this into account, and the vectors are calculated properly. See :ref:`Theory_page_PBC` for how this is done.

You can do many more things than just subtract - you can add points, or take the midpoint between two. Here's another example::

    x_uvec     ((1-0) + (2-0))/2.0  # takes the average between two vectors

Here, we need to divide by 2, but we don't want the program to mistake the number 2 by the position of the twoeth atom. To make the distinction - integers (numbers without a decimal point) are always interpreted to mean 'the position of the atom with index ...', while floats (numbers with a decimal point) are always interpreted to mean 'just this number'.

Any operation between two vectors can be performed (for those more experienced with python/numpy, you can even access numpy functions - ``x_uvec   np.cross((1-0), (2-0))`` does what you'd expect it to), but do be aware that all calculations are performed in box-coordinates, and not cartesian coordinates. This means that two vectors might not have the same angle, nor will they have the expected length. If this is an issue for your map, you can use a custom function in main.py instead.

For linear oscillators, this is enough: only one vector needs to be defined. The linear nature means that the other two directions should be equivalent, for the second direction, an arbitrary vector orthogonal to the first is chosen. The third is taken to be the cross product from the other two. For all other oscillators, we need to still define a second::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C
    y_uvec                  2-0

While the first vector could be taken at face value, the second cannot, as the two vectors must always be orthonormal. Therefore, GMAP does the following:

- Start by computing the first vector given (x in the example), in box coordinates.
- Transform the first vector to cartesian coordinates, and set its length to 1.
- Compute the second vector as given (y in the example), in box coordinates.
- Transform the second vector to cartesian coordinates, and subtract its projection along the first vector. In other words, in cartesian coordinates, of the second vector, leave only the part that is perpendicular to the first.
- Set the length of the second vector to 1.
- Finally, in cartesian coordinates, take the cross product of the first and second vector to give the third.


***************
r_pos and r_vec
***************

*Mandatory if can_output includes any of the following: ham, ene, dip*

.. attention::
    These parameters use indices. They filter through the 'used_atoms' information, so the zeroeth atom of that line is selected here by index 0.

When calculating the frequency at which an oscillator absorbs, we're usually building a hamiltonian. Such a hamiltonian is used for further spectroscopic calculations, which usually involve coupling. Regardless of whether the coupling between oscillators is explicitly calculated by GMAP, or whether it is done by a follow-up program, these calculations usually rely on dipoles. There are two important components to a dipole. First are the magnitude and direction of a dipole - the dipole vector. The second is the location of the dipole.

These two are specified using the parameters r_vec (the dipole vector) and r_pos (the position of the dipole). Specifying them works the same as specifying xyz_uvec::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C
    y_uvec                  2-0   # the part of N-C orthogonal to O-C
    r_vec                   1-0   # points along CO bond
    r_pos                   0     # vector lives on the carbon atom.

Just as with xyz_uvec, the calculations performed for r_vec and r_pos do take the periodic boundary conditions into account. :ref:`This page<Theory_page_PBC>` shows you how.

The vector found for r_vec will be normalized - its purpose is solely to indicate a direction.


*************
VEG_reference
*************

*Mandatory if electrostatic_choice is* **not** *set to None*

.. attention::
    This parameter uses indices. It filters through the 'used_atoms' information, so the zeroeth atom of that line is selected here by index 0.

Most mappings depend on some electrostatic property on some position(s). These properties are calculated by the program. While these electrostatic properties are dependent on all atoms around, the atoms closest by have the largest impact. Therefore, a lot of computational time is saved by only considering the atoms within a certain radius. But, within a certain radius of what? Thats what this parameter encodes. Of course, the center of this sphere of charges is very likely to be somewhere within the molecule considered, but exactly where can differ. This keyword lets you specify the exact point where the sphere should be centered. There are three different ways of doing so:


position
========

Defining the position works much the same as defining r_pos, where you determine this point using some atom positions::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C
    y_uvec                  2-0   # the part of N-C orthogonal to O-C
    r_vec                   1-0   # points along CO bond
    r_pos                   0     # vector lives on the carbon atom.
    VEG_reference           position 1  # at the position of the oxygen atom

Any kind of position determination is possible. Considering the above example::

    VEG_reference           position (0 + 1) / 2.0

This way, we define the position to be the average position of atoms 0 and 1, or, in other words, the position is halfway between the carbon and oxygen atoms.


CoM
===

Very often, this kind of sphere of charges is centred around a certain center of mass. This parameter simply lists a group of atoms, whose center of mass defines the center of the sphere of charges. The indices are compared to used_atoms::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C
    y_uvec                  2-0   # the part of N-C orthogonal to O-C
    r_vec                   1-0   # points along CO bond
    r_pos                   0     # vector lives on the carbon atom.
    VEG_reference           CoM  0 1 3 4 5

In this example, the sphere is centered on the center of mass of the carbon, oxygen, nitrogen and two hydrogen atoms.


residues
========

Some maps are defined in an even simpler way - the sphere is centered on the center of mass of the entire residue the oscillator is a part of::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C
    y_uvec                  2-0   # the part of N-C orthogonal to O-C
    r_vec                   1-0   # points along CO bond
    r_pos                   0     # vector lives on the carbon atom.
    VEG_reference           residues 0

What happens here is a little bit more involved: the index provided is of an atom, just as with the 'position' and 'CoM' options. The program then checks which residue this atom belongs to. Then, the center of mass of this residue is found.

If multiple atoms are given, then for each atom, the residue is found. This allows to add the atoms of multiple residues together (for oscillators that live on multiple residues). If multiple atoms are given that all belong to the same residue, that residue gets more 'weight' - it is _not_ the case that 'extra' atoms of the same residue are ignored.


*******************
assume_length_units
*******************

| *optional parameter*
| *(options: angstrom, bohr. Default: angstrom)*

The program assumes (by default) that maps assume length to be specified in angstrom, and define their constants accordingly. However, this might not be true for all maps. If your map uses bohrs instead, use this keyword to indicate this.

If you use different units, you can do the unit conversion yourself using the function 'post_init()' in the map main.py file.

.. note::
    There are many ways to indicate angstrom and bohr. While the ones mentioned are preferred, many other alternatives are available. The detection is case insensitive.

    angstrom
        Angstrom, ang, Ang, a, A, aa, AA
    
    bohr
        Bohr, a0, A0, au, AU

*************
multiply_freq
*************

| *optional parameter*

.. warning::
    This parameter should only be used for unit conversions, not for other additional factors, like the dielectric constant. When a system contains a dielectric constant different from 1, users running the calculation should use the parameter 'dielectric_constant' in the input parameters file instead of a map implementing it itself.

There might be some unit conversions that can't be covered by the keyword 'assume_length_units'. In some of those cases, this parameter could help:

The value supplied here (a whole or decimal number) will be multiplied with all the values in the files specified using 'frequency_data_file_linear'  and 'frequency_data_file_quadratic'. This could be useful for a factor like 1/(4 pi epsilon).

If preferred, this keyword also accepts certain constants. All constants available in the numpy and scipy constants library (e.g. np.pi and sp_con.pi) are available, as well as all constants in the GMAP constants module. When using constants from sp_con, please be aware of the difference between the basic constants (e.g. ``sp_con.hbar``) and the 'physical_constants' dictionary (e.g. ``sp_con.physical_constants["Bohr radius"][0]``). The latter requires the additional ``[0]`` to have a number. An overview of all available constants:

- `Constants available in numpy <https://numpy.org/doc/stable/reference/constants.html>`__ . Please note that numpy is available as ``np``.
- `Constants available in scipy constants <https://docs.scipy.org/doc/scipy/reference/constants.html>`__ . Please note that scipy constants is available as ``sp_con``.
- `Constants available in GMAP constants <AddMap_FileStruct_GMAPconstants>`. Please note that this module is available as ``GM_con``.



*********
ham_first
*********

| *optional parameter*
| *(options: true, false)*

.. tip::
    This keyword only makes a difference when you have custom code in the main.py file. To be even more precise: if any custom code in the main.py file makes active changes to the ``map_`` or ``oscillator`` objects during either ``GM_calculate_frequency`` or ``GM_calculate_dipole``.

    If your map does not (need to) do that, you can safely skip this one.

The program assumes (by default) that the diagonal hamiltonian elements (i.e. the energy / absorbtion frequency) should be calculated first for a map. This means that if the map saves any additional attributes to the ``map_`` or ``oscillator`` objects during the energy calculation, these are accessible during the dipole moment calculation.

If, however, you need the reverse, this keyword should be set to false. Then, the dipole moment will be computed (and saved) first, and any attributes saved to the ``map_`` or ``oscillator`` objects during the dipole moment calculation are accessible during the frequency calculation.


****************
dipole_gas_phase
****************

*Mandatory if can_output includes any of the following: ham, ene, dip*

As illustrated under 'r_pos and r_vec', the dipole moment of oscillators is a key property for the program. While the information in that section is used to give the direction of the dipole moment vector (and its position), it doesn't contain any information on its magnitude. Thats what this parameter, and the parameter 'dipole_data_file' are for. This parameter specifies the (base) magnitude of the dipole moment, in Debye. If the magnitude can vary, see 'dipole_data_file'.

If this parameter is used alone (or in combination with the 'magnitude' mode of 'dipole_data_file'), you can just use a single decimal number to indicate the magnitude in Debye::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C
    y_uvec                  2-0   # the part of N-C orthogonal to O-C
    r_vec                   1-0   # points along CO bond
    r_pos                   0     # vector lives on the carbon atom.
    VEG_reference           position 1  # at the position of the oxygen atom
    dipole_gas_phase        0.32

If, instead, the parameter 'dipole_data_file' is used in 'xyz' mode, this parameter should be provided with **three** values, the gas-phase value for the x, y and z components. See the parameter 'dipole_data_file' for more information.


****************
dipole_data_file
****************

*optional parameter*

As illustrated under 'r_pos and r_vec', the dipole moment of oscillators is a key property for the program. While the information in that section is used to give the direction of the dipole moment vector (and its position), it doesn't contain any information on its magnitude. Thats what this parameter, and the parameter 'dipole_gas_phase' are for. If the magnitude of the dipole moment cannot vary, see dipole_gas_phase.

This parameter is used for defining how the dipole moment depends on the electrostatics from the environment. There are two different options; either the dipole has a set direction with the magnitude depending on the elecctrostatics, or each of the x, y and z components of the vector depend on the electrostatics separately. Each of the two options requires a slightly different file format, so this parameter is specified using two parts. First, you either specify ``magnitude`` or ``xyz`` (depending on which format), and then this is followed up by a filename (with extension) present in the same mapping directory. This file will contain the actual dependency.

.. tip::
    Each of the methods uses x, y and z directions. These are assumed local to the oscillator at the moment its dipole moment is determined (so, within a single frame), unless stated otherwise. The final dipole moment calculated by the program is in the same cartesian coordinates as the provided MD system was.


magnitude
=========

In this case, the dipole moment has a set direction (provided using the parameter 'r_vec'), with a varying magnitude. The program assumes the following formula for calculating the dipole moment magnitude:

.. math::
    magnitude = \mu_{gas} + \sum_n(V_n*c_{V_n} + \sum_i(\vec{E}_{n,i} * c_{E_{n,i}}) + \sum_i(\vec{G}_{n,i} * c_{G_{n,i}}))

Here, :math:`\mu_{gas}` is the gas phase magnitude - the magnitude in the absence of any electrostatic environment. This value is provided to the program through the parameter 'dipole_gas_phase'. :math:`V_n` is the electrostatic potential felt by atom :math:`n`, where :math:`n` loops over the atoms listed using the parameter 'electrostatic_atoms', while :math:`c_{V_n}` are the potential coefficients provided by the map. Similarly, :math:`\vec{E}_{n,i}` is the electric field felt by atom :math:`n`, in direction :math:`i` (loops over the directions provided under 'xyz_uvec'), while :math:`c_{E_{n,i}}` are the field coefficients provided by the map. In much the same way, :math:`\vec{G}_{n,i}` is the (flattened) elecric field gradient felt by atom :math:`n`, in direction :math:`i` (loops over the following combinations of directions provided under 'xyz_uvec': xx, yy, zz, xy, xz, yz), while :math:`c_{G_{n,i}}` are the gradient coefficients provided by the map.

So, how does the map provide these coefficients? That is what the file specified through this parameter is for. The file contains a grid of coefficients, with a row for each atom listed under 'electrostatic_atoms', and at most 10 columns. The first column contains the potential coefficients, the next three contain the field coefficients (in order x, y, z), and the last six contain the gradient coefficients (in order xx, yy, zz, xy, xz, yz).

If you specified 'G' as the choice for the parameter 'electrostatic_choice', all 10 columns must be present. They may contain zeros, but they must be there. If you specified 'E' as the choice for the parameter 'electrostatic_choice', the first 4 columns are mandatory. Any extras will be ignored. Similarly, if you specified 'V' as the choice for the parameter 'electrostatic_choice', only the first column must be present, and all others (if present) will be ignored.


xyz
====

In this case, the direction of the dipole moment can vary. Therefore, instead of defining a fixed direction with a magnitude depending on the electrostatic environment, this method allows each of the x, y and z components of the dipole moment to depend on the electrostatic environment. These components are in local coordinates (specified using the parameters 'xyz_uvec' - see that section), and at the end of the calculation returned to the same cartesian coordinates as the MD inputs had the positions defined in.

The formula for calculating these components is the same as the one listed above, for the magnitude. The only difference is that the formula will be executed three times, once for each of the vector components. That also means that there are many coefficients needed: the amount of electrostatic_atoms * 10 (potential + 3 electric field + 6 gradient) * 3 (x, y and z).

The file providing these coefficients looks exactly the same as the one explained above, but with one exception: we need triple the information. The coefficients are provided in blocks - so you first get all coefficients for the x-component (a single row for each atom in electrostatic_atoms), then all coefficients for the y component, and finally, all for the z component.

The three blocks can be separated by one or more empty lines, and '#' can be used to make comments. Anything after a '#' will be ignored, so you can make a header line (to detail the columns), or add a note after each row to know what atom they belong to.

Just as with the 'magnitude' choice for this parameter, the amount of columns that are actually required depends on the choice for electrostatic_choice.



*******************
frequency_gas_phase
*******************

*Mandatory if can_output includes any of the following: ham, ene*

Similar to dipoles, the oscillation frequency of oscillators is a key property for the program. This parameter specifies the (base) oscillation frequency, typically the one measured when the oscillator in question is in the gas phase. The units used are wavenumbers, and it is provided using a single decimal number, much like the dipole_gas_phase.

If the frequency can vary, you should also make use of the parameter frequency_data_file_linear (for a linear dependence) or frequency_data_file_quadratic (for a dependence on the square of the potential/field/gradient).

A basic example with just the gas phase::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    electrostatic_atoms     0 2  # C and N
    electrostatic_choice    E
    type                    standard
    x_uvec                  1-0   # O-C
    y_uvec                  2-0   # the part of N-C orthogonal to O-C
    r_vec                   1-0   # points along CO bond
    r_pos                   0     # vector lives on the carbon atom.
    VEG_reference           position 1  # at the position of the oxygen atom
    dipole_gas_phase        0.32
    frequency_gas_phase     1400


**************************
frequency_data_file_linear
**************************

*optional parameter*

This parameter can be used in conjunction with the parameter frequency_gas_phase, and is intended for when the frequency depends on the electrostatic environment.

.. tip::
    This parameter uses x, y and z directions. These are assumed local to the oscillator at the moment its frequency is determined (so, within a single frame), unless stated otherwise.

The formula/method used for calculating the dependence of frequency on the elecctrostatic environment is very similar to that of the dipole moment:

.. math::
    frequency = \omega_{gas} + \sum_n(V_n*c_{V_n} + \sum_i(\vec{E}_{n,i} * c_{E_{n,i}}) + \sum_i(\vec{G}_{n,i} * c_{G_{n,i}}))

Here, :math:`\omega_{gas}` is the gas phase frequency - the frequency in the absence of any electrostatic environment. This value is provided to the program through the parameter 'frequency_gas_phase'. :math:`V_n` is the electrostatic potential felt by atom :math:`n`, where :math:`n` loops over the atoms listed using the parameter 'electrostatic_atoms', while :math:`c_{V_n}` are the potential coefficients provided by the map. Similarly, :math:`\vec{E}_{n,i}` is the electric field felt by atom :math:`n`, in direction :math:`i` (loops over the directions provided under 'xyz_uvec'), while :math:`c_{E_{n,i}}` are the field coefficients provided by the map. In much the same way, :math:`\vec{G}_{n,i}` is the (flattened) elecric field gradient felt by atom :math:`n`, in direction :math:`i` (loops over the following combinations of directions provided under 'xyz_uvec': xx, yy, zz, xy, xz, yz), while :math:`c_{G_{n,i}}` are the gradient coefficients provided by the map.

So, how does the map provide these coefficients? That is what the file specified through this parameter is for. The file contains a grid of coefficients, with a row for each atom listed under 'electrostatic_atoms', and at most 10 columns. The first column contains the potential coefficients, the next three contain the field coefficients (in order x, y, z), and the last six contain the gradient coefficients (in order xx, yy, zz, xy, xz, yz).

If you specified 'G' as the choice for the parameter 'electrostatic_choice', all 10 columns must be present. They may contain zeros, but they must be there. If you specified 'E' as the choice for the parameter 'electrostatic_choice', the first 4 columns are mandatory. Any extras will be ignored. Similarly, if you specified 'V' as the choice for the parameter 'electrostatic_choice', only the first column must be present, and all others (if present) will be ignored.


*****************************
frequency_data_file_quadratic
*****************************

*optional parameter*

This parameter can be used in conjunction with the parameter frequency_gas_phase, and is intended for when the frequency depends on the square of the electrostatic environment. This dependence is not used nearly as often as the normal linear one.

.. tip::
    This parameter uses x, y and z directions. These are assumed local to the oscillator at the moment its frequency is determined (so, within a single frame), unless stated otherwise.

The formula/method used for calculating the dependence of frequency on the elecctrostatic environment can be expanded with the quadratic terms:

.. math::
    frequency = \omega_{gas} + \sum_n(V_n*c_{V_n} + \sum_i(\vec{E}_{n,i} * c_{E_{n,i}}) + \sum_i(\vec{G}_{n,i} * c_{G_{n,i}})) + \sum_n({{V_n}^2}*c_{V_n} + \sum_i(\vec{{{E}_{n,i}}^2} * c_{E_{n,i}}) + \sum_i(\vec{{{G}_{n,i}}^2} * c_{G_{n,i}}))

The symbols here still mean the same: :math:`\omega_{gas}` is the gas phase frequency - the frequency in the absence of any electrostatic environment. This value is provided to the program through the parameter 'frequency_gas_phase'. :math:`V_n` is the electrostatic potential felt by atom :math:`n`, where :math:`n` loops over the atoms listed using the parameter 'electrostatic_atoms', while :math:`c_{V_n}` are the potential coefficients provided by the map. Similarly, :math:`\vec{E}_{n,i}` is the electric field felt by atom :math:`n`, in direction :math:`i` (loops over the directions provided under 'xyz_uvec'), while :math:`c_{E_{n,i}}` are the field coefficients provided by the map. In much the same way, :math:`\vec{G}_{n,i}` is the (flattened) elecric field gradient felt by atom :math:`n`, in direction :math:`i` (loops over the following combinations of directions provided under 'xyz_uvec': xx, yy, zz, xy, xz, yz), while :math:`c_{G_{n,i}}` are the gradient coefficients provided by the map.

The map provides these coefficients just like the linear ones, in a separate file, specified using this parameter. The file contains a grid of coefficients, with a row for each atom listed under 'electrostatic_atoms', and at most 10 columns. The first column contains the potential coefficients, the next three contain the field coefficients (in order x, y, z), and the last six contain the gradient coefficients (in order xx, yy, zz, xy, xz, yz).

If you specified 'G' as the choice for the parameter 'electrostatic_choice', all 10 columns must be present. They may contain zeros, but they must be there. If you specified 'E' as the choice for the parameter 'electrostatic_choice', the first 4 columns are mandatory. Any extras will be ignored. Similarly, if you specified 'V' as the choice for the parameter 'electrostatic_choice', only the first column must be present, and all others (if present) will be ignored.


********
position
********

*Mandatory if can_output includes any of the following: pos, dbp*

.. attention::
    This parameter uses indices. It filters through the 'used_atoms' information, so the zeroeth atom of that line is selected here by index 0.

One of the available outputs of the program is positions. For each oscillator, (for each frame) a position is written to a file. This parameter allows to specify what position should be written for this oscillator to the positions file. It has no influence on the doublepos file. The syntax is the same as for defining ``r_pos`` and ``VEG_reference position``::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    position                0  # write the position of the CG atom to file.

Any kind of position determination is possible. Considering the above example::

    position                (0 + 1) / 2.0

This way, we define the position to be the average position of atoms 0 and 1, or, in other words, the position is halfway between the CG and OD1 atoms.


***************************
doublepos_0 and doublepos_1
***************************

*Mandatory if can_output includes any of the following: pos, dbp*

.. attention::
    These parameters use indices. They filter through the 'used_atoms' information, so the zeroeth atom of that line is selected here by index 0.

One of the available outputs of the program is doublepos. It is very similar to positions, except that for each oscillator, two separate positions are written to a file. These parameters allow to specify which positions should be written for this oscillator to the doublepos file. It has no influence on the positions file. The syntax is the same as for defining ``r_pos`` and ``VEG_reference position``::

    functional_group        [ASN]    CG  OD1  CB  ND2  HD21  HD22
    used_atoms              0 1 3 4   # CG OD1 ND2 HD21
    doublepos_0             0  # write the position of the CG atom to file.
    doublepos_1             2  # write the position of the ND atom to file.

Any kind of position determination is possible. Considering the above example::

    doublepos_0                (0 + 1) / 2.0

This way, we define the position to be the average position of atoms 0 and 1, or, in other words, the position is halfway between the CG and OD1 atoms.


****************
influencer_group
****************

*Optional parameter*

Lets completely shift gears now - the following parameters are more like helper-parameters for the map. This parameter is a good example. When performing a calculation, the user can specify a certain subset of atoms/residues that should be allowed to influence the electrostatic properties. It can be very useful to the user to have some preset groups they can use, but due to the generality of GMAP, it is hard to specify groups that are useful for a very large range of systems. Therefore, we decided to allow maps to specify some of these groups, as the use of a certain map helps predict what kind of system will be used.

As an added bonus, these groups can be accessed by the python code as well, so they can be used by the map itself, too.

Specifying groups here is very similar to how it is done in influencer files, see :ref:`UserGuide_page_influencer_specification` for more information on how it works in influencer files. Here an example from proteincore::

    influencer_group   prot_charged   ARG | HIS | LYS | ASP | GLU
    influencer_group   prot_polar    SER | THR | ASN | GLN
    influencer_group   prot_special_can    CYS | GLY | PRO   # cannonical 'specials'
    influencer_group   prot_hydrophobic    ALA | VAL | ILE | LEU | MET | PHE | TYR | TRP

    influencer_group   protein_cannonical    :prot_charged | :prot_polar | :prot_special_can | :prot_hydrophobic

    influencer_group   protein_extcann    ARN | ASH | GLH | HID | HIE | HIP | HSD | LYN | LYSH   # extension of the cannonicals - different protonation states.
    influencer_group   protein_extended   :protein_cannonical | :protein_extcann




************
add_corefile
************

*Optional parameter*

Some parameters for maps can be shared between multiple maps. For example, the influencer_group parameter - all oscillator maps that deal with proteins can use a proper definition of what a protein ís. Instead of having to change such a parameter in many different places, maps can 'import' a corefile - the contents of that file are appended at the bottom of the corefile that requested the addition. When adding a file, you have to specify the name (including extension) of the file. That file must then be present either within the same subfolder (Singles or Doubles) in which the directory of the map can be found, or one directory further up (the same directory as where Singles and Doubles live).


