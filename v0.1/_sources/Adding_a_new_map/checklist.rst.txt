.. _AddMap_checklist:


#############
Checklist
#############


So, you think you've made your map, but are you truly done? This checklist is designed to make sure you've done everything.


****************************************
The corefile is complete
****************************************

If everything is well, you've followed the steps for creating your map's core.txt file. :ref:`These are the instructions for a singles map<AddMap_FileStruct_SingCore>`, and :ref:`these are the instructions for a pairs map<AddMap_FileStruct_PairCore>`. For every available keyword, you have decided whether your map needs it, and if it does, you've done your best implementing it.



****************************************
The README is present and useful
****************************************

The strength of maps is that they can be shared with other users, and combined with other maps. For this purpose (and for your own administration) it is very important to have a clear explanation of your map. Ideally, it has the following chapters/topics/points addressed (see AmideBB map for an example):

- **intended use**: This section should explain when this map can be used. These questions could guide your writing:

  - (singles map) For what use is the map developed? What kind of oscillator/chromophore is described by the map?
  - (singles map) What kind of systems can it be used for? Are there any requirements for neighbouring molecules/assemblies? Is there any requirement for the solvent?
  - (pairs map) What kind of singles can be coupled? Is the map designed for a very specific (set of) single(s), or can it work with all? Is their a certain prerequisite a single must meet before it can be treated?

- **how to use**: This section should explain how the map can be applied properly. What settings can be used, what combinations, etc.

  - (both singles and pairs) What are requirements for using the map? Can it be used together with any map, or are there certain maps that must(n't) be used with it? Why?
  - (both singles and pairs) What should the calculation chain look like? Is the map intended to be used with a certain MD package or forcefield? Will results still make sense with another force field? What kind of outputs can the map give, and for what subsequent steps is the map intended? (NISE spectral calculations)
  - (both singles and pairs) Are there any GMAP settings that must be used when using this map? For example, can both different methods of calculating electrostatics be used?

- **available parameters**: Any information on parameters for this map. Does this map have its own custom parameters available? Maybe to set certain values, or make a certain choice of model? If there are parameters, explain them! What do they do, what options are available? If you accept a number, is their a certain lower or upper bound to this number beyond which it doesn't make any sense? If you use any physical values, what are the expected units?

- **warnings that can be raised by the map**: If users of your map commonly trigger a specific GMAP error, read on. Or if your map makes use of custom code (main.py), there is a chance you've also implemented specific errors to help things run smoothly. Whatever the case, this is the place to mention the error code of the error, along with some explanation what triggers it, how/why, and how to resolve the error.



***********************************************
The references file is present and complete
***********************************************

Credit where credit is due, right? GMAP uses the references file to see for what calculations (frequency, dipole, etc) which reference should be cited for your map. That means that if someone does a calculation for their publication, GMAP helps them with what papers to mention. If your map does not have a references file, that means it is more difficult for users to remember to cite your work.

Using the custom code in the main.py file, you can sort through the references file. This allows to only use references that belong to a certain method used if multiple are available. 



***********************************************
Calculation results have been confirmed
***********************************************

So you've created a map, and it runs with GMAP without returning errors. That doesn't mean your map is correct, though! The next imporant step is to confirm whether the map indeed runs the way you think it does, and whether it runs as it should. So, this next step consists of doing that.


(single only) Does the map identify the correct molecule/atoms?
========================================================================

This should be your first thing to test. Only a few things in the core file influence this, so its the easiest one to troubleshoot if needed. This step starts with obtaining MD files of a system containing your chromophore/oscillator/single (make sure you know exactly how many!), and running *just one* frame of them through GMAP. Make sure to set the verbosity to at least 2, and go to the section "MD system analysis", and look at the report there. It should list the name of your map, along with the amount of instances found.

If the amount of singles found by GMAP does not match the number you are expecting, something went wrong. If GMAP found none, make sure to check out the "files used" section - are these the ones you were planning on using? If you use the default MD system shipped with GMAP (but leaving all other file locations the same), can it find the AmideBB and AmideSC oscillators? If both are answered with 'yes', make sure you requested the correct singles map name with the 'maps_to_use' keyword, and the atom/molecule names.

When a group truly can't be found, you'll have to look into the MD files somehow, to see what atom/residue names are used. In the case of gromacs, you could try converting a tpr/xtc to gro, as the gro file contains all names. Other MD software might have something similar, and otherwise maybe a visualization tool (vmd, pymol) might help.

If you can't find all occurrence, but some, it might be interesting to see what the difference between the two is. You can add multiple strucutres to a singles map (see AmideSC for a clear example) if needed to capture all instances.



Does the map give the correct results?
========================================================================

This is a little harder to test - you need the 'correct' answer to know this. Without it, you can compute a spectrum and see if it matches the experiment, but that also involves the map being a good model, not just the map being implemented correctly. So, preferably, you test against computational data so you can really test just the implementation.

A test like this can performed until results are good, by hand, or you can make an automated implementation like done for the AmideBB, AmideSC and ProteinAmide maps. The question then becomes, how well should the results match? This is very personal. As the amide results could be directly compared against the AIM ones, I went down to computational accuracy (thousandths of wavenumbers), but anything below a single wavenumber (at least, in IR) is not noticable in experiment.

When results don't match, there's a lot more that could be wrong than with finding singles. One option is to try to set all constants to 0 except for the gas-phase frequency - your output file should contain just gas phase frequencies. A similar thing can be done for dipoles and couplings. If those match, its good to double check whether there is no typo in the data, and whether you're using the right units. Even if you think you are, double check!

Other things to check with odd frequencies are the atoms. Even if GMAP thinks it found your molecule (and thus no errors), did it really? This is more likely to be an issue if you have multiple atoms with the same name (easier mistakes in the functional_group field), or if you don't use the 'All' keyword for specifying the used_atoms, electrostatic_atoms and local_atoms field.

If you have a main.py file and not just the core.txt file, print everything you can think of! Not just data/structures created by you, but also attributes of the GMAP-generated oscillators/map objects of your map.

In all cases, double checking everything should help. Most likely, the error is caused by a misunderstanding of something about the program. Explaining something to someone else can be a good test of your understanding of something, so consider asking for help. And if all else fails, you could always reach out to us developers!



***********************************************
Easy mistakes to make during map development
***********************************************

- Getting units scrambled
- mistaking file paths / files
- indexing wrong. Don't forget that all indexes in core.txt files are 0-based!




