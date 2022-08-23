import pickle

import numpy as np
from qiskit.algorithms.optimizers import COBYLA

from qroestl.backends import Gurobi, Qiskit, Ocean, Cplex, Braket
from qroestl.model import Model
from qroestl.problems import MCMTWB_k_MaxCover, MPCMTWB_k_MaxCover

# pU, pR = MPCMTWB_k_MaxCover.gen_Q1(k=2, nR=1, R_width=100, R_height=100, nS_per_R=2, U_per_S=2)

# import cProfile, pstats
# profiler = cProfile.Profile()
# profiler.enable()

### Hack to use UE data
with open('data.pickle', 'rb') as f:
    data_pickle = pickle.load(f)
nU = data_pickle[0]
nS = data_pickle[1]
k = data_pickle[2]
R = data_pickle[3]
T = list(range(nS))  # data_pickle[4]
W = data_pickle[5]
UQ = data_pickle[6]
SQ = data_pickle[7]
C = data_pickle[8]
RC = data_pickle[9]

c1 = []
c2 = []
for i in range(len(RC)):
    c1.append(RC[i][0])
    c2.append(RC[i][1])
RC = [c1, c2]
RC = np.zeros(np.shape(RC), dtype=int).tolist()
### Hack end

### Syntehtic test data generation - "universe elements" (pU) and "region" (pR) approach
## Toy instance sample (for QC hardware)
# pU, pR = MPCMTWB_k_MaxCover.gen_partial(nR=1, nS_per_R=6, k=30, R_width=100, R_height=100, nT=20, minC1=90, minC2=80, overlap_ratio=1 / 3)
## Large instance sample (for classical solvers)
# pU, pR = MPCMTWB_k_MaxCover.gen_partial(nR=15, nS_per_R=50000, k=30, R_width=1000, R_height=1000, nT=20, minC1=90, minC2=80, overlap_ratio=1/3)

# profiler.disable()
# stats = pstats.Stats(profiler).sort_stats('cumtime')
# stats.print_stats()


tasks = [
    # (MCMTWB_k_MaxCover.gen_syn_fully_connected(100, 100), [MCMTWB_k_MaxCover.Standard()]),
    # (MCMTWB_k_MaxCover.gen_syn_random_coverages(10000, 100, 20), [MCMTWB_k_MaxCover.Standard()]),
    # (MCMTWB_k_MaxCover.Problem(nU=4, nS=3, k=2, R=[0, 0, 0, 0], T=[0, 0, 0], W=[1, 2.1, 1, 1], C=[[0], [1], [2, 3]]), [MCMTWB_k_MaxCover.Heuristic1()]),

    ### Used with the hack above to solve UE input
    (MPCMTWB_k_MaxCover.Problem(nU=nU, nS=nS, k=k, R=R, T=T, W=W, UQ=UQ, SQ=SQ, C=C, RC=RC), [MPCMTWB_k_MaxCover.Standard()]),

    # (MPCMTWB_k_MaxCover.Problem(nU=2, nS=3, k=2, R=[2, 0], T=[0, 1, 0], W=[1, 1], UQ=[50, 50], SQ=[50, 50, 52],
    #                             C=[  # List of dicts from tuple of sets to coverage
    #                                 # C1
    #                                 [
    #                                     {(0,): 60, (1,): 15, (2,): 20}, # u1
    #                                     {(2,): 20} # u2
    #                                 ],
    #                                 # C2
    #                                 [
    #                                     {(1, 2): 10}, # u1
    #                                     {} # u2
    #                                 ]
    #                             ],
    #                             RC=[
    #                                 # C1
    #                                 [15, # u1
    #                                  0 # u2
    #                                  ],
    #                                 # C2
    #                                 [10, # u1
    #                                  0]  # u2
    #                             ]),
    #                             [MPCMTWB_k_MaxCover.Standard()]),

    # (MPCMTWB_k_MaxCover.Problem(nU=4, nS=8, k=4, R=[0, 2, 1, 0], T=[0, 1, 2, 3, 4, 5, 6, 7], W=[1, 1, 1, 1], UQ=[50, 50, 50, 50], SQ=[50, 50, 52, 50, 50, 50, 50, 50],
    #                             C=[  # List of dicts from tuple of sets to coverage
    #                                 [{}, {(0,): 10, (1,): 30, (2,): 20, (3,): 33}, {(3,): 20, (4,): 50, (5,): 10}, {(5,): 20, (6,): 30, (7,): 10}],
    #                                 [{}, {(1, 2): 10}, {(3, 4): 10}, {(5,6): 15}]
    #                             ],
    #                             RC=[[0, 0, 0, 0], [0, 10, 0, 0]]),
    #                             [MPCMTWB_k_MaxCover.Standard()]),
    # (MPCMTWB_k_MaxCover.Problem(nU=1, nS=4, k=2, R=[2], T=[0, 1, 2, 0], W=[1], UQ=[50], SQ=[50, 50, 52, 50],
    #                             C=[  # List of dicts from tuple of sets to coverage
    #                                 [{(0,): 50, (1,): 20, (2,): 30, (3,): 40}],
    #                                 [{(1, 2): 10}]
    #                             ],
    #                             RC=[[10], [0]]), ## [0, 3] == 90
    #                             #RC=[[10], [10]]), ## [1, 2] == 50
    #  [MPCMTWB_k_MaxCover.Standard()]),
    #
    # (MPCMTWB_k_MaxCover.Problem(nU=1, nS=6, k=2, R=[2], T=[0, 1, 2, 4, 4, 5], W=[1], UQ=[50], SQ=[50, 50, 52, 50, 50, 50],
    #                             C=[  # List of dicts from tuple of sets to coverage
    #                                 [{(0,): 60, (1,): 50, (2,): 24, (3,): 68, (4,): 92, (5,): 30}],
    #                                 [{(0, 2): 17, (4, 5): 27}]
    #                             ],
    #                             RC=[[10], [10]]), ## [4, 5] == 122
    #  [MPCMTWB_k_MaxCover.Standard()]),

    # (MPCMTWB_k_MaxCover.Problem(nU=2, nS=12, k=4, R=[2]*2, T=range(12), W=[1]*2, UQ=[50]*2, SQ=[50]*12,
    #                             C=[  # List of dicts from tuple of sets to coverage
    #                                 [{(0,): 42, (1,): 91, (2,): 71, (3,): 21, (4,): 91, (5,): 41}, {(5,): 11, (6,): 53, (7,): 49, (8,): 70, (9,): 20, (10,): 86, (11,): 80}],
    #                                 [{(1, 2): 36, (3, 4): 10}, {(9, 5): 11, (6, 7): 11}]
    #                             ],
    #                             RC=[[10]*2, [10]*2]), ## [1, 2, 6, 7] == 264
    #  [MPCMTWB_k_MaxCover.Standard()]),

    # (MPCMTWB_k_MaxCover.gen2(nU=10, nS_per_U=100, k=40), [MPCMTWB_k_MaxCover.Standard()]),
    # (MPCMTWB_k_MaxCover.gen_U(k=3, Rs=MPCMTWB_k_MaxCover.gen_2d_random_boxes(nR=1, R_width=2, R_height=2, nS_per_R=2, U_per_S=2)), [MCMTWB_k_MaxCover.Standard()]),


    ### Used in conjunction with the partial generation above
    # (pR, [MPCMTWB_k_MaxCover.Standard()]),
    # (pU, [MCMTWB_k_MaxCover.Standard()]),
]

optimizers = [
    ### Qroestl
    #Model.BruteForce(),
    # MCMTWB_k_MaxCover.Greedy(),

    ### Qiskit
    #Qiskit.CPLEX(),
    # Qiskit.Gurobi(),
    # Qiskit.NumpyExact(),
    # Qiskit.DWaveAnnealer(),  # make sure that DWave tools / configuration is in place
    # Qiskit.VQE(quantum_instance=qdev, kwargs={'optimizer': COBYLA(1)}),
    # Qiskit.QAOA(kwargs={'reps': 2, 'optimizer': COBYLA(2)}),

    ### DWave
    # Ocean.Exact(),
    # Ocean.Greedy(),
    # Ocean.Tabu(),
    # Ocean.BQM(),
    # Ocean.BQM_Clique(),
    # Ocean.HybridBQM(),
    # Ocean.HybridCQM(),

    ### Braket
    # Braket.DWave(),

    ### Cplex
    Cplex.Optimizer(),
    # make sure that Cplex is installed, this unfortunately rather complex and only works in Python 3.8 for me (not in

    ### Gurobi
    # Gurobi.Optimizer(),
]
