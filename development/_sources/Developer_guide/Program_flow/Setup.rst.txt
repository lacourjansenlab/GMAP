#####
Setup
#####

Setup.py contains two functions, Setup(callcommand, Printer) and verify_target(target, target_srcdir, target_mapdir, Printer). If verify_target finds a mistake, it will terminate the program and inform the user. By calling GMAP Setup [target_map], first Setup is invoked.

Setup.Setup(callcommand, Printer):
 - Set Printer instance variables to correct values to allow for printing.
 - Extract the target folder, the folder where the user wants to copy to, from callcommand.
 - Create the paths that will lead to where sourcefiles_copy and maps_copy will exist.
 - Invoke Setup.verify_target, which will ensure the target directory exists and doesn't already contain sourcefiles_copy and maps_copy.
 - Find the paths that lead to where GMAP\sourcefiles and GMAP\maps currently live.
 - Copy the GMAP\sourcefiles and GMAP\maps to where they are supposed to be copied.
 - Notify the user that the copying was succesfull.

Setup.verify_target(target, target_srcdir, target_mapdir, Printer):
 - Verify that the given directory is a directory.
 - Verify that sourcefiles_copy doesn't already exist in the target directory.
 - Verify that maps_copy doesn't already exist in the target directory.