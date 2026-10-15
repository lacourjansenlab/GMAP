
###############################################################################
Using custom parameters
###############################################################################

Here, we will look at the AmideBB map. The challenge? It should display different behaviour between runs, depending on the preferences of the user. It needs parameters just like GMAP has parameters (those a user puts in the input file, like verbose, trajectory_file, etc). We'll have a short look at how to create and use them. It's assumed you've familiarized yourself with the :ref:`map parameters page <AddMap_page_map_parameters>` already.

If you want, you can view the entire map in the maps directory. Do note, however, that this map had to do multiple things in order to run, so not all code in the map main.py and extra code files will be discussed here.

.. warning::
    Map-specific parameters are very powerful, so their use is very much encouraged. However, do make sure there is a need for the parameter: if a GMAP parameter can do the same, then don't add it!



****************************************
The problem
****************************************

There are some choices/assumptions that need to be made for the AmideBB map to run. One example is the model: there are multiple maps/models for the Amide-I stretch in proteins (Tokmakoff, Skinner, Jansen, Cho, Hirst), and only one can be used at a time. This map needs the user to make a choice which it will apply.

Another example is the Torii dipole angle. This is the example we will solve below, as it is a simpler case than the others. This will let us focus on the 'how' of parameters, instead of intricacies of the map. The point of this parameter is to allow the dipole moment to be at a different angle to the molecule than the original paper suggested.


****************************************
The solution
****************************************

GMAP has infrastructure available to make it as easy as possible to define parameters, but it does need to be used correctly. The first step is to define our parameter in the parameters.txt file in the map directory:

.. code-block:: text

    Torii_dipole_angle[float]      10  # in degrees

This line basically tells GMAP this: "This map (AmideBB) should have a parameter named 'Torii_dipole_angle'. When a user uses this parameter, make sure their choice is (or can be converted to) a single float. If a user doesn't specify the parameter, assume the value is 10.". The comment ('# in degrees') is not used, and is useful for coders/(map)developers looking in this file, as well as for advanced users as clarification.

Then, GMAP does its work. There is a default value given here in this map's parameter reference file, but the user can use a default parameter file, an input file, and define parameters on the command line. GMAP looks through all these sources, interprets them, finds out what choice to use. Then it checks whether the choice is indeed a float, and turns it into one. Then, it is made available to our map for use in further code.

So, lets use this parameter in a function! As the code for AmideBB is rather complicated, the code below will be a simplified example, leaving out anything not relevant here.

.. code-block:: python

    import GMAP.src.tools.system_reader as GM_sr

    def GM_calculate_dipole(map_, system, osc):  # actually, MC_CM.calc_dipole_torii
        # COvec is the vector pointing from central carbon to oxygen
        # CNvec is the vector pointing from central carbon to nitrogen
        # Both are important for defining directions/axes in the molecule
        r_pos, COvec, CNvec = dipole_pos(system, osc)


        dri = 0.665*COvec + 0.258*CNvec
        dridri = GM_mf.dotprod(dri, dri)
        COvecdri = GM_mf.dotprod(COvec, dri)
        # direction of the dipole moment
        itheta = np.float32(
            1 / np.tan(GM_con.deg2rad * map_.run_pars.Torii_dipole_angle))
        r_vec = dri - (COvecdri + np.sqrt(dridri - COvecdri*COvecdri)*itheta)*COvec

        # giving the dipole moment the correct magnitude
        r_vec /= GM_mf.vec3_len(r_vec)
        r_vec *= map_.core.dipole_gas_phase

        return r_vec, r_pos


Yes, the example is still quite mathy, but we can ignore most of that. It is here because vector addition/multiplication is a lot cheaper than the sines/cosines this code otherwise needs. Our focus is mainly on the line defining the factor itheta (inverse theta - although that's not important for us). In that line, we can see where the GMAP parameters are stored: in the ``RunPars`` object stored as an attribute of the ``map_`` object. Within that run_pars, we just look for the name that we chose in the parameters file, and we get the specified datatype back: in this case a float.

A brief note on this ``map_.run_pars`` object - it stores all parameters of the map it is an attribute of. It also contains a link to the main RunPars object of GMAP - the one that contains the choices for the main program (like verbose and trajectory_file). Both have the same structure and way of use. That main runpars object can be accessed using ``map_.run_pars.main_run_pars``, but **changes to it should never be made!**

Small bonus: this map also shows an example on how to read values from the core.txt file. Know that there are two versions in the code. One is called rawcore - it is the most crude direct parse from the text file. The other is the ``map_.core`` object: it contains more parsed/checked information of more usable formats. Unless abslutely needed, this ``map_.core`` version should be used over the other one!
