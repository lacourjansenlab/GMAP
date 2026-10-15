.. _AddMap_units:


#####
Units
#####

When creating a map, a lot of questions about units within the program may arise. This section hopes to answer all of those questions.


***********
Basic units
***********

The program uses the following units:

=============   =========================================
Quantity        unit
=============   =========================================
distance        angstrom (Here: :math:`a`)
charge          elementary charge (:math:`e`)
mass            unified atomic mass unit (:math:`u`), Dalton (:math:`Da`)
energy          wavenumbers (:math:`cm^{-1}`)
dipole moment   Debye
=============   =========================================



**********************************
Units expected for map input files
**********************************

When creating a map, the program wants to know quite a few values from you. This section aims to clarify what units to use. If you instead want to know units used in specific data structures in the program (for when writing code in a maps main.py file, for example), go to the next section.


Maps in the Singles directory
=============================

core.txt
--------

frequency_gas_phase
    This base value is expected in units of wavenumbers.

dipole_gas_phase
    This base value is expected in units of Debye.


File provided for frequency_data_file_linear
--------------------------------------------

The values in this file are recognized as an array (a matrix). This array is multiplied element-wise with the VEG array (see VEGout of Oscillator below), and the resulting values are summed together and added to the gas phase frequency. Therefore, each element (after multiplication) should be in units of wavenumbers. This means that the values in this file should do the following conversions through multiplication:

column 0
    These values should transform the potential (:math:`e/a`) to wavenumbers.

column 1-3
    These values should transform the electric field (:math:`e/{a^2}`) to wavenumbers.

column 4-9
    These values should transform the electric gradient (:math:`e/{a^3}`) to wavenumbers.

.. tip::
    We are aware that not all maps are published with Angstrom in mind. Many infrared maps, for example, use Bohr. Other units can be used as follows:

    When using Bohr, you can use the map keyword 'assume_length_units', and indicate Bohr. Then, you can replace all the 'a' in the units above with bohrs (so, for example, for potential, your map should transform :math:`e/a_0` to wavenumbers).

    When using other units, you can choose to keep the arrays in your own units, and convert them yourself in the function 'post_init()' in the maps main.py file. After conversion, the values should match the description above.



File provided for frequency_data_file_quadratic
-----------------------------------------------

The values in this file are recognized as an array (a matrix). This array is multiplied element-wise with the element-wise square of the VEG array (see VEGout of Oscillator below), and the resulting values are summed together and added to the gas phase frequency. Therefore, each element (after multiplication) should be in units of wavenumbers. This means that the values in this file should do the following conversions through multiplication:

column 0
    These values should transform the potential squared (:math:`{e^2}/{a^2}`) to wavenumbers.

column 1-3
    These values should transform the electric field squared (:math:`{e^2}/{a^4}`) to wavenumbers.

column 4-9
    These values should transform the electric gradient squared (:math:`{e^2}/{a^6}`) to wavenumbers.

.. tip::
    We are aware that not all maps are published with Angstrom in mind. Many infrared maps, for example, use Bohr. Other units can be used as follows:

    When using Bohr, you can use the map keyword 'assume_length_units', and indicate Bohr. Then, you can replace all the 'a' in the units above with bohrs (so, for example, for potential, your map should transform :math:`{e^2}/{{a_0}^2}` to wavenumbers).

    When using other units, you can choose to keep the arrays in your own units, and convert them yourself in the function 'post_init()' in the maps main.py file. After conversion, the values should match the description above.



File provided for dipole_data_file
----------------------------------

The values in this file are recognized as an array (a matrix). This array is multiplied element-wise with the VEG array (see VEGout of Oscillator below), and the resulting values are summed together and added to the gas phase dipole moment. Therefore, each element (after multiplication) should be in units of Debye. This means that the values in this file should do the following conversions through multiplication:

column 0
    These values should transform the potential (:math:`e/a`) to Debye

column 1-3
    These values should transform the electric field (:math:`e/{a^2}`) to Debye

column 4-9
    These values should transform the electric gradient (:math:`e/{a^3}`) to Debye

.. tip::
    We are aware that not all maps are published with Angstrom in mind. Many infrared maps, for example, use Bohr. Other units can be used as follows:

    When using Bohr, you can use the map keyword 'assume_length_units', and indicate Bohr. Then, you can replace all the 'a' in the units above with bohrs (so, for example, for potential, your map should transform :math:`e/a_0` to Debye).

    When using other units, you can choose to keep the arrays in your own units, and convert them yourself in the function 'post_init()' in the maps main.py file. After conversion, the values should match the description above.


*********************************
Units of existing data structures
*********************************

There are a lot of basic properties available in the program by default. This is an overview of the units (and other standards) of each of them:


Attributes of SingleCore class
==============================

Some of these overlap with the Oscillator class. While this is a blueprint, the Oscillator class represents a specific case - so the indices are in a different 'base'.

These represent the choices/values made in a Map's core.txt file.

used_atoms
    Which atoms matter to oscillators of this type. Zero-based, but NOT in system.atnums. Instead, it is in regards to the atoms defined in functional_group.

elecctrostatic_atoms
    For which atoms the electrostatic properties should be calculated. In 'units' of used_atoms.

local_atoms
    Which atoms cannot influence the elecctrostatic properties computed for this oscillator. In 'units' of used_atoms.

dipole_gas_phase
    The base magnitude of the dipole moment. In units of Debye.

dipole_data_array
    The map coefficients stored in the file indicated by the map keyword dipole_data_file. The units should be fit for converting the units of Oscillator.VEGout to Debye by multiplication.

frequency_gas_phase
    The base absorption frequency. In units of wavenumbers.

frequency_data_array_linear
    The map coefficients stored in the file indicated by the map keyword frequency_data_file_linear. The units should be fit for converting the units of Oscillator.VEGout to wavenumbers by multiplication.

frequency_data_array_quadratic
    The map coefficients stored in the file indicated by the map keyword frequency_data_file_quadratic. The units should be fit for converting the square of the units of Oscillator.VEGout to wavenumbers by multiplication.



Attributes of Oscillator class
==============================

Many of these overlap with the Map class. While the Map class is a blueprint, this represents a specific case - so the indices are in a different 'base'.

dipole_pos
    (only exists if dipoles are calculated during this run, which is true for choices 'ham', 'ene', and 'dip')

    The position of the dipole moment of this oscillator in angstrom (cartesian / MD coordinates).

dipole_vec
    (only exists if dipoles are calculated during this run, which is true for choices 'ham', 'ene', and 'dip')

    The dipole moment of this oscillator in Debye.

electrostatic_atoms
    For which atoms the electrostatic properties should be calculated. In 'units' of System.atnums

local_atoms
    Which atoms cannot influence the elecctrostatic properties computed for this oscillator. In 'units' of System.atnums

oscix
    The oscillator-index of this oscillator. Zero-based. This is the position in the output files etc.

positions_box
    The positions of each of the atoms in used atoms, transposed to box coordinates. Box coordinates means 'expressed in terms of box vectors'. These are used for computing differences, average positions, etc. Because of these box coordinates, they are dimensionless fractional coordinates.

rotation_matrix
    The local basis of this oscillator expressed in terms of cartesian coordinates. The x, y and z components must be orthonormal. In units of angstrom.

used_atoms
    Which atoms matter to this oscillator. In 'units' of System.atnums.

VEGout
    The electrostatic properties computed for this oscillator. A 2D structure with a row for each atom in Oscillator.elecctrostatic_atoms, and 10 columns. Is initially calculated in the original MD basis, but almost immediately rotated to the oscillators local 

    The first column represents the potential, computed/expressed as elementary charge over angstrom: :math:`e/a`.

    The next three columns represent the x, y and z component of the electric field respectively, computed/expressed as elementary charge / angstrom squared: :math:`e/{a^2}`

    The last 6 columns represent the electric gradient tensor (the xx, yy, zz, xy, xz, yz components, respectively), computed/expressed as elementary charge / angstrom cubed: :math:`e/{a^3}`

VEG_refpos
    The position on which the sphere defining the electrostatics should be centered. In cartesian coordinates (as MD), in angstrom.



Attributes of System class
==========================

angles
    The angles between the three box defining vectors (see boxvects and boxdims), in degrees.

atnums
    These are indices, zero based. The first atom in the MD files gets number 0. These numbers never reset - each atom has a unique atnum. These atnums are used as identifiers for the atoms.

boxdims
    The length of each of the three box-defining vectors, in angstrom.

boxvects
    The three vectors defining the MD simulation box, in angstrom.

boxvects_inv
    The inverse of the boxvects matrix. Units of angstrom :math:`^{-1}`

charges
    These are the charges of the atoms, as used in the MD calculations. These charges can be partial charges to represent how charge is distributed in a molecule.

halfbox
    Same as boxdims, but halved. Also in angstrom.

masses
    These are the masses of the atoms in daltons. For those unsure - hydrogen has a mass of 1.008, carbon-12 has a mass of exactly 12.

positions
    These are the positions of the atoms in cartesian coordinates. They are in angstrom. However, due to the :ref:`periodic boundary conditions<Theory_page_PBC>` of the MD system, these can be 'wrapped around'. The positions should always lie within a single positive whole box, meaning that each of the three components of the position vector is positive, and will never exceed a single box length.

resnums
    These are indices, zero based. The first residue in the MD files gets number 0. These numbers never reset - each residue has a unique resnum. If multiple atoms belong to the same residue, all those atoms get the same resnum.

safesphere
    The radius of the sphere within which distances can be calculated accurately, in angstrom. If the length of any vector exceeds this size, there is a change that vector is not actually the shortest one available. This has to do with :ref:`periodic boundary conditions<Theory_page_PBC>`.



