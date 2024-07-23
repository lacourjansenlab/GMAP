
# we only want to keep half of the oscillators
def GM_adjust_oscillators(Files, Map, Syst, oscillator_list):
    oscillator_list = [
        oscillator for oscillator in oscillator_list
        if oscillator.used_atoms[1] < oscillator.used_atoms[3]
    ]

    return oscillator_list
