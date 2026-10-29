.. _UserGuide_page_adding_map_getting_started:

################
Getting Started
################


This guide will get you on your way to creating your first map. Please note this guide will only explain how to create the structures needed by GMAP, but not how to generate the values/data needed.



********************************************************************************
Familiarize yourself with the concept of a map
********************************************************************************

GMAP is built around the concept of maps. GMAP contains the physics, and provides the necessary tools. Maps, in turn, detail how to use these to obtain specific spectra. They do so by containing both parameters (also called mapping coefficients) along with instructions on how to apply them.

In practice, a map is a directory containing one or more files, which will be interpreted by GMAP. After setting up GMAP, we can explore some examples of these!

Then, ask yourself whether you want to create a 'Single' map, or a 'Pair' map. The difference between these :ref:`is explained here <UserGuide_page_adding_map_file_structure>`. If you've never created a GMAP map, it might be rather difficult to start with a Pairs map. We'd recommend creating a Singles map first, even if it is just a dummy/model map, to get the hang of GMAP.



********************************************************************************
Get yourself a working installation of GMAP
********************************************************************************

Now you know GMAP and maps cannot work without each other, make sure to install GMAP. Installation instructions can be found both `in the GMAP repository README<https://github.com/lacourjansenlab/GMAP#how-to-install>`__ and :ref:`in the docs <Quickstart_installation>`. You don't need to install in developer mode, but it wont hurt, either.

Not all kinds of maps require you to know code, but they do require you to read carefully. There's two important sources of information: this manual, and errors thrown by GMAP. When working on a map, you can ask GMAP to try and use your map whenever you like.

.. note::
    As long as you don't write code (main.py file), GMAP should be providing you with custom messages explaining what went wrong. If you encounter a 'raw' python error (recognizable from the ``Traceback (most recent call last):`` line), you can consider this a bug, and open an issue on github.

    **However**, if you *are* writing code yourself, these python errors can't be all avoided (and are probably even useful to you), so please work those out yourself, and don't report them.



********************************************************************************
Have an example on the side
********************************************************************************

When working on your own map, it can be useful to have an example on the side. After you installed GMAP, have a look at the 'maps' directory (inside the 'GMAP' directory). If you want to create a 'Single' map, the 'Tryptophan_1La' map is a good basic example. If you want to create a 'Pair' map, have a look at the 'DipDip' map. You will see the DipDip map is more complicated, hence the advice to have a taste of creating a 'Single' map first.



********************************************************************************
Familiarize yourself with your two roles
********************************************************************************

When creating a new map, you are secretly performing the tasks of two different parties. Those of the user, and those of a map creator. It is very important to notice which set of tasks you are performing. It is a lot easier to distinguish between these roles if you have already used GMAP for a (trial) calculation before starting.

The user:

- Will have data files (output from an MD calculation) somewhere in a 'data' directory, and GMAP installed in a 'programs' directory.
- In (or next to) their data directory, they will have an :ref:`input parameter file <UserGuide_page_specifying_parameters_file>` to tell GMAP what calculation they want to run.
- Might have a special 'maps' directory in which they put downloaded maps. Their input parameter file will point to this directory, and request a specific map from this directory.
- Will have read the README of any map they use, but not understand anything else. **They don't edit any files within the maps directory.**
- Performs a GMAP run, and uses the output from GMAP with other tools/programs.


The map creator:

- Writes/creates/edits files in one directory, which lives either in the 'Singles' or 'Pairs' directory in any maps directory.


So, if you are testing a map (and therefore calling GMAP) you are performing tasks from general users. This distinction is very useful, as it also explains where your different files should live. When deep into creating maps, some people forget the difference between an input parameter file and a 'core' file. If that happens, read this section again.



********************************************************************************
Making your map
********************************************************************************


Now, it is finally time to create some files! But first, create a directory for them to live in. If you chose to create a 'Single' map, place your directory in the 'Singles' directory, and if you chose to create a 'Pair' map, place your directory in the 'Pairs' directory.

The name of the directory should be short enough that it is not inconvenient to type out, but long enough to be unique and descriptive.

Then, follow the steps according to your type of map:


Singles maps
==========================

The creation of a singles map starts with the 'core.txt' file. :ref:`Here <AddMap_FileStruct_SingCore>` you can find a very detailed walkthrough explaining how to create one. Go through it, step by step. During the creation of the core.txt, you might also create a functional_group.txt file, and a file with map coefficients. GMAP itself will generate a 'parameters.ref' file, which you may ignore.

If your molecule fits neatly within the options available in a core.txt file, congratulations! Your map should now be functional. You are not done yet, but the hardest part is over. You can continue to the next section, and ignore the rest of this one.

If you felt too limited by the available choices, welcome! There is a whole deeper layer to map creation you will soon discover. GMAP allows you to customize anything, through writing your own python code. If you are new to python, have a look at some of the examples, and maybe you will learn a new skill today!

For writing this code, :ref:`the main.py page <AddMap_FileStruct_SingMainPy>` is a good reference guide. It gives all details and context. It might be overwhelming, though, so have a look at one of the :ref:`map code tutorials <UserGuide_page_adding_map_Tutorials>`. Each of those will describe an issue, and the corresponding solution. They use examples from maps that come with GMAP.

You might also need other files, all are defined :ref:`here <UserGuide_page_adding_map_file_structure>`.



Pairs maps
==========================

To those familiar with Singles maps, it might come as a surprise that for Pairs maps, :ref:`the core.txt file <AddMap_FileStruct_PairCore>` is optional. We still recommend going through the page linked here, and see if your map requires it.

By nature, pairs mappings are more complex, as we (as GMAP creators) can make way fewer assumptions. Therefore, you must write some code to a pair map. This means that :ref:`the main.py file<AddMap_FileStruct_PairMainPy>` is **not** optional for pairs maps. This does, however, not mean that all functions need to be defined. In fact, GMAP does not force a pairs map to have a main.py at all; but without it, GMAP will not do anything.

When creating a main.py, you will most likely want to have at least a definition of the function ``GM_calc_coupling``. If your map is unreasonably slow, you might benefit from a definition of ``GM_prep_coupling`` (which might, in turn, need a definition of ``GM_pre_run``, see the DipDip example mentioned before), so you don't need to do repeat work.

Of course, you can make the main.py a lot more complicated than the DipDip map's one if needed. The ProteinAmide map is a more complicated example, as it works together with 6 child maps (named ProteinAmide_something). Similarly, the TrEsp map is a more complicated example, as it allows maps to communicate with it. It does this by, just like GMAP, giving a 'single' map the option to define a keyword or function that only it can understand.

You might also need other files, all are defined :ref:`here <UserGuide_page_adding_map_file_structure>`.

After your core.txt, main.py, and optional extra code/data files are in place, congratulations! Your map should now be functional. You are not done yet, but the hardest part is over.



********************************************************************************
Making your map usable
********************************************************************************

While your map should now be functional, it is not yet easily accessible to future you (you will probably forget how it worked again), colleagues, and others in the community. Luckily, that problem can be solved! In this stage, :ref:`The checklist <AddMap_checklist>` is your friend. Make sure you finish all steps!


********************************************************************************
Making your map accessible
********************************************************************************

Now your map is done, please share it with us! To do so, see the `GMAP map library repository on github <https://github.com/lacourjansenlab/GMAP_map_library>`__ for details and instructions.


