C8S3 map
------------
The amphiphilic cyanine dye, 3,3’-bis(2-sulfopropyl)-5,5',6,6’-tetrachloro-1,1’-dioctylbenzimidacarbocyanine, C8S3, is a pigment molecule known to form double-walled nanotubes in water.
Its extended π-system makes it a valuable component for designing functional light-harvesting materials with various high-tech and medical applications.


Intended use
------------
This map is intended for treating C8S3 molecules.
The parameters in this map are taken from the literature. 
The CHELP charge difference is taken from TD-DFT calculations of the ground and excited states.
The gas phase molecular excitation anergy value is also taken from TD-DFT calculations and/or the experimental value of the absoprtion maximum of the monomer in a methanol soluton. 
There are no specific parameters available.  


How to use
----------
This map has no specific requirements beyond a trajectroy and topology file. 
This map was tested on a GROMACS All Atom simulation (cubic box with 8 nm sides) of a dimer system solvated in water with 1:1 ratio of counterions to solute. 


Available parameters
--------------------
At this point the frequency map has no options or parameters. 
It is possible to use a different gas phase excitation energy by manually chaning the value of the *frequency_gas_phase* in the *core.txt* map file.
If the value is changed then it is the responsability of the user that made the change to adeqautely cite the source of the new value they use.


Warnings that can be raised by this map
---------------------------------------
This map is based on the accompaning .gro atom labels. 
There is no systematic naming for the atoms in the C8S3 molecule.
If another strcuture is used the user needs to make sure the atom labels correspond to those from this map. 
A .gro and .pdb structure file of the C8S3 structure used to make this map is available.