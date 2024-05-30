# Quick menu
- [General rules for code](#general-rules-for-code)
- [General code-related remarks](#general-code-related-remarks)
- [Roadmap](#roadmap)
- [wishlist](#wishlist)
- [Package structure](#package-structure)
- [notes](#notes)
- [structure/concepts of maps in/for GEM](#structureconcept-of-maps-infor-gem)
- [How GEM looks for/through parameter files to obtain runpar](#how-gem-looks-forthrough-parameter-files-to-obtain-runpar)
- [How to calculate potential (and other electrostatic properties)](#how-to-calculate-potential-and-other-electrostatic-properties)
- [Rough program flow](#rough-program-flow-gem)
- [To discuss](#to-discuss)
- [Dump section](#dump-section)
- [Old notes/goals/thoughts/etc](#old-notesgoalsthoughtsetc)



# General rules for code
- Follow the TOCM group python style guidelines (which are heavily based on PEP8), can be found [here](https://github.com/lacourjansenlab/CoffeeCodeClub/tree/master/ProgramStyle)
- Make use of comments when function of code isn't easily discernable!
- Its the modern era, we have storage space! Code does not need to be compactly written, legibility is the most important in this project
- Don't worry about efficiency/speed of a function if it doesnt take more than 1% of total calculation time. This doesn't mean we should aim for blatantly needlessly expensive code.
- Document the choices/assumptions/etc you make, so they can be put in a (dev)manual later. If it's too much to immediately write them down neatly, put them over [here](#dump-section)
- Printing should *_always_* be done with a custom print command (except when defining these), not the python default print. if you want to temporarily print something during development, use ```GMAP.src.tools.PrintTools.devprint()``` instead. It behaves _EXACTLY_ like print does, but adds a linenumber and name of file/function to the print - this way, it is easy to find it back, and remove it.
- When creating strings for printing, f-strings are the preferred method.

[back to top](#quick-menu)

# General code-related remarks
- Use pathlib! (not os)
- Leave no map in core! This means also amideBB should be decoupled from code
- After having had a look at argparse, I (KvA) will not use it for the cmdline. It doesn't quite give me what I'm looking for, and doesn't feel quite right.

[back to top](#quick-menu)

# Roadmap
This is a rough overview of the different steps (in order) that are needed to get ```GEM run``` running.
- Step 0: (Done!) Gmap interface, command prompt menu to navigate the different tools
- Step 1: (Done!) Create test suite, documentation system
- Step 2: (Done!) Parameter parsing
- Step 3: (Done!) Map parsing (maybe also already develop a map? - requires core algorithms?)
  - ?? create file like reference parameters that specifies what things a map can contain?
  - for each map, interpret the core.txt file. reject map if incomplete/wrong.
  - for each map, see if there is a main.py file. If so, import and check for completeness.
  - if incomplete, alias default functions for the missing ones.
  - write those default functions in a separate file (sourcefiles?) - This file can function for these functions much like reference parameter files work for parameters.
  - If the user requests the use of this map, throw error if map was loaded unsuccessfully.
- Step 4: (Done!) System analysis (requires map parsing for group recognition)
  - Load in system (mda universe)
  - extract 'basic' data (positions, masses, charges, etc)
  - find requested oscgroup atoms
- Step 5: Core algorithms
  - A function to calculate just potentials (perhaps multiple depending on algorithm)
  - A function to calculate potentials + fields (perhaps multiple depending on algorithm)
  - A function to calculate potentials + fields + gradients (perhaps multiple depending on algorithm)
- Step 6: (Done!) Map creation (or maybe already during parsing?)
- Step 7: Performing per-frame calculation
- Step 8: Adding extra functionality
  - Black-/whitelists - what kind of typing would they need? a new one?

Other things for GMAP
- Include AIM
- Add more functions for GEM, like
- run (current WIP) - 'just' do the intended calculation
  - (issue made) demo - like run, but for a pre-generated file (and pre-generated settings)? So user can see how the program is supposed to run, and whether there are technical issues?
  - (issue made) setup - As GEM needs different files to run (most notably inside the maps directory and the sourcefiles directory) - copy these to a target location, so the user can make their own changes (just like the installable AIM)
  - (issue made) trial - same as run, but without the perframe loop. Or, alternatively (maybe setting?), a single frame. This way, the user can see how the system will be interpreted (and get a legend for the hamiltonian, the parameters.txt, etc), and possibly a calculation-time estimate, file size estimate, etc?
  - maptest - a way for a map-developer to test whether their map is correct (the program can understand, no errors, etc) ?
  - ?? Way to output any already calculated property.

[back to top](#quick-menu)

# wishlist
- Non-cubic PBCs
- Create 'scan' functionality -> run all GEM/AIM preparations, but not the actual per-frame, just to see how the system is recognized. also, resnum info for black/whitelists (get an overview of which element in the hamiltonian corresponds to which residue number)
- Parallelization? Not if we don't expect this to make a huge difference, instead, create an embarassingly parallel example.
- Assign each (type/family of) error a code, so the user can silence (a specified amount of) them, similar to GROMACS' maxwarn parameter.
- (issue made) Print cmdline call to log file!
- (issue made) also output a 'legend' file. it would contain a description of every entry in the hamiltonian, so a user could retrace which is which.

[back to top](#quick-menu)

# Package structure
- There will be one big package (currently named GMAP). The concept of this will equal that of GROMACS. It will contain different programs/tools (GEM, AIM, other relevant projects), just like GROMACS contains mdrun, trjconv, etc.
- There will be a copy of the ['old' AIM](https://github.com/Kimvana/AIM/tree/Version-1.0-(main)) as a tool within the package. This will remain a copy, and will receive very few updates/changes to stay close to the original.
- There will be a new program in the package (currently named GEM) that is very similar to AIM, but can _also_ deal with non-IR maps. It should still be capable of treating the systems AIM was made for.

[back to top](#quick-menu)

# notes
- There should be no FILES.logdir_hc and FILES.outdir_hc
- AIM had a 6-length array: C<sub>x</sub>, O<sub>x</sub>, Ca<sub>x</sub>, N<sub>x+1</sub>, H<sub>x+1</sub>, Ca<sub>x+1</sub>

[back to top](#quick-menu)

# structure/concept of maps in/for GEM
As of writing this, this is still a work-in-progress. A (rough) sketch. Will be refined after further discussion and/or when the code develops.

(All maps can be put on a scale from 'simple' to 'complex'. Simple mappings need only a single (mandatory) file, complex ones need (many) more.)
- The program will look for one or more directories supplied under the 'maps_directory' parameter. Each of these directories contains 2 folders - one folder for single-oscillator maps, one for coupling maps.
- Each map (both simple and complex) will be its own directory, listed under either of the two previously mentioned directories.
- Each map (both simple and complex) will have a 'main' file in the directory, called core.txt. It contains the following:
  - How to identify the functional group the map is made for (AIMs extramaps called this resname+atnames) (can be a separate file)
  - What atoms are relevant (AIMs extramaps had all these in the oscarray)
  - What atoms we would like to calculate PEG for (AIM called this relevant_j)
  - Choice for PEG. For potential, electric field, gradient, indicate whether it should be calculated.
  - map constants. gas phase frequency, gas phase dipole moment, all factors to np.multiply with the PEG matrix. (and more?)
  - [optional] r_vec (to use for dipoles, useful for Thomas' type 1 and 1b systems)
  - [optional] x_uvec, y_uvec, z_uvec (to use for maps that require pEG, like Thomas' type 2 and 2b systems)
    - type 3 systems only require x_uvec
  - [optional] info for anharmonicity/polarization
  - type indicator (e.g. is the molecule linear?)
  - other data
    - bib reference(s)
    - more?
  - [optional?] What coupling methods can(not) be applied (black/whitelists)
  - [optional?] Dipole to use for dipole-dipole interactions
  - [optional] delta-q to use for tresp/TCC coupling method
  - [optional?] what coupling method to apply to interactions between oscillators of this species (in case none is given in inpar file). None should also be an option.
- Complex maps must have (are defined by having) a python script named main.py to be executed by GEM.
  - The file must contain a function that returns a dict with all the functions GEM might want to look for. By having them returned as a dict, they could also live in a different .py file, made and used by the map (or a dependency)
  - The file can contain many functions (AIM inspired - calc_freq(), pre_calc(), post_frame(), more) that GMAP will look for. If they are not present, GMAP will use the 'default' (i.e. the one used for a 'simple' map)
  - The file can also alter any of the data specified in core.txt (for example, AIM's amide map can have, depending on choice (skinner, etc) different choices for rel_j, PEG_choice, constants, and references)
  - The script should only alter data linked to the specific map (if desired), and treat all other data supplied to it as read-only.
- Complex maps can have a default/reference parameter file named parameters.ref, in case the extra code requires it (for example, amides would need to know the choice of map - skinner etc). Also specifies expected type & allowed options & whether par must be specified.

Data structures involved with maps (or just as a result of them):
- AIMs OscAts. The big np array in which each row stores the indices of the atoms relevant for that group.
  - old way - a rectangular array, all entries had to be filled. The size was known easily - 6 columns (hard coded), same amount of rows as groups detected.
  - possible new way - larger rectangular array - as many columns as the largest group detected, same amount of rows as groups detected.
    - advantage: true to the old way, one big np array is fast
    - disadvantage: what to fill in for 'missing' / unneeded items
    - disadvantage: size.
  - possible new way - list of 1D np arrays.

[back to top](#quick-menu)

# How GEM looks for/through parameter files to obtain runpar.
1. Check if GEM was called in demo-mode
2. Basic command line parse. Extract the requested job, inparfile and arguments. Check if the requested job is defined/understood. Check if the specified inparfile exists, and is a file. (don't do anything with arguments)
3. See if the arguments from the command line contain anything on sourcedir or defparfile. If so, check if format is correct, and if so, return the given choice (without checking if the given locations exist). If not, throw error and quit.
4. If command line included an input file, very simple parser to extract parameters and choices. No reading/interpretation.
5. Knowing the command line arguments, inpar and the hardcoded location for the defparfile, find out which to use, according to table below. After choice is made, check if the file exists. If not, throw error and quit.

| cmd has srcdir | cmd has defpar | inpar has srcdir | inpar has defpar | used file                          |
|----------------|----------------|------------------|------------------|------------------------------------|
| Yes            | Yes            | Any              | Any              | cwd/cmd.srcdir/cmd.defpar          |
| Yes            | No             | Any              | Yes              | cwd/cmd.srcdir/inpar.defpar        |
| Yes            | No             | Any              | No               | cwd/cmd.srcdir/FILES.refpar_hc     |
| No             | Yes            | Any              | Any              | cwd/cmd.defpar                     |
| No             | No             | Yes              | Yes              | inpar/inpar.srcdir/inpar.defpar    |
| No             | No             | Yes              | No               | inpar/inpar.srcdir/FILES.refpar_hc |
| No             | No             | No               | Yes              | inpar/inpar.defparfile             |
| No             | No             | No               | No               | FILES.srcdir_hc/FILES.refpar_hc    |
6. Find refparfile
7. parse refparfile
8. parse defparfile
9. parse inparfile (at least, start it, we can only finish after having read the maps)
10. find mapdir in cmdline > inparfile > defparfile > refparfile
11. for each map, see if there is a parameters.ref. If so, parse it.
12. now, knowing all refparfiles, finish parsing cmdline, inparfile

to do (not yet implemented)
1. now, knowing all refparfiles, finish parsing defparfile (part of step 12)
2. combine cmdline, inparfile, defparfile, refparfile choices into runpar
   1. Not just in order (fill in gaps with lower order) also take into account possible conflicts arising from this
   2. check whether requested files exist, are of correct format, etc. If a parameter is not defined in defpars, it will also not be present in refpars. If we're missing a directory, we'll use the cwd instead. If we're missing a filename, we'll use the stub-name 'name_not_defined_x', where x is a number starting at 0 and counting upwards for each missing parameter name.

| cmd<br>dir | cmd<br>file | inp<br>dir | inp<br>file | def<br>dir | def<br>file | final file used                      |
|------------|-------------|------------|-------------|------------|-------------|--------------------------------------|
| Yes        | Yes         | Any        | Any         | Any        | Any         | cwd/cmd.dir/cmd.file                 |
| Yes        | No          | Any        | Yes         | Any        | Any         | cwd/cmd.dir/inpar.file               |
| Yes        | No          | Any        | No          | Any        | Yes         | cwd/cmd.dir/defpar.file              |
| Yes        | No          | Any        | No          | Any        | No          | cwd/cmd.dir/name_not_defined_x       |
| No         | Yes         | Any        | Any         | Any        | Any         | cwd/cmd.file                         |
| No         | No          | Yes        | Yes         | Any        | Any         | inpar/inpar.dir/inpar.file           |
| No         | No          | Yes        | No          | Any        | Yes         | inpar/inpar.dir/defpar.file          |
| No         | No          | Yes        | No          | Any        | No          | inpar/inpar.dir/name_not_defined_x   |
| No         | No          | No         | Yes         | Any        | Any         | inpar/inpar.file                     |
| No         | No          | No         | No          | Yes        | Yes         | defpar/defpar.dir/defpar.file        |
| No         | No          | No         | No          | Yes        | No          | defpar/defpar.dir/name_not_defined_x |
| No         | No          | No         | No          | No         | Yes         | defpar/defpar.file                   |
| No         | No          | No         | No          | No         | No          | cwd/name_not_defined_x               |
3. step 2, but for maps

[back to top](#quick-menu)


# How to calculate potential (and other electrostatic properties)

In principle, calculating the potential at a given point (here we'll call it the PoI) is incredibly simple. Sum up the potential felt from each point charge around. However, not all point charges are that close by. A very distant point charge has a very small influence, so it is probably not worth the computational effor to include it. How do we approximate the potential accurately using the smallest possible amount of charges? Different options include:

- **atom-atom**. If a charge is closer to the PoI than the given limit, it's influence is included, otherwise, it is not. 
  - *Advantage*: the found potential is relatively true to the actual potential at the POI
  - *Disadvantage*: when taking the difference of two potentials, those potentials are influenced by a different group of charges, resulting in a VERY noisy spectrum. 
  - *Disadvantage*: the total charge around does not have to be 0, or even an integer.
  - *Disadvantage*: A pair of opposite charges can be split in half - creating the illusion of a much stronger potential.
- **molecule-atom**. If a charge is closer to the centre of mass (CoM) of the residue of the PoI than the given limit, it's influence is included, otherwise, it is not.
  - *Advantage*: all atoms in the molecule feel the same set of charges, so taking differences becomes more meaningful.
  - *Disadvantage*: The total charge around does not have to be 0, or even an integer. 
  - *Disadvantage*:, if the residue is very large, the PoI might be very far away from the CoM, leading to a less accurate potential, or requiring a larger radius within which to consider charges.
  - *Disadvantage*: A pair of opposite charges can be split in half - creating the illusion of a much stronger potential.
- **molecule-molecule** (also labeled perres). The influence of a charge on a PoI is only included if the CoM's of the residues each belongs to are within a certain limit. 
  - *Advantage*: all atoms in the molecule feel the same set of charges, so taking differences becomes more meaningful.
  - *Advantage*: the chance that the total charge is neutral is much larger, and otherwise, it must at least be an integer (with the 'off' charge probably being quite far away)
  - *Disadvantage*: If either the residue of the PoI or any of the residues around is large, a charge could come very close to the PoI, but still not be counted. This can either lead to a (much) less accurate potential, or require a larger radius within which to consider charges.
  - *Disadvantage*: A pair of opposite charges can be split in half - creating the illusion of a much stronger potential.
- **soft cutoff**. Can be applied to each of the three methods. The most important reason for using this method is to deal with the general mentioned issue above - if two opposite charges are closeby to eachother, they could be 'split' in half, where one is close enough to be considered, and the other is not. The soft cutoff, as the name implies, is more gentle. Charges close enough are considered fully, but charges close to the cutoff are considered partly, with a formula (often linear) linking the distance and their 'weight'. The main disadvantage is that a larger radius is needed to accomodate the charges, and that applying the soft part is more computationally expensive (requiring more if-checks)
- **neutralizing charges**. Can be applied to each of the three methods. Some magic to get neutral charge to influence the PoI. May or may not be applicable to electric fields (and gradients)? Should have the advantage of much less noise in the potential-distance graph.
- **splitting residues**. If a residue is very large, split it in (neutral) parts. Only applicable for ma and mm methods.
  - Advantage: removes the issue of possible ignoring closeby charges.
  - Disadvantage: When splitting through the residue of the PoI, the disadvantage of different groups of charges influencing the PoI returns.
  - maybe, split all but the residue of the PoI? Or, when splitting the residue of the PoI, don't split the PoIs contributing to a single frequency?

[back to top](#quick-menu)


# Rough program flow (GEM)
- See if GEM is in demo mode
- Very basic cmdline parse (find definition of parameter file and arguments)
- parse parameters:
  - first cmdline argparse - find anything on srcdir/defpar
  - inparfile to dict
  - find which defpar to use
  - find refparfile
  - parse refparfile
  - parse defparfile
  - parse inparfile (not map part)
  - find mapdir in cmdline > inparfile > defparfile
  - for each map, parse parameters.ref
  - parse cmdline
  - for each map, make cmdpars, inpars, defpars
  - check if all parameters from cmdpars, inpars, defpars have now been found
  - make RunPars
- for each map, make RunPars
TO DO
- read/interpret maps:
  - (X) for each map, find (+check? complete?) main.py 
  - (X) for each map, call func to change RunPars
  - (X) for each map, parse core.txt
  - (X) for each map, call func to change strs in core.txt
  - for each map, interpret core.txt / make funcs
  - ?? for each map, call ???
- (X) find/open top/trj files
- (X) run MDA.Universe
- (X) check whether universe is right-angled, neutral
- extract basic universe data:
  - (X) atnums, atnames, resums, resnames, segids, and (VERY PROTECTED!) molnums
  - The protected way of extracting molnums
  - (X) positions, masses, charges, types (and from arr size, natoms), boxdims, halfbox
  - (X) rebuild resnums to make them count from 0 (never resetting)
  - (X) AIMs residues - basically, look-up tables with 1 entry/whatev per residue
    - (X) lowest ix present
    - (X) highest ix present
    - (X) !!! AIM also does the main residue check here! extracts a list of all residue names that should be counted amongst the protein and influencers - also reports unknown resnames. - maybe, instead, have black/whitelists for what residues should(n't) be considered? 
  - ?? AIMs indices? Appears to only look for the protein part of the system?
  - Find all molnums. If not stored in the system, extract them in another way. (how to deal with non-protein multiple-residue chains?)
  - (X) ?? AIM does this - fish out the maps that were actually requested by the user, ditch the rest.
- initialize universe:
  - (X) identify the indices of all atoms involved in oscillators - basis of AIMs oscarr
  - find resnums of protein, (X) influencers, COMgroups
  - create c-frienly objects if needed
  - initialize arrays to use for calculating couplings
  - run 'characterizer' - aids in sorting through atoms later
  - find all local ixs for each oscillator
- run the calculation:
  - precalc:
    - create some empty dicts
    - build the couptype array
    - call the pre-calc functions of maps
    - alias mda.universe.trajectory
    - compare runpar.endframe to mda nframes, correct endframe if needed to not exceed mda nframes.
  - ```for frame in trj[startframe:]:```
    - manage framenum (if not within range, skip iteration / break loop, prints, ETA calc, quit if too slow, etc)
    - rebuild frame-specific data (positions, box, etc)
    - recalculate COM (NSA?)
    - initialize output structures (like hamiltonian)
    - call the pre-frame functions of maps
    - calculate the actual data for hamiltonian, dipoles, etc:
      - calcdiag - for each oscillator:
        - find ix that are in range
        - calculate PEG
        - calculate freq + rotation matrix
        - add nnmap edit to freq
        - if needed, adjust PEG
        - calc dipole
        - calc raman
      - calccoupling:
        - prepcoup - many couplings need some data that is oscillator-specific, not pair specific. That data is found in a per-oscillator fashion
        - calccoup - for each pair, apply correct coupling method.
      - findatpos - save position of an atom for each oscillator
    - call the post-frame functions of maps
    - write the calculated data
- fincalc:
  - print a report to the command line
  - manage the profiler

[back to top](#quick-menu)


# To discuss
(discuss, then put in relevant section)

### discuss soon
- custom refparfile issue
- can maps have (and thus specify) dependencies on other maps, which, if not present, means the map will be invalid/ignored?
- If so, think about (introducing a ?) load order.
- Before creating out & log files: if not specified in the inparfile (maybe still if anyways?) check for file existence before assigning.
- what more parameters (input file) would GEM/AIM/GMAP need?
- Maybe, let maps indicate what method for calculating Epot/field/grad is desired? In 'simple' map file?
- calc all PEG in 1 c-pass, not the AIM way?
- Expected behaviour for (source)dir & (def_par)filename in multiple locations?
- How to deal with missing/invalid info/files/etc in maps?
- How to go about test driven development? especially the complex/specific funtions?
- Is it possible to type hint classes/kwargs properly in a way that suits the project? Or can/should we only type the basic ones?
- Whats a good program/data structure? (for example, AIM's WS class is not ideal...)

### discuss later
- NN locals -> why use list sortcritNN if it can only contain resnum & C-term NB?
- find way to remove setnames from code (special chars in def_parfile?)
- parallelization and update of positions... make sure that goes as expected.
- How to check if defparfile is complete? if user specifies different one, use that file for the choises, but still use def_hc for completeness test?
- find a way to automagically install/compile c library?

[back to top](#quick-menu)


### ===============================
# Dump section
### ===============================

If you need a place to quickly write something down, do it here! It can be tidied/sorted/discussed later. If you can write it down cleanly/properly immediately, please do so. But it is better to leave a poor note (that at least you (if no one else) will understand later), than none at all... Thats why I (KvA) made this dump section.


- (KvA) TODO before PR:
  - Done!
- (KvA) TODO:
  - map main.py documentation - calc_frequency still has dipole outputs?!
  - potential maps don't need rotation matrix, but program still looks for the get_func (which doesn't exist) - why? Are we still using xyz_uvec from core.txt?
  - start on mapdev-checklist. What things should a mapmaker double check before starting the map (and, simultaneously, have map-testing feature do these checks where possible - at least, write down what it should test)
  - have c code for potential take the influencers into account (possibly not within c code, but create mirror of system? new position/charges/etc array containing only valid influencers?)
  - Links to relevant packages etc in explanation in main documentation page.
- (KvA) GEM doesnt check whether command line specifies a refparfile (in case we do want to use them)
- (KvA) Is the way GEM currently finds the defparfile correct? or should we check more/different locations?
- (KvA) Inpars could/should contain section with coupling choices. First, specify the types of each of the coupled oscillators (N*N-1 options, for N different types of oscillators (= selected maps)), then, the coupling method to be used.
  - How to deal when user doesn't specify? Maps could/must indicate a default for how to couple with itself, then it shouldn't be absolutely necessary a user gives that information.
  - Similarly, AIM had a setting for when/wheter to use dipole-dipole coupling for coupling between different kinds of oscillator... What to do?
- (KvA) Refparfile currently doesn't indicate whether a parameter is optional, or MUST be given by the user. Or is the N/A choice sufficient?
- (KvA) Chosen map structure forces coupling maps to be complex? At some point, discuss coupling maps more?
- (KvA) the inpar and temp_cmd dictionaries have a list with choices as the value, even if only a single choice is expected. This is because at the time of creating these objects, we cannot yet know whether we expect a single, or multiple choices.
- (KvA) I've added some shorthands for cmdlinepars:
  | parameter name in refparfile | full command line parameter name | shorthand command line parameter name |
  |------------------------------|----------------------------------|---------------------------------------|
  | source_directory             | --source_directory               | -sd                                   |
  | default_parameter_filename   | --default_parameter_filename     | -dpf                                  |
  | map_directory                | --map_directory                  | -md                                   |
- (KvA) in spirit of the above, how about -v for verbose=2 (or whatever would be nice/common to use as verbose), -vv for verbose=4 (very verbose), and -nov for verbose=0 (making use of the 'no' prefix we want to include anyways)
- (KvA) what if a parameter check fails? currently, all warnings have an exitbool=True, but is this always necessary/desired?
- (KvA) currently, cmd line parser assumes a variable has either 1 assigned choice, or a variable amount.
- (KvA) currently, code to create a RawPars instance for command line input is one big function, not the prettiest - needs tidying up? - maybe other functs, too?
- (KvA) Added keyword parameter 'prevent_overwrite' (bool). It determines how to treat files that should be created. If the program has the instruction to create a new file, but the supplied fname already exists, what should happen? if this new keyword is set to false, the existing file will simply be overwritten. If it is set to True, the existing file will be renamed, so the supplied filename can be used for the new file. The new name for the file will be #oldname.num# - where num is the lowest integer number for which a file does not yet exist.
- (KvA) Made it so that every map instance has its own CmdPars, InPars, DefPars, RefPars, RunPars. Each map shouldn't need any parameters but it's own, except for perhaps GEM-wide parameters. GEM itself shouldn't need any of the map parameters, so this all should work out.
- (KvA) In order to run the unittests, move in command prompt to the GMAP directory. In there, run ```pytest tests``` to run all tests. adding the flag ```-s``` allows (some?) python prints to pass through, the flag ```--cov=src``` gives the coverage of the current unit tests. In case of issues, ```--full-trace``` gives a lot more tracebacks and other information. Finally, to see what parts of the code are not covered by the tests, run ```pytest --cov-report term-missing --cov=src tests```. The Fanciest of all? ```pytest --cov-report term-missing:skip-covered --cov=src tests```. Overview:

  - ```-s```  lets (some?) python prints through
  - ```-x```  makes pytest quit after it encountered its first error
  - ```-full-trace```  gives the full traceback
  - ```-k```  selects tests of the correct name: ```pytest -k "MyClass and not method"``` ```pytest -k my_function```
  - ```pytest mod.py``` runs all tests defined in a given module
  - ```pytest testing/``` runs all tests defined in a file stored in a given directory
  - A specific test can be found like this: ```pytest test_mod.py::test_func```, ```pytest test_mod.py::TestClass::test_method```
  - ```-m``` allows selecting tests with certain markers. Just as with ```-k```, you can add logic to these (using and, or, not, etc). ```-m slow``` only runs tests that have the ```@pytest.mark.slow``` decorator.
- (KvA) Gave every warning it's own error code. Currently, there are two uses in mind - Providing a way for the unittests to check whether the program was quit for the right reason, and providing a way for users to easily get more information on a specific issue in the manual - In the manual, they're easy to find, and references to other places in the manual can easily be added there. But maybe, more uses can be implemented in the future? for example, a way to skip/silence warnings of a specific error code?
- (KvA) list-type parameters must always come with at least one choice (at least, when parsing from the command line). But maybe, that choice can just be '\\;'?
- (KvA) RefPars is just a tool for reading parameter inputs, and creating the corresponding parameter datastructures. After they've been made, it's served its purpose, and is no longer needed. Any function after should only use defpars, not refpars.
- (KvA) demo mode test and command line separation should not be part of get_parameters (Think of when the job 'setup' is implemented)
- (KvA) currently, the type path_sep must lead to files, not directories... This is the reason map_directory is taken separately.
- (KvA) Unittest todo:
  - Make test for GM_FH.get_def_parfile (covered by test_GEM, I believe, but still, unittests, so test it!)
  - Make test for GM_FH errors SU_FH_1-3
  - Make test for warning SU_GM_1
  - Make test for warnings MI_MR_1-5
  - Make test for warnings MI_MC_10
  - Make test for warnings MI_GEM_1
  - Make test for warnings MD_SU_5
  - check docstrings of testfiles for further todo on tests.
- (KvA) should the RunPars docstring contain (under attributes) all parameters as defined in the reference parameter file?
- (KvA) GM_MR.scan_mapdirs() does not check whether a name occured twice. There is no need to disallow it (just yet?), but it would be nice to warn the user, and report the location that ís used.
- (KvA) Should a check be added to confirm whether a parameter name from a reference parameter file can be used as a class attribute?
- (KvA) Can a single map give 2 different frequencies?
- (KvA) Add option to only output hamiltonian diagonal
- (KvA) Add option to output potentials (e.g. only potential caused by a-helix on atoms nearby)
  - Or, more generally, option to output any property the program calculates? Maybe as a separate GEM functionality?
- (KvA) If the top/trj files come from a type(DefPars) == RefPars, or from a RefPars itself, automatically enter demo mode?
- (KvA) I think there might be an issue with the residue number allocation - What if there's an MD package with repeating residue numbers, but segments of only 1 residue? then, the residue number would stay consistent, but it would in fact be a different residue :/ -- means that tools/SystemReader.system.abs_resnums needs an update.

[back to top](#quick-menu)


### ===============================
# Old notes/goals/thoughts/etc
### ===============================

## wishlist
(old ones, early '22?)
- Parallelization?
- Non-cubic PBCs


## thoughts
(old ones, early '22?)
- There should be no FILES.logdir_hc and FILES.outdir_hc
- Before creating out & log files: if not specified in the inparfile (maybe still if anyways?) check for file existence before assigning.
- Assign each (type/family of) error a code, so the user can silence (a specified amount of) them, similar to GROMACS' maxwarn parameter.
- extramaps file structure needs thought
- amideBB should be decoupled from code
- what more parameters (input file) would GEM/AIM/GMAP need?
- should AIM get variable oscsize?
- could AIM and GEM be combined into one?
- AIM had a 6-length array: C<sub>x</sub>, O<sub>x</sub>, Ca<sub>x</sub>, N<sub>x+1</sub>, H<sub>x+1</sub>, Ca<sub>x+1</sub>
- NN locals -> why use list sortcritNN if it can only contain resnum & C-term NB?
- Maybe, let maps indicate what method for calculating Epot/field/grad is desired?
- calc all PEG in 1 c-pass, not the AIM way?
- Create 'scan' functionality -> run all GEM/AIM preparations, but not the actual per-frame, just to see how the system is recognized. also, resnum info for black/whitelists
- also output a 'legend' file? it would contain a description of every entry in the hamiltonian, so a user could retrace which is which.
- each map has own pars? requires def_par file, which also specifies expected type & allowed options & if par must be specified.
- 'simple' map should require (almost?) no code, but still allow for full code!
- Leave no map in core!
- Use pathlib! (not os)
- consider argparse for cmdline? or would we rather parse the string manually?
- Print cmdline call to log file!
- find way to remove setnames from code (special chars in def_parfile?)
- Expected behaviour for (source)dir & (def_par)filename in multiple locations?
- parallelization and update of positions... make sure that goes as expected.
- How to check if defparfile is complete? if user specifies different one, use that file for the choises, but still use def_hc for completeness test?
- find a way to automagically install/compile c library?


## map thoughts
(old ones, early '22?)
- a map _could_ be a single file (similar to AIM extramaps) in its own directory
- a map may have its own def_parfile (linked in main mapfile?) to store default choices of map-specific parameters
- maps may have separate config/makeup file to specify molecule
- map may have its own codebase
- How to deal with missing/invalid info/files/etc?

## finding parfile - steps
(old ones, early '22?)
- read cmdline args, interpret inparfile, defparfile
- read inparfile, interpret defparfile parameter (only if not in cmd?)
- using inparfile.defparfile, read defparfile
- using cmd > inpar > defpar, interpret cat. 1 pars (extra_mapdir + very generics)
- Using cat. 1 pars, read all maps in extra_mapdir. Only complete maps are saved, cat.1 pars may influence?
  - includes interpreting map-specific pars from cmdline & inpar (but NOT defpar, maps have their own defpar) (what if, just as for program, users would like to use a separate defpar from what was supplied with the map?)


## questions from tsjerk
(old ones, early '22?)
These are to aid code development
- what do we have
- what needs to be done
- what future additions can we think of?
- what choices to make with regards to:
  - design philosophy
  - code formatting/style
  - API
  - more!


## questions from kim
(old ones, early '22?)
Again, hoping to aid code development
- Whats a good program/data structure? (for example, AIM's WS class is not ideal...)
- How to go about test driven development? especially the complex/specific funtions?
- Is it possible to type hint classes/kwargs properly in a way that suits the project? Or can/should we only type the basic ones?

[back to top](#quick-menu)
