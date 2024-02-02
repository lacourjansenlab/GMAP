

def GM_adjust_map_core_raw(Files, Printer, Map):

    all_amino_acid_codes = [
        "ARG", "HIS", "LYS", "ASP", "GLU", "SER", "THR", "ASN", "GLN",
        "CYS", "GLY", "PRO", "ALA", "VAL", "ILE", "LEU", "MET", "PHE",
        "TYR", "TRP"
    ]
    amino_acids_joined = ",".join(all_amino_acid_codes)
    amino_acids_joined = f"[{amino_acids_joined}]"

    Map.rawcore["functional_group"] = [
        # first (and only) struct
        [
            amino_acids_joined,
            "N", "CA", "C(1)", "O",
            amino_acids_joined,
            "N(1)", "H", "CA", "C"
        ]
        # could later add more in case of special caps?
    ]
