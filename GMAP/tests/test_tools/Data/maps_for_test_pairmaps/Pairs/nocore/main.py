
def GM_calc_coupling(Printer, Map, Syst, hamiltonian):
    for pair in Map.allpairs:
        oscix1, oscix2 = pair
        J = 1.234
        hamiltonian[oscix1, oscix2] = J
        hamiltonian[oscix2, oscix1] = J