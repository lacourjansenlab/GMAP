.. _UserGuide_page_map_parameters:

==============
parameters.ref
==============

This is an optional file containing all keyword parameters the map needs.
The file must be of the name 'parameters.ref' for it to be recognized.

Any parameter specified here can be set/supplied by the user, so choices
can vary for each calculation.

In the program, the contents of this file are stored in the map-specific
instance of a :class:`~GMAP.src.tools.MapReader.Map` object, as the `RefPars`
attribute.
