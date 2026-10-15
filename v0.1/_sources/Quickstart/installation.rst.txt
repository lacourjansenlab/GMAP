

######################
How to Install
######################


Everyone should follow the 'simple' installation instructions. For developers of the program, there might be some additional steps needed.

If you plan to create a map, you might already benefit from a developer-level installation, especially if your map needs a main.py file.

The installation instructions mention using a venv. This virtual environment is a little like a quarantine for modules. Anything you do in the virtual environment, stays there. So if multiple programs need different versions of the same module, you don't have to keep re-installing that module when switching programs.

While the instructions work without one, it is definitely good practice to use one, so we highly recommend it!



****************************************
How to install (general users):
****************************************


1. Clone this github repo, and navigate to the directory this file is located in.
2. Using ``python -m venv env_GMAP``, create a virtual environment.
3. Activate the environment by running

   - (Unix)  ``source env_GMAP/bin/activate``
   - (Windows) ``env_GMAP\Scripts\activate.bat`` (doesn't work in powershell)
4. | (optional) Don't forget to compile the GMAP C library! There are also some maps that might need to have their C libraries installed, they will mention this in their README. Compilation instructions are system dependent, and given lower down in this file. After this installation, the program is ready for use.
   | This step is optional, because compiled versions of all files come with the program. If you'd rather compile yourself than using ours, this is the time to do so!
5. Install GMAP:

   - (general users) run ``python3 -m pip install .``
   - (developers) run ``python3 -m pip install -e ".[testing]"``
6. now, from anywhere, typing ``GMAP`` will start the program. If not, something has gone wrong. However, we're not done yet.
7. Once you're done using the program, you can deactivate the environment again by typing 'deactivate' (without the quotation marks in the terminal/command line).


****************************************
How to install (developers)
****************************************

1. Follow steps 1-6 of the non-developer guide.
2. Build your changes before opening a pull request. ``pip install build`` if you don't have it yet; then ``python -m build`` (all from repo home directory)
3. only relevant for some developers: If you want to fully profile the code and have GMAP generate the flow-chart-png for you, an installation of [graphvis](https://graphviz.org/) must be present. It is responsible for executing the 'dot' command on the command line. At the moment of writing this, a single test will fail if graphvis is not installed.


****************************************
How to use (after installing)
****************************************

1. Make sure you installed the program.
2. Activate the environment you created during installation. Activation instructions are in step 3 of the installation instructions.
3. Run the program; do what you want to do.
4. After you're done, you deactivate your environment, just as in step 7 of installation.
