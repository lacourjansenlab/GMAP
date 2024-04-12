#include <math.h>calcPot_subbox
#include <stdio.h>
#include <algorithm>

// Windows only!

extern "C" {
    __declspec(dllexport) void calcPot_atoms(float *positions, float *charges, int Natoms, int *tocalc, int nOscAts, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out);
    __declspec(dllexport) void calcPot_subbox_aa(float *positions, float *charges, int Natoms, int *tocalc, int nOscAts, int *n_subbox, float *subboxdims, int *nat_psbox, int *atix_psbox, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out);
    __declspec(dllexport) void calcPot_subbox_ma(float *positions, float *charges, int Natoms, int *tocalc, int nOscAts, int *n_subbox, float *subboxdims, int *nat_psbox, int *atix_psbox, float *goalCOM, float *COMs, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out);
    __declspec(dllexport) void calcPot_residues_aa(float *positions, float *charges, int *resnums, int Natoms, int *tocalc, int nOscAts, int *reslens, int Nres, float *COMs, float *ressize, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out);
    __declspec(dllexport) void calcPot_perres_mm(float *positions, float *charges, int *resnums, int *tocalc, int nOscAts, int *reslens, int Nres, float *COMs, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out);    
    __declspec(dllexport) void move_box(float *positions, int Natoms, int firstat, int lastat, float *boxdims, float *halfbox);
    __declspec(dllexport) void calc_COM(float *positions, int Natoms, float *masses, int *reslens, int Nres, float *COMs, float *boxdims, float *halfbox);
    __declspec(dllexport) void calc_ressize(float *positions, int Natoms, int *reslens, int Nres, float *ressize, float *boxdims, float *halfbox);

}



extern "C" {
    // definitely much slower!
    void PBC_diff_test1(float *vect1, float *vect2, float *halfbox, float *boxdims, float *vectout) {
        for (int i = 0; i < 3; i++) {
            vectout[i] = vect1[i] - vect2[i] + halfbox[i];
            // printf("%f %f %f %f ", vect1[i], vect2[i], halfbox[i], vectout[i]);
            int wholes = vectout[i] / boxdims[i];
            // if (wholes != 0) {
            //     printf("nwholes: %d \n", wholes);
            // }
            // printf("%d ", wholes);
            vectout[i] -= ((wholes * boxdims[i]) + halfbox[i]);
            // printf("%f \n", vectout[i]);
        }
    }

    void PBC_diff_test2(float *vect1, float *vect2, float *halfbox, float *boxdims, float *vectout) {
        for (int i = 0; i < 3; i++) {
            vectout[i] = vect1[i] - vect2[i];
            if (abs(vectout[i]) > halfbox[i]) {
                if (vectout[i] > halfbox[i]) {
                    vectout[i] -= boxdims[i];
                } else {
                    vectout[i] += boxdims[i];
                }
            }
        }
    }

    void PBC_diff(float *vect1, float *vect2, float *halfbox, float *boxdims, float *vectout) {
        for (int i = 0; i < 3; i++) {
			vectout[i] = vect1[i] - vect2[i];
			if (vectout[i] > halfbox[i]) {
				vectout[i] -= boxdims[i];
			}
			else if (vectout[i] < -1 * halfbox[i]) {
				vectout[i] += boxdims[i];
			}
		}
	}

    void PBC_diff_dumb(float *vect1, float *vect2, float *halfbox, float *boxdims, float *vectout) {
        // this function has the same signature as the 'smart' one for aliassing purposes,
        // but the halfbox and boxdims arguments are not actually used!
        for (int i = 0; i < 3; i++) {
            vectout[i] = vect1[i] - vect2[i];
        }
    }

    void minmaxfinder_ma(int subboxnum, int axis, float *subboxdims, float *goalCOM, float *halfbox, float *boxdims, float *minout, float *maxout) {
        float dif1 = abs(subboxnum * subboxdims[axis] - goalCOM[axis]);
        float dif2 = abs((subboxnum + 1) * subboxdims[axis] + goalCOM[axis]);

        if (dif1 > halfbox[axis]) {
            dif1 = abs(dif1 - boxdims[axis]);
        }
        if (dif2 > halfbox[axis]) {
            dif2 = abs(dif2 - boxdims[axis]);
        }

        if (dif1 < subboxdims[axis] && dif2 < subboxdims[axis]) {
            minout[axis] = 0;
        }
        else {
            minout[axis] = std::min(dif1, dif2);
        }
        maxout[axis] = std::max(dif1, dif2);
    }

    inline float numveclen2(float num1, float num2, float num3) {
        return (num1 * num1 + num2 * num2 + num3 * num3);
    }

    inline float veclen2(float *vec) {
        return (vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]);
    }

    float potential_linear(float dist, float charge, float min_dist, float max_dist, float smooth_domain){
        if (dist <= min_dist){
            return charge / dist; 
        }   // If the function is outside of smoothing domain, simply return the potential
        else {
            return charge * (1 - (dist - min_dist) / smooth_domain) / dist;
        }   // Returns a linear slope, starting at min_dist and ending at max_dist with 0
     }

    int test_inarray(int tofind, int *array, int array_len) {
        for (int i = 0; i < array_len; i++) {
            if (array[i] == tofind) {
                return 1;
            }
        }
        return 0;
    }

    void move_box(float *positions, int Natoms, int firstat, int lastat, float *boxdims, float *halfbox) {
        int nats = lastat - firstat + 1;
        float refpos[3], cumpos[3], diff[3];
        for (int i = 0; i < 3; i++) {
            refpos[i] = positions[firstat * 3 + i];
            cumpos[i] = 0;
        }

        for (int ix = firstat; ix <= lastat; ix++) {
            PBC_diff(refpos, &positions[ix * 3], halfbox, boxdims, diff);
            for (int i = 0; i < 3; i++) {
                cumpos[i] += diff[i];
            }
        }

        for (int i = 0; i < 3; i++) {
            cumpos[i] = (cumpos[i] / nats) + refpos[i];
            // now, cumpos stores geometric centre of the desired atoms

            cumpos[i] = (halfbox[i] - cumpos[i]);
            // now, cumpos stores the necessary shift for all atoms
            // such that the centre of the interesting part is in the centre.

            if (cumpos[i] > halfbox[i]) {
                cumpos[i] -= boxdims[i];
            } else if (cumpos[i] < -1 * halfbox[i]) {
                cumpos[i] += boxdims[i];
            }            
        }
        

        for (int ix = 0; ix < Natoms; ix++) {
            for (int i = 0; i < 3; i++) {
                positions[ix * 3 + i] += cumpos[i];
                if (positions[ix * 3 + i] > boxdims[i]) {
                    positions[ix * 3 + i] -= boxdims[i];
                } else if (positions[ix * 3 + i] < 0) {
                    positions[ix * 3 + i] += boxdims[i];
                }
            }
        }
    }

    void calc_COM(float *positions, int Natoms, float *masses, int *reslens, int Nres, float *COMs, float *boxdims, float *halfbox) {

        int Nresats, startix, stopix;
        float refpos[3], diff[3], cumpos[3], cummass, icummass;
        stopix = -1;

        for (int resnum = 0; resnum < Nres; resnum++) {
            Nresats = reslens[resnum];
            startix = stopix + 1;
            stopix += Nresats;
            for (int i = 0; i < 3; i++) { 
                // printf(" %f", positions[atix * 3 + i]);
                refpos[i] = positions[startix * 3 + i];
                cumpos[i] = 0.0;
            }
            cummass = masses[startix];

            for (int atix = startix + 1; atix <= stopix; atix++) {
                PBC_diff(&positions[atix * 3], refpos, halfbox, boxdims, diff);
                for (int i = 0; i < 3; i++) {
                    cumpos[i] += masses[atix] * diff[i];
                }
                cummass += masses[atix];
            }
            icummass = 1 / cummass;

            for (int i = 0; i < 3; i++) {
                COMs[resnum * 3 + i] = (cumpos[i] * icummass) + refpos[i];
            }

        }
    }

    void calc_ressize(float *positions, int Natoms, int *reslens, int Nres, float *ressize, float *boxdims, float *halfbox) {

        float maxdist2, diff[3], dist2;
        int startix, stopix;

        stopix = -1;

        for (int resnum = 0; resnum < Nres; resnum++) {
            // printf("\n\nresnum %d ", resnum);
            maxdist2 = 0;
            startix = stopix + 1;
            stopix += reslens[resnum];

            for (int atix = startix; atix < stopix; atix++) {
                // printf("\natix %d at %f %f %f", atix, positions[atix*3], positions[atix*3 + 1], positions[atix*3 + 2]);
                for (int ix = atix + 1; ix <= stopix; ix++) {
                    PBC_diff(&positions[atix * 3], &positions[ix * 3], halfbox, boxdims, diff);
                    dist2 = diff[0] * diff[0] + diff[1] * diff[1] + diff[2] * diff[2];
                    // printf("\ndist %f for %d and %d", dist2, atix, ix);
                    if (dist2 > maxdist2) {
                        maxdist2 = dist2;
                    }
                }
            }
            // printf("\natix %d at %f %f %f", (stopix-1), positions[(stopix-1)*3], positions[(stopix-1)*3 + 1], positions[(stopix-1)*3 + 2]);

            ressize[resnum] = sqrt(maxdist2);
            // printf("\nressize %f ", ressize[resnum]);

        }
    }

   void calcPot_atoms(float *positions, float *charges, int Natoms, int *tocalc, int nOscAts, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out) {

        float min_dist = maxdist - smooth_domain;
        
        // printf("test\n");
        float charge, dist2, idist2, idist, maxdist2;
        float diff[3];
        // float refpos[3*nOscAts];
        // float *refpos = new float[3*nOscAts];
        float *refpos;
        refpos = (float *)calloc(3*nOscAts, sizeof(float));



        // printf("1");

        // Number of residues is: 27675
        // Number of atoms per residue is: 121
        for (int subix = 0; subix < nOscAts; subix++) {
            
            int mainix = tocalc[subix];
            for (int i = 0; i < 3; i++) {
                refpos[subix * 3 + i] = positions[mainix * 3 + i];
            }
        }
        maxdist2 = maxdist * maxdist;
        for (int ix = 0; ix < Natoms; ix++) {
            charge = charges[ix];
            for (int subix = 0; subix < nOscAts; subix++) {
                PBC_diff(&refpos[subix * 3], &positions[ix * 3], halfbox, boxdims, diff);
			    dist2 = veclen2(diff);
                if (maxdist2 > dist2 && dist2 > 0) {
                    
			        float dist = sqrt(dist2);

                    if (dist > maxdist) {
                        continue;
                    }
                    out[subix] += potential_linear(dist, charge, min_dist, maxdist, smooth_domain);
                }
			    
            }
        }
        free(refpos);
    } 

    // For calculating aa
    void calcPot_subbox_aa(float *positions, float *charges, int Natoms, int *tocalc, int nOscAts, int *n_subbox, float *subboxdims, int *nat_psbox, int *atix_psbox, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out) {
        // printf("1maxdist : %f\n", maxdist);
        float min_dist = maxdist - smooth_domain;
        // struct smoothing_struct{
        //     float (*potentialPtr)(float, float, float, float);
        //     float min_dist;
        // }
        // float (*potentialPtr)(float, float, float, float, float);
        // float min_dist = smooth_variables(maxdist, smoothing, smooth_domain, potentialPtr);
        // printf("2maxdist : %f\n", maxdist);
        // printf("min_dist was computed!\n");
        // printf("3maxdist : %f\n", maxdist);
        using func = void(*)(float *, float *, float *, float *, float *);
        func use_PBCdiff = PBC_diff;
        // printf("%f\n", maxdist);
        float charge, dist2, idist2, idist, maxdist2;
        // printf("4maxdist : %f\n", maxdist);
        maxdist2 = maxdist * maxdist;
        float diff[3];

        // float *temp_charge;
        
        float *temp_charge; 
        temp_charge = (float *)calloc(nOscAts, sizeof(float));

        // = new float[nOscAts]();
        // for (int idx = 0; idx < nOscAts; idx++) {
        //     temp_charge[idx] = 0;
        // }

        // float refpos[3*nOscAts];
        // int subbox[3*nOscAts];
        // int check[nOscAts];
        float *refpos;
        int *subbox, *check, *tots;
        int tempbox[3];
        int minix, maxix;
        int subix;
        refpos = (float *)calloc(3*nOscAts, sizeof(float));
        subbox = (int *)calloc(3*nOscAts, sizeof(int));
        check = (int *)calloc(nOscAts, sizeof(int));
        tots = (int *)calloc(nOscAts, sizeof(int));

        int checksum, pbc_choice_sum, pbc_choice;
        // for (int i = 0; i < 3; i++) {
        //     printf("%f  ", subboxdims[i]);
        // }
        minix = tocalc[0];
        maxix = tocalc[0];
        for (int subix = 0; subix < nOscAts; subix++) {
            
            
            // subix = sub_subbix * 121 + atoms_of_interest[loopy];
            
            // printf("%d", subix);

            // 121 is the number of atoms in a residue
            int mainix = tocalc[subix];
            minix = std::min(minix, mainix);
            maxix = std::max(maxix, mainix);
            check[subix] = 0;
            for (int i = 0; i < 3; i++) {
                // printf("%f  ", positions[mainix * 3 + i]);
                // printf("%d\n",subix);
                refpos[subix * 3 + i] = positions[mainix * 3 + i];
                // printf("Grrrr\n");
                // printf("%f  ", refpos[subix * 3 + i]);
                // subbox[subix * 3 + i]
                // printf("UwU\n");
                subbox[subix * 3 + i] = refpos[subix * 3 + i] / subboxdims[i];
                // printf("%d  ", subbox[subix * 3 + i]);
            }
        }
        // printf("405");
        // printf("done init\n");
        checksum = 0;

        int smallest;
        int boxchoice[3];
        while (checksum < nOscAts) {
            float temp_potential = 0;
            // printf("started new loop iter\n");
            // find lowest relJ that hasn't been considered yet
            smallest = nOscAts;
            for (int subix = 0; subix < nOscAts; subix++) {
                if (check[subix] == 0) {
                    smallest = std::min(smallest, subix);
                }
                // printf("%f ", out[subix]);
            }
            // printf("%d ", smallest);
            // printf("\n");

            // extract subbox of this lowest relJ
            pbc_choice_sum = 0;
            for (int i = 0; i < 3; i++) {
                boxchoice[i] = subbox[smallest * 3 + i];
                if (boxchoice[i] * subboxdims[i] > maxdist) {
                    pbc_choice_sum += 1;
                }
                if ((boxchoice[i] + 1) * subboxdims[i] < boxdims[i] - maxdist) {
                    pbc_choice_sum += 1;
                }
            }

            if (pbc_choice_sum == 6) {
                use_PBCdiff = PBC_diff_dumb;
                pbc_choice = 1;
            }
            else {
                use_PBCdiff = PBC_diff;
                pbc_choice = 0;
            }

            // find the other relJ from the same box
            int tot = 0;
            for (int subix = 0; subix < nOscAts; subix++) {
                tots[subix] = 999999999;
                int temp = 0;
                for (int i = 0; i < 3; i++) {
                    if (boxchoice[i] == subbox[subix * 3 + i]) {
                        temp += 1;
                    }
                }
                if (temp == 3) {
                    tots[tot] = subix;
                    // printf("%d  %d\n", tots[tot], tot);
                    tot += 1;
                    check[subix] = 1;
                }
            }

            // printf("start box loop\n");

            float xmin, ymin, zmin;
            float xmax, ymax, zmax;
            int curat = 0;
            // printf("%d", n_subbox[0]);
            for (int x = 0; x < n_subbox[0]; x++) {
                int xdif = abs(x - boxchoice[0]);
                tempbox[0] = x;
                if (xdif == 0) {
                    xmin = 0;
                    xmax = subboxdims[0];
                } else {
                    // n_subbox[0] = amount of boxes along x
                    if (xdif > n_subbox[0] / 2) {
                        xdif = abs(xdif - n_subbox[0]);
                    }
                    xmin = (xdif - 1) * subboxdims[0];
                    xmax = (xdif + 1) * subboxdims[0];
                }
                for (int y = 0; y < n_subbox[1]; y++) {
                    int ydif = abs(y - boxchoice[1]);
                    tempbox[1] = y;
                    if (ydif == 0) {
                        ymin = 0;
                        ymax = subboxdims[1];
                    } else {
                        // n_subbox[1] = amount of boxes along y
                        if (ydif > n_subbox[1] / 2) {
                            ydif = abs(ydif - n_subbox[1]);
                        }
                        ymin = (ydif - 1) * subboxdims[1];
                        ymax = (ydif + 1) * subboxdims[1];
                    }
                    for (int z = 0; z < n_subbox[2]; z++) {
                        int zdif = abs(z - boxchoice[2]);
                        tempbox[2] = z;
                        if (zdif == 0) {
                            zmin = 0;
                            zmax = subboxdims[2];
                        } else {
                            // n_subbox[2] = amount of boxes along z
                            if (zdif > n_subbox[2] / 2) {
                                zdif = abs(zdif - n_subbox[2]);
                            }
                            zmin = (zdif - 1) * subboxdims[2];
                            zmax = (zdif + 1) * subboxdims[2];
                        }
                        // float boxdist2 = xmin * xmin + ymin * ymin + zmin + zmin;
                        float boxdist2 = numveclen2(xmin, ymin, zmin);
                        // printf("%d  ", curat);

                        // printf("box found\n");
                        // if the box is too far away, skip it!
                        if (boxdist2 > maxdist2) {
                            curat += nat_psbox[x * n_subbox[1] * n_subbox[2] + y * n_subbox[2] + z];
                            continue;
                        }

                        if (pbc_choice == 0) {
                            pbc_choice_sum = 0;
                            for (int i = 0; i < 3; i++) {
                                if (tempbox[i] * subboxdims[i] > maxdist) {
                                    pbc_choice_sum += 1;
                                }
                                if ((tempbox[i] + 1) * subboxdims[i] < boxdims[i] - maxdist) {
                                    pbc_choice_sum += 1;
                                }
                            }
                            if (pbc_choice_sum == 6) {
                                use_PBCdiff = PBC_diff_dumb;
                            }
                            else {
                                use_PBCdiff = PBC_diff;
                            }
                        }
                        else {
                            use_PBCdiff = PBC_diff_dumb;
                        }

                        // printf("just checking!  ");
                        // float xmax = xmin + (subboxdims[0] * 2);
                        // float ymax = ymin + (subboxdims[1] * 2);
                        // float zmax = zmin + (subboxdims[2] * 2);
                        // boxdist2 = xmax * xmax + ymax * ymax + zmax * zmax;
                        boxdist2 = numveclen2(xmax, ymax, zmax);

                        // printf("box accepted\n");
                        // if the box is very close, use all!
                        int checkval = curat + nat_psbox[x * n_subbox[1] * n_subbox[2] + y * n_subbox[2] + z];
                        // printf("maxdist2: %f \n", maxdist2);
                        // printf("boxdist2: %f \n", boxdist2);
                        if (boxdist2 < maxdist2) {
                            // printf("atom in boxrange\n");
                            for (int i = curat; i < checkval; i++) {
                                int atnum = atix_psbox[i];
                                charge = charges[atnum];
                                // dont do this atom if it one of those in tocalc
                                if (atnum >= minix && atnum <= maxix) {
                                    if (test_inarray(atnum, tocalc, nOscAts) == 1) {
                                        // printf("561");
                                        continue;
                                    }
                                }
                                for (int subix = 0; subix < nOscAts; subix++) {
                                    int usesub = tots[subix];
                                    // printf("%d %d %d %d\n", subix, usesub, tocalc[usesub], atnum);
                                    if (tots[subix] == 999999999) {
                                        break;
                                    }
                                    if (tocalc[usesub] == atnum) {
                                        continue;
                                    }
                                
                                    use_PBCdiff(&refpos[usesub * 3], &positions[atnum * 3], halfbox, boxdims, diff);

                                    dist2 = veclen2(diff);
                                    float dist = sqrt(dist2);
                                    if (dist > maxdist) {
                                        continue;
                                    }
                                    // printf("out!\n");

                                    out[usesub] += potential_linear(dist, charge, min_dist, maxdist, smooth_domain);
                                    if (dist <= min_dist || smooth_domain == 0){
                                    temp_charge[subix] += charge;
                                    }   else {
                                        temp_charge[subix] += (1 - (dist - min_dist) / smooth_domain) * charge;
                                    }
                                }
                            }
                        // if the box is somewhere in between, all must be checked!
                        } else {
                            for (int i = curat; i < checkval; i++) {
                                int atnum = atix_psbox[i];
                                charge = charges[atnum];

                                // dont do this atom if it one of those in tocalc
                                if (atnum >= minix && atnum <= maxix) {
                                    if (test_inarray(atnum, tocalc, nOscAts) == 1) {
                                        continue;
                                    }
                                }
                                for (int subix = 0; subix < nOscAts; subix++) {
                                    int usesub = tots[subix];
                                    if (tots[subix] == 999999999) {
                                        break;
                                    }
                                    if (tocalc[usesub] == atnum) {
                                        continue;
                                    }
                                    use_PBCdiff(&refpos[usesub * 3], &positions[atnum * 3], halfbox, boxdims, diff);
                                    dist2 = veclen2(diff);
                                    float dist = sqrt(dist2);
                                    if (dist > maxdist) {
                                        continue;
                                    }
                                    out[usesub] += potential_linear(dist, charge, min_dist, maxdist, smooth_domain);
                                    if (dist <= min_dist || smooth_domain == 0){
                                    temp_charge[subix] += charge;
                                } else {
                                    temp_charge[subix] += (1 - (dist - min_dist) / smooth_domain) * charge;
                                    // printf("%f\n",temp_charge[subix]);
                                }
                                    // printf("out : %f\n", *out);
                                    }
                                }
                            }
                        curat += nat_psbox[x * n_subbox[1] * n_subbox[2] + y * n_subbox[2] + z];
                    }
                }
            }
            checksum = 0;
            for (int subix = 0; subix < nOscAts; subix++) {
                checksum += check[subix];
            }
        }
        float contra_charge_dist = maxdist- smooth_domain/2;

        for (int usesub = 0; usesub < nOscAts; usesub++){
            out[usesub] += potential_linear(maxdist, temp_charge[usesub], maxdist, maxdist, smooth_domain);
        }

        free(refpos), free(subbox), free(check), free(tots);

    }

    void calcPot_residues_aa(float *positions, float *charges, int *resnums, int Natoms, int *tocalc, int nOscAts, int *reslens, int Nres, float *COMs, float *ressize, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out) {

        float min_dist = maxdist - smooth_domain;

        float *refpos;
        int *refres, *check, *tots;

        float diff[3];
        float dist2, dist;
        float findist;
        float maxdist2;

        float *temp_charge;
        temp_charge = (float *)calloc(nOscAts, sizeof(float));

        int checksum;

        refpos = (float *)calloc(3*nOscAts, sizeof(float));
        refres = (int *)calloc(nOscAts, sizeof(int));
        check = (int *)calloc(nOscAts, sizeof(int));
        tots = (int *)calloc(nOscAts, sizeof(int));

        for (int subix = 0; subix < nOscAts; subix++) {
            int mainix = tocalc[subix];
            refres[subix] = resnums[mainix];
            for (int i = 0; i < 3; i++) {
                refpos[subix * 3 + i] = positions[mainix * 3 + i];
            }
        }

        maxdist2 = maxdist * maxdist;
        checksum = 0;
        int smallest, resnum;
        
        while (checksum < nOscAts) {
            // find lowest relJ that hasn't been considered yet
            // (just like with subbox, this function allows for the atoms of
            // this 'oscillator' to belong to different 'groups'. In this case,
            // a 'group' is a residue as defined by MDA)
            smallest = nOscAts;
            for (int subix = 0; subix < nOscAts; subix++) {
                if (check[subix] == 0) {
                    smallest = std::min(smallest, subix);
                }
            }
            
            // extract resnum of this lowest relJ
            resnum = refres[smallest];
            
            // find the other relJ from the same residue
            int tot = 0;
            for (int subix = 0; subix < nOscAts; subix++) {
                tots[subix] = 999999999;
                if (refres[subix] == resnum) {
                    tots[tot] = subix;
                    tot += 1;
                    check[subix] = 1;
                }
            }

            float refsize = ressize[resnum];
            // refCOM = COMs[resnum];

            int atsinres = 0;
            int curat = 0;
            float charge;

            for (int resix = 0; resix < Nres; resix++) {
                curat += atsinres;
                atsinres = reslens[resix];
                // resnum = resnum of the residue where the field is calculated
                float resix_size = ressize[resix];
                // resix_COM = COMs[resix];

                // find how distant this residue is

                PBC_diff(&COMs[resnum * 3], &COMs[resix * 3], halfbox, boxdims, diff);
                dist2 = veclen2(diff);
                dist = sqrt(dist2);

                // we must take into account how close atoms can actually get
                // printf("%d\n", resix);
                // printf("%f %f %f %f %f %f\n", COMs[resnum * 3], COMs[resnum * 3 + 1], COMs[resnum * 3 + 2], COMs[resix * 3], COMs[resix * 3 + 1], COMs[resix * 3 + 2]);
                // printf("%f %f %f %f\n", dist, resix_size, refsize, maxdist);
                findist = dist - ((resix_size + refsize));

                // if the residue is too far away, skip it!
                if (findist > maxdist) {
                    continue;
                }

                // in all other cases, check all pairs of atoms!
                for (int atnum = curat; atnum < curat + atsinres; atnum++) {
                    charge = charges[atnum];
                    for (int subix = 0; subix < nOscAts; subix++) {
                        int usesub = tots[subix];
                        if (tots[subix] == 999999999) {
                            break;
                        }
                        if (tocalc[usesub] == atnum) {
                            continue;
                        }

                        PBC_diff(&refpos[usesub * 3], &positions[atnum * 3], halfbox, boxdims, diff);

                        float dist2 = veclen2(diff);
                        float dist = sqrt(dist2);

                        if (dist > maxdist) {
                           continue;
                        }
                        
                        out[subix] += potential_linear(dist, charge, min_dist, maxdist, smooth_domain);
                        if (dist <= min_dist || smooth_domain == 0){
                            temp_charge[subix] += charge;
                        } else {
                            temp_charge[subix] += (1 - (dist - min_dist) / smooth_domain) * charge;
                        }
                    }

                }
            }
        
        checksum = 0;

        } // end of while loop
        for (int subix = 0; subix < nOscAts; subix++) {
            checksum += check[subix];
        }
        for (int usesub = 0; usesub < nOscAts; usesub++){
            out[usesub] += potential_linear(maxdist, temp_charge[usesub], maxdist, maxdist, smooth_domain);
        }

        free(refpos), free(refres), free(check), free(tots), free(temp_charge);

    }

    // For calculating ma
    void calcPot_subbox_ma(float *positions, float *charges, int Natoms, int *tocalc, int nOscAts, int *n_subbox, float *subboxdims, int *nat_psbox, int *atix_psbox, float *goalCOM, float *COMs, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out) {
        /* 
        Just like calcPot_subbox_aa, this calculates the potential felt by each
        of the atoms in tocalc. However, the atoms influencing the atoms we're
        calculating the potential for are found differently.
        In _aa, for each of the nOscAts, the sphere of influencers (bound by 
        maxdist) is found separately: an influencing atom may influence some of
        the nOscAts, not necessarily all.
        Here, only atoms that are within a given distance from the COM's of the
        OscAts will be influencers, and they'll influence all.
        Therefore, none of the atoms amongst OscAts can be influencers.
        How are the COM's calculated? during dev, the output of calc_COM is used,
        but as long as the array has the correct shape, it can just as well be
        something else!
        */

        float min_dist = maxdist - smooth_domain;

        using func = void(*)(float *, float *, float *, float *, float *);
        func use_PBCdiff = PBC_diff;

        // float *temp_charge = new float[nOscAts]();
        // for (int idx = 0; idx < nOscAts; idx++) {
        //     temp_charge[idx] = 0;
        // }

        float *temp_charge;
        temp_charge = (float *)calloc(nOscAts, sizeof(float));

        float *refpos;
        refpos = (float *)calloc(3*nOscAts, sizeof(float));
        float diff[3];
        int COMbox[3];

        int lowatix, highatix;
        float maxdist2 = maxdist * maxdist;
        float charge, dist2, dist;
        
        // save positions of each of the atoms of tocalc into refpos array
        // also, find lowest and highest atix in tocalc (most likely, will be close by)
        lowatix = tocalc[0];
        highatix = tocalc[0];
        for (int subix = 0; subix < nOscAts; subix++) {
            int mainix = tocalc[subix];
            lowatix = std::min(lowatix, mainix);
            highatix = std::max(highatix, mainix);
            for (int i = 0; i < 3; i++) {
                refpos[subix * 3 + i] = positions[mainix * 3 + i];
            }
        }

        // find out to which subbox the COM belongs
        for (int i = 0; i < 3; i++) {
            COMbox[i] = goalCOM[i] / subboxdims[i];
        }
        
        // loop over all boxes
        float minboxdist[3];
        float maxboxdist[3];
        int curat = 0;
        for (int x = 0; x < n_subbox[0]; x++) {
            minmaxfinder_ma(x, 0, subboxdims, goalCOM, halfbox, boxdims, minboxdist, maxboxdist);

            for (int y = 0; y < n_subbox[1]; y++) {
                minmaxfinder_ma(y, 1, subboxdims, goalCOM, halfbox, boxdims, minboxdist, maxboxdist);
                
                for (int z = 0; z < n_subbox[2]; z++) {
                    minmaxfinder_ma(z, 2, subboxdims, goalCOM, halfbox, boxdims, minboxdist, maxboxdist);

                    float boxdist2 = veclen2(minboxdist);

                    // if the box is too far away, skip it!
                    if (boxdist2 > maxdist2) {
                        // printf("Box was skipped!\n");
                        curat += nat_psbox[x * n_subbox[1] * n_subbox[2] + y * n_subbox[2] + z];
                        continue;
                    }

                    boxdist2 = veclen2(maxboxdist);

                    int checkval = curat + nat_psbox[x * n_subbox[1] * n_subbox[2] + y * n_subbox[2] + z];

                    // if the box is very close, use all!
                    if (boxdist2 < maxdist2) {
                        // printf("Entire box is used!\n");
                        for (int i = curat; i < checkval; i++) {
                            int atnum = atix_psbox[i];
                            charge = charges[atnum];

                            // dont do this atom if it is one of those in tocalc
                            if (atnum >= lowatix && atnum <= highatix) {
                                if (test_inarray(atnum, tocalc, nOscAts) == 1) {
                                    continue;
                                }
                            }

                            // otherwise, add influence of this atom to all!
                            for (int subix = 0; subix < nOscAts; subix++) {
                                use_PBCdiff(&refpos[subix * 3], &positions[atnum * 3], halfbox, boxdims, diff);
                                dist2 = veclen2(diff);
                                dist = sqrt(dist2);

                                if (dist > maxdist) {
                                    continue;
                                }

                                out[subix] += potential_linear(dist, charge, min_dist, maxdist, smooth_domain);
                                if (dist <= min_dist || smooth_domain == 0){
                                    temp_charge[subix] += charge;
                                } else {
                                    temp_charge[subix] += (1 - (dist - min_dist) / smooth_domain) * charge;
                                }
                            }
                        }
                    }
                    // if the box is somewhere in between, all must be checked!
                    else {
                        // printf("box is somewhere in between!\n");
                        for (int i = curat; i < checkval; i++) {
                            int atnum = atix_psbox[i];
                            charge = charges[atnum];

                            // dont do this atom if it one of those in tocalc
                            if (atnum >= lowatix && atnum <= highatix) {
                                if (test_inarray(atnum, tocalc, nOscAts) == 1) {
                                    continue;
                                }
                            }

                            // dont do this atom if it is too far away from COM
                            use_PBCdiff(goalCOM, &positions[atnum * 3], halfbox, boxdims, diff);
                            dist2 = veclen2(diff);
                            if (dist2 > maxdist2) {
                                continue;
                            }

                            // otherwise, add influence of this atom to all!
                            for (int subix = 0; subix < nOscAts; subix++) {
                                use_PBCdiff(&refpos[subix * 3], &positions[atnum * 3], halfbox, boxdims, diff);
                                dist2 = veclen2(diff);
                                dist = sqrt(dist2);

                                if (dist > maxdist) {
                                     continue;
                                }

                                out[subix] += (potentialPtr)(dist, charge, min_dist, maxdist, smooth_domain);
                                if (dist <= min_dist || smooth_domain == 0){
                                    temp_charge[subix] += charge;
                                } else {
                                    temp_charge[subix] += (1 - (dist - min_dist) / smooth_domain) * charge;
                                }
                            }
                        }
                    }
                    curat += nat_psbox[x * n_subbox[1] * n_subbox[2] + y * n_subbox[2] + z];
                }
            }
        }
        for (int subix = 0; subix < nOscAts; subix++) {
            out[subix] -= (potentialPtr)(maxdist, temp_charge[subix], maxdist, maxdist, smooth_domain);
        }

        free(refpos), free(temp_charge);
    }

    // For calculating mm
    void calcPot_perres_mm(float *positions, float *charges, int *resnums, int *tocalc, int nOscAts, int *reslens, int Nres, float *COMs, float *halfbox, float *boxdims, float maxdist, int smoothing, float smooth_domain, float *out) {

        float min_dist = maxdist - smooth_domain;
        
        float *refpos;
        refpos = (float *)calloc(3*nOscAts, sizeof(float));

        float diff[3];

        float dist2, dist;
        float maxdist2 = maxdist * maxdist;
        float comp_smoothing;

        int resnum;

        float *temp_charge;
        temp_charge = (float *)calloc(nOscAts, sizeof(float));

        for (int subix = 0; subix < nOscAts; subix++) {
            int mainix = tocalc[subix];
            for (int i = 0; i < 3; i++) {
                refpos[subix * 3 + i] = positions[mainix * 3 + i];
            }
        }

        // get resnum of this molecule
        resnum = resnums[tocalc[0]];

        int atsinres = 0;
        int curat = 0;
        float charge;

        for (int resix = 0; resix < Nres; resix++) {
            curat += atsinres;
            atsinres = reslens[resix];

            // find distance to residue
            PBC_diff(&COMs[resnum * 3], &COMs[resix * 3], halfbox, boxdims, diff);
            dist2 = veclen2(diff);
            dist = sqrt(dist2);
            // if the residue is too far away, skip it
            if (dist2 >= maxdist2) {
                continue;
            }

            // if it's the same residue, skip it
            if (resix == resnum) {
                continue;
            }

            if (dist >= min_dist){
                comp_smoothing = (1 - (dist - min_dist) / smooth_domain);
            }
            else {
                comp_smoothing = 1;
            }

            for (int atnum = curat; atnum < curat + atsinres; atnum++) {
                charge = charges[atnum];
                for (int subix = 0; subix < nOscAts; subix++) {
                    PBC_diff(&refpos[subix * 3], &positions[atnum * 3], halfbox, boxdims, diff);
                    dist2 = veclen2(diff); // Redefining of dist2 and running PBC_diff is not an accident!!! 
                    dist = sqrt(dist2);
                    
                    float float_temp = charge / dist * comp_smoothing;

                    out[subix] += float_temp; // This way of computing smoothing is very scuffed!
                    temp_charge[subix] += comp_smoothing * charge;
                }
            }
        }
        for (int subix = 0; subix < nOscAts; subix++) {
            out[subix] -= potential_linear(maxdist, temp_charge[subix], maxdist, maxdist, smooth_domain);
            // printf("%f \n", out[subix]);
        }


        free(refpos), free(temp_charge);

    }
}