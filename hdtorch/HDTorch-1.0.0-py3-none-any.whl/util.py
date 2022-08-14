'''
Created on Apr 8, 2022

@author: wsimon
'''

import torch

def flipVectorValues(vector, vecType = 'bin'):
    '''turns 0 into 1 and 1 into 0'''
    if (vecType=='bin'):
        vectorFliped=(vector*(-1)+1)
    else:
        vectorFliped = vector * (-1)
    return(vectorFliped)

def xor( vec_a, vec_b):
    ''' xor between vec_a and vec_b'''
    vec_c = (torch.add(vec_a, vec_b) == 1).short()  # xor
    return vec_c

def xor_bipolar( vec_a, vec_b):
    ''' xor between vec_a and vec_b'''
    #vec_c = (torch.sub(vec_a, vec_b) != 0).short()  # 1
    vec_c = torch.sub(vec_a, vec_b)
    vec_c [vec_c!=0]= 1
    vec_c[vec_c == 0] = -1
    return vec_c

def rotateVec(mat,shifts):
    n_rows, n_cols = mat.shape
    arange1 = torch.arange(n_cols,device=mat.device).view(( 1,n_cols)).repeat((n_rows,1))
    arange2 = (arange1.unsqueeze(0) - shifts.unsqueeze(2)) % n_cols
    return torch.gather(mat.unsqueeze(0).expand(shifts.shape[0],-1,-1),2,arange2)

def normalizeAndDiscretizeData(data, min_val, max_val, numSegLevels):
    ''' normalize train and test data using normalization values from train set
    also discretize values to specific number of levels  given by numSegLevels'''
    
    #normalize and discretize train adn test data
    dataNorm = (data - min_val) / (max_val - min_val)
    dataDisc = torch.floor((numSegLevels - 1) * dataNorm)
    #check for outliers
    dataDisc[dataDisc >= numSegLevels] = numSegLevels - 1
    dataDisc[dataDisc < 0] = 0
    dataDisc[torch.isnan(dataDisc)] = 0
    #discr values to int
    return dataDisc.to(int)