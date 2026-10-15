.. _UserGuide_page_helpers:

##################
Helpers
##################

Helpers are intended to provide the user with functionality
that isn't (yet) integrated into GMAP. They are not a core part
of GMAP: helpers dont rely on GMAP and vice versa. 

If you have created any code that is small in scope, easy to use, 
that's tangental to GMAP, and that you would like to share, you can ask the developers to add them as a helper.

******
HamVis
******

HamVis is intended to visualize Hamiltonians.


It can be called with:
`python HamVis.py fname frames average cut outname scale` whilst your current working
directory is GMAP/helpers.
The variables in the line of code above mean:

fname is the name of the file you want to turn into a figure.

frames are the indices of the frames you want to investigate
seperated by ','. If '...' is given, the range between the
preceeding and following index is filled. So 0,1,2,3 == 0,...,3.

average should be True or False depending on wether to average
the frames.

cut is the area you want to plot given as 'x0,x1,y0,y1'
or 'False' if you dont want to exclude anything. x0 and y0 are
inclusive and x1 and y1 are exclusive, so 0,1,0,1 will only give
entry 0-0 of the Hamiltonian.

outname is the name the output files should have.

scale determines how the display of the couplings is scaled, the
should either be 'lin_lr', 'lin_ld' or 'log2' to have the
intensities of the couplings be displayed linearly with less
range or data or be displayed with less range logarithmically in
powers 2.

Everything should be correctly capitalized. 

For example: 

    python HamVis.py ../../../2N0A/Energy.bin 0,...,9 False 20,40,0,20 Bob log2

, will invoke HamVis.py. It will process the file Energy.bin in the folder ../../../2N0A/ .
Note that ../ will jump to the folder containing your current location. The frames 
0, 1, 2, 3, 4, 5, 6, 7, 8 and 9 will be processed. The program will not create an average
of the selected frames and will thus create 10 different images, one for each selected frame.
The graphs it will create will show positions everything that is both between and including 
20 and 39 in the x dimension and between and including 0 and 19 in the y dimension. 
The files will be named Bob and scaling one the couplings will be logarithmically. 
In other words, a coupling that is 1 higher in the graphs, will be twice as strong.

The output graphs will be named as {outname}_{frames}.pdf where frames 
specifically are the frames used to create the graph. So the first one in the
example will be named Bob_0.pdf