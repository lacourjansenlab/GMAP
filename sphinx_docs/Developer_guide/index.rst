.. _DevGuide_page_home:

################
Developers guide
################

Welcome! Nice to see you'd like to contribute to GMAP! These pages contain information specifically for developers of the program itself, but can also be useful for developers of maps. Scroll down this page for a general introduction, or select a topic from the menu here.

.. note::
    Map != map()! The main program in the GMAP package (GEM) serves a specific purpose: converting an md trajectory into a Hamiltonian trajectory. In the spectroscopic community, this conversion is traditionally done using so-called maps. In this package, :class:`~GMAP.src.tools.map_reader.Map` objects contain all information on such a spectroscopic map. Do not confuse these objects with python's built-in map() function - it doesn't occur yet in the program as of writing this text (january 2024), and is not expected to, either.




.. grid:: 1 2 2 3

    .. grid-item-card::
        :margin: 0 3 0 0
        :link: useful_resources
        :link-type: doc

        **useful resources**
        ^^^^^^^^^^^^^^^^
        All kinds of links and information 

    .. grid-item-card::
        :margin: 0 3 0 0
        :link: Program_flow/index
        :link-type: doc

        **Program flow**
        ^^^^^^^^^^^^^^
        A rough outline of how the program is structured.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: code_style
        :link-type: doc

        **Code Style**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        Guidelines on how to style your code to keep the entire codebase consistent.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: print_colors
        :link-type: doc

        **print_colors**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        A chart of the available colors and how they'll render.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: VScode_setup
        :link-type: doc

        **VScode setup**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        How to recreate my exact coding environment.
    
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: documentation
        :link-type: doc

        **Documentation**
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        Everything pertaining to the new documentation
    

    .. grid-item-card::
        :margin: 0 3 0 0
        :link: GMAP_and_parameters
        :link-type: doc

        **File scanning for RunPar**
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        How GMAP interprets file contents.
    
    .. grid-item-card::
        :margin: 0 3 0 0
        :link: estatic_methods
        :link-type: doc

        **Electrostatic calculations**
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Presents different ways of calculating electrostatic properties.



*********************************
General rules when writing code
*********************************

- Follow the TOCM group python style guidelines (which are heavily based on PEP8), can be found `here <https://github.com/lacourjansenlab/CoffeeCodeClub/tree/master/ProgramStyle>`__, or in the GMAP documentation (Developer Guide -> Code Style)
- Make use of comments when function of code isn't easily discernable!
- Its the modern era, we have storage space! Code does not need to be compactly written, legibility is the most important in this project
- Don't worry about efficiency/speed of a function if it doesnt take more than 1% of total calculation time. This doesn't mean we should aim for blatantly needlessly expensive code.
- Document the choices/assumptions/etc you make, so they can be put in (the developers parts of) the manual later.
- Printing should **always** be done with a custom print command (except when defining these), not the python default print. if you want to temporarily print something during development, use ``GMAP.src.tools.print_tools.devprint()`` instead. It behaves _EXACTLY_ like print does, but adds a linenumber and name of file/function to the print - this way, it is easy to find it back, and remove it.
- When creating strings for printing, f-strings are the preferred method.


*********************************
General code-related remarks
*********************************

- Use pathlib! (not os)
- No traces/preference for any map should be visible in the main GMAP codebase. This means also amideBB has been removed (compared to AIM)
- After having had a look at argparse, I (KvA) will not use it for the cmdline. It doesn't quite give me what I'm looking for, and doesn't feel quite right.
- On package structure:

  - There will be one big package (currently named GMAP). The concept of this will equal that of GROMACS. It will contain different programs/tools (GEM, other relevant projects), just like GROMACS contains mdrun, trjconv, etc.
  - We've decided that we won't add the old AIM to the project. It sounded useful, but would require a full rewrite. Users preferring AIM should just download it separately, but GEM should be able to do what AIM did before.
- RefPars is just a tool for reading parameter inputs, and creating the corresponding parameter datastructures. After they've been made, it's served its purpose, and is no longer needed. Any function after should only use defpars, not refpars.
- The inpar and temp_cmd dictionaries have a list with choices as the value, even if only a single choice is expected. This is because at the time of creating these objects, we cannot yet know whether we expect a single, or multiple choices.




.. _DevGuide_page_home_workflow:

***********************************************
Workflow for any developer on the project
***********************************************

You'd like to contribute to the development of GMAP? Nice! Thanks! Here is the general workflow everyone should use, to maintain the current project structure.

- **Pick a task.** What will you do? Usually, this means choosing an issue from the issue page (or project board) and *reading it well.* If you're unsure what to do, ask one of the other developers! Make sure to add your name to the issue, so others know you're tackling it!
- **Make a plan.** How are you going to solve the issue? Sometimes, it might be useful to discuss with other developers about how to go about it.
- **Create a branch.** On github, for the issue, you can create a separate branch. The auto-suggested name by github (equals the name of the issue) is the one you should use.
- **Keep up to date from development.** If you notice anything happening there, pull the updates (GH desktop has the tab branch -> compare to branch). Keep doing this during all steps to come! In GH desktop, in the 'compare to branch' window, you can see in the bottom left that you will be pulling development to your personal branch.
- **Do the thing.** Usually, this is coding, sometimes, it's something else.
- **Prettify.** This could mean many things. Make sure you adhere to the general rules when writing code listed above (including PEP8 code style), you removed commented lines of code, fixed spelling/grammar issues, etc.
- **Documentation.** Nice that you did the thing, but others should know about it. Make sure that your changes are well documented. This means:

  - Clear commit messages. Report on all changes, especially those that are important to other developers (changed function signatures, functions whose purpose changed, new functions, removed ones, etc)
  - In-code documentation. Docstrings, and comments where needed (see code style instructions. Generally - if reading the code doesn't make it obvious in 2 seconds, add the comment!)
  - Update the manual. If users need to know about your changes, too, make sure to add it to the manual. Think about general explanation, adding a new error code to the list, adding a new parameter, etc.
- **Confirm current tests work.** Before you, others have already put in hard work. Tests specify what their code should do, so please run all existing tests. If they don't pass, make sure they do. Sometimes it makes sense (your change was expected to break things), but if not, look at your code. Don't blindly change the tests themselves. Don't continue to the next step until all tests pass!
- **Add new tests for your contribution.**  You've made sure other people's work didn't break, now lets make sure other people can't unknowingly break yours! Create tests for all functionality that you've added, and make sure they pass. This is also the last (and most thorough) bug-fixing step. Any promise you've made in the documentation should be confirmed/reflected in a test. Make sure your own tests pass. All code in src/tools should be covered by tests in tests/test_tools. If you can't cover a statement for whatever reason, add this to the top of the document. Some already have examples of this. Possible reasons for not being able to cover a statement could be:

  - You're missing the required dataset for testing. This should be noted, so it is not forgotten, and the dataset (and test) can be added later.
  - You can't reach the statement. Sometimes, you code in more failsaves than needed. Sometimes it makes sense to remove that test, sometimes there's a (future-proofing) reason not to. If you keep it, write it down! That way, someone can compare the expected amount of missed statements to the one actually found!
- **Prettify, pt2.** You've probably done more work since the last prettifying step, so lets do a final round. See instructions in the first prettifying step!
- **Update from development.** Make sure you are still up to date. If not, and you take changes from development, do the tests and prettifying again!
- **Pull request.** Open a pull request to merge your changes to the **development** branch. Make sure to add 2 reviewers, and resolve any issues they might have. When they are happy, you can merge to main.
- **Celebrate!** Congratulations, you're done!



***********************************************
Pytest instructions
***********************************************

In order to run the unittests, move in command prompt to the GMAP directory. In there, run ``pytest tests`` to run all tests. adding the flag ``-s`` allows (some?) python prints to pass through, the flag ``--cov=src`` gives the coverage of the current unit tests. In case of issues, ``--full-trace`` gives a lot more tracebacks and other information. Finally, to see what parts of the code are not covered by the tests, run ``pytest --cov-report term-missing --cov=src tests``. The Fanciest of all? ``pytest --cov-report term-missing:skip-covered --cov=src tests``. Overview:

- ``-s``  lets (some?) python prints through
- ``-v``  Makes pytest more verbose (every test name is listed, errors aren't abbreviated)
- ``-x``  makes pytest quit after it encountered its first error
- ``-full-trace``  gives the full traceback
- ``-k``  selects tests of the correct name: ``pytest -k "MyClass and not method"`` ``pytest -k my_function``
- ``pytest mod.py`` runs all tests defined in a given module
- ``pytest testing/`` runs all tests defined in a file stored in a given directory
- A specific test can be found like this: ``pytest test_mod.py::test_func``, ``pytest test_mod.py::TestClass::test_method``
- ``-m`` allows selecting tests with certain markers. Just as with ``-k``, you can add logic to these (using and, or, not, etc). ``-m slow`` only runs tests that have the ``@pytest.mark.slow`` decorator.

Pytest also gives the ability to generate a web page to look at everything in more detail. It can also answer the question "which test(s) cover this line?". To get an answer to this question, perform the following steps:

- run ``pytest --cov-context=test --cov-report term-missing:skip-covered --cov=src -x tests``
- run ``coverage html --show-contexts``
- open the file it said it created
- navigate to 'functions', scroll down to the function you want to check out, click it.
- Here, scroll to the line, and on the right side of the screen, click the dropdown menu.




***********************************************
Random good-to-knows
***********************************************

- AIM had a 6-length array: C_x, O_x, Ca_x, N\_(x+1), H\_(x+1), Ca\_(x+1)
- On Mac, at some point, too new python versions would trigger issues with the colorama module not being able to be found. Downgrading to older python solved it. We might want to keep this in mind, and even test later?
- | Printing to a file in c (not python):
  | fhand = fopen(fname, mode); -> create handle (modes as in python)
  | fprintf(fhand, \*just like printf);
  | fclose(fhand);
- colorama can detect background color (on windows) like this:

  .. code-block:: python
    
    import colorama
    colors = colorama.win32.GetConsoleScreenBufferInfo().wAttributes
    background_color = colors >> 4
    foreground_color = colors % 16

  Why does this work? The colors are stored in binary format. Counting from the right, the first 3 bits are used for the color (allowing the 8 choices used in 4-bit colors), then a bit for bright/not bright, then 3 bits for the background color, and another for bright/not bright. The order of the colors is different from ANSI: black, blue, green, cyan, red, magenta, yellow, white. There doesn't seem to be an easy alternative for non-windows :(

- (RUG only) You can use the cluster 'directly' through: portal.hb.hpc.rug.nl
 



***********************************************
Random thoughts
***********************************************

These might become issues later.

- Should maps have the option to specify what method for computing estatics is desired? Of course, using main.py they can already check and error.
- Should we find a way to automagically install/compile the c libraries?
- In spirit of the parameter shorthands, how about -v for verbose=2 (or whatever would be nice/common to use as verbose), -vv for verbose=4 (very verbose), and -nov for verbose=0 (making use of the 'no' prefix we want to include anyways)
- Currently, the type path_sep must lead to files, not directories... This is the reason map_directory is taken separately.
- GM_MR.scan_mapdirs() does not check whether a name occured twice. There is no need to disallow it (just yet?), but it would be nice to warn the user, and report the location that ís used.
- Can a single map give 2 different frequencies?
- Add option to output potentials (e.g. only potential caused by a-helix on atoms nearby)?
  - Or, more generally, option to output any property the program calculates? Maybe as a separate GEM functionality?
- we already allow silencing specific error codes, do we also want something like GROMACS' maxwarn functionality?



.. toctree::
    :hidden:
    
    useful_resources
    Program_flow/index
    code_style
    print_colors
    VScode_setup
    documentation
    GMAP_and_parameters
    estatic_methods
