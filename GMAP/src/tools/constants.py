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


printed_colors = {
        (0, 0, 0): (0, False),
        (128, 128, 128): (0, True),
        (192, 192, 192): (7, False),
        (255, 255, 255): (7, True),
        (128, 0, 0): (1, False),
        (255, 0, 0): (1, True),
        (128, 128, 0): (3, False),
        (255, 255, 0): (3, True),
        (0, 128, 0): (2, False),
        (0, 255, 0): (2, True),
        (0, 128, 128): (6, False),
        (0, 255, 255): (6, True),
        (0, 0, 128): (4, False),
        (0, 0, 255): (4, True),
        (128, 0, 128): (5, False),
        (255, 0, 255): (5, True)
    }

printed_colors_r = {v: k for k, v in printed_colors.items()}
