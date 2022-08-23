import abc
from enum import Enum
from typing import List, Union


class PauliType(Enum):
    """PauliType"""
    POT_PAULI_I = 0
    POT_PAULI_X = 1
    POT_PAULI_Y = 2
    POT_PAULI_Z = 3


class Observable(abc.ABC):
    """Observable class"""
    @abc.abstractmethod
    def obs_data(self):
        """return Observable data."""


class Pauli(Observable):
    """Pauli operator base class"""
    def __init__(self, targets: List[int], pauli_type=PauliType.POT_PAULI_I):
        self.targets = targets
        self.pauli_type = pauli_type

    def obs_data(self):
        """Get Observable data."""
        puali_list = []
        for temp in self.targets:
            pauli = {}
            pauli['oper_type'] = self.pauli_type.value
            pauli['target'] = temp
            puali_list.append(pauli)
        return puali_list


class PauliArrary(Observable):
    """Apply the Pauli"""

    def __init__(self, obj_arrary: List[Pauli]):
        self.obj_arrary = obj_arrary

    def obs_data(self):
        """Get Observable data."""
        puali_list = []
        for obj in self.obj_arrary:
            puali_list = puali_list + obj.obs_data()
        return puali_list


class PauliCoeffi(Observable):
    """Apply the PauliCoeffi"""
    def __init__(self, pauli_types: List[PauliType], coeffis: List[float]):
        self.pauli_types = pauli_types
        self.coeffis = coeffis

    def obs_data(self):
        """Get Observable data."""
        paulis = []
        for temp in self.pauli_types:
            paulis.append(temp.value)
        return (paulis, self.coeffis)
