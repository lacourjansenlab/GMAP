#include <math.h>
#include <stdio.h>
#include <stdlib.h>  // calloc!

/*
This file will contain all functions (and their helpers) required for
calculating the electric potential, field and gradient on any given list
of points.
*/

#ifdef _WIN32
    extern "C" {
        __declspec(dllexport) void calcVEG_perres_mm(
            int *tocalc, int n_osc_ats, float *spherepos, int calc_choice,
            float *positions,
            float *charges, float *COMs, int *res_first_ix, int *res_last_ix,
            int n_res, int *local_atoms, int n_locals, float r_sphere,
            float r_smooth, float *halfbox, float *boxdims, float *out
        );
    }
#endif



extern "C" {
    void PBC_diff_cubic(
        float *vect1, float *vect2, float *halfbox, float *boxdims,
        float *vectout
    ) {
        /*Calculates the difference vect1 - vect2, assuming a cubic MD
        system, and assuming vect1 and vect2 are inside the system
        currently.

        Parameters
        ----------
        vect1, vect2 : float[3]
            The positions between which the difference vector should be
            calculated.
        halfbox, boxdims : float[3]
            The size of the PBC (MD system size). Halfbox is assumed to
            equal boxdims/2.
        vectout : float[3]
            The output will be written here. It is the difference vector
            between vect1 and vect2, corrected for the PBC.
        */

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
        /*Calculates the square of the length of the input vector.

        Parameters
        ----------
        vec : float[3]
            The input vector.

        Returns
        -------
        len2 : float
            The length of the input vector, squared.
        */

        return (vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]);
    }

    int in_ordered_array_int(
        int *ordered_array, int to_find, int start, int arr_length, int *endpos
    ) {
        /*Sees if the requested integer is present in the provided array.

        This function only works if the provided array is sorted (most
        negative value first), and if any subsequent calls are also
        sorted (most negative value first).

        The function is designed to live in a big loop. Looping over a
        (sorted!) array of values x, for each of them, see if they are
        present in a second (sorted!) array y. As both are sorted, they
        can be scanned in lock-step, we just need to remember the
        current position in both. The loop calling this function keeps
        track of the position in x, this function reads and writes the
        position of y from/into to_find/endpos resp.
        In the calls to this function, to_find and endpos should most
        likely refer to the same value - to_find is the value itself,
        endpos is its address.

        Parameters
        ----------
        ordered_array : int[arr_length]
            The array in which the requested value may or may not be
            present.
        to_find : int
            The value which we are hoping to find in ordered_array
        start : int
            At what position in the array we should start looking (as we
            are certain to_find will not occur before then).
        arr_length : int
            The length of ordered_array.
        endpos : &int
            A pointer to the integer which we should overwrite. The
            position at which the next integer (the smallest one that is
            larger than to_find) is located.

        Returns
        -------
        is_present : int
            Whether to_find is present in ordered_array. 1 if it is,
            0 if it is not.
        */
        
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

    inline float getweight_linear_smoothing(
        float dist2, float puredist, float *charges, int sysix, float r_smooth
    ) {
        /*Get the weighted charge for an atom considering its distance
        and the smoothing rules.

        This function will yield unexpected results if sqrt(dist2) is
        larger than puredist + r_smooth.

        Parameters
        ----------
        dist2 : float
            The square of the distance of this atom to the VEG reference.
        puredist : float
            The distance up until which charges should get the maximum
            weight.
        charges : float[unknown]
            The charges of all atoms in the system.
        sysix : int
            The system index of the atom of which we want to know the
            weighted charge.
        r_smooth : float
            The distance over which the weighted charges should decrease
            to zero.
        */

        float dist = sqrt(dist2);
        if (dist > puredist) {
            return (charges[sysix] * (1 - ((dist - puredist) / r_smooth)));
        } else {
            return charges[sysix];
        }
    }

    inline float getweight_linear_nosmooth(
        float dist2, float puredist, float *charges, int sysix, float r_smooth
    ) {
        /*Get the (weighted) charge for an atom considering there is no
        smoothing.

        Parameters
        ----------
        dist2 : float
            Unused, present for universal signature.
        puredist : float
            Unused, present for universal signature.
        charges : float[unknown]
            The charges of all atoms in the system.
        sysix : int
            The system index of the atom of which we want to know the
            weighted charge.
        r_smooth : float
            Unused, present for universal signature
        */
        return charges[sysix];
    }

    void calcNone(
        float *diff,  // The difference vector between the two atoms
        float weighted_charge,  // The charge of the atom, weighted by distance
        int oscix,  // The index of the atom we're treating
        float *out  // output is stored here
    ) {}

    void calcPot(
        float *diff,  // The difference vector between the two atoms
        float weighted_charge,  // The charge of the atom, weighted by distance
        int oscix,  // The index of the atom we're treating
        float *out  // output is stored here
    ) {
        out[oscix*10] += weighted_charge / sqrt(veclen2(diff));
    }

    void calcField(
        float *diff,  // The difference vector between the two atoms
        float weighted_charge,  // The charge of the atom, weighted by distance
        int oscix,  // The index of the atom we're treating
        float *out  // output is stored here
    ) {
        float idist2 = 1 / veclen2(diff);
        float idist = sqrt(idist2);
        float prefac = weighted_charge * idist2 * idist;

        out[oscix*10] += weighted_charge * idist;

        out[oscix*10 + 1] += diff[0] * prefac;
        out[oscix*10 + 2] += diff[1] * prefac;
        out[oscix*10 + 3] += diff[2] * prefac;
    }

    void calcGrad(
        float *diff,  // The difference vector between the two atoms
        float weighted_charge,  // The charge of the atom, weighted by distance
        int oscix,  // The index of the atom we're treating
        float *out  // output is stored here
    ) {
        float idist2 = 1 / veclen2(diff);
        float idist = sqrt(idist2);
        float prefac = weighted_charge * idist2 * idist;
        float prefac2 = 3.0 * prefac * idist2;

        float diffX = diff[0];
        float diffY = diff[1];
        float diffZ = diff[2];

        out[oscix*10] += weighted_charge * idist;

        out[oscix*10 + 1] += diffX * prefac;
        out[oscix*10 + 2] += diffY * prefac;
        out[oscix*10 + 3] += diffZ * prefac;

        out[oscix*10 + 4] += prefac - (diffX * diffX * prefac2);
        out[oscix*10 + 5] += prefac - (diffY * diffY * prefac2);
        out[oscix*10 + 6] += prefac - (diffZ * diffZ * prefac2);
        out[oscix*10 + 7] -= diffX * diffY * prefac2;
        out[oscix*10 + 8] -= diffX * diffZ * prefac2;
        out[oscix*10 + 9] -= diffY * diffZ * prefac2;
    }
}

    /*
    Calculate the potential for an oscillator. The sphere determining whether
    an influencer counts is centered on spherepos. After an atom is deemed in
    range, its actual influence is calculated by the distance between it, and
    the position of the atom it influences (which is stored in refpos).

    !! local_atoms MUST be sorted for this function to work (fast)!
    */
    void calcVEG_perres_mm(
        // single-osc parameters
        int *tocalc,  // the sys-ix of the atoms whose properties are requested
        int n_osc_ats,  // amount of atoms in the oscillator
        float *spherepos,  // center of influencersphere
        int calc_choice,  // V, E, or G?

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
        /*Calculates the potential on any number of points.

        The potential is caused by a group of atoms, each of which is
        within r_sphere + r_smooth/2 of spherepos. If an atom is given
        in local_atoms, it should never attribute to the potential,
        regardless of its distance to spherepos.

        This method takes into account periodic boundary conditions.

        Parameters
        ----------
        tocalc : int[n_osc_ats]
            The indices of the atoms at whose position the potential
            should be calculated.
        n_osc_ats : int
            The amount of atoms of which we want to know the potential
        spherepos : float[3]
            The center of the group of charges that may influence the
            potential on each of the atoms in tocalc
        calc_choice : int
            What electrostatic properties should be calculated:
            0 for nothing (this function should never be called with 0)
            1 for potential only
            2 for potential and field
            3 for potential, field and gradient
        positions : float[3 * unknown]
            The positions of all atoms in the MD system. Any provided
            indices into this function are guaranteed to exist in this
            array. The size of this array is exactly three times that
            of charges.
        charges : float[unknown]
            The charges of all atoms in the MD system. Any provided
            indices into this function are guaranteed to exist in this
            array. The size of this array is exactly one third that
            of positions.
        COMs : float[3 * n_res]
            The centre of mass of each residue present in the MD system
        res_first_ix : int[n_res]
            The (global/system) index of the first atom of each residue
            present in the MD system
        last_first_ix : int[n_res]
            The (global/system) index of the last atom of each residue
            present in the MD sytem
        n_res : int
            The amount of residues present in the MD system.
        local_atoms : int[n_locals]
            These atoms should never contribute to the potential
            calculated by this function.
        n_locals : int
            The amount of atoms that should never contribute to the
            potential calculated by this function.
        r_sphere : float
            The radius of the sphere defining the contributing charges.
        r_smooth : float
            The distance over which the charges (and their contributions)
            should be smoothed. This distance is placed around the
            boundary of r_sphere.
        halfbox, boxdims : float[3]
            The size of the PBC (MD system size). Halfbox is assumed to
            equal boxdims/2.
        out : float[n_osc_atoms]
            The output array to which all potentials will be written.
        */
        
        using smoothfunc = float(*)(float, float, float *, int, float);
        smoothfunc get_weighted_charge = getweight_linear_nosmooth;
        if (r_smooth > 0) {
            get_weighted_charge = getweight_linear_smoothing;
        }
        using VEGfunc = void(*)(float *, float, int, float *);
        VEGfunc calc_VEG = calcNone;
        if (calc_choice == 1) {calc_VEG = calcPot;}
        else if (calc_choice == 2) {calc_VEG = calcField;}
        else if (calc_choice == 3) {calc_VEG = calcGrad;}

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
        // *10, as we want to clear all entries for each oscillator
        for (oscix = 0; oscix < n_osc_ats * 10; oscix++) {
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

                weighted_charge = get_weighted_charge(
                    dist2, puredist, charges, sysix, r_smooth
                );

                // Use this line when smoothing on perres basis
                // weighted_charge = charges[sysix] * smooth_factor;


                // loop over the atoms of the oscillator
                for (oscix = 0; oscix < n_osc_ats; oscix++) {
                    // yes, its needed (and allowed/possible) to redo PBCdiff
                    // and dist(2) again.
                    PBC_diff_cubic(
                        &refpos[oscix * 3], &positions[sysix * 3],
                        halfbox, boxdims, diff);
                    calc_VEG(diff, weighted_charge, oscix, out);
                } 
            }
        }  // per-residue loop

        // // correction for if the total charge is not 0 within the sphere.
        // for (oscix = 0; oscix < n_osc_ats; oscix++) {
        //     // placing the remaining charge on the edge of the sphere.
        //     out[oscix] -= total_charge[oscix] / maxdist;
        // }

        free(refpos);  // free(diff)
    }
