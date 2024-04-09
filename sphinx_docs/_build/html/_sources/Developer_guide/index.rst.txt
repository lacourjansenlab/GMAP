.. _DevGuide_page_home:

################
Developers guide
################

These pages will contain information specifically for developers of the program.

.. note::
    Map != map()! Two main programs in the GMAP package (GEM and AIM) serve a specific purpose: converting an md trajectory into a Hamiltonian trajectory. In the spectroscopic community, this conversion is traditionally done using so-called maps. In this package, :class:`~GMAP.src.tools.MapReader.Map` objects contain all information on such a spectroscopic map. Do not confuse these objects with python's built-in map() function - it doesn't occur yet in the program as of writing this text (january 2024), and is not expected to, either.

.. toctree::
    
    Useful_resources
    program_flow/index
    Code_Style