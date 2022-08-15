# -*- coding: utf-8 -*-
from anastruct import SystemElements
ss = SystemElements()
import matplotlib.pyplot as plt

#! Using Anastruct example
#! Anastruct is a python package that allow analyse 2D frames and trusses for slender structures. Determine the bending moments, shear forces, axial forces and displacements.
#! Here is the Anastruct documentation:
#! https://anastruct.readthedocs.io/en/latest/index.html
#! https://github.com/ritchie46/anaStruct

ss.add_element(location=[[0, 0], [3, 4]])
ss.add_element(location=[[3, 4], [8, 4]])

ss.add_support_hinged(node_id=1)
ss.add_support_fixed(node_id=3)

load = -10 #<< - uniform load

ss.q_load(element_id=2, q=load)
ss.solve()

fig = ss.show_structure(show=False)
plt #%plt
plt.clf()

fig = ss.show_shear_force(show=False)
plt #%plt
plt.clf()

fig = ss.show_displacement(show=False)
plt #%plt
plt.clf()