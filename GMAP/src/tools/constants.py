"""
A file containing all kinds of constants that the program might need.
"""


import numpy as np


# constants
h = 6.62607015e-34  # planck constant in (J Hz-1)
c = 2.99792458e8  # speed of light in (m s-1)
e = 1.602176634e-19  # elementary charge in (coulombs)
deg2rad = np.float32(np.pi/180)  # 1 degree in radians

# lengths
angstrom = 1e-10  # angstrom in m
bohr = 5.29177210544e-11  # bohr in m
bohr2ang = bohr/angstrom  # converting from bohrs to angstroms
ang2bohr = angstrom/bohr  # converting from angstroms to bohr

# energies
eV = 1.602176634e-19  # eV in J
cm2eV = 100 * h * c / eV

# dipoles
Debye = 1e-21 / c  # debye in (coulomb meter)
ea0 = e * bohr  # ebohr in (coulomb meter)
Debye2ea0 = Debye/ea0
