
################################################################
Ways of calculating electrostatic properties
################################################################


In principle, calculating the potential at a given point (here we'll call it the PoI) is incredibly simple. Sum up the potential felt from each point charge around. However, not all point charges are that close by. A very distant point charge has a very small influence, so it is probably not worth the computational effort to include it. How do we approximate the potential accurately using the smallest possible amount of charges? Different options include:

- **atom-atom**. If a charge is closer to the PoI than the given limit, it's influence is included, otherwise, it is not. 
  - *Advantage*: the found potential is relatively true to the actual potential at the POI
  - *Disadvantage*: when taking the difference of two potentials, those potentials are influenced by a different group of charges, resulting in a VERY noisy spectrum. 
  - *Disadvantage*: the total charge around does not have to be 0, or even an integer.
  - *Disadvantage*: A pair of opposite charges can be split in half - creating the illusion of a much stronger potential.
- **molecule-atom**. If a charge is closer to the centre of mass (CoM) of the residue of the PoI than the given limit, it's influence is included, otherwise, it is not.
  - *Advantage*: all atoms in the molecule feel the same set of charges, so taking differences becomes more meaningful.
  - *Disadvantage*: The total charge around does not have to be 0, or even an integer. 
  - *Disadvantage*:, if the residue is very large, the PoI might be very far away from the CoM, leading to a less accurate potential, or requiring a larger radius within which to consider charges.
  - *Disadvantage*: A pair of opposite charges can be split in half - creating the illusion of a much stronger potential.
- **molecule-molecule** (also labeled perres). The influence of a charge on a PoI is only included if the CoM's of the residues each belongs to are within a certain limit. 
  - *Advantage*: all atoms in the molecule feel the same set of charges, so taking differences becomes more meaningful.
  - *Advantage*: the chance that the total charge is neutral is much larger, and otherwise, it must at least be an integer (with the 'off' charge probably being quite far away)
  - *Disadvantage*: If either the residue of the PoI or any of the residues around is large, a charge could come very close to the PoI, but still not be counted. This can either lead to a (much) less accurate potential, or require a larger radius within which to consider charges.
  - *Disadvantage*: A pair of opposite charges can be split in half - creating the illusion of a much stronger potential.
- **soft cutoff**. Can be applied to each of the three methods. The most important reason for using this method is to deal with the general mentioned issue above - if two opposite charges are closeby to eachother, they could be 'split' in half, where one is close enough to be considered, and the other is not. The soft cutoff, as the name implies, is more gentle. Charges close enough are considered fully, but charges close to the cutoff are considered partly, with a formula (often linear) linking the distance and their 'weight'. The main disadvantage is that a larger radius is needed to accomodate the charges, and that applying the soft part is more computationally expensive (requiring more if-checks)
- **neutralizing charges**. Can be applied to each of the three methods. Some magic to get neutral charge to influence the PoI. May or may not be applicable to electric fields (and gradients)? Should have the advantage of much less noise in the potential-distance graph.
- **splitting residues**. If a residue is very large, split it in (neutral) parts. Only applicable for ma and mm methods.
  - Advantage: removes the issue of possible ignoring closeby charges.
  - Disadvantage: When splitting through the residue of the PoI, the disadvantage of different groups of charges influencing the PoI returns.
  - maybe, split all but the residue of the PoI? Or, when splitting the residue of the PoI, don't split the PoIs contributing to a single frequency?
