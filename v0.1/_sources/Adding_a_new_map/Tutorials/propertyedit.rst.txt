
###############################################################################
Changing properties
###############################################################################

Sometimes, the choices/values used by GMAP for properties do not make sense for a particular map. Here, we look at an example from the bacteriochlorophyll c map (Bchl-c). You can view the entire map in the maps directory.



****************************************
The problem
****************************************

It is desired that the map is implemented such that the distance between two Bchl-c molecules is defined as the distance between their central magnesium atoms. This distance is used when calculating the electrostatic influence of one molecule on the other. While the core.txt file allows to define the 'center' of the 'influenced' chromophore, it does not allow to define that of the 'influencing' chromophore. 


****************************************
The solution
****************************************

in the core.txt file, we add the following line:

.. code-block:: text

    VEG_reference       position 26      # position of Mg

This line says 'when calculating the electrostatics felt by a chromophore of this name/type, the distance to any influencing atoms/groups/molecules should be calculated from the position of the atom numbered 26 (being magnesium)'.
The atom numbered 26 is the magnesium atom, because that's what on that position in the used_atoms list.

Now, we just need a way to define what point of the influencing Bchl-c molecules we should calculate the distance to. This should be done using the main.py file, to which we add the following function:

.. code-block:: python

    def GM_pre_frame(map_,system):
        mg_idx = 26  # in the current funcgroup file, Mg is at index 26.
        # read choice for treat_box parameter
        boxtreat = map_.run_pars.main_run_pars.treat_box

        for oscillator in system.oscillators_ordered["BChl-c"]:
            resnum = system.resnums[oscillator.used_atoms[mg_idx]]

            # Overwrite center of mass (2 times)
            system.residues.CoM_box[resnum] = oscillator.positions_box[mg_idx]
            if boxtreat == "orthorhombic":
                system.residues.CoM[resnum] = oscillator.positions[mg_idx]

This function is called by GMAP at the beginning of every new frame, after GMAP did its own pre-frame initialization. It obtained the new atom positions for this frame, updated all kinds of arrays, etc.

The ``system`` object contains a lot of information about the MD system. The dictionary ``system.oscillators_ordered`` contains, for each requested map (the keys of the dictionary), a list of all the oscillators of that type. So, the for-loop here loops over all Bchl-c molecules that GMAP identifies.

The next step is to find out what the residue number of this specific Bchl-c molecule is. For this, we have a list with the residue number of each atom (more specifically, the residue number of the residue that atom is in) called ``system.resnums``, in which we look up our Bchl-c molecule. We need an atom, not molecule, so we ask for the residue number of the magnesium atom. The ``oscillator.used_atoms[mg_idx]`` gives us the atom number of the magnesium atom.

The last step is to use the found residue number to find the location where that residue's center of mass is saved. ``system.residues`` contains information on a per-residue basis, so ``system.residues.CoM_box`` has all centers of mass in box coordinates (CoM has them in cartesian). This molecule of Bchl-c's center of mass is therefore ``system.residues.CoM_box[resnum]``. We overwrite the current saved center of mass with the current position of the magnesium atom (in box coordinates), which we can find in ``oscillator.positions_box[mg_idx]``. We do the same with the cartesian-coordinate version of the center of mass and position, but only if they are actually used by the program (which is only the case for orthorhombic mode - we expect to actually use this mode a lot).

Why do we have to define both separately? The program uses both, and only does the conversion once. At the beginning of each frame, GMAP calculates the centers of mass once (see GEM.py, trj_loop(), call to System.update_properties(), which is defined in system_reader.py, which has a call to clib.calc_CoM_box()), but does this in box coordinates, as that's the cheaper way of calculating them. After they've been calculated, if the program runs in orthorhombic mode, the box CoMs are converted to cartesian coordinates once, and the program never changes them, so doesn't update this conversion in between steps. We therefore have to do both to make sure we always use the correct values for things!

