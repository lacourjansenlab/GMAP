

############
Program flow
############

These pages give an overview of the steps taken by GMAP during runtime.

Calling 'GMAP' from the command line (with or without further arguments) starts the function 'main()' from the file 'GMAP/__main__.py'. This function does the following:

 - A :class:`~GMAP.src.tools.file_handler.FileLocations` instance is created. It stores the location of GMAP, the current working directory, the time at which the program was started, as well as the hard-coded locations of the sourcefiles directory, maps directory and reference parameters file.
 - A :class:`~GMAP.src.tools.print_tools.Printer` instance is created. It stores the name/location of the log file (which for now, upon creation is a temporary name of the format f"crash_{Files.now_str}.log"), the backlog, and program state. It will store verbose levels in the future, too. When asked to print, prints will be sent to the backlog while program_state == startup. This way, if all goes well, the temporary log file is not used, and when the final file is found, the program state is changed, and the backlog emptied to the final choice of file.
 - Print the main header/logo of GMAP
 - See what (if any) other information was on the command line. If a 'help' is requested, the corresponding docstrings are printed. If a specific program is requested (GEM, Setup), that program is started.

Program flows within GEM

.. toctree::
    GEM/run
    Setup


