# Quick menu
- [General rules for code](/development%20notes-goals-thoughts.md#general-rules-for-code)
- [General code-related remarks](/development%20notes-goals-thoughts.md#general-code-related-remarks)
- [Roadmap](/development%20notes-goals-thoughts.md#roadmap)
- [wishlist](/development%20notes-goals-thoughts.md#wishlist)
- [Package structure](/development%20notes-goals-thoughts.md#package-structure)
- [notes](/development%20notes-goals-thoughts.md#notes)
- [structure/concepts of maps in/for GEM](/development%20notes-goals-thoughts.md#structureconcept-of-maps-infor-gem)
- [How GEM looks for/through parameter files to obtain runpar](/development%20notes-goals-thoughts.md#how-gem-looks-forthrough-parameter-files-to-obtain-runpar)
- [To discuss](/development%20notes-goals-thoughts.md#to-discuss)
- [Dump section](/development%20notes-goals-thoughts.md#dump-section)
- [Old notes/goals/thoughts/etc](/development%20notes-goals-thoughts.md#old-notesgoalsthoughtsetc)



# General rules for code
- Follow the TOCM group python style guidelines (which are heavily based on PEP8), can be found [here](https://github.com/lacourjansenlab/CoffeeCodeClub/tree/master/ProgramStyle)
- Make use of comments when function of code isn't easily discernable!
- Its the modern era, we have storage space! Code does not need to be compactly written, legibility is the most important in this project
- Don't worry about efficiency/speed of a function if it doesnt take more than 1% of total calculation time. This doesn't mean we should aim for blatantly needlessly expensive code.
- Document the choices/assumptions/etc you make, so they can be put in a (dev)manual later. If it's too much to immediately write them down neatly, put them over [here](https://github.com/Kimvana/GEMAIM-dev/blob/main/development%20notes-goals-thoughts.md#dump-section)
- Printing should *_always_* be done with a custom print command (except when defining these), not the python default print. if you want to temporarily print something during development, use ```GMAP.src.tools.PrintTools.devprint()``` instead. It behaves _EXACTLY_ like print does, but adds a linenumber and name of file/function to the print - this way, it is easy to find it back, and remove it.
- When creating strings for printing, f-strings are the preferred method.

# General code-related remarks
- Use pathlib! (not os)
- Leave no map in core! This means also amideBB should be decoupled from code
- After having had a look at argparse, I (KvA) will not use it for the cmdline. It doesn't quite give me what I'm looking for, and doesn't feel quite right.

# Roadmap

This is a rough overview of the different steps (in order) that are needed to get ```GEM run``` running.
- Step 0: (Done!) Gmap interface, command prompt menu to navigate the different tools
- Step 1: (Done!) Create test suite, documentation system
- Step 2: (Done!) Parameter parsing
- Step 3: Map parsing (maybe also already develop a map? - requires core algorithms?)
  - ?? create file like reference parameters that specifies what things a map can contain?
  - for each map, interpret the core.txt file. reject map if incomplete/wrong.
  - for each map, see if there is a main.py file. If so, import and check for completeness.
  - if incomplete, alias default functions for the missing ones.
  - write those default functions in a separate file (sourcefiles?) - This file can function for these functions much like reference parameter files work for parameters.
  - If the user requests the use of this map, throw error if map was loaded unsuccessfully.
- Step 4: System analysis (requires map parsing for group recognition)
  - Load in system (mda universe)
  - extract 'basic' data (positions, masses, charges, etc)
  - find requested oscgroup atoms
- Step 5: Core algorithms
  - A function to calculate just potentials (perhaps multiple depending on algorithm)
  - A function to calculate potentials + fields (perhaps multiple depending on algorithm)
  - A function to calculate potentials + fields + gradients (perhaps multiple depending on algorithm)
- Step 6: Map creation (or maybe already during parsing?)
- Step 7: Performing per-frame calculation
- Step 8: Adding extra functionality
  - Black-/whitelists - what kind of typing would they need? a new one?

Other things for GMAP
- Include AIM
- Add GEM demo, GEM setup (just like installable AIM), maybe also a way to run GEM without calculating frames (to see if system is recognized, file sizes, etc)?

# wishlist
- Non-cubic PBCs
- Create 'scan' functionality -> run all GEM/AIM preparations, but not the actual per-frame, just to see how the system is recognized. also, resnum info for black/whitelists (get an overview of which element in the hamiltonian corresponds to which residue number)
- Parallelization? Not if we don't expect this to make a huge difference, instead, create an embarassingly parallel example.
- Assign each (type/family of) error a code, so the user can silence (a specified amount of) them, similar to GROMACS' maxwarn parameter.
- Print cmdline call to log file!
- also output a 'legend' file. it would contain a description of every entry in the hamiltonian, so a user could retrace which is which.

# Package structure
- There will be one big package (currently named GMAP). The concept of this will equal that of GROMACS. It will contain different programs/tools (GEM, AIM, other relevant projects), just like GROMACS contains mdrun, trjconv, etc.
- There will be a copy of the ['old' AIM](https://github.com/Kimvana/AIM/tree/Version-1.0-(main)) as a tool within the package. This will remain a copy, and will receive very few updates/changes to stay close to the original.
- There will be a new program in the package (currently named GEM) that is very similar to AIM, but can _also_ deal with non-IR maps. It should still be capable of treating the systems AIM was made for.

# notes
- There should be no FILES.logdir_hc and FILES.outdir_hc
- AIM had a 6-length array: C<sub>x</sub>, O<sub>x</sub>, Ca<sub>x</sub>, N<sub>x+1</sub>, H<sub>x+1</sub>, Ca<sub>x+1</sub>

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
  - [mandatory for complex maps] name of the 'main' python file, and name of the function giving the functdict.
  - [optional?] What coupling methods can(not) be applied (black/whitelists)
  - [optional?] Dipole to use for dipole-dipole interactions
  - [optional] delta-q to use for tresp/TCC coupling method
  - [optional?] what coupling method to apply to interactions between oscillators of this species (in case none is given in inpar file). None should also be an option.
- Complex maps must have (are defined by having) a python script to be executed by GEM.
  - The file must contain a function that returns a dict with all the functions GEM might want to look for. By having them returned as a dict, they could also live in a different .py file, made and used by the map (or a dependency)
  - The file can contain many functions (AIM inspired - calc_freq(), pre_calc(), post_frame(), more) that GMAP will look for. If they are not present, GMAP will use the 'default' (i.e. the one used for a 'simple' map)
  - The file can also alter any of the data specified in core.txt (for example, AIM's amide map can have, depending on choice (skinner, etc) different choices for rel_j, PEG_choice, constants, and references)
  - The script should only alter data linked to the specific map (if desired), and treat all other data supplied to it as read-only.
- Complex maps can have a default/reference parameter file named parameters.ref, in case the extra code requires it (for example, amides would need to know the choice of map - skinner etc). Also specifies expected type & allowed options & whether par must be specified.

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


### ===============================
# Dump section
### ===============================

If you need a place to quickly write something down, do it here! It can be tidied/sorted/discussed later. If you can write it down cleanly/properly immediately, please do so. But it is better to leave a poor note (that at least you (if no one else) will understand later), than none at all... Thats why I (KvA) made this dump section.


- (KvA) In preparation for next CCC:
  - Give a reason why GEM is needed.
  - Demo of AIM
  - Overview of methods to calculate potential.
- (KvA) TODO before pull to main:
  - Roadmap of what the next steps will be.
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
- (KvA) Clearly state/explain somewhere what the syntax (/ rules) for command line parameters is.
- (KvA) Added keyword parameter 'prevent_overwrite' (bool). It determines how to treat files that should be created. If the program has the instruction to create a new file, but the supplied fname already exists, what should happen? if this new keyword is set to false, the existing file will simply be overwritten. If it is set to True, the existing file will be renamed, so the supplied filename can be used for the new file. The new name for the file will be #oldname.num# - where num is the lowest integer number for which a file does not yet exist.
- (KvA) Made it so that every map instance has its own CmdPars, InPars, DefPars, RefPars, RunPars. Each map shouldn't need any parameters but it's own, except for perhaps GEM-wide parameters. GEM itself shouldn't need any of the map parameters, so this all should work out.
- (KvA) In order to run the unittests, move in command prompt to the GMAP directory. In there, run ```pytest tests``` to run all tests. adding the flag ```-s``` allows (some?) python prints to pass through, the flag ```--cov=src``` gives the coverage of the current unit tests. In case of issues, ```--full-trace``` gives a lot more tracebacks and other information. Finally, to see what parts of the code are not covered by the tests, run ```pytest --cov-report term-missing --cov=src tests```. The Fanciest of all? ```pytest --cov-report term-missing:skip-covered --cov=src tests```.
- (KvA) Gave every warning it's own error code. Currently, there are two uses in mind - Providing a way for the unittests to check whether the program was quit for the right reason, and providing a way for users to easily get more information on a specific issue in the manual - In the manual, they're easy to find, and references to other places in the manual can easily be added there. But maybe, more uses can be implemented in the future? for example, a way to skip/silence warnings of a specific error code?
- (KvA) list-type parameters must always come with at least one choice (at least, when parsing from the command line). But maybe, that choice can just be '\\;'?
- (KvA) RefPars is just a tool for reading parameter inputs, and creating the corresponding parameter datastructures. After they've been made, it's served its purpose, and is no longer needed. Any function after should only use defpars, not refpars.
- (KvA) demo mode test and command line separation should not be part of get_parameters (Think of when the job 'setup' is implemented)
- (KvA) currently, the type path_sep must lead to files, not directories... This is the reason map_directory is taken separately.
- (KvA) Unittest todo:
  - Make test for GM_FH.get_def_parfile (covered by test_GEM, I believe, but still, unittests, so test it!)
  - Make test for GM_FH errors SU_FH_1-3
  - Make test for warning SU_GM_1
  - check docstrings of testfiles for further todo on tests.
- (KvA) should the RunPars docstring contain (under attributes) all parameters as defined in the reference parameter file?
- (KvA) GM_MR.scan_mapdirs() does not check whether a name occured twice. There is no need to disallow it (just yet?), but it would be nice to warn the user, and report the location that ís used.
- (KvA) Should a check be added to confirm whether a parameter name from a reference parameter file can be used as a class attribute?


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
