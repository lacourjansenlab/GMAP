#include <math.h>
#include <stdio.h>
#include <stdlib.h>  // calloc!

/*
This file will contain all functions (and their helpers) required for
calculating the electric potential, field and gradient on any given list
of points.
*/

extern "C" {
    __declspec(dllexport) int testadd(int a, int b);
    __declspec(dllexport) void calcPot_perres_mm(
        int *tocalc, int n_osc_ats, float *spherepos, float *positions, float *charges, float *COMs, int *res_first_ix, int *res_last_ix, int n_res, int *local_atoms, int n_locals, float r_sphere, float r_smooth, float *halfbox, float *boxdims, float *out
    );
}


extern "C" {
    int testadd(int a, int b) {
        return (a + b);
    }

    void PBC_diff_cubic(
        float *vect1, float *vect2, float *halfbox, float *boxdims,
        float *vectout
    ) {
        for (int i = 0; i < 3; i++){
            vectout[i] = vect1[i] - vect2[i];
			if (vectout[i] > halfbox[i]) {
				vectout[i] -= boxdims[i];
			}
			else if (vectout[i] < -1 * halfbox[i]) {
				vectout[i] += boxdims[i];
			}
        }
    }

    inline float veclen2(float *vec) {
        return (vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]);
    }


    int in_ordered_array_int(
        int *ordered_array, int to_find, int start, int arr_length, int *endpos
    ) {
        for (int pos = start; pos < arr_length; pos++) {
            if (ordered_array[pos] < to_find) {
                continue;
            } else if (ordered_array[pos] == to_find) {
                *endpos = pos + 1;
                return 1;
            } else {  // the value isn't present, we just passed it
                *endpos = pos;
                return 0;
            }
        }
        return 0;
    }

    /*
    Calculate the potential for an oscillator. The sphere determining whether
    an influencer counts is centered on spherepos. After an atom is deemed in
    range, its actual influence is calculated by the distance between it, and
    the position of the atom it influences (which is stored in refpos).

    !! local_atoms MUST be sorted for this function to work (fast)!
    */
    void calcPot_perres_mm(
        // single-osc parameters
        int *tocalc,  // the sys-ix of the atoms whose properties are requested
        int n_osc_ats,  // amount of atoms in the oscillator
        float *spherepos,  // center of influencersphere

        // system parameters
        float *positions, // positions of all atoms in the MD system
        float *charges,  // charges of all atoms in the MD system
        
        // residue parameters
        float *COMs,  // the COM of each residue in the system
        int *res_first_ix,  // the sysix of first atom in each residue
        int *res_last_ix,  // the sysix of the last atom in each residue
        int n_res,  // the amount of residues in the system
        
        int *local_atoms,  // the atoms that cannot be influencers
        int n_locals,  // the amount of local atoms
        float r_sphere,  // how far away the residue can be
        float r_smooth,  // how far should we smooth
        float *halfbox,  // half of boxdims
        float *boxdims,  // the size of the CUBIC box
        float *out  // output is stored here
    ) {
        // build refpos array (positions of osc ats)
        float *refpos;
        refpos = (float *)calloc(3*n_osc_ats, sizeof(float));
        int oscix, sysix, dir;
        for (oscix = 0; oscix < n_osc_ats; oscix++) {
            sysix = tocalc[oscix];
            for (dir = 0; dir < 3; dir++) {
                refpos[oscix * 3 + dir] = positions[sysix * 3 + dir];
            }
        }

        // clear output array
        float *total_charge;
        total_charge = (float *)calloc(n_osc_ats, sizeof(float));
        for (oscix = 0; oscix < n_osc_ats; oscix++) {
            out[oscix] = 0;
        }

        // get all distances straight
        float maxdist, maxdist2;  // when an atom can have influence
        float puredist, puredist2;   // when an atom has full influence

        maxdist = r_sphere + (r_smooth * 0.5);
        maxdist2 = maxdist * maxdist;

        puredist = r_sphere - (r_smooth * 0.5);
        puredist2 = puredist * puredist;

        int resnum, local_search;
        local_search = 0;
        float diff[3], dist, dist2, smooth_factor, weighted_charge;
        for (resnum = 0; resnum < n_res; resnum++) {
            // find distance to residue
            PBC_diff_cubic(
                spherepos, &COMs[resnum * 3], halfbox, boxdims, diff);
            dist2 = veclen2(diff);

            // if the residue is too far away, skip it
            if (dist2 > maxdist2) {
                continue;
            }
            // dist = sqrt(dist2);


            // // check whether this residue is part of smoothing
            // if (dist > puredist) {
            //     smooth_factor = 1 - ((dist - puredist) / r_smooth);
            // } else {
            //     smooth_factor = 1;
            // }
            smooth_factor = 1;

            // loop over all atoms in this residue (together with residue loop,
            // this becomes all atoms in the system)
            for (
                sysix = res_first_ix[resnum];
                sysix <= res_last_ix[resnum];
                sysix++
            ) {
                // if this atom is in local_atoms, skip!
                if (in_ordered_array_int(
                    local_atoms, sysix, local_search, n_locals, &local_search)
                ) {
                    continue;
                }

                // Use this part for smoothing on perat basis
                PBC_diff_cubic(
                    spherepos, &positions[sysix * 3],
                    halfbox, boxdims, diff);
                dist2 = veclen2(diff);
                if (dist2 > maxdist2) {
                    continue;
                }
                // weighted_charge = charges[sysix];  // no smoothing
                // dist = sqrt(dist2);  // yes smoothing
                // if (dist > puredist) {  // yes smoothing
                //     weighted_charge = charges[sysix] * (
                //         1 - ((dist - puredist) / r_smooth));
                // } else {
                //     weighted_charge = charges[sysix];
                // }
                // end of perat basis smoothing

                // Use this line when smoothing on perres basis
                weighted_charge = charges[sysix] * smooth_factor;


                // loop over the atoms of the oscillator
                for (oscix = 0; oscix < n_osc_ats; oscix++) {
                    // yes, its needed (and allowed/possible) to redo PBCdiff
                    // and dist(2) again.
                    PBC_diff_cubic(
                        &refpos[oscix * 3], &positions[sysix * 3],
                        halfbox, boxdims, diff);
                    out[oscix] += weighted_charge / sqrt(veclen2(diff));
                    total_charge[oscix] += weighted_charge;
                } 
            }
        }  // per-residue loop

        // correction for if the total charge is not 0 within the sphere.
        for (oscix = 0; oscix < n_osc_ats; oscix++) {
            // placing the remaining charge on the edge of the sphere.
            out[oscix] -= total_charge[oscix] / maxdist;
        }

        free(refpos), free(total_charge);  // free(diff)
    }
}
