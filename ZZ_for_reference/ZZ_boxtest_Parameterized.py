import ctypes as ct
import time

import matplotlib.pyplot as plt
import MDAnalysis as MDA
import numpy as np
import sys


class Universe():
    def __init__(self, univ, clibfname, outfiles, smoothing_domain, smoothing, out_name):
        print("start __init__")
        self.universe = univ
        self.get_properties()
        print(smoothing_domain, smoothing)
        self.smooth_domain = np.float32(smoothing_domain)
        self.out_name = out_name

        match smoothing: # Convert the smoothing type to an integer to pass it to C more easily
            case "hard":
                self.smoothing = np.int32(0)
            case "linear":
                self.smoothing = np.int32(1)
            case "quadratic":
                self.smoothing = np.int32(2)
        # for i in range(50):
        #     print(
        #         self.atnums[i], self.atnames[i], self.resnums[i],
        #         self.resnames[i]
        #     )

        self.def_system()
        clib = get_clib(clibfname)
        # self.calcall(outfiles, clib)
        # self.fast_compare_atat(clib)

        # self.make_residues()
        # self.calc_COM(clib)
        # self.make_boxes()
        # self.calcallpots_subbox_ma(clib)

        print("compare with sphereradius")

        self.compare_with_sphererad(clib)

    def compare_with_sphererad(self, clib):
        self.make_residues()
        self.calc_COM(clib)
        self.calc_ressize(clib)
        self.make_boxes()

        allradii = [out_name]  # VesTube
        # allradii = [r/10 for r in range(1, 600)]  # PsbS dimer
        do_aa = False
        do_ma = True
        do_mm = True

        start = time.time()
        if do_aa:
            print("doing aa")
            t0 = time.perf_counter()
            collector = []
            for step, radius in enumerate(allradii):
                if step % 25 == 0:
                    print(step)
                # get potential per radius
                # print(f"step : {step}")
                pot_sb_aa = self.calcallpots_perbox(clib, radius)
                collector.append(pot_sb_aa)
            t01 = time.perf_counter()
            # print(collector)
            # print(self.out_name)
            with open(f"subbox_aa_{self.out_name}.txt", "w") as file:
                for radius, lst in zip(allradii, collector):
                    file.write(str(radius) + " ")
                    for arr in lst:
                        for num in arr:
                            file.write(str(num) + " ")
                    file.write("\n")
            # print("Loop complete")
            toplot = [arr[0][0] for arr in collector]

            plt.plot(allradii, toplot, label="aa")
            print(t01-t0)

        if do_ma:
            t1 = time.perf_counter()
            collector = []
            for step, radius in enumerate(allradii):
                if step % 25 == 0:
                    print(step)
                # get potential per radius
                pot_sb_ma = self.calcallpots_subbox_ma(clib, radius)
                # print(f"collector: {pot_sb_ma}")
                collector.append(pot_sb_ma)
            t11 = time.perf_counter()

            with open(f"subbox_ma_{self.out_name}.txt", "w") as file:
                for radius, lst in zip(allradii, collector):
                    file.write(str(radius) + " ")
                    for arr in lst:
                        for num in arr:
                            file.write(str(num) + " ")
                    file.write("\n")

            toplot = [arr[0][0] for arr in collector]

            plt.plot(allradii, toplot, label="ma")
            print(t11-t1)

        if do_mm:
            tstart = time.perf_counter()
            collector = []
            for step, radius in enumerate(allradii):
                if step % 25 == 0:
                    print(step)
                # get potential per radius
                pot_res_mm = self.calcallpots_perres_mm(clib, radius)
                # print(pot_res_mm)
                collector.append(pot_res_mm)
            tend = time.perf_counter()

            with open(f"perres_mm_{self.out_name}.txt", "w") as file:
                for radius, lst in zip(allradii, collector):
                    file.write(str(radius) + " ")
                    for arr in lst:
                        for num in arr:
                            file.write(str(num) + " ")
                    file.write("\n")
            toplot = [arr[0][0] for arr in collector]

            plt.plot(allradii, toplot, label="mm")
            print(tend - tstart)

        # if any((do_aa, do_ma, do_mm)):
        #     plt.legend()
        #     plt.show()
        #     plt.close()
        end = time.time()
        print(f"time it took: {end - start} \n for radii: {allradii} \n aa:{do_aa} \n ma:{do_ma} \n perres:{do_mm}")

    def fast_compare_atat(self, clib):
        t0 = time.perf_counter()
        for i in range(0):
            print(i)
            self.calcallpots_peratom(clib)
        t1 = time.perf_counter()

        dorounds = 1
        for j in range(1):
            for i in range(dorounds):
                # print(i)
                self.make_boxes()
            ttemp = time.perf_counter()
            for i in range(dorounds):
                self.calcallpots_perbox(clib)
        t2 = time.perf_counter()

        for i in range(0):
            print(i)
            self.calcallpots_perres(clib)
        t3 = time.perf_counter()

        print(t1-t0, (t1-t0)/(checkthis+1))
        print(t2-t1, ttemp-t1, t2-ttemp, (t2-ttemp)/(checkthis+1))
        # print(t2-t1, ttemp-t1, t2-ttemp, (t2-t1)/(3800*dorounds/1000000))
        print(t3-t2, (t3-t2)/(checkthis+1))

    def calcall(self, outfiles, clib):
        for fname in outfiles:
            with open(fname, 'w') as file:
                pass

        # print(self.relJ)

        # self.make_boxes()

        for i in range(1):
            print(i)
            print(self.nOsc)
            # print(self.positions)
            # clib.move_box(
            #     self.positions_c, self.natoms,
            #     np.int32(0), np.int32(3800),
            #     self.boxdims_c, self.halfbox_c
            # )
            # print(self.positions)
            t0 = time.perf_counter()
            # res1 = self.calcallpots_peratom(clib)
            res1 = []
            t1 = time.perf_counter()
            print("time perats: ", t1-t0)
            resedit = "\n".join(
                [" ".join([str(num) for num in sublist]) for sublist in res1]
            )
            with open(outfiles[0], 'a') as file:
                file.write(resedit)

            self.make_boxes()
            res2 = self.calcallpots_perbox(clib)
            t2 = time.perf_counter()
            print("time perbox: ", t2-t1)
            resedit = "\n".join(
                [" ".join([str(num) for num in sublist]) for sublist in res2]
            )
            with open(outfiles[1], 'a') as file:
                file.write(resedit)

            self.make_residues()
            self.calc_COM(clib)
            self.calc_ressize(clib)

            res3 = self.calcallpots_perres(clib)
            t3 = time.perf_counter()
            print("time perres: ", t3-t2)
            resedit = "\n".join(
                [" ".join([str(num) for num in sublist]) for sublist in res3]
            )
            with open(outfiles[2], 'a') as file:
                file.write(resedit)

            # compare subbox
            results = [np.all(x == y) for x, y in zip(res1, res2)]
            print("allat vs subbox", sum(results))

            # compare resmeth
            results = [np.all(x == y) for x, y in zip(res1, res3)]
            print("allat vs perres", sum(results))

            # compare subres
            results = [np.all(x == y) for x, y in zip(res2, res3)]
            print("subbox vs perres", sum(results))

    def get_properties(self):
        self.atnums = self.universe.atoms.ix
        self.atnames = self.universe.atoms.names
        self.resnums = self.universe.atoms.resnums
        print("Resnums is {}".format(self.resnums))
        self.resnames = self.universe.atoms.resnames
        self.positions = self.universe.atoms.positions
        self.masses = self.universe.atoms.masses
        self.charges = self.universe.atoms.charges
        self.types = self.universe.atoms.types
        self.segids = self.universe.atoms.segids

        self.natoms = np.int32(self.resnums.shape[0])

        self.nres = np.int32(self.resnums[-1] + 1)

        self.boxdims = self.universe.dimensions[:3].astype('float32')
        self.halfbox = self.boxdims/2
        self.halfbox = self.halfbox.astype('float32')

        self.molnums = self.universe.atoms.molnums

        self.charges = self.charges.astype('float32')
        self.charges_c = np.ctypeslib.as_ctypes(self.charges)
        self.masses = self.masses.astype('float32')
        self.masses_c = np.ctypeslib.as_ctypes(self.masses)
        self.resnums = self.resnums.astype('int32')
        self.resnums_c = np.ctypeslib.as_ctypes(self.resnums)
        self.positions = self.positions.astype('float32')
        self.positions_c = np.ctypeslib.as_ctypes(np.ravel(self.positions))
        self.halfbox_c = np.ctypeslib.as_ctypes(self.halfbox)
        self.boxdims_c = np.ctypeslib.as_ctypes(self.boxdims)

        self.element_name = self.universe.atoms.elements

        atom = 0
            # print(self.atnames[atom], self.element_name[atom], self.atnums[atom], self.resnames[atom], self.resnums[atom])
        res_list = []
        for res in self.resnames:
            if res not in res_list:
                res_list.append(res)
        print(res_list)

        print(f"Number of residues is: {self.resnums[-1]}")

        # print(self.boxdims)
        # print(self.positions[[3906, 4529, 5062,
        # 063, 5161, 5320, 5781, 5828, 5830], :])

    def AbsResnums(self):
        """
        CHARMM support. Makes sure that every residue number is unique, and
        that the first one has ID 0.
        """
        prevresnum = -1
        writeresnum = -1
        for atomnum, ix in enumerate(self.atnums):
            if atomnum != ix:
                print(
                    "The atom number of the atom at position "
                    + str(atomnum)
                    + " does not match the position in the list! Quitting!")
            resnum = self.resnums[atomnum]
            if resnum != prevresnum:
                writeresnum += 1
            self.resnums[atomnum] = writeresnum
            prevresnum = resnum

    def def_system(self):
        resnames_Protein = [
            "ARG", "HIS", "LYS", "ASP", "GLU", "SER", "THR", "ASN", "GLN",
            "CYS", "GLY", "PRO", "ALA", "VAL", "ILE", "LEU", "MET", "PHE",
            "TYR", "TRP",

            "SOL", "NA"
        ]

        # resnames_Protein = [
        #     "MOL"
        # ]

        prevresnum = -1
        allats = []
        templist = []
        for ix in range(self.natoms):
            resnum = self.resnums[ix]
            if resnum != prevresnum:
                if ix != 0:
                    allats.append(templist)
                    templist = []
                resname = self.resnames[ix]
                if resname not in resnames_Protein:
                    break
            templist.append(ix)
            prevresnum = resnum
        else:
            allats.append(templist)

        print(len(allats))

        alllens = [len(v) for v in allats]
        # print("hoihoi, length = ", sum(alllens))
        maxlen = max(alllens)
        allats = [v + [v[-1]]*(maxlen - len(v)) for v in allats]

        self.allats = np.array(allats, dtype='int32')
        # print(self.allats)
        # print(self.allats.shape)
        self.relJ = [[x for x in range(y)] for y in alllens]
        # print(self.relJ)
        self.nOsc = len(self.relJ)

    def make_boxes(self):
        nbox = []
        target_size = 10
        for dim in self.boxdims:
            if ((dim % target_size) / target_size) > 0.5:
                nbox.append(dim//target_size + 1)
            else:
                nbox.append(dim//target_size)

        nbox = [int(x) for x in nbox]
        boxsize = [self.boxdims[x]/nbox[x] for x in range(3)]

        boxsize = np.array(boxsize)
        boxloc = self.positions // boxsize
        boxloc = boxloc.astype('int32')

        per_box = {}
        for ix in range(self.natoms):
            subbox = tuple(boxloc[ix, :])
            if subbox in per_box:
                per_box[subbox].append(ix)
            else:
                per_box[subbox] = [ix]

        at_ix_per_box = np.zeros((self.natoms), dtype='int32')
        n_at_per_subbox = np.zeros((nbox[0]*nbox[1]*nbox[2]), dtype='int32')
        cum_sum = 0
        cum_ix = 0
        for x in range(nbox[0]):
            for y in range(nbox[1]):
                for z in range(nbox[2]):
                    coords = (x, y, z)
                    try:
                        n_ats = len(per_box[coords])
                        atsarr = np.array(per_box[coords], dtype='int32')
                        at_ix_per_box[cum_sum:cum_sum+n_ats] = atsarr
                    except Exception:
                        n_ats = 0

                    n_at_per_subbox[cum_ix] = n_ats

                    cum_ix += 1
                    cum_sum += n_ats

        self.n_subbox = nbox  # number of subboxes in each dim
        self.subboxdims = boxsize  # size of each subbox in each dim
        self.subboxloc = boxloc  # ix of subbox of each atom
        self.n_at_per_subbox = n_at_per_subbox  # amount of atoms per subbox
        self.at_ix_per_subbox = at_ix_per_box  # atom ix sorted by subbox

        self.n_subbox_c = np.ctypeslib.as_ctypes(
            np.array(self.n_subbox, dtype='int32'))
        self.subboxdims_c = np.ctypeslib.as_ctypes(
            np.array(self.subboxdims, dtype='float32'))
        self.n_at_per_subbox_c = np.ctypeslib.as_ctypes(self.n_at_per_subbox)
        self.at_ix_per_subbox_c = np.ctypeslib.as_ctypes(self.at_ix_per_subbox)

    def calcallpots_peratom(self, clib, rdist=20):
        allpots = []
        maxdist = np.float32(rdist)

        smoothing = self.smoothing
        smooth_domain = self.smooth_domain

        # for oscgroup in range(self.nOsc):
        for oscgroup in range(checkthis + 1):
            # if oscgroup % 10 == 0:
            #     print(oscgroup)
            relJ = self.relJ[oscgroup]
            nOscAts = np.int32(len(relJ))

            tocalc = [self.allats[oscgroup, x] for x in relJ]
            tocalc_c = np.ctypeslib.as_ctypes(np.array(tocalc, dtype='int32'))
            pots = np.zeros((nOscAts), dtype='float32')
            pots_c = np.ctypeslib.as_ctypes(pots)

            clib.calcPot_atoms(
                self.positions_c, self.charges_c, self.natoms, tocalc_c,
                nOscAts, self.halfbox_c, self.boxdims_c, maxdist, smoothing, smooth_domain, pots_c
            )
            pots = np.ctypeslib.as_array(pots_c)
            # if oscgroup == checkthis:
            #     print(np.round(pots, decimals=5))
            # allpots.append(np.round(pots, decimals=6))
            # print(allpots)
        return allpots

    def calcallpots_perbox(self, clib, rdist=20):
        allpots = []
        maxdist = np.float32(rdist)
        # for oscgroup in range(self.nOsc):
        # print(f"maxdist is {maxdist}")
        for oscgroup in range(checkthis + 1):
            # if oscgroup % 100 == 0:
            #     print(oscgroup)
            relJ = self.relJ[oscgroup]
            nOscAts = np.int32(len(relJ))

            tocalc = [self.allats[oscgroup, x] for x in relJ]
            tocalc_c = np.ctypeslib.as_ctypes(np.array(tocalc, dtype='int32'))
            pots = np.zeros((nOscAts), dtype='float32')
            pots_c = np.ctypeslib.as_ctypes(pots)

            # print(f"line 431: domain = {type(self.smooth_domain)} and type = {type(self.smoothing)}" )
            # print("call calcPot_subbox_aa")
            clib.calcPot_subbox_aa(
                self.positions_c, self.charges_c, self.natoms, tocalc_c,
                nOscAts,
                self.n_subbox_c, self.subboxdims_c, self.n_at_per_subbox_c,
                self.at_ix_per_subbox_c,
                self.halfbox_c, self.boxdims_c, maxdist, self.smoothing, 
                self.smooth_domain, pots_c 
                
            )
            pots = np.ctypeslib.as_array(pots_c)

            # if oscgroup == checkthis:
            #     print(np.round(pots, decimals=5))
            allpots.append(np.round(pots, decimals=6))
            # print(f"allpots is : {allpots}")
            # print(f"checkthis is : {checkthis}")
            # print(f"oscgroup is : {oscgroup}")
        return allpots

    def calcallpots_perres(self, clib, rdist=20):
        allpots = []
        maxdist = np.float32(rdist)

        smoothing = self.smoothing
        smooth_domain = self.smooth_domain

        for oscgroup in range(checkthis + 1):
            # if oscgroup % 100 == 0:
            #     print(oscgroup)
            relJ = self.relJ[oscgroup]
            nOscAts = np.int32(len(relJ))

            tocalc_lst = [self.allats[oscgroup, x] for x in relJ]
            tocalc = np.array(tocalc_lst, dtype='int32')
            tocalc_c = np.ctypeslib.as_ctypes(tocalc)
            pots = np.zeros((nOscAts), dtype='float32')
            pots_c = np.ctypeslib.as_ctypes(pots)

            # print(self.positions.shape)
            # print(self.charges.shape)
            # print(self.resnums.shape)
            # print(self.natoms)
            # print(tocalc.shape, tocalc)
            # print(nOscAts)
            # print(self.reslens.shape)
            # print(self.nres)
            # print(self.COMs.shape)
            # print(self.ressize.shape)
            # quit()

            clib.calcPot_residues_aa(
                self.positions_c, self.charges_c, self.resnums_c, self.natoms,
                tocalc_c, nOscAts, self.reslens_c, self.nres, self.COMs_c,
                self.ressize_c, self.halfbox_c, self.boxdims_c, maxdist, smoothing, smooth_domain, pots_c
            )

            pots = np.ctypeslib.as_array(pots_c)

            # if oscgroup == checkthis:
            #     print(np.round(pots, decimals=5))
            # allpots.append(np.round(pots, decimals=6))
        return allpots

    def calcallpots_subbox_ma(self, clib, rdist=20):
        allpots = []
        maxdist = np.float32(rdist)

        smoothing = self.smoothing
        smooth_domain = self.smooth_domain

        for oscgroup in range(checkthis + 1):
            # if oscgroup % 100 == 0:
            #     print(oscgroup)
            relJ = self.relJ[oscgroup]
            nOscAts = np.int32(len(relJ))
            # print(nOscAts)

            tocalc = [self.allats[oscgroup, x] for x in relJ]
            tocalc_c = np.ctypeslib.as_ctypes(np.array(tocalc, dtype='int32'))
            pots = np.zeros((nOscAts), dtype='float32')
            pots_c = np.ctypeslib.as_ctypes(pots)

            # the choice COM is the COM of the residue that the 0th atom of
            # this oscgroup belongs to
            goalCOM = self.COMs[self.resnums[tocalc[0]], :]
            goalCOM_c = np.ctypeslib.as_ctypes(goalCOM)

            clib.calcPot_subbox_ma(
                self.positions_c, self.charges_c, self.natoms, tocalc_c,
                nOscAts, self.n_subbox_c, self.subboxdims_c,
                self.n_at_per_subbox_c, self.at_ix_per_subbox_c,
                goalCOM_c, self.COMs_c, self.halfbox_c, self.boxdims_c,
                maxdist, smoothing, smooth_domain, pots_c
            )

            pots = np.ctypeslib.as_array(pots_c)
            allpots.append(np.round(pots, decimals=6))
        return allpots

    def calcallpots_perres_mm(self, clib, rdist=20):
        allpots = []
        maxdist = np.float32(rdist)

        smoothing = self.smoothing
        smooth_domain = self.smooth_domain

        for oscgroup in range(checkthis + 1):
            relJ = self.relJ[oscgroup]
            nOscAts = np.int32(len(relJ))

            tocalc_lst = [self.allats[oscgroup, x] for x in relJ]
            tocalc = np.array(tocalc_lst, dtype='int32')
            tocalc_c = np.ctypeslib.as_ctypes(tocalc)
            pots = np.zeros((nOscAts), dtype='float32')
            pots_c = np.ctypeslib.as_ctypes(pots)

            clib.calcPot_perres_mm(
                self.positions_c, self.charges_c, self.resnums_c, tocalc_c,
                nOscAts, self.reslens_c, self.nres, self.COMs_c,
                self.halfbox_c, self.boxdims_c, maxdist, smoothing, smooth_domain, pots_c
            )
            
            pots = np.ctypeslib.as_array(pots_c)
            # print(pots)
            allpots.append(np.round(pots, decimals=6))
        return allpots

    def make_residues(self):
        self.reslens = np.zeros((self.nres), dtype='int32')

        tot = 0
        prevresnum = 0
        for resnum in self.resnums:
            if resnum != prevresnum:
                self.reslens[prevresnum] = tot
                tot = 0
                prevresnum = resnum
            tot += 1
        else:
            self.reslens[resnum] = tot
        self.reslens_c = np.ctypeslib.as_ctypes(self.reslens)

    def calc_COM(self, clib):
        self.COMs = np.zeros((self.nres, 3), dtype='float32')
        self.COMs_c = np.ctypeslib.as_ctypes(np.ravel(self.COMs))
        clib.calc_COM(
            self.positions_c, self.natoms, self.masses_c, self.reslens_c,
            self.nres, self.COMs_c, self.boxdims_c, self.halfbox_c
        )

    def calc_ressize(self, clib):
        self.ressize = np.zeros((self.nres), dtype='float32')
        self.ressize_c = np.ctypeslib.as_ctypes(self.ressize)
        clib.calc_ressize(
            self.positions_c, self.natoms, self.reslens_c,
            self.nres, self.ressize_c, self.boxdims_c, self.halfbox_c
        )


def get_clib(fname):
    clib = ct.CDLL(fname)

    clib.calcPot_atoms.argtypes = [
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.c_int, ct.POINTER(ct.c_int),
        ct.c_int, ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float), ct.c_float, ct.c_int, ct.c_float,
        ct.POINTER(ct.c_float)
    ]
    clib.calcPot_atoms.restype = None

    clib.calcPot_subbox_aa.argtypes = [
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.c_int, ct.POINTER(ct.c_int),
        ct.c_int,
        ct.POINTER(ct.c_int), ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_int), ct.POINTER(ct.c_int),
        ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float), ct.c_float, ct.c_int, ct.c_float,
        ct.POINTER(ct.c_float)
    ]
    clib.calcPot_subbox_aa.restype = None

    clib.calcPot_subbox_ma.argtypes = [
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.c_int, ct.POINTER(ct.c_int),
        ct.c_int,
        ct.POINTER(ct.c_int), ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_int), ct.POINTER(ct.c_int),
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float), ct.c_float, ct.c_int, ct.c_float,
        ct.POINTER(ct.c_float)
    ]
    clib.calcPot_subbox_ma.restype = None

    clib.calcPot_residues_aa.argtypes = [
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_int), ct.c_int,
        ct.POINTER(ct.c_int), ct.c_int,
        ct.POINTER(ct.c_int), ct.c_int,
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.c_float, ct.c_int, ct.c_float, ct.POINTER(ct.c_float)
    ]
    clib.calcPot_residues_aa.restype = None

    clib.calcPot_perres_mm.argtypes = [
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_int), ct.POINTER(ct.c_int),
        ct.c_int, ct.POINTER(ct.c_int), ct.c_int,
        ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float),
        ct.c_float, ct.c_int, ct.c_float, ct.POINTER(ct.c_float)
    ]

    clib.move_box.argtypes = [
        ct.POINTER(ct.c_float), ct.c_int,
        ct.c_int, ct.c_int,
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float)
    ]
    clib.move_box.restype = None

    clib.calc_COM.argtypes = [
        ct.POINTER(ct.c_float), ct.c_int,
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_int),
        ct.c_int, ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float)
    ]
    clib.calc_COM.restype = None

    clib.calc_ressize.argtypes = [
        ct.POINTER(ct.c_float), ct.c_int,
        ct.POINTER(ct.c_int),
        ct.c_int, ct.POINTER(ct.c_float),
        ct.POINTER(ct.c_float), ct.POINTER(ct.c_float)
    ]
    clib.calc_ressize.restype = None

    return clib


def get_universe(topfile, trjfile):
    universe = MDA.Universe(topfile, trjfile)
    print(universe.dimensions)
    return universe

def main(topfile, trjfile, clibfname, outfiles, out_name, smoothing_domain, smoothing):

    univ = get_universe(topfile, trjfile)
    print("start universe")
    WS = Universe(univ, clibfname, outfiles, smoothing_domain, smoothing, out_name)
    print(WS)

if __name__ == "__main__":
    tutfol = "D:\\VesnaTube\\VesnaTube\\2n0a_files"

    if len(sys.argv) != 4:
        raise Exception(
            "To use this file, you should type: "
            "ZZ_boxtest_Parameterized.py out_name smoothing_domain smoothing'")
    # topfile = tutfol + "PsbS-Mneq/PsbS_01.tpr"
    # trjfile = tutfol + "PsbS-Mneq/PsbS_01.xtc"

    # topfile = tutfol + "PsbS-Deq/PsbS_Deq_A_200.tpr"
    # trjfile = tutfol + "PsbS-Deq/PsbS_Deq_A_200_short.xtc"

    # topfile = tutfol + "VesnaTube/mix_nvt_new.tpr"
    # trjfile = tutfol + "VesnaTube/traj_comp_5_frames.xtc"

    # topfile = "/Users/kim/Documents/PhD/Data/md_0_1.tpr"
    # trjfile = "/Users/kim/Documents/PhD/Data/md_0_1_med.xtc"

    topfile = "2n0a.tpr"
    trjfile = "2n0a.xtc"

    out_name = str(sys.argv[1])
    
    # topfile = "D:\\Data\\PhD\\Tutorials\\PsbS-Mneq\\PsbS_01.tpr"
    # trjfile = "D:\\Data\\PhD\\Tutorials\\PsbS-Mneq\\PsbS_01.xtc"
    checkthis = 527490

    clibfname = tutfol + "\\ZZ_testclib.dll"
    # clibfname = "ZZ_testclib.dll"
    outfiles=["aa", "ma", "mm"]
    print(clibfname)

    smoothing_domain = int(sys.argv[2])
    smoothing = str(sys.argv[3])

    main(topfile, trjfile, clibfname, outfiles, out_name, smoothing_domain, smoothing)