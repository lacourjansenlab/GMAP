
#########
GEM - run
#########

These steps are always performed by GEM, regardless of method:
- First parse of command line - extract the job GEM is requested to do, the name of the input parameter file as requested, and the parameters requested for the run.

When GEM is run in 'run' mode, the following steps are performed:

GEM.get_parameters():
 - extract a temporary dict from the command line arguments. Basically, just look for the 'source_directory' and 'default_parameter_filename' parameters.
 - Create a temporary dict from the input parameter file, if there is one.
 - Using the command line arguments and the temporary input file dict (if present), find the default parameter file location. If there was no choice given, the filename of the hardcoded reference parameter file is used.
 - Store the contents of the found default parameter file:
   - If the file ends in '.txt', create a :class:`~GMAP.src.tools.parameter_parser.RawPars` instance.
   - elif the filename is the same as that of the reference parameter file, make def_pars an alias of ref_pars, and create an attribute named 'not_found' (assigned value is an empty dictionary), so it can mimick the behaviour of a :class:`~GMAP.src.tools.parameter_parser.RawPars` instance.
   - elif the filename ends in '.ref', create a :class:`~GMAP.src.tools.parameter_parser.RefPars` instance. (This is not yet supported, see error SU_FP_1)
 - Create a :class:`~GMAP.src.tools.parameter_parser.RawPars` instance for the input parameter file (an empty one if no file was supplied).
 - Find all the map directories the program should use, using information from command line and input-, default-, and reference parameter files.
 - Search through the found map directories for maps. Create a :class:`~GMAP.src.tools.map_reader.Map` instance for each found map, it only stores its name, and the location where its files can be found.
 - For each map, see if there is a reference parameter file, and if there is, make a :class:`~GMAP.src.tools.parameter_parser.RefPars` instance for each.
 - Finish parsing the command line, and make its own :class:`~GMAP.src.tools.parameter_parser.RawPars` instance. This can only be done now, as we need the map-specific :class:`~GMAP.src.tools.parameter_parser.RefPars` instances to know how many arguments a map-specific parameter takes.
 - For each map, go through cmd_pars, in_pars and def_pars to find all parameters for that map, and put them in a map specific cmd_pars, in_pars and def_pars.
 - Check if all parameters supplied to cmd_pars, in_pars and def_pars have been recognized. If not, throw warning.
 - Combine the 'main' cmd_pars, in_pars and def_pars into run_pars - following the correct precedence, find the final choice to use for each parameter.
 - Create a RunPars object for each map.


