.. _AddMap_page_map_parameters:

##############
parameters.ref
##############

(This applies both to singles and pairs maps)

This is an optional file containing all keyword parameters the map needs. The file must be of the name 'parameters.ref' for it to be recognized.

Any parameter specified here can be set/supplied by the user, so choices can vary for each calculation.

In the program, the contents of this file are stored in the map-specific instance of a :class:`~GMAP.src.tools.map_reader.Map` object, as the `ref_pars` attribute.

For a good example, you can look at the file 'reference_parameters.ref' in the sourcefiles directory. It contains all the parameters used by the program.


***********
File layout
***********

As with all GMAP source files, when a hashtag (#) is found, it and everything ater it on that line will be ignored. This allows for making notes and comments in the file.

A reference parameter file consists of many lines, most of which are independent. A line has the following format:
parameter_name(shorthand)[parameter_type] parameter_choice
In this format, notice how there is only one whitespace - in between the closing square bracket and the parameter choice. In between these two, there can be an arbitrary amount of whitespaces, but they cannot be anywhere else (except within parameter_choice, see below). Now, to explain each section:

parameter_name is the name of the parameter. It is case-sensitive, and the text used here is how you can access it in the code. So, (the choice for) a parameter named MyPar will be accessible as MyMapInstance.run_pars.MyPar, while a parameter named mypar will be accessible as MyMapInstance.run_pars.mypar. Note that within this parameter file, parameter names must be unique. They can be reused between maps and the main program.

shorthand is the (optional!) shorthand that can be used when specifying a choice on the command line. Assuming the parameter is called mypar, a shorthand of mp is chosen, and the map is called mymap, then, the shorthand allows the user to specify the parameter on the command line using '-mymap.mp' instead of '--mymap.mypar'. As for these parameters you should use the same PEP8 guidelines as for python variable names, they can get uncomfortably long to type in the command line; thats why the shorthand might be preferred.
Notice that the shorthand does not influence the map name itself. This means that multiple maps can safely share the same shorthand. They can consist of multiple characters, but may also consist of a single letter.
The shorthand is fully optional. If you don't want to specify one, leave it out, and don't add the parentheses. 

.. _AddMap_page_map_parameters_types:

parameter_type denotes what the python datatype of the parameter choice should be. Currently, the options are 'path' (for pathlib.Path type - file names), 'str' (for strings), 'bool' (for booleans), 'int' (for integers), and 'float'.
If a parameter should be allowed (but still not required) to take more than one argument, the type should be prepended with 'list\_'. So, if the desired type is multiple strings, the type should be 'list_str'.
In the case of 'path' parameter types, something must be appended, too. There are three options: 'path_sep' is for when a path exists on its own, 'path_dir' is for a directory name - 'path_rel' is for files that are expected in a directory stored in a 'path_dir' parameter. To denote which 'path_rel's belong to which 'path_dir', an extra suffix is used. The suffix can be chosen freely, but must be unique within the parameter file. So, for example, all parameters of the type 'path_rel_1' are expected relative to the location stored in the parameter of type 'path_dir_1' (of this type, there should be only one), while all parameters of type 'path_dir_ts' are expected relative to the location stored in the parameter of type 'path_dir_ts'.
Finally, all files denoted as above are expected to already exist. If a parameter should denote a filename for a file to be created during a run, the parameter type should be appended with '_c'. This should go after anything else.

While all the above gives information on how the program should deal with the parameter, parameter_choice contains the actual choice(s) to be used. There are a few different possibilities.
Firstly, it might not make sense at all to define this parameter in the reference file. This is like a default file, so, for example, the parameter storing the default parameter file name doesn't make sense to be there. But another valid reason might just be that the program is easier to use if the parameter is not defined there, like the log file name. Whatever the case, if you don't want to allow the default parameter file to contain a choice (and not have a choice in the reference file either), you opt for the choice '[N/A]'.
Secondly, you might want to limit what choices a user can make. For example, for the verbose setting, we only want to allow the user the numbers 0-4 (inclusive). In that case, all choices are entered (separated by whitespaces), and the default choice is marked by a pair of square brackets. So, for verbose, the choice looks like this: '0 1 [2] 3 4'. If the parameter type is prepended by 'list\_', multiple items may be marked. A default MUST be marked (in order to identify that there are limited options). 
Finally, a user might have free choice. In that case, only the default choices have to be given. The format is the same as above - items separated by whitespaces. If the parameter type is prepended by 'list', there may be multiple default choices, otherwise, at most one.
Please note that implicit to the parameter type, bools can only take 'True' or 'False' (capitalization is ignored by the program) - this does not need to be supplied as options in the reference parameter file.