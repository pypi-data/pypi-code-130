import multiprocessing

import PyFGH.molecule_gui as molecule_gui

from PyFGH.util import DataObject as DataObject
import math

"""
The code in this file is for a gui (graphic user interface) application. This code is written with the tkinter library framework.
Author: Josiah Randleman
© Copyright 2021, Josiah Randleman, All rights reserved. jrandl516@gmail.com
"""

def main_window(valuesN, valuesL, dimensions, calculationtype, calculation2type, equilibrium_file, potential_energy, NumberOfEigenvalues):
    holder = DataObject.InputData()
    # valuesN = [11,11,11]
    # valuesL = [1.1,1.1,1.65]

    holder.setNlist(valuesN)
    holder.setLlist(valuesL)
    holder.setD(dimensions)

    print(holder.getNlist())
    print(holder.getLlist())
    print(holder.getD())

    def test():
        try:
            eq, pes = molecule_gui.molecule_testing(holder)
            holder.setEquilMolecule(eq)
            holder.setPES(pes)
        except:
            pass

    # holder.setequilibrium_file(r"C:\Users\Josiah Randleman\Downloads\water-equil.csv")
    holder.setequilibrium_file(equilibrium_file)
    # calculation = "Full Matrix"
    # calculation2 = "Read from File"
    calculation = calculationtype
    calculation2 = calculation2type
    holder.setcores_amount(max(1, multiprocessing.cpu_count()))
    # holder.setNumberOfEigenvalues(10)
    holder.setNumberOfEigenvalues(NumberOfEigenvalues)
    holder.setVmethod(calculation2)
    if calculation == "Sparse Matrix":
        holder.setEigenvalueMethod(True)

    if calculation == "Full Matrix":
        holder.setEigenvalueMethod(False)

    if calculation2 == "Read from File":
        # holder.setpotential_energy(r"C:\Users\Josiah Randleman\Downloads\water-potential.csv")
        holder.setpotential_energy(potential_energy)
        test()

    return holder


