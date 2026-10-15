
################################################################
How GMAP analyses parameter files to find run_pars
################################################################

The following is specific to GEM, if other tools differ, add them here, too!

0. **simple parameter check.** Before GMAP calls any program, it checks for the dark mode, safe mode, and color choice parameters, and changes settings accordingly.
1. **check if GEM was called in demo mode.** This is needed, as demo mode does not allow extra parameters to be provided - it runs with the default parameters chosen in the reference parameter file in sourcefiles.
2. **basic command line parse.** Extract the requested job (e.g. run), input parameter file and arguments. Check if the requested job is defined/understood. Check if the specified input parameter file exists, and is a file. (don't do anything with arguments)
#. **arguments.** See if the arguments from the command line contain anything on sourcedir or defparfile. If so, check if the format is correct, and if so, return the given choice (without checking if the given locations exist). If not, throw error and quit.
#. **input parameters file.** If the command line included an imput file, run a very simple parser to extract parameters and choices. No reading/interpretation is done.
#. **finding default parameter file.** Knowing the command line arguments, input parameter file and the hardcoded location for the default parameter file, find out which to use, following the table below. After the choice is made, check if the file exists. If not, throw error and quit.

   ==============   ==============   ================   ================   ================================================
   cmd has srcdir   cmd has defpar   inpar has srcdir   inpar has defpar   used file
   ==============   ==============   ================   ================   ================================================
   Yes              Yes              Any                Any                cwd/cmd.srcdir/cmd.defpar
   Yes              No               Any                Yes                cwd/cmd.srcdir/inpar.defpar
   Yes              No               Any                No                 cwd/cmd.srcdir/Files.refpar_hc
   No               Yes              Any                Any                cwd/cmd.defpar
   No               No               Yes                Yes                inpar/inpar.srcdir/inpar.defpar
   No               No               Yes                No                 inpar/inpar.srcdir/Files.refpar_hc
   No               No               No                 Yes                inpar/inpar.defpar
   No               No               No                 No                 Files.srcdir_hc/Files.refpar_hc
   ==============   ==============   ================   ================   ================================================

#. **find reference parameter file** Any of command line (cmd), input parameter file (inpar) and default parameter file (defpar) can contain the location of the reference parameter file (refpar). That file contains all available parameters with allowed choices (where applicable), so is required by the program. cmd, inpar and defpar are searched for the refparfile location specifically.
#. **parse reference parameter file.** Go through the files, learn what parameters are available, and what type they are.
#. **parse default parameter file.** Parse (the GMAP part, not maps part of) the default parameter file.
#. **parse input parameter file.** Parse (the GMAP part, not maps part of) the input parameter file.
#. **find mapdir.** We need to know where the maps are saved and should be read from. The first of the following that contains a specified location for this directory is used, the rest ignored: command line, input parameter file, default parameter file, reference parameter file.
#. **maps reference parameters.** for each map, parse the parameters.ref file if present.
#. **finish parsing.** Now we know what parameters to expect for all maps, we can finish parsing the command line argument, input parameter file and default parameter file. If any parameters are still not recognized (not defined by either GMAP or maps), throw an error.
#. **Find all run parameter choices.** The run parameters are those actually used, and created from cmd, inpar, defpar and refpar sources. We first do this for GMAP only, but after all substeps here are performed, this is also done for each map.

   - Most parameters are merged in a simple way: if cmd contains a choice, use it. If not - if inpar contains a choice, use it. If not, use it from defpar.
   - For parameters where the above doesn't work (for example, start- stop- and number of frames), execute custom code/instructions for determining these.
   - Files are treated as follows: Use the table below to see what happens depending on which sources contain which parameters. After the supposed file is defined, see if it exists, is of correct format, etc. If the file should be created, but already exists (and shouldn't be overwritten), it is renamed to preserve it, and the requested name will be the name of the newly created file. If a file name is missing, the stub-name 'name_not_defined_x' is used, where x is a number starting at 0 and counting upwards for each missing parameter name.

   ====  ====  ====  ====  ====  ====  ===================================
   cmd   cmd   inp   inp   def   def   final file used
   dir   file  dir   file  dir   file   
   ====  ====  ====  ====  ====  ====  ===================================
   Yes   Yes   Any   Any   Any   Any   cwd/cmd.dir/cmd.file
   Yes   No    Any   Yes   Any   Any   cwd/cmd.dir/inpar.file
   Yes   No    Any   No    Any   Yes   cwd/cmd.dir/defpar.file
   Yes   No    Any   No    Any   No    cwd/cmd.dir/name_not_defined_x
   No    Yes   Any   Any   Any   Any   cwd/cmd.file
   No    No    Yes   Yes   Any   Any   inpar/inpar.dir/inpar.file
   No    No    Yes   No    Any   Yes   inpar/inpar.dir/defpar.file
   No    No    Yes   No    Any   No    inpar/inpar.dir/name_not_defined_x
   No    No    No    Yes   Any   Any   inpar/inpar.file
   No    No    No    No    Yes   Yes   defpar/defpar.dir/defpar.file
   No    No    No    No    Yes   No    defpar/defpar.dir/name_not_defined_x
   No    No    No    No    No    Yes   defpar/defpar.file
   No    No    No    No    No    No    cwd/name_not_defined_x
   ====  ====  ====  ====  ====  ====  ===================================






