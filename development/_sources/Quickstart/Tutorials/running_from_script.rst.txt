
################################
Running GMAP from a script
################################


The default way to use GMAP is to call it directly from the command line. However, there might be some situations where that is undesired, or simply does not work. For those cases, we've made it possible to run it through python, too! Here's a quick minimal working example:

.. code-block:: python

    # import the required module
    from GMAP.src.tools import cmd_interface as GM_ci

    # call the function
    GM_ci.cmd_interface(["GMAP"])


This example is equivalent to calling 'GMAP' in the command line.

Performing a GEM run:

.. code-block:: python

    # import the required modules
    from pathlib import Path
    from GMAP.src.tools import cmd_interface as GM_ci

    # find the input file (here, in same directory as this python script)
    input_file = Path("input_file.txt")

    # call the function
    GM_ci.cmd_interface(["GMAP", "GEM", "run", input_file.resolve()])


When using parameters that can have multiple choices provided, we know the last choice should be followed by a ``\;``. In python, the backslash character has a special meaning in strings, so we have to adjust a little:


.. code-block:: python

    # import the required modules
    from pathlib import Path
    from GMAP.src.tools import cmd_interface as GM_ci

    # find the input file (here, in same directory as from where this python
    # script is called)
    input_file = Path("input_file.txt")

    # call the function
    GM_ci.cmd_interface([
        "GMAP", "GEM", "run", input_file.resolve(),
        "--maps_to_use", "AmideBB", "AmideSC\\;"])

And that's about it! Make sure that you are always using the correct file. Optionally, make a path using an absolute path, so you know exactly which file is being read.

