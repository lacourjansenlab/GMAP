.. _Theory_page_PBC:

##################################
Periodic boundary conditions (PBC)
##################################

When performing an MD simulation, it is not possible to model infinitely many atoms. Yet, to properly model the forces acting on an atom, it is not an option to just have your cloud of atoms stop. This problem is solved by assuming that the box in which all atoms live, is repeated infinitely, much like grid paper.

In practice, this means that 2-dimensional analogue of an MD system is actually pacman: when you leave the pacman field on the right side, you'll enter it again on the left. Same with the top and bottom. In an MD system, if an atom crosses one of the sides of the box, it will be moved to the other side. A single atom can be considered to have infinite images, one in every 'copy' of the box. MD software considers all infinite copies by using the particle mesh ewald (PME) approximation.

While GMAP does not have to do the same extensive calculations as MD software, it is subject to the consequences of these PBC. When calculating anything geometrical, the program must ask itself - am I using the correct image of this particle? If, for example, you want the distance between two atoms, you must make sure that you take the two closest images of those atoms. The simulation box is large enough, that the closest and second closest are so different in distance, that the latter does already not make sense.

The influence of the PBC is noticable in a few parts of the code, and not all parts deal with it in the same way. The rest of this page is an overview of which parts of the code have to deal with the PBC, and how they do it.


***********************************
Calculating vectors for oscillators
***********************************

The properties calculated for a single oscillator should not change if the entire box is rotated. Therefore, maps usually rotate the cartesian coordinates to a localized coordinate system, where the axes are defined by the shape of the molecule. This allows a map to let a property of an oscillator depend on the electrostatic properties in a given direction. For example, the frequency of absorbed light is dependent on the strength of the electric field along a certain atomic bond.

To allow this, :ref:`a map specifies its local coordinates<map_defining_xyz_uvec>` in terms of atom positions. It can, for example, say something like "my local x axis should point in the same direction as this oxygen atom is located compared to this carbon atom". This could be expressed by saying the x vector is defined by subtracting the position of the carbon atom from that of the oxygen atom.

It is this kind of maths with positions that leads to trouble with PBC. Just subtracting atom positions (or adding them, or dividing them by a scalar) can lead to the wrong results. That is why these operations are not performed in cartesian coordinates, but rather in box coordinates. Box coordinates are basically the transformation performed using the vectors defining the bounding box. Any MD package will make clear what kind of box you are using. Any box can be defined using three vectors. The first vector is commonly used for the shortest side of the box, and will point along the x axis. The second vector is the middle side of the box, living in the xy plane, and the third is the longest side of the box, living in xyz space.

Then we can expres an atom's position in terms of these vectors - for example, 0.5*x + 0.2*y + 0.6*z. Here, note that, if an atom lied inside of the box initially, all three coefficients should be positive, and between 0 and 1. Or, for a slightly different convention, between -0.5 and 0.5.

The neat thing is that if we add, subtract, average, or anything like that within these box coordinates, we will always end up in a valid position. It might not be the image that lies within the central box, but we will always find an image. Then, we only need to remove the integer part (and keep the decimal), to find the image that lies within the box. Finally, this central image can be converted back in cartesian coordinates for further use.

To explain the above in (pseudo) python code:

.. code-block:: python
    :caption: an idea as to how to calculate the average position of the atoms 1 and 0 of any given oscillator.

    import MDAnalysis as MDA
    import numpy as np

    universe = MDA.Universe()

    box_vectors = MDA.lib.mdamath.triclinic_vectors(
        universe.dimensions
    )
    box_vectors_inv = np.linalg.inv(box_vectors)

    # MDA returns numpy arrays
    local_positions_cart = universe.atoms.positions[oscillator.used_atoms]

    # @ is shorthand for matrix multiplication
    local_positions_box = local_positions_cart @ box_vectors_inv

    # keep the decimal part only
    local_positions_box -= np.floor(local_positions_box + 0.5)

    avg_pos = (local_positions_box[1] + local_positions_box[0]) / 2
    avg_pos -= np.floor(avg_pos + 0.5)  # keep the decimal part only

    avg_pos_cartesian = avg_pos @ box_vectors

    



