.. _UserGuide_page_references_file:

##############
references.bib
##############

(This applies both to singles and pairs maps)

This is an optional file containing all references that might need to be cited when a paper uses a GMAP calculation. Each reference is present in the default .bib format, with the exeption of two extra (mandatory!) fields being present. It is highly recommended to add a references file to a map, as it makes it a lot easier (and thus, more likely) for users to see which references to cite, and do so. Credit where credit is due!

When a calculation is performed, GMAP checks if a map is involved in the calculation at all. Only if the map was both requested (either by the user or by another map) and used (i.e. its molecules are present), its references are considered.

Figuring out what references to print for a map is a two-step process:
- The first step is to ask the map if it is okay with the current .bib file contents. This step is important for maps which have multiple models with separate references (like the amide maps that come with GMAP), as only the model used should be referenced, and the others shouldn't. A map influences this step through the ``GM_report_references`` function in the main.py file of the map. Map makers will probably want to use the 'mapkey' field for this purpose.
- The second step is for GMAP, to see if a reference was actually used for that specific calculation. This is because a reference can only be for a single property, like the dipole moment. But if the dipole moment is not used, it would be incorrect to list that resource for that calculation. This is where the 'reporttext' field is useful: it mentions which message should be printed for that resource, for which calculation output. If none of the outputs mentioned in the reporttext field were calculated, the reference will not be cited.



***********
File layout
***********

Personally, I don't 'create' these files, but use a downloaded .bib from somewhere. A lot of journals allow to download the reference to a paper already in the .bib format. I add extra flags, might clean up some fields, but use the .bib files themselves. That means that the .bib file here has the exact same format as bibtex standard .bib files!



********************************
Procedure for making these files
********************************

For me, the procedure starts with a .bib file from your reference manager (Zotero/Mendeley/etc), or downloaded from the paper website. Then, I take the following steps:
- Is all the information correct? I look at all fields (both names and contents) just to be sure.
- Check whether the title is in a usable format. Some .bib-using-programs do weird stuff with capitalization of words, so especially the title field might have some extra characters to protect the capitalization. GMAP doesn't change capitalization, and would directly print these special characters. If you don't want them to show up, do some polishing now.
- Check whether the authors are correct. The assumed format is that authors are separated by ' and ', and that the family name is provided first, with the given name after. The family name is separated from the given names using a comma. For example, a paper from the brothers A and B LastName would have the following author field: "LastName, A and LastName, B". An author can have multiple first- and last names, and the first names may either be letters (initials), or full names. Again, here, don't forget capitalization!
- Check whether all desired fields are present. GMAP can interpret the following fields:  title, author, year, month, journal, volume, number, pages, issn, doi, url.
- Add the mapkey and reporttext fields. See the next section for more details.
- Run the program with your map to check whether the right references show up at the right time, and whether they are displayed as intended.


************
mapkey field
************

This field has the sole purpose of allowing a map-creator to easily select the correct references. The exact keys you use are completely up to you, as long as individual keys are separated by semicolons. Still, I think the following example would be useful to know how to actually use the field.


In this example, I will be using some references from the AmideBB map, with a few changes:
- To not obscure the details that matter, I'm leaving out quite a few fields from the .bib. Please do try to include those in your files!
- The code is to give an idea, not exactly as present in the map.

.. code-block:: text

    @article{TsuboiThomasJr.1997,
        title = {Raman Scattering Tensors in Biological Molecules and Their Assemblies},
        author = {Tsuboi, Masamichi and Thomas Jr., George J.},
        mapkey = {RamanAmide},
        reporttext = {ram: raman tensor of AmideBB}
    }

    @article{ReppertTokmakoff2013,
        title = {Electrostatic Frequency Shifts in Amide I Vibrational Spectra: Direct Parameterization against Experiment},
        author = {Reppert, Mike and Tokmakoff, Andrei},
        mapkey = {EmapTokmakoff},
        reporttext = {ham, ene: frequency of AmideBB}
    }

    @article{JansenKnoester2006a,
        title = {A Transferable Electrostatic Map for Solvation Effects on Amide I Vibrations and Its Application to Linear and Two-Dimensional Spectroscopy},
        author = {Jansen, Thomas la Cour and Knoester, Jasper},
        mapkey = {EmapJansen; DmapJansen},
        reporttext = {ham, ene: frequency of AmideBB; dip: dipole moment of AmideBB}
    }

    @article{ToriiTasumi1998,
        title = {Ab Initio Molecular Orbital Study of the Amide I Vibrational Interactions between the Peptide Groups in Di- and Tripeptides and Considerations on the Conformation of the Extended Helix},
        author = {Torii, Hajime and Tasumi, Mitsuo},
        mapkey = {DmapTorii},
        reporttext = {dip: dipole moment of AmideBB}
    }
 

.. code-block:: python

    def GM_report_references(map_, system):
        return_these = []

        # Selecting the right frequency/energy map reference depending on
        # the model used
        if map_.run_pars.frequency_map_choice == "Tokmakoff":
            return_these.append("EmapTokmakoff")
        elif map_.run_pars.frequency_map_choice == "Jansen":
            return_these.append("EmapJansen")
        
        # Selecting the right dipole map reference depending on the model used.
        if map_.run_pars.dipole_map_choice == "Torii":
            return_these.append("DmapTorii")
        elif map_.run_pars.dipole_map_choice == "Jansen":
            return_these.append("DmapJansen")

        # only one choice for Raman map
        return_these.append("RamanAmide")

        return {key: map_.references[key] for key in report_these}


The default implementation of this function is very simple, and helps contextualize the above example:

.. code-block:: python

    def GM_report_references(map_, system):
        return map_.references

So, our model-selecting example chooses to return a subset of ``map_.references`` instead of the entire thing. For details on the structure of ``map_.references``, please see the documentation on this function. All we need to know here, is that we can create a list of all mapkeys that we want to have present. This means that map keys should not occur in multiple references, unless you always want to select them together.

In the example, keys were chosen such to both reflect the type of model/application of the reference (frequencies, dipole moment or raman tensor), and the specific model (by author name - that's how the Amide models are typically named).

If you paid close attention, you will have noticed that one of the references has two keys in the mapkey field, and depending on the choices for this map, that reference might be selected twice (if both frequency_map_choice and dipole_map_choice are set to Jansen). This is no problem - GMAP will look all individually provided references, and their reason to be called. If a single reference occurs multiple times, that is simply because it has multiple reasons to be called. This is recognized by the program, and it simply lists multiple reasons along with the one reference.

In order to identify two references as the same, all the following fields have to be identical: title, author, year, month, journal, volume, number, pages, issn, doi, url. This means that if these match between two different maps, they can be grouped together when both applicable!



****************
reporttext field
****************

This field tells the program two things. Firstly, it tells for what kinds of outputs the reference should be mentioned. Secondly, it spells out what message the program should present when the reference is provided to the user.

The format allows the same message to be used for different outputs and a single output to have multiple messages:
- ``reporttext = {ham: a message}`` means that the reference should only be printed when the 'ham' output is created (chosen for the input parameter output_data). The output type and message are separated using a colon and whitespace.
- ``reporttext = {ham: a message; dip: another message}`` means that the reference is both important for the hamiltonian and dipole outputs, and each of them has a different message. The two type-message pairs are separated from each other using a semicolon and white space, and the same type may occur in multiple pairs.
- ``reporttext = {ham, ene: a message}`` means that the reference is both used for the hamiltonian and energies outputs, in the same way, so they have the same message. The types are separated from each other using a comma and a white space. A type should not be repeated within a single pair like this.






