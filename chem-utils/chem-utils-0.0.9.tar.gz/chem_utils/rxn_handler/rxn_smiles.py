#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2022/8/15 17:15
# @Author  : zbc@mail.ustc.edu.cn
# @File    : rxn_smiles.py
# @Software: PyCharm


from rdkit.Chem import AllChem
from rdkit.Chem.AllChem import ChemicalReaction


class RxnSmiles:

    # region ===== rdrxn_from_indigo_smiles =====

    @classmethod
    def _parse_indigo_tag(cls, indigo_tags_str: str) -> [[int]]:

        for tags in indigo_tags_str.split(','):
            pass
        indigo_tags = [[int(tag) for tag in tags.split('.')] for tags in indigo_tags_str.split(',')]
        return indigo_tags

    @classmethod
    def _split_smiles_by_indigo_tags(cls, rxn_smiles: str, indigo_tags: [[int]]) -> ([str], [str]):
        rs_smiles, ps_smiles = rxn_smiles.split('>>')
        r_smileses = rs_smiles.split('.')
        p_smileses = ps_smiles.split('.')
        all_smileses = r_smileses.copy()
        all_smileses.extend(p_smileses)
        num_rs = len(r_smileses)
        rs = []
        ps = []
        all_tags = []
        for tags in indigo_tags:
            all_tags.extend(tags)
            mol_smileses = []

            for tag in tags:
                mol_smileses.append(all_smileses[tag])
            if tags[0] >= num_rs:
                ps.append('.'.join(mol_smileses))
            else:
                rs.append('.'.join(mol_smileses))
        for i, smiles in enumerate(all_smileses):
            if i in all_tags:
                continue
            if i >= num_rs:
                ps.append(smiles)
            else:
                rs.append(smiles)
        return rs, ps

    @classmethod
    def _rdrxn_from_smileses(cls, r_smileses: [str], p_smileses: [str]):
        rdrxn = ChemicalReaction()
        for r_smiles in r_smileses:
            rdrxn.AddReactantTemplate(AllChem.MolFromSmiles(r_smiles))
        for p_smiles in p_smileses:
            rdrxn.AddProductTemplate(AllChem.MolFromSmiles(p_smiles))
        return rdrxn

    @classmethod
    def _split_indigo_smiles(cls, indigo_smiles: str) -> (str, str):
        if ' |f:' in indigo_smiles:
            rxn_smiles, indigo_tags_str = indigo_smiles.split(' |f:')
        else:
            rxn_smiles = indigo_smiles
            indigo_tags_str = ''

        if '^' in indigo_tags_str:
            indigo_tags_str = indigo_tags_str.split('^')[0]
        indigo_tags_str = indigo_tags_str.strip('|')
        return rxn_smiles, indigo_tags_str

    @classmethod
    def rdrxn_from_indigo_smiles(cls, indigo_smiles: str):
        rxn_smiles, indigo_tags_str = cls._split_indigo_smiles(indigo_smiles)
        indigo_tags = cls._parse_indigo_tag(indigo_tags_str)
        r_smileses, p_smileses = cls._split_smiles_by_indigo_tags(rxn_smiles, indigo_tags)
        return cls._rdrxn_from_smileses(r_smileses, p_smileses)

    # endregion


if __name__ == "__main__":
    pass
