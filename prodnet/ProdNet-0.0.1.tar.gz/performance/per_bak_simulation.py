""" Simple script to simulate a simple supply chain economy according to
the paper by Bak et al, 1992

The economy has L layers and each firm in each layer has two suppliers from the
layer below. The firms are on a cylindrical lattice of width L.
"""
import numpy as np
import matplotlib.pyplot as plt
from ProdNet import PerBak
from ProdNet.lib import icdf
import time

# Select economy depth and width, and total number of iterations
L = 1600
T = 1000

# Time performance for reference
start = time.time()

# Initialize simulation object
model = PerBak(L, T)

# Compute p, probability of demand "shock"
model.set_final_demand()

# Simulate
model.simulate()

# Print elapsed time
print(time.time() - start)  # current best=37s

# Plot Y distribution
Y = np.sum(model.P, axis=(1, 2))
x, p = icdf(Y)
plt.scatter(x, p)
plt.yscale('log')
plt.xscale('log')
plt.show()
