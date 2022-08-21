#!/usr/bin/env python
from __future__ import print_function
from irff.reaxfflib import read_lib,write_lib
# from irff.irnnlib_new import write_lib
from irff.qeq import qeq
from ase.io import read
import argh
import argparse
import json as js
from os import environ,system


def q(gen='packed.gen'):
    p,zpe,spec,bonds,offd,angs,torp,hbs= read_lib(libfile='ffield')
    A = read(gen)
    q = qeq(p=p,atoms=A)
    q.calc()



def i():
    p,zpe,spec,bonds,offd,angs,torp,hbs= read_lib(libfile='ffield-C')

    fj = open('ffield.json','w')
    # j = {'p':p,'m':[],'bo_layer':[],'zpe':[]}
    j = {'p':p,'m':None,
         'EnergyFunction':0,
         'MessageFunction':0, 
         'messages':1,
         'bo_layer':None,
         'mf_layer':None,
         'be_layer':None,
         'vdw_layer':None,
         'MolEnergy':{} ,
         'rcut':None,
         'rEquilibrium':None,
         'rcutBond':None}
    js.dump(j,fj,sort_keys=True,indent=2)
    fj.close()


def ii():
    p,zpe,spec,bonds,offd,angs,torp,hbs= read_lib(libfile='ffield')
    write_lib(p_,spec,bonds,offd,angs,torp,hbs,libfile='ffield_')



def j():
    lf = open('ffield.json','r')
    j = js.load(lf)
    p_ = j['p']
    m_ = j['m']
    bo_layer_ = j['bo_layer']
    lf.close()

    spec,bonds,offd,angs,torp,hbs = init_bonds(p_)
    write_lib(p_,spec,bonds,offd,angs,torp,hbs,libfile='ffield')


def jj():
    lf = open('ffield.json','r')
    j = js.load(lf)
    p_ = j['p']
    m_ = j['m']
    bo_layer = j['bo_layer']
    lf.close()

    spec,bonds,offd,angs,torp,hbs = init_bonds(p_)
    p,zpe,spec,bonds,offd,angs,torp,hbs= read_lib(libfile='ffield')

    system('mv ffield.json ffield_.json')
    fj = open('ffield.json','w')
    j = {'p':p,'m':m_,'bo_layer':bo_layer,'zpe':None}
    js.dump(j,fj,sort_keys=True,indent=2)
    fj.close()


def t():
    lf = open('ffield.json','r')
    j = js.load(lf)
    p_ = j['p']
    m_ = j['m']
    bo_layer = j['bo_layer']
    lf.close()

    p = {}
    for key in p_:
        k = key.split('_')[0]
        if k=='n.u.':
           continue
        if k in ['V1','V2','V3','tor1','cot1']:
           k_ = key.split('_')[1]
           k2 = 'X' + k_[1:-1] + 'X'
           key_ = k + '_' + k2
           p[key_] = p_[key]
        else:
           p[key] = p_[key]


    system('mv ffield.json ffield_.json')
    fj = open('ffield.json','w')
    j = {'p':p,'m':m_,'bo_layer':bo_layer,'zpe':None}
    js.dump(j,fj,sort_keys=True,indent=2)
    fj.close()


def s():
    lf = open('ffield.json','r')
    j = js.load(lf)
    p  = j['p']
    m = j['m']
    bo_layer = j['bo_layer']
    lf.close()
    # spec,bonds,offd,angs,torp,hbs = init_bonds(p)

    m_ = {}
    for key in m:
        if key[1] == '1':
           m_[key] = m[key]

    system('mv ffield.json ffield_.json')
    fj = open('ffield.json','w')
    j = {'p':p,'m':m_,'bo_layer':bo_layer,'zpe':None}
    js.dump(j,fj,sort_keys=True,indent=2)
    fj.close()

    # cons=['val','vale',
    #       # 'ovun1', 'ovun2','ovun3','ovun4',
    #       # 'ovun5','ovun6','ovun7','ovun8',
    #       # 'lp2', # 'lp1',
    #       'lp3',
    #       # 'bo1','bo2','bo3','bo4','bo5','bo6',
    #       'cot1','cot2',
    #       'coa1','coa2','coa3','coa4',
    #       'pen1','pen2','pen3','pen4',
    #       #'Devdw','rvdw',# 'gammaw',
    #       'Dehb','rohb','hb1','hb2','hbtol',
    #       'Depi','Depp','cutoff','acut',
    #       #'val1_O-O-O','val1_O-O-N','val1_H-C-O','val2_H-C-H','val2_H-C-N',
    #       'val8','val9','val10', # 1.0,2.5,3.0
    #       ]

def v():
    p,zpe,spec,bonds,offd,angs,torp,hbs= read_lib(libfile='ffield')

    with open('ffield.json','r') as lf:
         j = js.load(lf)

    pv =   ['ovun1', 'ovun2','ovun3','ovun4',
            'ovun5','ovun6','ovun7','ovun8',
            'lp2',  'lp1', 
            'gammaw','vdw1','rvdw','Devdw','alfa']

    for k in p:
        key = k.split('_')[0]
        if key in pv:
           j['p'][k] = p[k]

    with open('ffield_.json','w') as fj:
         # j = {'p':p,'m':m,'bo_layer':bo_layer,'zpe':zpe}
         js.dump(j,fj,sort_keys=True,indent=2)


def f(ffield='ffield.json'):
    with open(ffield,'r') as lf:
         j = js.load(lf)
         p_ = j['p']
         m_ = j['m']
         bo_layer = j['bo_layer']
    spec,bonds,offd,angs,torp,hbs = init_bonds(p_)
    cons   = ['val','vale','lp3','cutoff','acut','hbtol']
    p_g    = ['boc1','boc2','coa2','ovun6','lp1','lp3',
              'ovun7','ovun8','val6','val9','val10','tor2',
              'tor3','tor4','cot2','coa4','ovun4',               # 
              'ovun3','val8','coa3','pen2','pen3','pen4','vdw1',
              'cutoff','acut','hbtol']
    p_spec = ['valboc','ovun5',
              'lp2','boc4','boc3','boc5','rosi','ropi','ropp',
              'ovun2','val3','val5','atomic',
              'gammaw','gamma','mass','chi','mu',
              'Devdw','rvdw','alfa','valang','val','vale']
    p_offd = ['Devdw','rvdw','alfa','rosi','ropi','ropp']
    p_bond = ['Desi','Depi','Depp','bo5','bo6','ovun1',
              'be1','be2','bo3','bo4','bo1','bo2','corr13','ovcorr']
    p_ang  = ['theta0','val1','val2','coa1','val7','val4','pen1']
    p_tor  = ['V1','V2','V3','tor1','cot1']

    p_name = []
    for g in p_g: 
        p_name.append(g)
    for s in spec:
        for k in p_spec:
            p_name.append(k+'_'+s)
    for bd in bonds:
        for k in p_bond:
            p_name.append(k+'_'+bd)
    for bd in offd:
        for k in p_offd:
            p_name.append(k+'_'+bd)
    for ang in angs:
        for k in p_ang:
            p_name.append(k+'_'+ang)
    for tor in torp:
        for k in p_tor:
            p_name.append(k+'_'+tor)


def init_bonds(p_):
    spec,bonds,offd,angs,torp,hbs = [],[],[],[],[],[]
    for key in p_:
        # key = key.encode('raw_unicode_escape')
        # print(key)
        k = key.split('_')
        if k[0]=='bo1':
           bonds.append(k[1])
        elif k[0]=='rosi':
           kk = k[1].split('-')
           # print(kk)
           if len(kk)==2:
              if kk[0]!=kk[1]:
                 offd.append(k[1])
           elif len(kk)==1:
              spec.append(k[1])
        elif k[0]=='theta0':
           angs.append(k[1])
        elif k[0]=='tor1':
           torp.append(k[1])
        elif k[0]=='rohb':
           hbs.append(k[1])
    return spec,bonds,offd,angs,torp,hbs


if __name__ == '__main__':
   ''' use commond like ./gmd.py nvt --T=2800 to run it'''
   parser = argparse.ArgumentParser()
   argh.add_commands(parser, [q,i,ii,j,jj,s,t,v])
   argh.dispatch(parser)

