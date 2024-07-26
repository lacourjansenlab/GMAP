

def GM_adjust_map_core_raw(Files, Map):

    all_amino_acid_codes = [
        "ARG", "HIS", "LYS", "ASP", "GLU", "SER", "THR", "ASN", "GLN",
        "CYS", "GLY", "PRO", "ALA", "VAL", "ILE", "LEU", "MET", "PHE",
        "TYR", "TRP"
    ]
    amino_acids_joined = ",".join(all_amino_acid_codes)

    oldentry = Map.rawcore["functional_group"]

    Map.rawcore["functional_group"] = [
        [
            word.replace("anyprot", amino_acids_joined)
            for word in struct
        ] for struct in oldentry
    ]
