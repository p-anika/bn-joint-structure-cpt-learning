"""bnjoint: reusable code for joint Bayesian-network structure + CPT-type learning.

Modules
-------
config       shared file paths and constants (number of states, scoring2a settings)
io           read BN-data.csv; write the `.dat` file that scoring2a reads
gobnilp_io   read the learned parent sets out of a GOBNILP console log
cpt_scores   BIC of the three CPT types (STD, MLR, OLR), convergence flags, the tie rule
structures   read an adjacency-matrix CSV (bnlearn) and a reference table; compare per node

The map of how these modules and the scripts fit together is in
`docs/code-guide/ARCHITECTURE.md`.
"""
