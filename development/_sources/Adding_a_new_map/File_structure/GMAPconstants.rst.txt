.. _AddMap_FileStruct_GMAPconstants:

####################################################
Constants available in GMAP.src.tools.constants
####################################################

GMAP needs a handful of (physical) constants to run. Here you find an overview of the constants available in the GMAP constants module.

h
    The Planck constant expressed in Joule/Hz, with a value of 6.62607015e-34. This is an alias for ``scipy.constants.h``.

c
    The speed of light expressed in meter/second, with a value of 2.99792458e8. This is an alias for ``scipy.constants.c``.

e
    The elementary charge expressed in Coulombs, with a value of 1.602176634e-19. This is an alias for ``scipy.constants.e``.

eps
    The vacuum permittivity in Farad/meter, or C^2 kg^-1 m^-3 s^2. It has a value of 8.854187818814e-12. This is an alias for ``scipy.constants.epsilon_0``.

deg2rad
    One degree expressed in radians. Multiplying a value in units of degrees with this number will convert it to radians. It has a value of 0.017453292. Calculated as ``np.float32(np.pi/180)``.

rad2deg
    One radian expressed in degrees. Multiplying a value in units of radians with this number will convert it to degrees. It has a value of 57.29578. Calculated as ``np.float32(180/np.pi)``.

angstrom
    One angstrom expressed in meters, with a value of 1e-10.

bohr
    The bohr radius expressed in meters, with a value of 5.29177210544e-11.

bohr2ang
    One bohr expressed in angstroms. Multiplying a value in units of bohr with this number will convert it to angstroms. It has a value of 0.52177210544. Calculated as ``bohr/angstrom``.

ang2bohr
    One angstrom expressed in bohrs. Multiplying a value in units of angstrom with this number will convert it to bohrs. It has a value of 1.8897261259077824. Calculated as ``angstrom/bohr``

eV
    One electronvolt expressed in Joules, with a value of 1.602176634e-19. This is an alias for ``scipy.constants.eV``.

cm2eV
    The factor by which to multiply a value in wavenumbers to convert it to units of electronvolt. It has a value of 0.00012398419843320026, and is calculated as ``100 * h * c / eV``.

J2cm
    The factor by which to multiply a value in Joules to convert it to units of wavenumbers. It has a value of 5.0341165675427096e22, and is calculated as ``1 / (100 * h * c)``.

i4pieps
    Also known as the Coulomb constant, this is the constant of proportionality in coulombs law. It is expressed in SI units N*m^2*C^-2. It has a value of 8.98755178615e9 and is calculated as ``1 / (4 * np.pi * eps)``.

e2i4pieps_angcm
    The square of the elementary charge multiplied with the coulomb constant, all expressed in angstroms for distance and wavenumbers for energies. While this value might seem arbitrary, it is used often for TrEsp charges. It has a value of 116140.9732096081 and is calculated as ``e * e * i4pieps * J2cm / angstrom``.

Debye
    One Debye expressed in coulomb meter. It has a value of 3.33564095198152e-30 and is calculated as ``1e-21 / c``.

ea0
    The atomic unit of electric dipole moment 'elementary charge * bohr' expressed in coulomb meter. It has a value of 8.478353619788951e-30 and is calculated as ``e * bohr``.

Debye2ea0
    The factor to multiply with a value in Debye to convert it to atomic units. It has a value of 0.3934302697868071 and is calculated as ``Debye / ea0``.
