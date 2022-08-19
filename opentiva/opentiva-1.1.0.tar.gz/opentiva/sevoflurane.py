from . model import Model

"""
opentiva.sevoflurane
====================

This module contains the classes for the sevoflurane models.

All Classes have the same parameters and attributes.

Parameters
----------
sex
    0 for male or 1 for female
age
    in years
weight
    in kg
height
   in cm

Attributes
----------
compartments : int
    number of compartments to model; 1, 2 or 3
concentration_unit : str
    drug concentration unit
target_unit : str
    target concentration unit
age_lower : float
    lower age limit of model; -1 if no limit
age_upper : float
    upper age limit of model; -1 if no limit
weight_lower : float
    lower weight limit of model; -1 if no limit
weight_upper : float
    upper weight limit of model; -1 if no limit
pmid : str
    Pubmed ID of model's reference
doi : str
    Digital Object Identifier (DOI) of model's reference
warning : str
    Warnings relating to non-validated anthropometric values
v1 : float
    volume of central compartment
k10 : float
    equilibrium rate constant from compartment 1 to 0
k12 : float
    equilibrium rate constant from compartment 1 to 2
k13 : float
    equilibrium rate constant from compartment 1 to 3
k21 : float
    equilibrium rate constant from compartment 2 to 1
k31 : float
    equilibrium rate constant from compartment 3 to 1
ke0 : float
    effect compartment equilibrium rate constant
"""


class Cortinez(Model):
    """Cortinez class holds pharmacokinetic parameters for the Cortinez
    sevoflurane model.

    Reference: PMID: 30117213 DOI: 10.1111/pan.13465
    """

    def __init__(self, sex: int, age: float, weight: float, height: float):
        super().__init__(sex, age, weight, height)

        self.compartments = 3
        self.concentration_unit = "%"
        self.age_lower = 3
        self.age_upper = 71
        self.weight_lower = -1
        self.weight_upper = -1
        self.target_unit = "bis"
        self.pmid = "30117213"
        self.doi = "10.1111/pan.13465"
        self.validate_anthropometric_values()

        self.v1 = 4.45 * weight * 10
        self.v2 = 3.94 * weight * 10
        self.v3 = 17.6 * weight * 10

        self.cl1 = 4.8 * weight * 10
        self.cl2 = 2.34 * weight * 10
        self.cl3 = 3.07 * weight * 10

        self.k10 = self.cl1 / self.v1
        self.k12 = self.cl2 / self.v1
        self.k13 = self.cl3 / self.v1
        self.k21 = self.cl2 / self.v2
        self.k31 = self.cl3 / self.v3

        if age <= 38:
          self.ke0 = 0.693 / 1.22
        else:
          self.ke0 = 0.690 / (1.22 * 1.54)

