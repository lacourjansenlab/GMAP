

######################
For AIM users
######################


Making the switch from AIM? The programs have some similarities, so lets compare them here!

How large the differences are depends partially on what version of AIM you used - the installable version, or the 'manual' one. Besides that, these instructions assume that you want to use GMAP as a replacement for AIM. The module in GMAP that does this is called GEM. 



****************************************
Calling the program
****************************************

These commands do the same, provided you have a program-specific input file with parameters:

| 'manual' AIM:  ``your/AIM/path/AIM.py AIMinputfile.txt``
| installable AIM:  ``AIM run AIMinputfile.txt``  (requires installation first)
| GMAP:  ``GMAP GEM run GEMinputfile.txt``  (requires installation first)



****************************************
Parameter names
****************************************

Both GMAP's GEM and AIM use similar parameters for similar purposes. Got an input file you'd like to translate to GMAP? Here's an overview of parameters.


AIM parameter
    name in GMAP.

topfile
    :ref:`topology_file <UserGuide_page_parameter_overview_topfile>` is fully equivalent.

trjfile
    :ref:`trajectory_file <UserGuide_page_parameter_overview_trjfile>` is fully equivalent.

sourcedir
    :ref:`source_directory <UserGuide_page_parameter_overview_sourcedir>` is equivalent, but the GMAP sourcefiles directory is not a one-to-one copy of the AIM one.

referencefile
    GMAP has all references stored in the separate maps, so this file (and the corresponding parameter) no longer exists.

def_parfile
    :ref:`default_parameter_filename <UserGuide_page_parameter_overview_defpar>` is fully equivalent.

NN_Map
    Has no GMAP equivalent. Instead, make a copy of the AmideBB map and save it in a separate maps directory (in a Singles subdirectory), as well as all ProteinAmide ones (those go in the Pairs subdirectory). You can then edit the map parameters in those copies (ProteinAmide_GLDP/maps contains the parameters for the ProteinAmide maps), and request the copy similar to this: ``map_directory   my_map_copies``

Tasumi_Map
    Has no GMAP equivalent. Instead, make a copy of the all ProteinAmide ones, and save those in a separate maps directory (in a Pairs subdirectory). You can then edit the map parameters in the ProteinAmide_Tasumi/constants.txt file, and request the copy similar to this: ``map_directory   my_map_copies``

TCC_Map
    Has no GMAP equivalent. Instead, make a copy of the all ProteinAmide ones, and save those in a separate maps directory (in a Pairs subdirectory). You can then edit the map parameters in the ProteinAmide_TCC/constants.txt file, and request the copy similar to this: ``map_directory   my_map_copies``

resnamesfile
    Has no direct GMAP equivalent. How to proceed depends on what you used this file for:

    - If you used this file for 'just making it work', good news! This bothered us too, so is no longer needed. Instead, GMAP will just guess what to do with unknown residue names. However, no program is perfect, so it might guess wrongly. Make sure to watch the 'influencers' section in the program output (command line or log file), it will list the guesses used.
    - If you used file for specifying certain groups to select as influencers, you'll now want to use one of the influencer-series parameters:

      - :ref:`influencers_whitelist <UserGuide_page_parameter_overview_inflWL>` lists residue names that *are* allowed to influence.
      - :ref:`influencers_blacklist <UserGuide_page_parameter_overview_inflBL>` lists residue names that are **not** allowed to influence.
      - :ref:`influencers_file <UserGuide_page_parameter_overview_inflfile>` stores the filename in which groups are defined much like with AIM's resnamesfile. Its not the same, so read-up carefully!
      - :ref:`influencers_select_atoms <UserGuide_page_parameter_overview_inflSA>` allows an MDAnalysis-style filter for selecting influencing residues/atoms. Most versatile and powerful, but often more than needed, and you do need to know their selection language.

atnamesfile
    The AmideBB map has non-Gromacs support build in - no need to specify your version explicitly, making this parameter redundant.

libfile
    :ref:`VEG_clib_file <UserGuide_page_parameter_overview_VEGlib>` is fully equivalent.

use_c_lib
    The current version of GEM forces the use of a c-library file, making this parameter redundant.

extramapdir
    :ref:`output_directory <UserGuide_page_parameter_overview_mapdir>` is fully equivalent.

outdir
    :ref:`output_directory <UserGuide_page_parameter_overview_outdir>` is fully equivalent.

outfilename
    :ref:`output_hamiltonian_filename <UserGuide_page_parameter_overview_outhamfile>` is fully equivalent.

outdipfilename
    :ref:`output_dipole_filename <UserGuide_page_parameter_overview_outdipfile>` is fully equivalent.

outramfilename
    :ref:`output_raman_filename <UserGuide_page_parameter_overview_outramfile>` is fully equivalent.

outposfilename
    :ref:`output_positions_filename <UserGuide_page_parameter_overview_outposfile>` is fully equivalent.

outparfilename
    :ref:`output_parameter_filename <UserGuide_page_parameter_overview_outparfile>` is fully equivalent.

logdir
    :ref:`log_directory <UserGuide_page_parameter_overview_logdir>` is fully equivalent.

logfilename
    :ref:`log_filename <UserGuide_page_parameter_overview_logfile>` is fully equivalent.

proffilename
    :ref:`log_profiling_filename <UserGuide_page_parameter_overview_proffile>` is fully equivalent

pngfilename
    :ref:`log_profiling_graph_filename <UserGuide_page_parameter_overview_profgraphfile>` is fully equivalent.

output_format
    :ref:`output_format <UserGuide_page_parameter_overview_outform>` is fully equivalent.

output_type
    :ref:`output_data <UserGuide_page_parameter_overview_output_data>` is fully equivalent.

Verbose
    :ref:`verbose <UserGuide_page_parameter_overview_verbose>` is fully equivalent, although you might prefer a different value now.

Verbose_log
    :ref:`verbose_log <UserGuide_page_parameter_overview_verboselog>` is fully equivalent, although you might prefer a different value now.

profiler
    :ref:`profiler <UserGuide_page_parameter_overview_prof>` is fully equivalent.

pngout
    :ref:`profiler_graph <UserGuide_page_parameter_overview_profgraph>` is fully equivalent.

influencers
    Replaced by the 4 influencer-type parameters:

    - :ref:`influencers_whitelist <UserGuide_page_parameter_overview_inflWL>` lists residue names that *are* allowed to influence.
    - :ref:`influencers_blacklist <UserGuide_page_parameter_overview_inflBL>` lists residue names that are **not** allowed to influence.
    - :ref:`influencers_file <UserGuide_page_parameter_overview_inflfile>` stores the filename in which groups are defined much like with AIM's resnamesfile. Its not the same, so read-up carefully!
    - :ref:`influencers_select_atoms <UserGuide_page_parameter_overview_inflSA>` allows an MDAnalysis-style filter for selecting influencing residues/atoms. Most versatile and powerful, but often more than needed, and you do need to know their selection language.

oscillators
    Replaced by :ref:`maps_to_use <UserGuide_page_parameter_overview_usemaps>`. Very similar in function, besides there not being any hardcoded options left.

apply_dd_coupling
    Replaced by :ref:`couplings_to_use <UserGuide_page_parameter_overview_usecoup>`. The new couplings to use is much more general: you now indicate what kind of coupling you'd like to use for each type of oscillator/single. Dipole-dipole coupling is one of the options (that coupling map comes with the GMAP download).

map_choice
    This is no longer covered by GMAP. Instead, you need to tell the AmideBB and AmideSC maps your choice for this one - they have this parameter now. See the readme of those maps for more information; parameters to be used are:

    - ``AmideBB.frequency_map_choice``
    - ``AmideSC.frequency_map_choice``

Dipole_choice
    This is no longer covered by GMAP. Instead, you need to tell the AmideBB and AmideSC maps your choice for this one - they have this parameter now. See the readme of those maps for more information; parameters to be used are:

    - ``AmideBB.dipole_map_choice``
    - ``AmideSC.dipole_map_choice``

coupling_choice
    This one became more general in GMAP. There's two possibilities:

    - You want to indicate what kind of coupling map to use between two singles/oscillators. In that case, you should now use :ref:`couplings_to_use <UserGuide_page_parameter_overview_usecoup>`, this also allows to specify custom coupling maps.
    - You want to indicate the exact method of coupling between AmideBB/AmideSC groups. In this case, you should choose the ``ProteinAmide`` coupling map using the parameter ``couplings_to_use``, and then tell the ProteinAmide map your specific choice using ``ProteinAmide.coupling_choice``.

    Please note that the TDCKrimm map from AIM and AmideImaps has been renamed to TDCKnoester in GMAP to more closely reflect the map's source.

NN_coupling_choice
    This one is similar to the previous: you should choose the ``ProteinAmide`` coupling map using the parameter ``couplings_to_use``, and then tell the ProteinAmide map your specific choice using ``ProteinAmide.NN_coupling_choice``.
    
    Please note that the TDCKrimm map from AIM and AmideImaps has been renamed to TDCKnoester in GMAP to more closely reflect the map's source.

AtomPos_choice
    This is no longer covered by GMAP. Instead, you need to tell the AmideBB and AmideSC maps your choice for this one - they have this parameter now. See the readme of those maps for more information; parameters to be used are:

    - ``AmideBB.pos_choice``
    - ``AmideSC.pos_choice``

start_frame
    :ref:`start_frame <UserGuide_page_parameter_overview_startframe>` is fully equivalent.

nFrames_to_calculate
    :ref:`number_frames <UserGuide_page_parameter_overview_numframe>` is fully equivalent.

end_frame
    :ref:`stop_frame <UserGuide_page_parameter_overview_stopframe>` is fully equivalent.

max_time
    :ref:`time_limit <UserGuide_page_parameter_overview_timelimit>` is fully equivalent.

SphereSize
    :ref:`estatic_range <UserGuide_page_parameter_overview_estatrange>` is fully equivalent.

replicate_orig_AIM
    This is no longer covered by GMAP. Instead, you need to tell the AmideBB and AmideSC maps your choice for this one - they have this parameter now. See the readme of those maps for more information; parameters to be used are:

    - ``AmideBB.legacy_mode``
    - ``AmideSC.legacy_mode``

NSA_toggle
    The neighbour-searching algorithm has not yet been implemented in GMAP/GEM, so there is no equivalent parameter.

NSA_nframes
    The neighbour-searching algorithm has not yet been implemented in GMAP/GEM, so there is no equivalent parameter.

NSA_spheresize
    The neighbour-searching algorithm has not yet been implemented in GMAP/GEM, so there is no equivalent parameter.

atom_based_chainID
    The AmideBB map has non-Gromacs support build in - no need to adjust for your version explicitly, making this parameter redundant.

use_protein_specials
    This is no longer covered by GMAP. Instead, you should need to tell the AmideBB map the choice for this one, but it does not yet support this.

Scale_LR_coupling
    :ref:`estatic_range <UserGuide_page_parameter_overview_scalecoup>` is equivalent, but has more freedom than in AIM.

Use_AmGroup_selection_criteria
    This has been replaced by :ref:`singles_whitelist <UserGuide_page_parameter_overview_singWL>` and :ref:`singles_blacklist <UserGuide_page_parameter_overview_singBL>`

resnum_whitelist
    :ref:`singles_whitelist <UserGuide_page_parameter_overview_singWL>` has a similar function, but different language/method of use.

resnum_blacklist
    :ref:`singles_blacklist <UserGuide_page_parameter_overview_singBL>` has a similar function, but different language/method of use.

resname_whitelist
    :ref:`singles_whitelist <UserGuide_page_parameter_overview_singWL>` has a similar function, but different language/method of use.

resname_blacklist
    :ref:`singles_blacklist <UserGuide_page_parameter_overview_singBL>` has a similar function, but different language/method of use.

TreatNN
    This is no longer covered by GMAP. Instead, you need to tell the AmideBB map your choice for this one - they have this parameter now. See the readme of that map for more information; parameter to be used is:

    - ``AmideBB.consider_nearest_neighbours``


