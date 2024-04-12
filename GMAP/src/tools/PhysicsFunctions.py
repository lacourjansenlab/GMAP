

def calc_frame(Printer, RunPars, System, dipoles, hamiltonian):

    for oscix, oscillator in enumerate(System.oscillators):
        if any(data in RunPars.output_data for data in ("ham", "dip")):
            dipoles[oscix:] = calc_dipole()

        if "ham" in RunPars.output_data:
            hamiltonian[oscix, oscix] = calc_frequency()
            prep_coupling()

    # for every oscillator pair (that should be covered) - calc_coupling

    return hamiltonian, dipoles


def calc_dipole():
    return


def calc_frequency():
    return


def prep_coupling():
    return


def calc_coupling():
    return
