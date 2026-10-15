
###############################################################################
Adding oscillators/chromophores (and some custom couping)
###############################################################################

Here, we will look at the water map. For the water map we want to use more chromophores than GMAP normally finds, so we'll learn how to define multiple chromophores. To do this, we will make use of existing functionality within GMAP.

If you want, you can view the entire map in the maps directory (in the location GMAP/maps/Singles/Water/). Do note, however, this map has to perform multiple tasks in order to run, so not all code in the map main.py will be discussed here.



****************************************
The problem
****************************************

When GMAP looks for a molecule specified by a map, it will find it once. However, to get an accurate simulation of the water (a)symmetric stretch, the model we want to apply requires a separate calculation for the two OH bonds in water, which are then coupled in a special way. Adding the same molecule (but in reverse) as an extra newstruct to the funcgroup file does not work.



****************************************
The solution
****************************************

Conveniently enough, GMAP already gives the option to confirm the chromophores (named oscillators in the code) it found. We can use the ``GM_adjust_oscillators`` function to add some more chromophores:

.. code-block:: python

    import GMAP.src.tools.system_reader as GM_sr

    def GM_adjust_oscillators(map_, system, oscillator_list):
        oscillator_list_adjusted = []
        for oscillator in oscillator_list:
            # add the one found by GMAP (the first bond of this molecule)
            oscillator_list_adjusted.append(oscillator)
            # add the oscillator representing the other bond of this molecule
            oscillator_list_adjusted.append(GM_sr.Oscillator(
                system,
                [oscillator.used_atoms[0], *oscillator.used_atoms[2:0:-1]],
                map_))

        return oscillator_list_adjusted

That's a lot to take in, lets take it step by step.

This function is designed to pass us a list of :class:`~GMAP.src.tools.system_reader.Oscillator` objects, and expects us to return the 'correct' one based on the one we were given. What happens here is that we create a new list to store oscillators. Then, for every oscillator we encounter in the list provided, we add both it, and a second one for this molecule to the new list. After we've done this for all oscillators in the provided list, we return our new one.

But, how do we add that second oscillator? What's happening with that ``GM_sr.Oscillator`` call? Well, we're making smart use of the original definition of the Oscillator objects. The oscillators in the provided oscillator list were also created with a call to that same function. If you were to go to the source code and look at the docstring of the oscillator object constructor (or look it up in the documentation of :class:`~GMAP.src.tools.system_reader.Oscillator`), you find the following information::

    Stores all information on a single oscillator.

    Parameters
    ----------
    system : :class:`~GMAP.src.tools.system_reader.System`
        The class containing all the information on the system of the
        MD trajectory.
    atoms : list of int
        The indices of the atoms that make up this oscillator. All atoms
        specified in functional_group are in here.
    map_ : :class:`~GMAP.src.tools.map_reader.SingleMap`
        The map that this oscillator belongs to.

So, if we want to make our own oscillator object, we need to pass it 3 things. The first and last are not a problem, they were provided to us as arguments to this function. The second is where the trick is. If we look at the core.txt file of the water map, or the definition of it's dipole function, we see that it almost exclusively only uses it's 0th (oxygen) and 1th (HW1) atoms for calculations. Therefore, we want to create another oscillator, but for it, swap the oneth and twoeth atom.

For the second argument, we have to provide a list of atom indices. Conveniently, these indices are already stored in our current oscillator's used_atoms, so we just have to reorder them into a new list provided to the ``GM_sr.Oscillator`` constructor. 



*******************************************************************************
Bonus: distinguishing inter- and intramolecular couplings
*******************************************************************************

This bonus will be brief, as this will not be a general introduction in creating coupling maps. Instead, we will quickly introduce the general structure of files, and then show how the water map distinguishes inter- and intramolecular coupling, so these oscillator pairs we made before can become the (a)symmetric stretches.

For starters, the water coupling map actually consists of two separate coupling maps. We have Water_Intra for intermolecular couplings, and WaterCoupling for 'sorting' our water couplings. The idea is that, when a user wants to couple the water molecules, they tell GMAP they want to use the WaterCoupling map. The WaterCoupling map is then responsible for assigning any intermolecular couplings to the dipole-dipole map, and the intramolecular ones to the Water_Intra map.

In the WaterCoupling map we therefore added the corresponding protections to the core.txt file::

    require_pairs         DipDip Water_Intra
    singles_whitelist     Water

Firstly, as this map will be assigning oscillator pairs (couplings) to the DipDip and Water_Intra maps, it tells GMAP it can't function without them being present. Secondly, it also says it can only be applied to couplings between oscillators of type Water (i.e. from the Water singles map).

Then, in main.py, it makes use of the ``GM_change_coup_type`` function - this allows a coupling map to assign a different coupling map to the provided pair. That's exactly what we want to do here! The code below is an approximation of the original code, only focussing on how we do this switch.

.. code-block:: python

    def GM_change_coup_type(map_, system, oscix1, osc1, oscix2, osc2):
        # If the oscillators are in the same water molecule we must choose intra
        # Check if the OH stretches share the same oxygen
        if osc1.used_atoms[0] == osc2.used_atoms[0]:
            return "Water_Intra"
        # The OH stretches are in different molecules. If the user specified to use
        else:
            return "DipDip"

The difficulty here might stem from the provided arguments. We want to analyse the coupling between two oscillators, here labelled 1 and 2. For each, we get the oscillator index (oscix), and the oscillator object itself (osc). In our case, it makes more sense to use the oscillator objects. 

Then, we have one question remaining: are these two oscillators part of the same molecule, or not? The easiest way to check is to see if both have the same oxygen atom. If they do, they must be in the same molecule. Therefore, we check whether the atom index in used_atoms, on the zeroeth index (as that's where our water is defined in the Water funcgroupfile) is the same for both!
