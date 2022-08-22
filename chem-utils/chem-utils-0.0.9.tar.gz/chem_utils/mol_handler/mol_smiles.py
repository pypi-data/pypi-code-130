#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2022/8/22 10:48
# @Author  : zhangbc0315@outlook.com
# @File    : mol_smiles.py
# @Software: PyCharm
import copy

from rdkit.Chem.rdchem import Mol
from rdkit.Chem import AllChem


class MolSmiles:

    @classmethod
    def get_smiles_without_map_num(cls, rdmol: Mol) -> str:
        _rdmol = copy.deepcopy(rdmol)
        for atom in _rdmol.GetAtoms():
            atom.SetAtomMapNum(0)
        return AllChem.MolToSmiles(_rdmol)


if __name__ == "__main__":
    rxn = AllChem.MolFromSmiles("[F:1][C:2]1[CH:7]=[CH:6][C:5](Br)=[CH:4][N:3]=1")
    print(MolSmiles.get_smiles_without_map_num(rxn))
